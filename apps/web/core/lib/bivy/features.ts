// Copyright (c) 2023-present Plane Software, Inc. and contributors
// SPDX-License-Identifier: AGPL-3.0-only
// See the LICENSE file for details.
//
// Bivy feature flags — frontend types + fetcher.
// Per ADR 0007 (bivy repo: docs/decisions/0007-feature-flags-over-strip.md).
//
// The flag map is fetched once at app boot and stored in React context
// (see ./context.tsx). Components consume via the useBivy() hook (see
// apps/web/core/hooks/use-bivy.tsx) or the <FeatureGate> wrapper (see
// apps/web/core/components/bivy/feature-gate.tsx).

/**
 * Known Bivy feature flag names. Keep this list in sync with
 * apps/api/plane/settings/bivy_features.py and
 * docs/FEATURE_REGISTRY.md in the bivy repo.
 */
export type BivyFeatureName =
  | "cycles"
  | "modules"
  | "estimates"
  | "issue_types"
  | "views"
  | "analytics"
  | "drafts"
  | "intake"
  | "deploy_board"
  | "stickies"
  | "exporter";

/**
 * The full flag map. All known features as boolean keys.
 */
export type BivyFeatures = Record<BivyFeatureName, boolean>;

/**
 * API response shape from GET /api/v1/bivy/features
 */
export interface BivyFeaturesResponse {
  features: BivyFeatures;
}

/**
 * Default all-off feature map. Used as the initial state before the API
 * fetch completes — matches the Basecamp-simple v1 UX (everything hidden).
 */
export const DEFAULT_BIVY_FEATURES: BivyFeatures = {
  cycles: false,
  modules: false,
  estimates: false,
  issue_types: false,
  views: false,
  analytics: false,
  drafts: false,
  intake: false,
  deploy_board: false,
  stickies: false,
  exporter: false,
};

/**
 * Fetch the Bivy feature flag snapshot from the API.
 *
 * Throws on network errors or non-2xx responses. Callers should catch and
 * fall back to DEFAULT_BIVY_FEATURES (or the last known state) when the
 * fetch fails — graceful degradation to "everything off" is the right v1
 * behavior since OFF matches the Basecamp-simple default UX.
 */
export async function fetchBivyFeatures(): Promise<BivyFeatures> {
  const response = await fetch("/api/v1/bivy/features/", {
    method: "GET",
    headers: { Accept: "application/json" },
  });

  if (!response.ok) {
    throw new Error(
      `Failed to fetch Bivy features: ${response.status} ${response.statusText}`,
    );
  }

  const data = (await response.json()) as BivyFeaturesResponse;
  return data.features;
}
