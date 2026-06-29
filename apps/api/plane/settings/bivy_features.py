# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

"""Bivy feature flags.

Per ADR 0007 (bivy repo: docs/decisions/0007-feature-flags-over-strip.md),
Plane features that would otherwise be stripped to achieve Basecamp-simple
UX are instead hidden behind config-driven feature flags. Default OFF for
v1. Customers asking for a feature flip it on via environment variable.

Per-workspace overrides arrive in v1.5 — see ADR 0007 § "Per-workspace
overrides."

The flag map is consumed by:
- The `requires_feature` decorator in `plane.utils.bivy_features`
- The `/api/v1/bivy/features` API endpoint
- The frontend on app boot via `useBivy()`

See `docs/FEATURE_REGISTRY.md` in the bivy repo for the full per-flag
description, gates, and when-to-flip-on criteria.
"""

import os


def _bool_env(key: str, default: bool = False) -> bool:
    """Read a boolean from env. Accepts 1/0, true/false, yes/no, on/off."""
    raw = os.environ.get(key)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


BIVY_FEATURES = {
    "cycles":       _bool_env("FEATURE_CYCLES",       default=False),
    "modules":      _bool_env("FEATURE_MODULES",      default=False),
    "estimates":    _bool_env("FEATURE_ESTIMATES",    default=False),
    "issue_types":  _bool_env("FEATURE_ISSUE_TYPES",  default=False),
    "views":        _bool_env("FEATURE_VIEWS",        default=False),
    "analytics":    _bool_env("FEATURE_ANALYTICS",    default=False),
    "drafts":       _bool_env("FEATURE_DRAFTS",       default=False),
    "intake":       _bool_env("FEATURE_INTAKE",       default=False),
    "deploy_board": _bool_env("FEATURE_DEPLOY_BOARD", default=False),
    "stickies":     _bool_env("FEATURE_STICKIES",     default=False),
    "exporter":     _bool_env("FEATURE_EXPORTER",     default=False),
}
