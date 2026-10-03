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

### ADR-009 Thin LLM wrapper — Accepted; provider part superseded by ADR-013
One `structured()` function with per-task model config instead of a framework-level abstraction. Model IDs per task come from config (see ADR-013 for the provider and defaults). LangChain is pulled in only as LangGraph's dependency; its chains/agents are not used.

### ADR-010 PRAW for Reddit access — Proposed
PRAW handles OAuth, pagination and basic rate limiting, and is maintained. It runs inside Celery workers (sync is fine there). It is wrapped in a small `RedditClient` so normalisation and our stricter QPM ceiling live in one place. Fall back to raw `httpx` only if PRAW blocks something.

### ADR-011 Budget day and schedules in IST — Proposed
The user is in India and the Indian communities are primary. Daily reports run at 08:00 IST. The LLM token cap follows Groq's quota day (UTC), see ADR-013. All timestamps are still stored in UTC.

### ADR-012 Region filter instead of separate Indian/Global pages in MVP — Proposed
The Indian Reddit and Global Reddit pages are presets of Trend Explorer (`?region=IN|GLOBAL`). This avoids three near-identical pages; dedicated pages can come later if they need unique widgets.

### ADR-016 Same-origin API through the Next.js proxy — Accepted (2026-10-03)
The browser never calls FastAPI directly. `frontend/proxy.ts` (Next 16's renamed middleware) rewrites `/api/*` to `API_INTERNAL_URL` at runtime, and server components call the API with the user's cookie forwarded. Consequences: the session cookie is first-party, there is no CORS config, and `SameSite=Lax` covers CSRF for our JSON POSTs, so no CSRF-token machinery is needed. The API port isn't exposed publicly in prod.

### ADR-017 Sync SQLAlchemy 2 + psycopg 3 — Accepted (2026-10-03)
Celery workers are sync and FastAPI runs sync endpoints in its threadpool, so one sync session layer serves both. Async would double the patterns for no measurable gain at one-user scale.

### ADR-013 Groq free tier as the only LLM provider — Accepted (2026-10-03)
User constraint: no paid providers. Groq's free plan (no card) gives each model 30 RPM, 1K req/day, 8K TPM and 200K tokens/day (checked against console.groq.com/docs on 2026-10-03). Model roles: `openai/gpt-oss-20b` cheap, `openai/gpt-oss-120b` strong, `qwen/qwen3.8-27b` vision. All three support strict JSON-schema outputs. Because limits are per model, spreading tasks across the three roughly triples daily capacity (~480K usable tokens/day). Consequences: budget is tokens, not dollars; every call must fit in ~7K tokens; drafts are limited to ~15/day on the strong model; quality is below frontier models, which the critic and evals must account for. **Never add a credit card**: that switches the org to paid billing. Model IDs change often, so they live in config only.

### ADR-014 NSFW excluded entirely — Accepted (2026-10-03)
`over_18` posts are dropped at ingestion and never stored; NSFW subreddits can't be added. There is no toggle.

### ADR-015 Politics included in MVP — Accepted (2026-10-03)
Indian and global politics subreddits are monitored. The critic's sensitive-subject checks (politics, religion, caste, communal topics) apply to every draft for these subs, and opinion summaries must stay attributional ("commenters argue…"), never taking a side.
