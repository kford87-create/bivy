// Copyright (c) 2023-present Plane Software, Inc. and contributors
// SPDX-License-Identifier: AGPL-3.0-only
// See the LICENSE file for details.
//
// Bivy feature flags — React hook.
// Per ADR 0007 (bivy repo: docs/decisions/0007-feature-flags-over-strip.md).
//
// Usage:
//
//     import { useBivy } from "@/core/hooks/use-bivy";
//
//     export function MyComponent() {
//       const { features, isLoading } = useBivy();
//       if (!features.cycles) return null;
//       return <CyclesView />;
//     }
//
// For declarative gating, prefer <FeatureGate> (see
// apps/web/core/components/bivy/feature-gate.tsx) which wraps this hook.

import { useContext } from "react";

import { BivyContext, BivyContextValue } from "@/core/lib/bivy/context";

/**
 * Access the Bivy feature flag map + fetch status.
 *
 * Returns the current flags (defaults to all-off before the boot fetch
 * completes) plus loading/error state. Use the `isLoading` and `error`
 * fields to render appropriate fallbacks at the layout level if needed.
 *
 * Throws if used outside of a <BivyProvider>. Provider goes in
 * apps/web/app/provider.tsx alongside Plane's existing providers.
 */
export function useBivy(): BivyContextValue {
  const context = useContext(BivyContext);
  if (!context) {
    throw new Error(
      "useBivy() must be used within a <BivyProvider>. " +
        "Add the provider to apps/web/app/provider.tsx.",
    );
  }
  return context;
}
