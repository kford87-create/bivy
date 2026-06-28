// Copyright (c) 2023-present Plane Software, Inc. and contributors
// SPDX-License-Identifier: AGPL-3.0-only
// See the LICENSE file for details.
//
// Proman feature flags — React hook.
// Per ADR 0007 (proman repo: docs/decisions/0007-feature-flags-over-strip.md).
//
// Usage:
//
//     import { useProman } from "@/core/hooks/use-proman";
//
//     export function MyComponent() {
//       const { features, isLoading } = useProman();
//       if (!features.cycles) return null;
//       return <CyclesView />;
//     }
//
// For declarative gating, prefer <FeatureGate> (see
// apps/web/core/components/proman/feature-gate.tsx) which wraps this hook.

import { useContext } from "react";

import { PromanContext, PromanContextValue } from "@/core/lib/proman/context";

/**
 * Access the Proman feature flag map + fetch status.
 *
 * Returns the current flags (defaults to all-off before the boot fetch
 * completes) plus loading/error state. Use the `isLoading` and `error`
 * fields to render appropriate fallbacks at the layout level if needed.
 *
 * Throws if used outside of a <PromanProvider>. Provider goes in
 * apps/web/app/provider.tsx alongside Plane's existing providers.
 */
export function useProman(): PromanContextValue {
  const context = useContext(PromanContext);
  if (!context) {
    throw new Error(
      "useProman() must be used within a <PromanProvider>. " +
        "Add the provider to apps/web/app/provider.tsx.",
    );
  }
  return context;
}
