# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.
#
# ============================================================================
# BIVY PHASE 3 STEP 2 (2026-06-28)
# ============================================================================
# Cal.com booking auto-scaffold Celery worker.
# Per ADR 0002 (bivy repo: docs/decisions/0002-calcom-for-scheduling.md).
#
# Triggered by the Cal.com webhook receiver (apps/api/plane/api/views/
# calcom_webhook.py) once it has persisted a CalcomBookingEvent and verified
# the HMAC signature. This task does the actual project scaffolding —
# creating Plane work items from the BookingTemplate.
#
# Idempotency: the unique constraint on CalcomBookingEvent.calcom_booking_id
# guarantees we never process the same Cal.com booking twice. Workers that
# crash mid-task leave the event in 'processing' status; operator manually
# re-queues (v1.5 will add an auto-retry cleanup).
# ============================================================================

import logging
from datetime import timedelta

from celery import shared_task
from django.db import transaction
from django.utils import timezone

from plane.db.models import (
    BookingLink,
    CalcomBookingEvent,
    Issue,
    Project,
)

logger = logging.getLogger(__name__)


# Placeholder regex resolved by the worker. v1 supports a small fixed set;
# v1.5 can expand if customer demand justifies. Unknown placeholders are
# left literal (no failure).
SUPPORTED_PLACEHOLDERS = (
    "{client_name}",
    "{client_email}",
    "{booking_date}",
    "{booking_time}",
    "{booking_datetime}",
    "{project_name}",
)


def _resolve_placeholders(text: str, context: dict) -> str:
    """Replace supported placeholders in text. Unknown placeholders pass through."""
    if not text:
        return text
    result = text
    for placeholder in SUPPORTED_PLACEHOLDERS:
        key = placeholder.strip("{}")
        if key in context:
            result = result.replace(placeholder, str(context[key]))
    return result


def _build_context(event: CalcomBookingEvent, link: BookingLink) -> dict:
    """Build the placeholder-resolution context from the Cal.com webhook payload.

    Cal.com webhook payload shape (BOOKING_CREATED):
      {
        "triggerEvent": "BOOKING_CREATED",
        "payload": {
          "type": "<event_type_slug>",
          "title": "<event_type_title>",
          "startTime": "ISO8601",
          "endTime": "ISO8601",
          "attendees": [{"name": "...", "email": "...", ...}],
          ...
        }
      }
    Reference: https://cal.com/docs/core-features/webhooks
    """
    payload = event.payload.get("payload", event.payload)
    attendees = payload.get("attendees", [{}])
    primary_attendee = attendees[0] if attendees else {}
    start_iso = payload.get("startTime", "")

    return {
        "client_name": primary_attendee.get("name", "Client"),
        "client_email": primary_attendee.get("email", ""),
        "booking_date": start_iso[:10] if start_iso else "",
        "booking_time": start_iso[11:16] if len(start_iso) > 16 else "",
        "booking_datetime": start_iso,
        "project_name": link.project.name if link.project_id else "",
    }


@shared_task
def auto_scaffold_from_calcom_booking(event_id: str) -> dict:
    """Apply a BookingTemplate to a Plane project from a Cal.com booking.

    Args:
        event_id: UUID string of a CalcomBookingEvent row (status='received').

    Returns a small status dict — useful for tests and operator inspection.
    Side effects: Issue rows created in Plane, BookingLink counters updated,
    CalcomBookingEvent status advanced.
    """
    try:
        event = CalcomBookingEvent.objects.select_related(
            "booking_link__project",
            "booking_link__template",
        ).get(id=event_id)
    except CalcomBookingEvent.DoesNotExist:
        logger.error("auto_scaffold: event %s not found", event_id)
        return {"status": "missing"}

    # Already terminal? Idempotent no-op.
    if event.status in ("success", "failed", "ignored"):
        return {"status": event.status, "reason": "already_processed"}

    event.status = "processing"
    event.save(disable_auto_set_user=True, update_fields=["status", "updated_at"])

    link = event.booking_link

    # No BookingLink resolved — webhook arrived for an event type we don't
    # have configured. Log + mark ignored. Don't error out (Cal.com would
    # retry).
    if link is None:
        event.status = "ignored"
        event.error_message = "No BookingLink found for this Cal.com event_type_id"
        event.processed_at = timezone.now()
        event.save(
            disable_auto_set_user=True,
            update_fields=["status", "error_message", "processed_at", "updated_at"],
        )
        return {"status": "ignored", "reason": "no_booking_link"}

    if not link.enabled:
        event.status = "ignored"
        event.error_message = "BookingLink is disabled"
        event.processed_at = timezone.now()
        event.save(
            disable_auto_set_user=True,
            update_fields=["status", "error_message", "processed_at", "updated_at"],
        )
        return {"status": "ignored", "reason": "link_disabled"}

    template = link.template
    if template is None:
        # No template — log success with zero issues created. Customer chose
        # to receive bookings without scaffolding.
        _mark_event_success(event, link, [])
        return {"status": "success", "issues_created": 0, "reason": "no_template"}

    context = _build_context(event, link)
    created_ids = []

    try:
        with transaction.atomic():
            for item_spec in template.work_items:
                name_template = item_spec.get("title", "")
                name = _resolve_placeholders(name_template, context)
                if not name:
                    continue  # skip blank-name items

                # Compute target_date (Plane stores due as target_date)
                target_date = None
                offset_days = item_spec.get("due_offset_days")
                if offset_days is not None:
                    start_iso = context.get("booking_datetime", "")
                    if start_iso:
                        try:
                            from datetime import datetime
                            booking_dt = datetime.fromisoformat(
                                start_iso.replace("Z", "+00:00")
                            )
                            target_date = (booking_dt + timedelta(days=int(offset_days))).date()
                        except (ValueError, TypeError):
                            pass

                # NOTE: Plane's Issue model requires more fields than just name
                # in some configurations (sort_order, state defaults via
                # signals, etc.). Engineering should verify this Issue.objects.create
                # call against Plane's standard issue-creation flow once the
                # dev environment is running. If create() fails due to
                # missing required fields, swap to using Plane's IssueService
                # or whatever helper they use in the standard view layer.
                issue = Issue.objects.create(
                    project=link.project,
                    workspace=link.workspace,
                    name=name[:255],  # name max_length=255
                    target_date=target_date,
                )
                created_ids.append(str(issue.id))

                # Default assignee (M2M) — set if template specifies one
                if template.default_assignee_id:
                    issue.assignees.add(template.default_assignee_id)
    except Exception as e:
        logger.exception("auto_scaffold: failed event_id=%s", event_id)
        event.status = "failed"
        event.error_message = f"{type(e).__name__}: {str(e)[:1500]}"
        event.processed_at = timezone.now()
        event.save(
            disable_auto_set_user=True,
            update_fields=["status", "error_message", "processed_at", "updated_at"],
        )
        return {"status": "failed", "error": str(e)}

    _mark_event_success(event, link, created_ids)

    # TODO Phase 3 follow-up: post the kickoff message as a Plane comment on
    # the project. Requires picking the right Comment model (project comments
    # vs issue comments — Plane has both). Defer to a follow-up commit.
    if template.kickoff_message_body:
        kickoff = _resolve_placeholders(template.kickoff_message_body, context)
        logger.info(
            "auto_scaffold: kickoff message ready for event %s (posting deferred): %s",
            event_id,
            kickoff[:200],
        )

    return {
        "status": "success",
        "issues_created": len(created_ids),
        "issue_ids": created_ids,
    }


def _mark_event_success(event: CalcomBookingEvent, link: BookingLink, created_ids: list) -> None:
    """Persist success status + update BookingLink counters atomically."""
    with transaction.atomic():
        event.status = "success"
        event.created_issue_ids = created_ids
        event.processed_at = timezone.now()
        event.save(
            disable_auto_set_user=True,
            update_fields=[
                "status",
                "created_issue_ids",
                "processed_at",
                "updated_at",
            ],
        )

        # Update BookingLink denormalized counters
        link.total_bookings = link.total_bookings + 1
        link.last_booking_at = event.processed_at
        link.save(
            disable_auto_set_user=True,
            update_fields=["total_bookings", "last_booking_at", "updated_at"],
        )
