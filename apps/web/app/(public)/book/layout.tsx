/**
 * Bivy Phase 4 — public booking route layout.
 * Per ADR 0002 + dashboard handoff Q1=A (iframe Cal.com).
 *
 * Minimal layout — the PublicBookingPage component provides its own brand
 * shell + header + AGPL footer. This layout exists only because React
 * Router v7 requires a layout file for the route group.
 */

import { Outlet } from "react-router";

export default function PublicBookingLayout() {
  return <Outlet />;
}
