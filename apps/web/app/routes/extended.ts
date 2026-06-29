/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { layout, route } from "@react-router/dev/routes";
import type { RouteConfigEntry } from "@react-router/dev/routes";

export const extendedRoutes: RouteConfigEntry[] = [
  // Bivy: public booking page (Phase 4 wire-up of Phase 3 Step 6).
  // Unauthenticated; iframes Cal.com inside the Bivy brand shell.
  // Per ADR 0002 + dashboard handoff Q1=A.
  layout("./(public)/book/layout.tsx", [
    route("book/:workspaceSlug/:bookingSlug", "./(public)/book/page.tsx"),
  ]),
];
