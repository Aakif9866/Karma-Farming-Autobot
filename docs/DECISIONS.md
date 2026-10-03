# Architecture Decision Records

Format: context → decision → consequences. Status: Proposed / Accepted / Superseded.

### ADR-001 Docs before code — Accepted (2026-10-03)
Large scope, solo developer. All design docs come first, then implementation phase by phase with approval gates.

### ADR-002 Modular monolith, three processes — Proposed
Microservices would add network boundaries, deployments and contracts with no benefit at one-user scale. One backend codebase runs as `api` / `worker` / `beat` processes from one image. Modules stay separated by package boundaries. Splitting a module out later is possible because services don't share ORM sessions across module lines.

### ADR-003 Local embeddings (384-d) instead of an embeddings API — Proposed
Every post gets embedded, so the volume is high and an API would be the biggest recurring cost. A small local sentence-embedding model (via `fastembed`/ONNX, CPU-only, no torch) costs nothing per call. The candidate models (English `bge-small-en-v1.5` vs multilingual `paraphrase-multilingual-MiniLM-L12-v2`) are chosen in Phase 0 by a quick test on a Hinglish sample. Both are 384-d. Consequence: slightly lower quality than large API embeddings, which is acceptable for clustering.

### ADR-004 Small per-job LangGraph graphs, not one mega-graph — Proposed
Selective execution is a requirement, and most steps are deterministic. Separate graphs (`collect_cycle`, `daily_report`, `generate_drafts`, `analyze_*`) share node functions. `collect_cycle` may be a plain Celery chain (no LLM, no need for graph semantics). LangGraph is used where checkpoints/interrupts/branching pay off (`daily_report`, `generate_drafts`, `analyze_*`).

### ADR-005 Celery + Redis for background jobs — Proposed
This was requested in the spec, it is mature, and beat gives scheduling. Alternatives (`arq`, APScheduler-in-process) are lighter, but Celery's retries, routing and visibility are worth it once there are 6+ periodic jobs. Redis doubles as the LLM output cache.

### ADR-006 No media storage or rehosting — Proposed
For copyright and cost reasons, previews are fetched transiently for pHash/OCR/vision and then discarded. Only derived features + Reddit URLs are stored.

### ADR-007 MVP publishing = copy & link, API publishing later — Proposed
API publishing adds OAuth auth-code flow, token encryption and abuse risk. MVP: copy to clipboard + open Reddit submit page + paste back the post URL to link it. API publishing (one click per approved item) comes in a later phase if wanted.

### ADR-008 Single-user MVP — Proposed
No multi-tenancy or signup. The `users` table exists and ownership FKs are present so multi-user can come later without schema rewrites.

### ADR-009 Thin LLM wrapper, Anthropic as default provider — Proposed
One `structured()` function with per-task model config instead of a framework-level abstraction. Defaults: `claude-haiku-4-5` (cheap tasks), `claude-sonnet-5-5` (generation, vision). A second provider adapter is added only when needed. LangChain is pulled in only as LangGraph's dependency; its chains/agents are not used.

### ADR-010 PRAW for Reddit access — Proposed
PRAW handles OAuth, pagination and basic rate limiting, and is maintained. It runs inside Celery workers (sync is fine there). It is wrapped in a small `RedditClient` so normalisation and our stricter QPM ceiling live in one place. Fall back to raw `httpx` only if PRAW blocks something.

### ADR-011 Budget day and schedules in IST — Proposed
The user is in India and the Indian communities are primary. Daily reports run at 08:00 IST; the budget resets at 00:00 IST. All timestamps are still stored in UTC.

### ADR-012 Region filter instead of separate Indian/Global pages in MVP — Proposed
The Indian Reddit and Global Reddit pages are presets of Trend Explorer (`?region=IN|GLOBAL`). This avoids three near-identical pages; dedicated pages can come later if they need unique widgets.
