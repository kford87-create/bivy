# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.
#
# Proman Phase 3 Step 7 — BookingLink + BookingTemplate management URLs.

from django.urls import path

from plane.api.views.booking import (
    BookingLinkViewSet,
    BookingTemplateViewSet,
    CalcomBookingEventReadOnlyViewSet,
)

urlpatterns = [
    # Booking links — workspace-scoped, optionally filtered by ?project_id=
    path(
        "workspaces/<slug:workspace_slug>/proman/booking-links/",
        BookingLinkViewSet.as_view({"get": "list", "post": "create"}),
        name="proman-booking-links-list",
    ),
    path(
        "workspaces/<slug:workspace_slug>/proman/booking-links/<uuid:pk>/",
        BookingLinkViewSet.as_view(
            {
                "get": "retrieve",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="proman-booking-links-detail",
    ),
    # Templates — workspace-scoped
    path(
        "workspaces/<slug:workspace_slug>/proman/booking-templates/",
        BookingTemplateViewSet.as_view({"get": "list", "post": "create"}),
        name="proman-booking-templates-list",
    ),
    path(
        "workspaces/<slug:workspace_slug>/proman/booking-templates/<uuid:pk>/",
        BookingTemplateViewSet.as_view(
            {
                "get": "retrieve",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="proman-booking-templates-detail",
    ),
    # Activity feed events — read-only
    path(
        "workspaces/<slug:workspace_slug>/proman/booking-events/",
        CalcomBookingEventReadOnlyViewSet.as_view({"get": "list"}),
        name="proman-booking-events-list",
    ),
    path(
        "workspaces/<slug:workspace_slug>/proman/booking-events/<uuid:pk>/",
        CalcomBookingEventReadOnlyViewSet.as_view({"get": "retrieve"}),
        name="proman-booking-events-detail",
    ),
]
