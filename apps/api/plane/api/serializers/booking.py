# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.
#
# Bivy Phase 3 Step 7 — DRF serializers for BookingLink + BookingTemplate.
# Per ADR 0002 and dashboard handoff Q2=C (hybrid per-project + workspace UI).

from rest_framework import serializers

from plane.db.models import BookingLink, BookingTemplate, CalcomBookingEvent


class BookingTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingTemplate
        fields = [
            "id",
            "workspace",
            "name",
            "description",
            "work_items",
            "kickoff_message_subject",
            "kickoff_message_body",
            "default_assignee",
            "is_default",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class BookingLinkSerializer(serializers.ModelSerializer):
    template_name = serializers.CharField(source="template.name", read_only=True)
    project_name = serializers.CharField(source="project.name", read_only=True)

    class Meta:
        model = BookingLink
        fields = [
            "id",
            "workspace",
            "project",
            "project_name",
            "slug",
            "calcom_event_type_id",
            "calcom_event_type_slug",
            "template",
            "template_name",
            "enabled",
            "last_booking_at",
            "total_bookings",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "project_name",
            "template_name",
            "last_booking_at",
            "total_bookings",
            "created_at",
            "updated_at",
        ]


class CalcomBookingEventSerializer(serializers.ModelSerializer):
    """Read-only — events are written by the webhook receiver, never via API."""

    booking_link_slug = serializers.CharField(
        source="booking_link.slug", read_only=True, default=None
    )
    project_name = serializers.CharField(
        source="booking_link.project.name", read_only=True, default=None
    )

    class Meta:
        model = CalcomBookingEvent
        fields = [
            "id",
            "calcom_booking_id",
            "calcom_event_type_id",
            "booking_link",
            "booking_link_slug",
            "project_name",
            "status",
            "created_issue_ids",
            "error_message",
            "processed_at",
            "created_at",
        ]
        read_only_fields = fields  # entirely read-only
