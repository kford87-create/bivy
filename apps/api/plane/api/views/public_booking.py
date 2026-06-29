# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.
#
# Proman Phase 3 Step 6 — public booking-link lookup endpoint.
# Per ADR 0002 + dashboard handoff Q1=A (iframe Cal.com).
#
# Unauthenticated GET endpoint that resolves a public booking URL
# (workspace_slug, booking_link_slug) → the Cal.com event-type slug to
# iframe. Returns minimal metadata for branding the booking page.

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from plane.db.models import BookingLink, Workspace


class PublicBookingLinkEndpoint(APIView):
    """GET /api/v1/proman/book/<workspace_slug>/<booking_slug>/

    Public, unauthenticated. Returns the Cal.com event-type slug for the
    booking page to embed, plus minimal branding metadata (project name,
    workspace name) so the page can render without a separate fetch.

    404 if the workspace or BookingLink doesn't exist or is disabled.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, workspace_slug, booking_slug):
        try:
            workspace = Workspace.objects.get(slug=workspace_slug)
        except Workspace.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        try:
            link = (
                BookingLink.objects.select_related("project", "workspace")
                .get(workspace=workspace, slug=booking_slug, enabled=True)
            )
        except BookingLink.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        if not link.calcom_event_type_slug:
            # Booking link exists but Cal.com event type not yet wired.
            # Return a structured response so the frontend can render
            # "this booking page is being set up" rather than a 404.
            return Response(
                {
                    "workspace_name": workspace.name,
                    "project_name": link.project.name,
                    "calcom_event_type_slug": None,
                    "calcom_event_type_id": None,
                    "status": "not_configured",
                },
                status=200,
            )

        return Response(
            {
                "workspace_name": workspace.name,
                "project_name": link.project.name,
                "calcom_event_type_slug": link.calcom_event_type_slug,
                "calcom_event_type_id": link.calcom_event_type_id,
                "status": "ready",
            },
            status=200,
        )
