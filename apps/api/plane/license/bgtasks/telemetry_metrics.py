# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.
#
# ============================================================================
# PROMAN STRIP 0001 (2026-06-28)
# ============================================================================
# This file is the no-op replacement for Plane's telemetry metrics module.
# Per ADR 0004, Proman strips the OTEL-based telemetry while preserving the
# function signatures so calling code (register_instance.py) doesn't break.
#
# Original file: 381 lines, exported `push_instance_metrics` as a Celery task
# that collected Plane instance metrics and pushed them to an OTEL collector.
#
# Reasons:
# - Self-hosted Proman customers should not phone home.
# - Aligns with our "open-source, no surveillance" positioning.
# - Configurable OTEL endpoint defaults are too easy to leak data to Plane.so
#   on a fresh install.
#
# If we ever want our own telemetry (opt-in, transparent, with consent), build
# it in a new app (e.g. plane.telemetry) rather than reactivating this file.
# ============================================================================

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


def _create_otlp_metric_exporter():
    """No-op stub. Replaced by Proman strip 0001 (ADR 0004)."""
    return None


def _collect_and_push_metrics() -> None:
    """No-op stub. Replaced by Proman strip 0001 (ADR 0004).

    Proman does not push telemetry. If you want your own self-host telemetry,
    point a separate OTEL collector at your install via standard environment
    variables and instrument your code in a new module.
    """
    logger.debug("Telemetry push skipped — Proman stripped this per ADR 0004.")
    return None


@shared_task
def push_instance_metrics():
    """No-op Celery task. Replaced by Proman strip 0001 (ADR 0004).

    Signature preserved so callers (e.g. register_instance management command)
    don't fail. Calling .delay() on this task succeeds and does nothing.
    """
    logger.debug("push_instance_metrics called — no-op (Proman strip 0001).")
    return None
