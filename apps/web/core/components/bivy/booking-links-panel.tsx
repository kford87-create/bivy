// Copyright (c) 2023-present Plane Software, Inc. and contributors
// SPDX-License-Identifier: AGPL-3.0-only
// See the LICENSE file for details.
//
// Bivy Phase 3 Step 7 — Booking Links panel (per-project Bookings tab).
// Per ADR 0002 + dashboard handoff Q2=C (hybrid).
//
// Renders within a Plane project's tab strip. Lists BookingLinks scoped to
// the current project, with create/edit/delete + copy public URL.
//
// Engineering follow-up (wire-up):
//   - Add a "Bookings" tab in the project view that renders this panel.
//   - Use Plane's existing project context to get workspaceSlug + projectId
//     instead of passing them as props.

import { JSX, useEffect, useState } from "react";

import {
  BookingLink,
  createBookingLink,
  deleteBookingLink,
  listBookingLinks,
  updateBookingLink,
} from "@/core/lib/bivy/booking-service";

export interface BookingLinksPanelProps {
  workspaceSlug: string;
  workspaceId: string;
  projectId: string;
  projectName: string;
  /** Public base URL for booking pages — e.g. "https://teambivy.com" */
  publicBaseUrl?: string;
}

export function BookingLinksPanel({
  workspaceSlug,
  workspaceId,
  projectId,
  projectName,
  publicBaseUrl = "",
}: BookingLinksPanelProps): JSX.Element {
  const [links, setLinks] = useState<BookingLink[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newSlug, setNewSlug] = useState("");

  async function reload() {
    setIsLoading(true);
    setError(null);
    try {
      const data = await listBookingLinks(workspaceSlug, {
        project_id: projectId,
      });
      setLinks(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Couldn't load booking links.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void reload();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [workspaceSlug, projectId]);

  async function handleCreate() {
    if (!newSlug.trim()) return;
    try {
      await createBookingLink(workspaceSlug, {
        workspace: workspaceId,
        project: projectId,
        slug: newSlug.trim(),
        enabled: true,
      });
      setNewSlug("");
      await reload();
    } catch (e) {
      setError(
        e instanceof Error ? e.message : "Couldn't create the booking link.",
      );
    }
  }

  async function handleToggle(link: BookingLink) {
    try {
      await updateBookingLink(workspaceSlug, link.id, {
        enabled: !link.enabled,
      });
      await reload();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Couldn't update the link.");
    }
  }

  async function handleDelete(link: BookingLink) {
    if (
      !confirm(
        `Delete the booking link "${link.slug}"? Past bookings stay in their projects.`,
      )
    )
      return;
    try {
      await deleteBookingLink(workspaceSlug, link.id);
      await reload();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Couldn't delete the link.");
    }
  }

  function publicUrlFor(link: BookingLink): string {
    return `${publicBaseUrl}/book/${workspaceSlug}/${link.slug}`;
  }

  function copy(text: string) {
    void navigator.clipboard?.writeText(text);
  }

  return (
    <section style={panelStyle}>
      <header style={{ marginBottom: "1.5rem" }}>
        <p style={sectionLabelStyle}>Booking links · {projectName}</p>
        <p style={{ color: "var(--ink-soft, #3d434a)", margin: 0 }}>
          Public URLs your clients use to book this project. Each one wraps a
          Cal.com event type and creates Plane work items when a slot is taken.
        </p>
      </header>

      {error ? <ErrorRow message={error} /> : null}

      <div style={{ marginBottom: "1.5rem" }}>
        <label style={labelStyle}>New booking link</label>
        <div style={{ display: "flex", gap: "0.6rem", alignItems: "stretch" }}>
          <input
            placeholder="slug-name"
            value={newSlug}
            onChange={(e) => setNewSlug(e.target.value)}
            style={inputStyle}
          />
          <button
            onClick={handleCreate}
            disabled={!newSlug.trim()}
            style={primaryBtnStyle}
          >
            Create
          </button>
        </div>
        <p style={{ margin: "0.5rem 0 0", fontSize: "0.82rem", color: "var(--ink-quiet, #6b7280)" }}>
          Slug must be unique within this workspace. After creating, link it to
          a Cal.com event type in the edit panel.
        </p>
      </div>

      {isLoading ? (
        <p style={{ color: "var(--ink-quiet, #6b7280)" }}>Loading…</p>
      ) : links.length === 0 ? (
        <EmptyState />
      ) : (
        <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
          {links.map((link) => (
            <li key={link.id} style={rowStyle}>
              <div style={{ flex: 1 }}>
                <p style={{ margin: "0 0 0.2rem", fontWeight: 600 }}>
                  /{link.slug}{" "}
                  <span
                    style={{
                      fontSize: "0.78rem",
                      color: link.enabled
                        ? "var(--accent, #0a7c61)"
                        : "var(--ink-quiet, #6b7280)",
                    }}
                  >
                    · {link.enabled ? "enabled" : "disabled"}
                  </span>
                </p>
                <p style={metaStyle}>
                  {link.total_bookings} booking
                  {link.total_bookings === 1 ? "" : "s"}
                  {link.last_booking_at
                    ? ` · last ${new Date(link.last_booking_at).toLocaleDateString()}`
                    : " · no bookings yet"}
                </p>
                {link.calcom_event_type_slug ? (
                  <p style={metaStyle}>
                    Cal.com event:{" "}
                    <code>{link.calcom_event_type_slug}</code>
                  </p>
                ) : (
                  <p style={{ ...metaStyle, color: "var(--warn, #b91c1c)" }}>
                    Not linked to a Cal.com event type yet
                  </p>
                )}
              </div>
              <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
                <button
                  onClick={() => copy(publicUrlFor(link))}
                  style={ghostBtnStyle}
                  title="Copy public URL"
                >
                  Copy link
                </button>
                <button
                  onClick={() => handleToggle(link)}
                  style={ghostBtnStyle}
                >
                  {link.enabled ? "Disable" : "Enable"}
                </button>
                <button
                  onClick={() => handleDelete(link)}
                  style={dangerBtnStyle}
                  title="Delete this booking link"
                >
                  Delete
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

function EmptyState() {
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
      No booking links yet. Create one above to give clients a public URL.
    </div>
  );
}

function ErrorRow({ message }: { message: string }) {
  return (
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
      {message}
    </p>
  );
}

// ---------- Inline styles (carry forward DESIGN.md tokens via CSS vars) ----------

const panelStyle: React.CSSProperties = {
  padding: "1.5rem",
};

const sectionLabelStyle: React.CSSProperties = {
  fontSize: "0.78rem",
  textTransform: "uppercase",
  letterSpacing: "0.14em",
  color: "var(--accent, #0a7c61)",
  fontWeight: 600,
  margin: "0 0 0.4rem",
};

const labelStyle: React.CSSProperties = {
  fontSize: "0.85rem",
  fontWeight: 500,
  color: "var(--ink, #111418)",
  display: "block",
  marginBottom: "0.4rem",
};

const inputStyle: React.CSSProperties = {
  flex: 1,
  padding: "0.7rem 1rem",
  fontSize: "0.95rem",
  border: "1px solid var(--ink, #111418)",
  borderRadius: "6px",
  background: "var(--paper, #ffffff)",
  color: "var(--ink, #111418)",
};

const primaryBtnStyle: React.CSSProperties = {
  padding: "0.7rem 1.2rem",
  minHeight: 44,
  border: "1px solid var(--ink, #111418)",
  borderRadius: 6,
  background: "var(--ink, #111418)",
  color: "var(--paper, #ffffff)",
  fontSize: "0.92rem",
  fontWeight: 500,
  cursor: "pointer",
};

const ghostBtnStyle: React.CSSProperties = {
  padding: "0.55rem 0.9rem",
  minHeight: 44,
  border: "1px solid var(--rule, #e4e4e7)",
  borderRadius: 6,
  background: "transparent",
  color: "var(--ink-soft, #3d434a)",
  fontSize: "0.88rem",
  cursor: "pointer",
};

const dangerBtnStyle: React.CSSProperties = {
  ...ghostBtnStyle,
  color: "var(--warn, #b91c1c)",
  borderColor: "rgba(185, 28, 28, 0.4)",
};

const rowStyle: React.CSSProperties = {
  display: "flex",
  alignItems: "flex-start",
  gap: "1rem",
  padding: "1.1rem 0",
  borderBottom: "1px solid var(--rule-soft, #f0f0f1)",
};

const metaStyle: React.CSSProperties = {
  margin: "0.15rem 0 0",
  fontSize: "0.82rem",
  color: "var(--ink-quiet, #6b7280)",
};
