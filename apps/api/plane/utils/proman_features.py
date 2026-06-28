# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

"""Proman feature-flag helpers.

Per ADR 0007. Provides:

- `is_feature_enabled(flag)` — query the flag map by name.
- `requires_feature(flag)` — decorator for DRF view methods that returns
  HTTP 404 when the flag is OFF. 404 (not 403) is deliberate — the route
  should appear not to exist in installations where the feature is off.
- `get_features_snapshot()` — returns the full flag dict for the
  `/api/v1/proman/features` endpoint.

Usage:

    from plane.utils.proman_features import requires_feature

    class CycleViewSet(BaseViewSet):
        @requires_feature("cycles")
        def list(self, request, *args, **kwargs):
            ...

Future v1.5: extend `is_feature_enabled` to accept an optional
`workspace_id` and consult per-workspace overrides before falling back to
the global flag map.
"""

from functools import wraps
from typing import Callable

from rest_framework import status
from rest_framework.response import Response

from plane.settings.proman_features import PROMAN_FEATURES


class UnknownFeatureFlag(KeyError):
    """Raised when a decorator or check references a flag not in the registry."""


def is_feature_enabled(flag: str) -> bool:
    """Return True if the named feature flag is enabled.

    Raises UnknownFeatureFlag if the flag isn't in PROMAN_FEATURES — catches
    typos at startup or in code review rather than silently returning False.
    """
    if flag not in PROMAN_FEATURES:
        raise UnknownFeatureFlag(
            f"Unknown Proman feature flag: {flag!r}. "
            f"Known flags: {sorted(PROMAN_FEATURES.keys())}"
        )
    return PROMAN_FEATURES[flag]


def get_features_snapshot() -> dict:
    """Return a shallow copy of the current feature flag map.

    Used by the /api/v1/proman/features endpoint to ship the flag state to
    the frontend on app boot.
    """
    return dict(PROMAN_FEATURES)


def requires_feature(flag: str) -> Callable:
    """Decorator: return HTTP 404 if the named flag is OFF.

    Validates the flag name at decoration time so typos surface at import,
    not at the first request.
    """
    # Validate early — UnknownFeatureFlag if mistyped
    if flag not in PROMAN_FEATURES:
        raise UnknownFeatureFlag(
            f"@requires_feature({flag!r}) — unknown flag. "
            f"Known flags: {sorted(PROMAN_FEATURES.keys())}"
        )

    def decorator(view_method: Callable) -> Callable:
        @wraps(view_method)
        def wrapper(self, request, *args, **kwargs):
            if not is_feature_enabled(flag):
                return Response(
                    {"error": "Not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            return view_method(self, request, *args, **kwargs)

        return wrapper

    return decorator
