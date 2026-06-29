/**
 * Bivy Phase 4 — public booking route page.
 * Route: /book/:workspaceSlug/:bookingSlug
 * Per ADR 0002 + dashboard handoff Q1=A (iframe Cal.com).
 *
 * Unauthenticated. Renders PublicBookingPage which fetches the booking
 * metadata + iframes the Cal.com booking flow.
 */

import { useParams } from "react-router";

import { PublicBookingPage } from "@/core/components/bivy/public-booking-page";

export default function BookPage() {
  const params = useParams<{ workspaceSlug: string; bookingSlug: string }>();
  const workspaceSlug = params.workspaceSlug ?? "";
  const bookingSlug = params.bookingSlug ?? "";
  return (
    <PublicBookingPage
      workspaceSlug={workspaceSlug}
      bookingSlug={bookingSlug}
    />
  );
}
