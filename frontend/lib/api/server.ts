import "server-only";
import { cookies } from "next/headers";

const API_URL = process.env.API_INTERNAL_URL ?? "http://localhost:8000";

/** Server-side call to the FastAPI backend, forwarding the user's session cookie. */
export async function apiFetch(path: string, init?: RequestInit): Promise<Response> {
  const cookieHeader = (await cookies()).toString();
  return fetch(`${API_URL}/api/v1${path}`, {
    ...init,
    headers: { ...init?.headers, cookie: cookieHeader },
    cache: "no-store",
  });
}
