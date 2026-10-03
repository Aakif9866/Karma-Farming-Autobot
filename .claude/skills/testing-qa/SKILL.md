---
name: testing-qa
description: Testing and quality specialist. Use when writing or fixing tests (pytest, Vitest, Playwright), building fixtures and fakes (respx Reddit fixtures, FakeLLM), setting up CI checks, running lint/type checks, measuring coverage, performance checks, or LLM golden-set evals.
when_to_use: Triggers on "test", "pytest", "vitest", "playwright", "fixture", "mock", "CI failing", "coverage", "lint", "mypy", "eval", "regression".
paths: "backend/tests/**,frontend/**/*.test.*,frontend/e2e/**,.github/workflows/**"
---

# Testing & QA

Source of truth: `docs/TESTING_STRATEGY.md`.

## Responsibilities
- Unit tests for pure logic, integration tests with real Postgres/Redis, API tests via `httpx.AsyncClient`, graph tests with `FakeLLM`, Vitest component tests, Playwright e2e against the compose stack with the mock seed.
- Fixtures: synthetic Reddit responses in real shapes (`backend/tests/fixtures/reddit/*.json`), FakeLLM outputs per schema.
- CI gates: ruff, mypy, eslint, tsc, pytest, vitest, alembic check, playwright smoke, gitleaks, pip-audit, pnpm audit.

## Execution
1. Reproduce first: write the failing test, then fix.
2. Run the narrowest scope while iterating (`uv run pytest tests/unit/test_scoring.py -q`), then the full suite before commit.
3. Run lint + types (`uv run ruff check . && uv run mypy app`, `pnpm lint && pnpm typecheck`).
4. Report results honestly: paste the failing output; never claim green without running.

## Constraints
- **No network in PR tests.** `respx` strict mode for HTTP, socket guard for everything else. Real Groq/Reddit only in `-m eval` or `scripts/smoke_*`.
- **Never skip or delete a failing test to get green.** `xfail(reason=..., strict=True)` needs a linked issue.
- Mock data must be `source="mock"`; keep the test asserting mock rows can't be saved as `reddit`.
- No real Reddit user content in fixtures or evals; synthetic or paraphrased only.
- Time-dependent code takes an injected clock; tests never `sleep`.
- Coverage ≥ 80% on `intelligence/`, `ingestion/`, `services/`.

## Examples
- *"Test velocity calculation."* → two snapshots `(t0, score=100)`, `(t0+30min, score=160)` → expect 120.0/h; plus an edge case with Δt < 20 min → falls back to the previous snapshot.
- *"Playwright flow for drafts."* → seed mock DB → login → opportunities → "Generate drafts" (FakeLLM via `LLM_FAKE=1`) → approve is disabled while a placeholder remains → fill it → approve → audit log entry visible.
