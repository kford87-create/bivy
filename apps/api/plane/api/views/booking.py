# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.
#
# Proman Phase 3 Step 7 — BookingLink + BookingTemplate management API.
# Per ADR 0002 + dashboard handoff Q2=C (hybrid per-project + workspace).
#
# Authenticated endpoints. Workspace-scoped via URL path. Authorization
# inherited from Plane's existing workspace-membership middleware (only
# workspace members can see / mutate their workspace's booking resources).

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from plane.api.middleware.api_authentication import APIKeyAuthentication
from plane.api.serializers.booking import (
    BookingLinkSerializer,
    BookingTemplateSerializer,
    CalcomBookingEventSerializer,
)
from plane.db.models import (
    BookingLink,
    BookingTemplate,
    CalcomBookingEvent,
    Workspace,
)


class BookingTemplateViewSet(ModelViewSet):
    """CRUD for BookingTemplate, scoped to the workspace in the URL."""

    serializer_class = BookingTemplateSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [APIKeyAuthentication]

    def get_queryset(self):
        workspace_slug = self.kwargs.get("workspace_slug")
        return BookingTemplate.objects.filter(
            workspace__slug=workspace_slug,
        ).select_related("workspace", "default_assignee")

    def perform_create(self, serializer):
        workspace_slug = self.kwargs.get("workspace_slug")
        workspace = Workspace.objects.get(slug=workspace_slug)
        serializer.save(workspace=workspace)


class BookingLinkViewSet(ModelViewSet):
    """CRUD for BookingLink. Workspace-scoped via URL; optional project filter."""

    serializer_class = BookingLinkSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [APIKeyAuthentication]

    def get_queryset(self):
        workspace_slug = self.kwargs.get("workspace_slug")
        qs = BookingLink.objects.filter(
            workspace__slug=workspace_slug,
        ).select_related("workspace", "project", "template")

        project_id = self.request.query_params.get("project_id")
        if project_id:
            qs = qs.filter(project_id=project_id)
        return qs

    def perform_create(self, serializer):
        workspace_slug = self.kwargs.get("workspace_slug")
        workspace = Workspace.objects.get(slug=workspace_slug)
        serializer.save(workspace=workspace)


class CalcomBookingEventReadOnlyViewSet(ReadOnlyModelViewSet):
    """Read-only listing of CalcomBookingEvents for the activity feed.

    Powers the workspace home activity feed + per-project runs view.
    Filters supported via query params:
      ?booking_link_id=<uuid>   restrict to one booking link
      ?status=<state>           restrict to one lifecycle state
      ?limit=<int>              cap row count (default 50)
    """

    serializer_class = CalcomBookingEventSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [APIKeyAuthentication]

    def get_queryset(self):
        workspace_slug = self.kwargs.get("workspace_slug")
        qs = CalcomBookingEvent.objects.filter(
            workspace__slug=workspace_slug,
        ).select_related("booking_link__project").order_by("-created_at")

        booking_link_id = self.request.query_params.get("booking_link_id")
        if booking_link_id:
            qs = qs.filter(booking_link_id=booking_link_id)

        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)

        # Limit (cap at 200 to keep dashboard requests bounded)
        try:
            limit = int(self.request.query_params.get("limit", "50"))
        except ValueError:
            limit = 50
        limit = min(max(limit, 1), 200)

        return qs[:limit]
