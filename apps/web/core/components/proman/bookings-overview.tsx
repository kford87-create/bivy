// Copyright (c) 2023-present Plane Software, Inc. and contributors
// SPDX-License-Identifier: AGPL-3.0-only
// See the LICENSE file for details.
//
// Proman Phase 3 Step 7 — Workspace bookings overview (Q2=C hybrid half).
// Per ADR 0002 + dashboard handoff Q2=C.
//
// Workspace-level summary of bookings across all projects + the narrative
// activity feed (carries forward the Bookend dashboard pattern).
// Mounts on the workspace home page.

import { JSX, useEffect, useState } from "react";

import {
  BookingLink,
  CalcomBookingEvent,
  listBookingEvents,
  listBookingLinks,
} from "@/core/lib/proman/booking-service";

export interface BookingsOverviewProps {
  workspaceSlug: string;
}

export function BookingsOverview({ workspaceSlug }: BookingsOverviewProps): JSX.Element {
  const [links, setLinks] = useState<BookingLink[]>([]);
  const [events, setEvents] = useState<CalcomBookingEvent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setIsLoading(true);
    Promise.all([
      listBookingLinks(workspaceSlug),
      listBookingEvents(workspaceSlug, { limit: 25 }),
    ])
      .then(([linkData, eventData]) => {
        if (!cancelled) {
          setLinks(linkData);
          setEvents(eventData);
        }
      })
      .catch((e: Error) => {
        if (!cancelled)
          setError(e.message || "Couldn't load workspace bookings.");
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [workspaceSlug]);

  const totalBookings = links.reduce((sum, l) => sum + l.total_bookings, 0);
  const enabledLinks = links.filter((l) => l.enabled);

  return (
    <section style={{ padding: "1.5rem 0" }}>
      <header style={{ marginBottom: "1.5rem" }}>
        <p
          style={{
            fontSize: "0.78rem",
            textTransform: "uppercase",
            letterSpacing: "0.14em",
            color: "var(--accent, #0a7c61)",
            fontWeight: 600,
            margin: "0 0 0.4rem",
          }}
        >
          Bookings
        </p>
        <h2
          style={{
            fontSize: "clamp(1.6rem, 2.6vw, 2.1rem)",
            fontWeight: 600,
            letterSpacing: "-0.02em",
            margin: "0 0 0.4rem",
            lineHeight: 1.2,
          }}
        >
          {totalBookings} {totalBookings === 1 ? "booking" : "bookings"} across{" "}
          {enabledLinks.length} active{" "}
          {enabledLinks.length === 1 ? "link" : "links"}
        </h2>
      </header>

      {error ? (
        <p
          role="alert"
          style={{
            color: "var(--warn, #b91c1c)",
            background: "rgba(185, 28, 28, 0.05)",
            border: "1px solid var(--warn, #b91c1c)",
            borderRadius: 6,
            padding: "0.6rem 0.9rem",
            margin: "0 0 1rem",
            fontSize: "0.92rem",
          }}
        >
          {error}
        </p>
      ) : null}

      {isLoading ? (
        <p style={{ color: "var(--ink-quiet, #6b7280)" }}>Loading…</p>
      ) : (
        <>
          <h3
            style={{
              fontSize: "0.85rem",
              textTransform: "uppercase",
              letterSpacing: "0.1em",
              color: "var(--ink-quiet, #6b7280)",
              fontWeight: 600,
              margin: "1.5rem 0 0.8rem",
            }}
          >
            Recent activity
          </h3>
          {events.length === 0 ? (
            <EmptyActivity />
          ) : (
            <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
              {events.map((event) => (
                <ActivityRow key={event.id} event={event} />
              ))}
            </ul>
          )}
        </>
      )}
    </section>
  );
}

function ActivityRow({ event }: { event: CalcomBookingEvent }) {
  const when = new Date(event.created_at).toLocaleString();
  const isFailure = event.status === "failed" || event.status === "ignored";

  // Best-effort narrative copy from the payload. Falls back to a neutral
  // form when fields are missing.
  const attendees =
    (event as unknown as { payload?: { payload?: { attendees?: Array<{ name?: string }> } } })
      .payload?.payload?.attendees ?? [];
  const attendeeName = attendees[0]?.name ?? "Someone";

  return (
    <li
      style={{
        padding: "1rem 0",
        borderBottom: "1px solid var(--rule-soft, #f0f0f1)",
      }}
    >
      <p
        style={{
          margin: 0,
          fontSize: "0.85rem",
          color: "var(--ink-quiet, #6b7280)",
          fontVariantNumeric: "tabular-nums",
        }}
      >
        {when}
        {event.project_name ? (
          <> · {event.project_name}</>
        ) : (
          <> · no project resolved</>
        )}
      </p>
      <p style={{ margin: "0.25rem 0 0", fontSize: "0.95rem" }}>
        <strong>{attendeeName}</strong>{" "}
        {event.status === "success"
          ? "booked a slot. Project scaffolded."
          : event.status === "processing"
            ? "booked a slot. Scaffolding…"
            : event.status === "received"
              ? "booked a slot. Queued for scaffolding."
              : event.status === "ignored"
                ? `booked a slot. Ignored: ${event.error_message || "no matching booking link."}`
                : `booked a slot. Failed: ${event.error_message || "unknown error"}.`}
      </p>
      {event.created_issue_ids && event.created_issue_ids.length > 0 ? (
        <p
          style={{
            margin: "0.2rem 0 0",
            fontSize: "0.85rem",
            color: "var(--ink-soft, #3d434a)",
          }}
        >
          → {event.created_issue_ids.length} work item
          {event.created_issue_ids.length === 1 ? "" : "s"} created
        </p>
      ) : null}
      {isFailure && event.error_message ? (
        <p
          style={{
            margin: "0.2rem 0 0",
            fontSize: "0.82rem",
            color: "var(--warn, #b91c1c)",
          }}
        >
          {event.error_message}
        </p>
      ) : null}
    </li>
  );
}

function EmptyActivity() {
  return (
    <div
      style={{
        background: "var(--paper-2, #fafafa)",
        border: "1px solid var(--rule, #e4e4e7)",
        borderRadius: 10,
        padding: "2rem",
        textAlign: "center",
        color: "var(--ink-soft, #3d434a)",
      }}
    >
      Nothing's happened yet. Share a booking link to see activity here.
    </div>
  );
}
