# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

"""Proman feature-flag API endpoint.

GET /api/v1/proman/features

Returns the current feature flag map for frontend consumption on app boot.
Per ADR 0007 in the proman repo.

Unauthenticated — the flag set is not sensitive (it describes which features
this install ships) and the frontend needs it before the user has logged in
(determines which login flows / signup paths to show).
"""

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from plane.utils.proman_features import get_features_snapshot


class PromanFeaturesEndpoint(APIView):
    """Return the Proman feature flag snapshot.

    Per ADR 0007. Frontend reads this once at app boot and stores the
    result in React context (see apps/web/core/lib/proman/context.tsx).
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        return Response({"features": get_features_snapshot()})
