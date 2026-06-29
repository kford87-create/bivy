// Copyright (c) 2023-present Plane Software, Inc. and contributors
// SPDX-License-Identifier: AGPL-3.0-only
// See the LICENSE file for details.
//
// Bivy feature flags — React context provider.
// Per ADR 0007 (bivy repo: docs/decisions/0007-feature-flags-over-strip.md).
//
// Fetches the flag map once at app boot and makes it available to all
// descendants. Consumers use useBivy() (see apps/web/core/hooks/use-bivy.tsx)
// or <FeatureGate> (see apps/web/core/components/bivy/feature-gate.tsx).
//
// INTEGRATION:
// Wrap the app's root with <BivyProvider> alongside Plane's existing
// providers. See apps/web/app/provider.tsx — add a wrapper there once this
// scaffolding is in place. Step 2 of Phase 2 leaves provider wiring as a
// follow-up task so this commit doesn't entangle with Plane's provider
// composition.

import { createContext, ReactNode, useEffect, useState } from "react";

import {
  DEFAULT_BIVY_FEATURES,
  fetchBivyFeatures,
  BivyFeatures,
} from "./features";

export interface BivyContextValue {
  /** Current feature flag map. Defaults to all-off until fetch completes. */
  features: BivyFeatures;
  /** True while the initial fetch is in flight. */
  isLoading: boolean;
  /** Set if the fetch errored; consumer can show a banner or just use defaults. */
  error: Error | null;
  /** Refetch the feature map (useful if features can change at runtime in v1.5+). */
  refetch: () => Promise<void>;
}

export const BivyContext = createContext<BivyContextValue>({
  features: DEFAULT_BIVY_FEATURES,
  isLoading: true,
  error: null,
  refetch: async () => {
    /* no-op default */
  },
});

interface BivyProviderProps {
  children: ReactNode;
  /** Override the initial map (useful for tests + SSR). */
  initialFeatures?: BivyFeatures;
  /** Skip the API fetch (useful for tests). */
  skipFetch?: boolean;
}

export function BivyProvider({
  children,
  initialFeatures = DEFAULT_BIVY_FEATURES,
  skipFetch = false,
}: BivyProviderProps) {
  const [features, setFeatures] = useState<BivyFeatures>(initialFeatures);
  const [isLoading, setIsLoading] = useState<boolean>(!skipFetch);
  const [error, setError] = useState<Error | null>(null);

  const refetch = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const next = await fetchBivyFeatures();
      setFeatures(next);
    } catch (e) {
      setError(e instanceof Error ? e : new Error(String(e)));
      // Graceful degradation: leave existing flags alone. All-off is the
      // safe default — matches the Basecamp-simple v1 UX.
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (skipFetch) return;
    void refetch();
    // Refetch is intentionally not in the deps — we want this to fire exactly
    // once on mount. Consumers can call refetch() explicitly if they need a
    // mid-session refresh.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [skipFetch]);

  return (
    <BivyContext.Provider value={{ features, isLoading, error, refetch }}>
      {children}
    </BivyContext.Provider>
  );
}
