// Copyright (c) 2023-present Plane Software, Inc. and contributors
// SPDX-License-Identifier: AGPL-3.0-only
// See the LICENSE file for details.
//
// Proman Phase 3 Step 5 — AGPL source-code link footer.
// Per AGPL §13: network-served modified AGPL software must offer source.
//
// Two source repositories must be linked (both AGPL-3.0 cores):
//   - Plane fork (Proman): https://github.com/kford87-create/plane
//   - Cal.com (bundled):   https://github.com/calcom/cal.com
//
// Renders a small, restrained line — `--ink-quiet` color, 0.82rem font.
// Doesn't compete with main content. Add to every authenticated AND public
// page's root layout.

import { JSX } from "react";

const PROMAN_FORK_URL = "https://github.com/kford87-create/plane";
const CALCOM_UPSTREAM_URL = "https://github.com/calcom/cal.com";

export interface AGPLFooterProps {
  /** Override the fork URL if Proman gets renamed / re-hosted. */
  promanForkUrl?: string;
  /** Override the Cal.com source link if we ever fork Cal.com too. */
  calcomUrl?: string;
  /** Extra className passthrough for layout-specific spacing. */
  className?: string;
}

export function AGPLFooter({
  promanForkUrl = PROMAN_FORK_URL,
  calcomUrl = CALCOM_UPSTREAM_URL,
  className = "",
}: AGPLFooterProps): JSX.Element {
  return (
    <footer
      className={`proman-agpl-footer ${className}`.trim()}
      style={{
        fontSize: "0.82rem",
        color: "var(--ink-quiet, #6b7280)",
        padding: "1rem 1.5rem",
        textAlign: "center",
        borderTop: "1px solid var(--rule-soft, #f0f0f1)",
      }}
    >
      Proman runs on{" "}
      <a
        href={promanForkUrl}
        target="_blank"
        rel="noopener noreferrer"
        style={{
          color: "var(--accent, #0a7c61)",
          textDecoration: "none",
        }}
      >
        Plane
      </a>{" "}
      and{" "}
      <a
        href={calcomUrl}
        target="_blank"
        rel="noopener noreferrer"
        style={{
          color: "var(--accent, #0a7c61)",
          textDecoration: "none",
        }}
      >
        Cal.com
      </a>{" "}
      (both AGPL-3.0).{" "}
      <a
        href={promanForkUrl}
        target="_blank"
        rel="noopener noreferrer"
        style={{
          color: "var(--ink-soft, #3d434a)",
          textDecoration: "underline",
          textDecorationThickness: "1px",
          textUnderlineOffset: "3px",
        }}
      >
        View source →
      </a>
    </footer>
  );
}
