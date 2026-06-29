# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.
#
# Proman Phase 3 Step 2 — Cal.com webhook URL pattern.

from django.urls import path

from plane.api.views import CalcomWebhookEndpoint

urlpatterns = [
    path(
        "proman/calcom-webhook/",
        CalcomWebhookEndpoint.as_view(http_method_names=["post"]),
        name="proman-calcom-webhook",
    ),
]
