import type { components } from "./schema";

// Generated from the backend's OpenAPI schema: run `pnpm gen:api` after backend API changes.
export type UserOut = components["schemas"]["UserOut"];
export type Readiness = components["schemas"]["Readiness"];

export type ApiError = { error: { code: string; message: string; details: Record<string, unknown> } };
