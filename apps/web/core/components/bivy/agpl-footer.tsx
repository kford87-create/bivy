// Copyright (c) 2023-present Plane Software, Inc. and contributors
// SPDX-License-Identifier: AGPL-3.0-only
// See the LICENSE file for details.
//
// Bivy Phase 3 Step 5 — AGPL source-code link footer.
// Per AGPL §13: network-served modified AGPL software must offer source.
//
// Two source repositories must be linked (both AGPL-3.0 cores):
//   - Plane fork (Bivy): https://github.com/kford87-create/bivy
//   - Cal.com (bundled):   https://github.com/calcom/cal.com
//
// Renders a small, restrained line — `--ink-quiet` color, 0.82rem font.
// Doesn't compete with main content. Add to every authenticated AND public
// page's root layout.

import { JSX } from "react";

const BIVY_FORK_URL = "https://github.com/kford87-create/bivy";
const CALCOM_UPSTREAM_URL = "https://github.com/calcom/cal.com";

export interface AGPLFooterProps {
  /** Override the fork URL if Bivy gets renamed / re-hosted. */
  bivyForkUrl?: string;
  /** Override the Cal.com source link if we ever fork Cal.com too. */
  calcomUrl?: string;
  /** Extra className passthrough for layout-specific spacing. */
  className?: string;
  /**
   * "block" renders a traditional bottom-of-page footer (used inside pages
   * that scroll, e.g. public booking page). "floating" renders a small
   * fixed-position link in the bottom-right corner — used at the app root
   * layout where Plane's h-screen overflow-hidden container leaves no
   * room for a traditional footer. Default: "block".
   */
  variant?: "block" | "floating";
}

export function AGPLFooter({
  bivyForkUrl = BIVY_FORK_URL,
  calcomUrl = CALCOM_UPSTREAM_URL,
  className = "",
  variant = "block",
}: AGPLFooterProps): JSX.Element {
  const isFloating = variant === "floating";
  const blockStyle: React.CSSProperties = {
    fontSize: "0.82rem",
    color: "var(--ink-quiet, #6b7280)",
    padding: "1rem 1.5rem",
    textAlign: "center",
    borderTop: "1px solid var(--rule-soft, #f0f0f1)",
  };
  const floatingStyle: React.CSSProperties = {
    position: "fixed",
    bottom: 8,
    right: 12,
    fontSize: "0.7rem",
    color: "var(--ink-quiet, #6b7280)",
    background: "rgba(255, 255, 255, 0.9)",
    padding: "0.25rem 0.65rem",
    borderRadius: 999,
    border: "1px solid var(--rule-soft, #f0f0f1)",
    pointerEvents: "auto",
    zIndex: 9999,
    backdropFilter: "blur(4px)",
  };
  return (
    <footer
      className={`bivy-agpl-footer ${className}`.trim()}
      style={isFloating ? floatingStyle : blockStyle}
    >
      Bivy runs on{" "}
      <a
        href={bivyForkUrl}
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
        href={bivyForkUrl}
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
