# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.
#
# ============================================================================
# PROMAN PHASE 3 STEP 1 (2026-06-28)
# ============================================================================
# Booking module data model. New tables added by the Proman fork; not part
# of upstream Plane.
#
# Per ADR 0002 (proman repo: docs/decisions/0002-calcom-for-scheduling.md),
# the scheduling substrate itself lives in bundled Cal.com. The models here
# map a Proman BookingLink → a Cal.com event type + a Plane project + a
# scaffold template. When Cal.com fires a BOOKING_CREATED webhook, the
# auto-scaffold worker reads the BookingLink, applies the BookingTemplate
# to the target project, and creates the scaffolded work items.
#
# `ScheduleEntry` from Phase 1 audit was dropped — Cal.com handles all
# scheduling primitives (availability, time zones, slot math). We just map
# the result onto a Plane project.
# ============================================================================

# Python imports
from django.conf import settings
from django.db import models

# Module imports
from .base import BaseModel


class BookingTemplate(BaseModel):
    """A scaffold template applied when a Cal.com booking lands on a project.

    Defines the work items + kickoff message that get auto-created on the
    target Plane project when a booking webhook arrives. A workspace can
    have many templates; each BookingLink references one template.

    `work_items` is a list of dicts. Each dict shape:
        {
            "title": "...",  # supports {client_name}, {booking_date} placeholders
            "description": "...",  # same placeholder support
            "due_offset_days": 7,  # set issue due_date = booking_date + N days
        }

    Placeholders are resolved by the auto-scaffold worker from the Cal.com
    webhook payload. Unknown placeholders are left literal.
    """

    workspace = models.ForeignKey(
        "db.Workspace",
        on_delete=models.CASCADE,
        related_name="booking_templates",
    )

    name = models.CharField(max_length=128)
    description = models.TextField(blank=True, default="")

    # The scaffold spec
    work_items = models.JSONField(default=list)
    kickoff_message_subject = models.CharField(max_length=256, blank=True, default="")
    kickoff_message_body = models.TextField(blank=True, default="")

    # Optional: who gets auto-assigned the new issues.
    default_assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",  # don't reverse-traverse from User
    )

    # Convenience flag — one template per workspace can be marked default.
    # The auto-scaffold worker uses this when a BookingLink doesn't pin a
    # specific template.
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Booking template"
        verbose_name_plural = "Booking templates"
        db_table = "booking_templates"
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.name} ({self.workspace_id})"


class BookingLink(BaseModel):
    """A public booking page tied to a Plane project + Cal.com event type.

    One BookingLink per (project, slug) combination within a workspace.
    The public URL is `proman.app/book/<workspace_slug>/<booking_slug>`
    (or whichever shape Phase 3 Q1 lands on — iframe / subdomain / clone).

    `calcom_event_type_id` mirrors the Cal.com event type's primary key.
    Nullable to allow creating a BookingLink before wiring up Cal.com
    (deferred Cal.com setup mode for v1 customers who only want PM features).
    """

    workspace = models.ForeignKey(
        "db.Workspace",
        on_delete=models.CASCADE,
        related_name="booking_links",
    )
    project = models.ForeignKey(
        "db.Project",
        on_delete=models.CASCADE,
        related_name="booking_links",
    )

    # Public URL slug; unique within workspace
    slug = models.SlugField(max_length=128)

    # Cal.com event type pointer; null until linked
    calcom_event_type_id = models.IntegerField(null=True, blank=True)
    calcom_event_type_slug = models.CharField(max_length=128, blank=True, default="")

    # Which template applies when bookings land here. PROTECT so accidentally
    # deleting a template that's in use doesn't break existing booking links.
    template = models.ForeignKey(
        BookingTemplate,
        on_delete=models.PROTECT,
        related_name="links",
        null=True,
        blank=True,
    )

    # Operational
    enabled = models.BooleanField(default=True)
    last_booking_at = models.DateTimeField(null=True, blank=True)
    total_bookings = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Booking link"
        verbose_name_plural = "Booking links"
        db_table = "booking_links"
        unique_together = (("workspace", "slug"),)
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.workspace_id}/{self.slug} → project {self.project_id}"
