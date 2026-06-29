# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.
#
# Bivy Phase 3 Step 6 — public booking-link URL pattern.

from django.urls import path

from plane.api.views import PublicBookingLinkEndpoint

urlpatterns = [
    path(
        "bivy/book/<slug:workspace_slug>/<slug:booking_slug>/",
        PublicBookingLinkEndpoint.as_view(http_method_names=["get"]),
        name="bivy-public-booking",
    ),
]
