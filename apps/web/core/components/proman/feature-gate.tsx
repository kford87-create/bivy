// Copyright (c) 2023-present Plane Software, Inc. and contributors
// SPDX-License-Identifier: AGPL-3.0-only
// See the LICENSE file for details.
//
// Proman feature flags — <FeatureGate> declarative wrapper.
// Per ADR 0007 (proman repo: docs/decisions/0007-feature-flags-over-strip.md).
//
// Usage (component gating):
//
//     <FeatureGate flag="cycles">
//       <CyclesSidebarItem />
//     </FeatureGate>
//
// Usage (route gating — render a 404 instead of null when the flag is off):
//
//     <FeatureGate flag="cycles" fallback={<NotFound />}>
//       <CyclesRoute />
//     </FeatureGate>
//
// Why declarative gating: most sidebar items, route components, and feature
// surfaces just need to render-or-not based on a flag. The hook + manual
// `if (!features.cycles) return null;` works, but a wrapper reads cleaner
// for the audit pass in Phase 2 step 3 where we gate 11 surfaces.

import { ReactNode } from "react";

import { useProman } from "@/core/hooks/use-proman";
import { PromanFeatureName } from "@/core/lib/proman/features";

interface FeatureGateProps {
  /** Which flag must be ON for children to render. */
  flag: PromanFeatureName;
  /** Children rendered when the flag is on. */
  children: ReactNode;
  /** Optional fallback when the flag is off. Default: render nothing. */
  fallback?: ReactNode;
  /** When true, render children during the initial loading window even though
   *  the flag is technically still "off" (avoids a brief flicker on app boot).
   *  Default false — we err on hiding because off matches the default UX. */
  renderWhileLoading?: boolean;
}

export function FeatureGate({
  flag,
  children,
  fallback = null,
  renderWhileLoading = false,
}: FeatureGateProps) {
  const { features, isLoading } = useProman();

  // During initial fetch, we don't yet know if the flag is on. Default to
  // hiding (matches v1 default-off UX); pass renderWhileLoading to override.
  if (isLoading && !renderWhileLoading) {
    return <>{fallback}</>;
  }

  if (!features[flag]) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
}
