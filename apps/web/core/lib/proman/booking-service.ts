// Copyright (c) 2023-present Plane Software, Inc. and contributors
// SPDX-License-Identifier: AGPL-3.0-only
// See the LICENSE file for details.
//
// Proman Phase 3 Steps 6 + 7 — frontend service for booking module API.
// Wraps the workspace-scoped REST endpoints.

export interface BookingLink {
  id: string;
  workspace: string;
  project: string;
  project_name: string;
  slug: string;
  calcom_event_type_id: number | null;
  calcom_event_type_slug: string;
  template: string | null;
  template_name: string | null;
  enabled: boolean;
  last_booking_at: string | null;
  total_bookings: number;
  created_at: string;
  updated_at: string;
}

export interface BookingTemplate {
  id: string;
  workspace: string;
  name: string;
  description: string;
  work_items: WorkItemSpec[];
  kickoff_message_subject: string;
  kickoff_message_body: string;
  default_assignee: string | null;
  is_default: boolean;
  created_at: string;
  updated_at: string;
}

export interface WorkItemSpec {
  title: string;
  description?: string;
  due_offset_days?: number;
}

export interface CalcomBookingEvent {
  id: string;
  calcom_booking_id: number;
  calcom_event_type_id: number | null;
  booking_link: string | null;
  booking_link_slug: string | null;
  project_name: string | null;
  status: "received" | "processing" | "success" | "failed" | "ignored";
  created_issue_ids: string[];
  error_message: string;
  processed_at: string | null;
  created_at: string;
}

export interface PublicBookingResolution {
  workspace_name: string;
  project_name: string;
  calcom_event_type_slug: string | null;
  calcom_event_type_id: number | null;
  status: "ready" | "not_configured";
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(path, {
    ...options,
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });
  if (!response.ok) {
    throw new Error(
      `Booking API request failed: ${response.status} ${response.statusText}`,
    );
  }
  return (await response.json()) as T;
}

// ---------- Public (unauthenticated) ----------

export async function resolvePublicBooking(
  workspaceSlug: string,
  bookingSlug: string,
): Promise<PublicBookingResolution> {
  return request<PublicBookingResolution>(
    `/api/v1/proman/book/${workspaceSlug}/${bookingSlug}/`,
    { method: "GET" },
  );
}

// ---------- BookingLink (authenticated workspace-scoped) ----------

export async function listBookingLinks(
  workspaceSlug: string,
  filters: { project_id?: string } = {},
): Promise<BookingLink[]> {
  const params = new URLSearchParams();
  if (filters.project_id) params.set("project_id", filters.project_id);
  const qs = params.toString() ? `?${params.toString()}` : "";
  return request<BookingLink[]>(
    `/api/v1/workspaces/${workspaceSlug}/proman/booking-links/${qs}`,
  );
}

export async function createBookingLink(
  workspaceSlug: string,
  data: Partial<BookingLink>,
): Promise<BookingLink> {
  return request<BookingLink>(
    `/api/v1/workspaces/${workspaceSlug}/proman/booking-links/`,
    { method: "POST", body: JSON.stringify(data) },
  );
}

export async function updateBookingLink(
  workspaceSlug: string,
  id: string,
  data: Partial<BookingLink>,
): Promise<BookingLink> {
  return request<BookingLink>(
    `/api/v1/workspaces/${workspaceSlug}/proman/booking-links/${id}/`,
    { method: "PATCH", body: JSON.stringify(data) },
  );
}

export async function deleteBookingLink(
  workspaceSlug: string,
  id: string,
): Promise<void> {
  await request<void>(
    `/api/v1/workspaces/${workspaceSlug}/proman/booking-links/${id}/`,
    { method: "DELETE" },
  );
}

// ---------- BookingTemplate ----------

export async function listBookingTemplates(
  workspaceSlug: string,
): Promise<BookingTemplate[]> {
  return request<BookingTemplate[]>(
    `/api/v1/workspaces/${workspaceSlug}/proman/booking-templates/`,
  );
}

export async function createBookingTemplate(
  workspaceSlug: string,
  data: Partial<BookingTemplate>,
): Promise<BookingTemplate> {
  return request<BookingTemplate>(
    `/api/v1/workspaces/${workspaceSlug}/proman/booking-templates/`,
    { method: "POST", body: JSON.stringify(data) },
  );
}

// ---------- Activity feed events ----------

export async function listBookingEvents(
  workspaceSlug: string,
  filters: {
    booking_link_id?: string;
    status?: CalcomBookingEvent["status"];
    limit?: number;
  } = {},
): Promise<CalcomBookingEvent[]> {
  const params = new URLSearchParams();
  if (filters.booking_link_id)
    params.set("booking_link_id", filters.booking_link_id);
  if (filters.status) params.set("status", filters.status);
  if (filters.limit) params.set("limit", String(filters.limit));
  const qs = params.toString() ? `?${params.toString()}` : "";
  return request<CalcomBookingEvent[]>(
    `/api/v1/workspaces/${workspaceSlug}/proman/booking-events/${qs}`,
  );
}
