# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.
#
# ============================================================================
# BIVY STRIP 0001 (2026-06-28)
# ============================================================================
# Modified per ADR 0004:
# - check_for_latest_version: GitHub API network call replaced with static
#   fallback (returns current_version unchanged). Plane's own latest-version
#   check phones api.github.com on every instance-register, which is a
#   third-party telemetry vector even though it's not plane.so directly.
# - push_instance_metrics.delay() call retained but the underlying task is
#   now a no-op (see telemetry_metrics.py in this strip set).
#
# Instance record creation logic is UNCHANGED — used internally by Plane.
# ============================================================================

# Python imports
import json
import secrets
import os

# Django imports
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

# Module imports
from plane.license.models import Instance, InstanceEdition
from plane.license.bgtasks.telemetry_metrics import push_instance_metrics


class Command(BaseCommand):
    help = "Check if instance is registered, else register (Bivy: no network calls)"

    def add_arguments(self, parser):
        parser.add_argument("machine_signature", type=str, help="Machine signature")

    def check_for_current_version(self):
        if os.environ.get("APP_VERSION", False):
            return os.environ.get("APP_VERSION")

        try:
            with open("package.json", "r") as file:
                data = json.load(file)
                return data.get("version", "v0.1.0")
        except Exception:
            self.stdout.write("Error checking for current version")
            return "v0.1.0"

    def check_for_latest_version(self, fallback_version):
        """Bivy strip 0001: network call to api.github.com removed.

        Original behavior queried Plane's GitHub releases API on every
        instance register to surface 'update available' UI. We don't ship
        that UI in Bivy (Phase 2 strip target FEATURE_ANALYTICS etc.
        hides the relevant settings page), so the network call has no
        consumer.

        Returns the fallback (current) version unchanged.
        """
        return fallback_version

    def handle(self, *args, **options):
        instance = Instance.objects.first()

        current_version = self.check_for_current_version()
        latest_version = self.check_for_latest_version(current_version)

        if instance is None:
            machine_signature = options.get("machine_signature", "machine-signature")

            if not machine_signature:
                raise CommandError("Machine signature is required")

            instance = Instance.objects.create(
                instance_name="Bivy Community",  # was: "Plane Community Edition"
                instance_id=secrets.token_hex(12),
                current_version=current_version,
                latest_version=latest_version,
                last_checked_at=timezone.now(),
                is_test=os.environ.get("IS_TEST", "0") == "1",
                edition=InstanceEdition.PLANE_COMMUNITY.value,
            )

            self.stdout.write(self.style.SUCCESS("Instance registered"))
        else:
            self.stdout.write(self.style.SUCCESS("Instance already registered"))

            instance.last_checked_at = timezone.now()
            instance.current_version = current_version
            instance.latest_version = latest_version
            instance.is_test = os.environ.get("IS_TEST", "0") == "1"
            instance.edition = InstanceEdition.PLANE_COMMUNITY.value
            instance.save()

        # No-op per ADR 0004 / telemetry_metrics.py strip
        push_instance_metrics.delay()

        return
