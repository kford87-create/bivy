# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

"""Bivy feature-flag API endpoint.

GET /api/v1/bivy/features

Returns the current feature flag map for frontend consumption on app boot.
Per ADR 0007 in the bivy repo.

Unauthenticated — the flag set is not sensitive (it describes which features
this install ships) and the frontend needs it before the user has logged in
(determines which login flows / signup paths to show).
"""

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from plane.utils.bivy_features import get_features_snapshot


class BivyFeaturesEndpoint(APIView):
    """Return the Bivy feature flag snapshot.

    Per ADR 0007. Frontend reads this once at app boot and stores the
    result in React context (see apps/web/core/lib/bivy/context.tsx).
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        return Response({"features": get_features_snapshot()})
