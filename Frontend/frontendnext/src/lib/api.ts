import { Ticket } from "@/types/ticket";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";

// ---------------------------------------------------------------------------
// Base fetch — cookies are sent automatically via credentials: "include"
// ---------------------------------------------------------------------------

async function fetchWithAuth(
  path: string,
  init: RequestInit = {}
): Promise<Response> {
  return fetch(`${API_BASE}${path}`, {
    ...init,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(init.headers as Record<string, string>),
    },
  });
}

// ---------------------------------------------------------------------------
// Auth API
// ---------------------------------------------------------------------------

export interface LoginCredentials {
  email: string;
  tenant_slug: string;
  password: string;
}

export interface UserInfo {
  email: string;
  full_name: string;
}

export interface SignupPayload {
  name: string;
  slug: string;
  admin_email: string;
  admin_password: string;
  admin_full_name?: string;
}

export interface SignupResult {
  id: string;
  name: string;
  slug: string;
  message: string;
}

export async function login(credentials: LoginCredentials): Promise<UserInfo> {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(credentials),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ?? `Login failed: ${res.status}`);
  }
  return res.json();
}

export async function logout(): Promise<void> {
  await fetch(`${API_BASE}/auth/logout`, {
    method: "POST",
    credentials: "include",
  });
}

export async function getMe(): Promise<UserInfo | null> {
  const res = await fetch(`${API_BASE}/auth/me`, { credentials: "include" });
  if (!res.ok) return null;
  return res.json();
}

export async function signup(payload: SignupPayload): Promise<SignupResult> {
  const res = await fetch(`${API_BASE}/tenants/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ?? `Registrierung fehlgeschlagen: ${res.status}`);
  }
  return res.json();
}

// ---------------------------------------------------------------------------
// Tickets API
// ---------------------------------------------------------------------------

export async function getTickets(): Promise<Ticket[]> {
  const res = await fetchWithAuth("/tickets/");
  if (!res.ok) {
    throw new Error(`Failed to fetch tickets: ${res.status}`);
  }
  return res.json();
}

export async function getTicketById(id: number): Promise<Ticket> {
  const res = await fetchWithAuth(`/tickets/${id}`);
  if (!res.ok) {
    throw new Error(`Failed to fetch ticket ${id}: ${res.status}`);
  }
  return res.json();
}
