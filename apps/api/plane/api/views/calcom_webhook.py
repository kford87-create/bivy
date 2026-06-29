# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.
#
# ============================================================================
# PROMAN PHASE 3 STEP 2 (2026-06-28)
# ============================================================================
# Cal.com webhook receiver.
# Per ADR 0002 (proman repo: docs/decisions/0002-calcom-for-scheduling.md).
#
# Receives BOOKING_CREATED / BOOKING_CANCELLED / BOOKING_RESCHEDULED webhooks
# from the bundled Cal.com instance, verifies the HMAC-SHA256 signature, and
# persists a CalcomBookingEvent + queues the auto-scaffold Celery task.
#
# Endpoint: POST /api/v1/proman/calcom-webhook/
# Auth: HMAC-SHA256 signature in the `X-Cal-Signature-256` header.
#       Secret read from env var CALCOM_WEBHOOK_SECRET (set in
#       /etc/proman/secrets.env on the server).
# ============================================================================

import hashlib
import hmac
import logging
import os

from django.db import IntegrityError
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from plane.bgtasks.calcom_auto_scaffold import auto_scaffold_from_calcom_booking
from plane.db.models import BookingLink, CalcomBookingEvent

logger = logging.getLogger(__name__)


def _verify_calcom_signature(secret: str, raw_body: bytes, signature_header: str) -> bool:
    """Constant-time HMAC-SHA256 verification of Cal.com webhook payload.

    Cal.com sends `X-Cal-Signature-256: <hex_digest>` per their webhook
    documentation (see https://cal.com/docs/core-features/webhooks).
    """
    if not secret or not signature_header:
        return False
    expected = hmac.new(
        key=secret.encode("utf-8"),
        msg=raw_body,
        digestmod=hashlib.sha256,
    ).hexdigest()
    # Strip an optional "sha256=" prefix if Cal.com adds it
    received = signature_header.removeprefix("sha256=").strip()
    return hmac.compare_digest(expected, received)


class CalcomWebhookEndpoint(APIView):
    """POST /api/v1/proman/calcom-webhook/

    Verifies HMAC signature, persists a CalcomBookingEvent (idempotently
    keyed on calcom booking id), and queues the auto-scaffold worker.

    Returns 200 OK on accepted events (including idempotent re-deliveries
    and ignored events) — Cal.com retries on non-2xx, so we want to ack
    fast and put any actual work in the background.

    Returns 401 on signature failure and 400 on malformed payload.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        secret = os.environ.get("CALCOM_WEBHOOK_SECRET", "")
        signature_header = request.headers.get("X-Cal-Signature-256", "")

        if not _verify_calcom_signature(
            secret=secret,
            raw_body=request.body,
            signature_header=signature_header,
        ):
            logger.warning(
                "calcom_webhook: signature verification failed (header_present=%s)",
                bool(signature_header),
            )
            return Response(
                {"error": "Signature verification failed"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Cal.com payload shape:
        #   {"triggerEvent": "BOOKING_CREATED", "payload": {...booking...}}
        body = request.data or {}
        trigger = body.get("triggerEvent", "")
        payload = body.get("payload", {}) or {}

        # We only auto-scaffold on BOOKING_CREATED. Cancellations + reschedules
        # are logged but don't trigger new project creation. v1.5 may add
        # reschedule handling (move the schedule entry but keep the project).
        if trigger != "BOOKING_CREATED":
            logger.info(
                "calcom_webhook: ignoring non-BOOKING_CREATED trigger=%s",
                trigger,
            )
            return Response({"received": True, "trigger": trigger, "action": "ignored"})

        calcom_booking_id = payload.get("id") or payload.get("bookingId")
        event_type_id = payload.get("eventTypeId") or payload.get("eventType", {}).get("id")

        if not calcom_booking_id:
            return Response(
                {"error": "Missing booking id in payload"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Resolve the BookingLink (may be None — that's fine, the worker
        # marks the event 'ignored').
        booking_link = None
        workspace = None
        if event_type_id:
            booking_link = (
                BookingLink.objects.select_related("workspace")
                .filter(calcom_event_type_id=event_type_id, enabled=True)
                .first()
            )
            if booking_link:
                workspace = booking_link.workspace

        # Persist the event. The unique constraint on calcom_booking_id is
        # our idempotency mechanism.
        try:
            event = CalcomBookingEvent.objects.create(
                workspace=workspace,
                booking_link=booking_link,
                calcom_booking_id=int(calcom_booking_id),
                calcom_event_type_id=event_type_id,
                payload=body,
                status="received",
            )
        except IntegrityError:
            # Duplicate delivery — Cal.com re-tried after we already
            # processed this booking. Ack with 200 so they stop retrying.
            logger.info(
                "calcom_webhook: duplicate delivery for booking_id=%s",
                calcom_booking_id,
            )
            return Response({"received": True, "action": "duplicate"})

        # Queue the auto-scaffold worker. Worker is responsible for
        # advancing event.status from 'received' → 'processing' → 'success' /
        # 'failed' / 'ignored'.
        auto_scaffold_from_calcom_booking.delay(str(event.id))

        return Response(
            {"received": True, "event_id": str(event.id), "action": "queued"},
            status=status.HTTP_200_OK,
        )
