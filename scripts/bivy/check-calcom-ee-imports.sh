#!/usr/bin/env bash
#
# Bivy Phase 3 Step 4 — Cal.com EE import guard.
# Per ADR 0002 (bivy repo: docs/decisions/0002-calcom-for-scheduling.md).
#
# Fails (exit 1) if any Bivy code references Cal.com's commercial-licensed
# EE directory. Cal.com's `packages/features/ee/` is under a separate
# Enterprise License; touching it would shift our license posture and costs
# us money once we cross 30 users.
#
# What this guard catches:
#   1. String imports referencing Cal.com EE paths (TS/JS).
#   2. Python references (in case we ever vendor Cal.com source).
#   3. Calls to known EE-only API surfaces (Teams, Orgs, Insights, Workflows).
#
# What this guard CAN'T catch:
#   - Runtime EE feature flag flips (Cal.com toggling EE behavior server-side).
#   - HTTP calls to /api/teams/* or /api/orgs/* (would need runtime traffic
#     inspection — out of scope for static lint).

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$PROJECT_ROOT"

# Directories to scan (Bivy's additions, not upstream Plane or vendored
# Cal.com).
SCAN_DIRS=(
  "apps/api/plane/api/views/calcom_webhook.py"
  "apps/api/plane/api/views/bivy_features.py"
  "apps/api/plane/bgtasks/calcom_auto_scaffold.py"
  "apps/api/plane/db/models/booking.py"
  "apps/api/plane/settings/bivy_features.py"
  "apps/api/plane/utils/bivy_features.py"
  "apps/web/core/lib/bivy"
  "apps/web/core/hooks/use-bivy.tsx"
  "apps/web/core/components/bivy"
)

# Patterns that flag commercial-license territory. Each match = build failure.
FORBIDDEN_PATTERNS=(
  "packages/features/ee"
  "@calcom/features/ee"
  "@calcom/ee"
  "/api/teams"
  "/api/organizations"
  "/api/insights"
  "/api/workflows"
)

FAILED=0

for path in "${SCAN_DIRS[@]}"; do
  if [ ! -e "$path" ]; then
    continue
  fi

  for pattern in "${FORBIDDEN_PATTERNS[@]}"; do
    if grep -rn --include="*.py" --include="*.ts" --include="*.tsx" --include="*.js" \
        --include="*.jsx" --include="*.yml" --include="*.yaml" \
        -e "$pattern" "$path" 2>/dev/null; then
      echo ""
      echo "❌ Forbidden Cal.com EE reference found: '$pattern'"
      echo "   Location: $path"
      echo "   Per ADR 0002, Bivy uses Cal.com's AGPL-3.0 core only."
      echo "   Multiplayer / EE features (Teams, Orgs, Insights, Workflows,"
      echo "   SSO/SAML) require a Cal.com commercial license + 30+ users."
      echo "   See: docs/decisions/0002-calcom-for-scheduling.md (bivy repo)"
      FAILED=1
    fi
  done
done

if [ "$FAILED" -ne 0 ]; then
  echo ""
  echo "Cal.com EE import check FAILED. Fix the references above before merging."
  exit 1
fi

echo "✓ Cal.com EE import check passed. No commercial-license boundary violations."
exit 0
