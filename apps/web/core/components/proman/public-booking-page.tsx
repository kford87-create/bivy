// Copyright (c) 2023-present Plane Software, Inc. and contributors
// SPDX-License-Identifier: AGPL-3.0-only
// See the LICENSE file for details.
//
// Proman Phase 3 Step 6 — Public booking page (Q1=A iframe Cal.com).
// Per ADR 0002 and dashboard handoff § Open design question Q1.
//
// Wraps the Cal.com booking page in Proman's brand shell. Visitor lands here
// (e.g. /book/<workspace>/<slug>), we look up the Cal.com event-type slug,
// and embed the Cal.com booking flow as an iframe.
//
// Route wiring (engineering follow-up):
//   apps/web/app/(public)/book/[workspaceSlug]/[bookingSlug]/route.tsx
//   loads this component and passes the route params.
//
// Cal.com URL pattern (matches docker-compose.proman.yml):
//   https://<host>/cal/<calcom_event_type_slug>
// The container hostname is internal; we serve through Plane's proxy.

import { JSX, useEffect, useState } from "react";

import {
  PublicBookingResolution,
  resolvePublicBooking,
} from "@/core/lib/proman/booking-service";

import { AGPLFooter } from "./agpl-footer";

const CALCOM_BASE_PATH = "/cal";

export interface PublicBookingPageProps {
  workspaceSlug: string;
  bookingSlug: string;
}

export function PublicBookingPage({
  workspaceSlug,
  bookingSlug,
}: PublicBookingPageProps): JSX.Element {
  const [resolution, setResolution] = useState<PublicBookingResolution | null>(
    null,
  );
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setIsLoading(true);
    resolvePublicBooking(workspaceSlug, bookingSlug)
      .then((data) => {
        if (!cancelled) setResolution(data);
      })
      .catch((e: Error) => {
        if (!cancelled)
          setError(
            e.message.includes("404")
              ? "This booking page doesn't exist."
              : "We couldn't load this booking page. Try again later.",
          );
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [workspaceSlug, bookingSlug]);

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        background: "var(--paper, #ffffff)",
        color: "var(--ink, #111418)",
        fontFamily:
          '"Hubot Sans", -apple-system, BlinkMacSystemFont, "Inter", system-ui, sans-serif',
      }}
    >
      <header
        style={{
          padding: "1.4rem 1.5rem",
          borderBottom: "1px solid var(--rule-soft, #f0f0f1)",
          display: "flex",
          alignItems: "center",
          gap: "0.5rem",
        }}
      >
        <span
          aria-hidden="true"
          style={{
            display: "inline-flex",
            alignItems: "center",
            justifyContent: "center",
            width: 28,
            height: 28,
            background: "var(--ink, #111418)",
            color: "var(--paper, #ffffff)",
            borderRadius: 6,
            fontWeight: 700,
            fontSize: "0.85rem",
          }}
        >
          ⌥
        </span>
        <span style={{ fontWeight: 600, fontSize: "1.15rem" }}>Proman</span>
      </header>

      <main
        style={{
          flex: 1,
          maxWidth: "52rem",
          margin: "0 auto",
          padding: "3rem 1.5rem",
          width: "100%",
        }}
      >
        {isLoading ? (
          <p style={{ color: "var(--ink-quiet, #6b7280)" }}>Loading…</p>
        ) : error ? (
          <ErrorState message={error} />
        ) : !resolution ? (
          <ErrorState message="Couldn't resolve this booking page." />
        ) : resolution.status === "not_configured" ? (
          <NotConfiguredState
            workspaceName={resolution.workspace_name}
            projectName={resolution.project_name}
          />
        ) : (
          <BookingFrame
            workspaceName={resolution.workspace_name}
            projectName={resolution.project_name}
            calcomEventTypeSlug={resolution.calcom_event_type_slug!}
          />
        )}
      </main>

      <AGPLFooter />
    </div>
  );
}

function BookingFrame({
  workspaceName,
  projectName,
  calcomEventTypeSlug,
}: {
  workspaceName: string;
  projectName: string;
  calcomEventTypeSlug: string;
}) {
  // Per Q1=A iframe Cal.com inside our shell. Cal.com renders its own
  // calendar UI; we wrap with our brand header and tagline.
  const calcomUrl = `${CALCOM_BASE_PATH}/${encodeURIComponent(calcomEventTypeSlug)}`;
  return (
    <div>
      <header style={{ marginBottom: "2rem" }}>
        <p
          style={{
            fontSize: "0.78rem",
            textTransform: "uppercase",
            letterSpacing: "0.14em",
            color: "var(--accent, #0a7c61)",
            fontWeight: 600,
            margin: "0 0 0.6rem",
          }}
        >
          {workspaceName}
        </p>
        <h1
          style={{
            fontSize: "clamp(1.6rem, 2.6vw, 2.1rem)",
            fontWeight: 600,
            letterSpacing: "-0.02em",
            margin: "0 0 0.6rem",
            lineHeight: 1.2,
          }}
        >
          Book a time for {projectName}
        </h1>
        <p
          style={{
            color: "var(--ink-soft, #3d434a)",
            fontSize: "1rem",
            margin: 0,
            lineHeight: 1.55,
          }}
        >
          Pick a slot below. We'll send you a confirmation by email, and{" "}
          {workspaceName} will see your booking land in their workspace.
        </p>
      </header>
      <iframe
        title={`Book a time for ${projectName}`}
        src={calcomUrl}
        style={{
          width: "100%",
          minHeight: "780px",
          border: "1px solid var(--rule, #e4e4e7)",
          borderRadius: "10px",
        }}
        loading="lazy"
      />
    </div>
  );
}

function NotConfiguredState({
  workspaceName,
  projectName,
}: {
  workspaceName: string;
  projectName: string;
}) {
  return (
    <div>
      <p
        style={{
          fontSize: "0.78rem",
          textTransform: "uppercase",
          letterSpacing: "0.14em",
          color: "var(--accent, #0a7c61)",
          fontWeight: 600,
          margin: "0 0 0.6rem",
        }}
      >
        {workspaceName}
      </p>
      <h1
        style={{
          fontSize: "clamp(1.6rem, 2.6vw, 2.1rem)",
          fontWeight: 600,
          letterSpacing: "-0.02em",
          margin: "0 0 1rem",
          lineHeight: 1.2,
        }}
      >
        {projectName} isn't accepting bookings yet
      </h1>
      <p
        style={{
          color: "var(--ink-soft, #3d434a)",
          fontSize: "1rem",
          lineHeight: 1.55,
          maxWidth: "44ch",
        }}
      >
        This booking page exists but hasn't been connected to a calendar yet.
        Reach out to {workspaceName} directly to schedule.
      </p>
    </div>
  );
}

function ErrorState({ message }: { message: string }) {
  return (
    <div>
      <h1
        style={{
          fontSize: "clamp(1.6rem, 2.6vw, 2.1rem)",
          fontWeight: 600,
          letterSpacing: "-0.02em",
          margin: "0 0 1rem",
          lineHeight: 1.2,
        }}
      >
        {message}
      </h1>
      <p style={{ color: "var(--ink-soft, #3d434a)" }}>
        If you think this is wrong, contact the person who sent you this link.
      </p>
    </div>
  );
}
