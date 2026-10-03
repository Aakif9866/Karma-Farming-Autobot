import { NextResponse, type NextRequest } from "next/server";

// Read at runtime (proxy runs on Node), so one image works in any environment.
const API_URL = process.env.API_INTERNAL_URL ?? "http://localhost:8000";
const SESSION_COOKIE = "kfa_session";

export function proxy(request: NextRequest) {
  const { pathname, search } = request.nextUrl;

  // Same-origin API: the browser talks to /api/*, we forward it to FastAPI (first-party cookie, no CORS).
  if (pathname.startsWith("/api/")) {
    return NextResponse.rewrite(new URL(pathname + search, API_URL));
  }

  // Optimistic check only; the (app) layout verifies the session with the API.
  if (pathname !== "/login" && !request.cookies.has(SESSION_COOKIE)) {
    return NextResponse.redirect(new URL("/login", request.url));
  }
  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
