# Security & Compliance

## Threat model (single-user, self-hosted)

| Asset | Threat | Mitigation |
|---|---|---|
| Reddit client secret, LLM API key | leak via repo/logs | env vars only; `.env` in `.gitignore`; `.env.example` has placeholders; log redaction filter for keys/tokens; `gitleaks` in CI |
| User's Reddit refresh token (L, publishing) | DB leak → account takeover | encrypted at rest (Fernet, key from `APP_ENCRYPTION_KEY` env); minimal scopes (`identity read submit`); revocable from Settings |
| The app itself | unauthenticated access to drafts/publishing | session auth (argon2 password hash, signed HTTP-only SameSite=Lax cookie, Secure in prod); same-origin API via the Next.js proxy, so there is no CORS and SameSite blocks cross-site POSTs (ADR-016); no public signup; login rate limit per email (10 per 5 min, Redis) |
| LLM pipelines | prompt injection via Reddit content | content passed as delimited data; schema-only outputs; models that read Reddit text have no tools; see [AI_AGENT_DESIGN.md](AI_AGENT_DESIGN.md) |
| Rendering Reddit text in UI | XSS | render as text / sanitised markdown (no raw HTML); strict CSP on frontend |
| Outbound fetches of media previews | SSRF | allow-list hosts (`preview.redd.it`, `i.redd.it`, `external-preview.redd.it`, `v.redd.it`, `i.imgur.com`), size cap 5 MB, timeout 10 s, no redirects off-list |
| DB/Redis | network exposure | not published outside the compose network; strong passwords in prod |
| Dependencies | supply chain | lockfiles (`uv.lock`, `pnpm-lock.yaml`); Dependabot; `pip-audit` + `pnpm audit` in CI |

## Platform compliance (non-negotiable)

- Authorized Reddit Data API only. No HTML scraping, no third-party archives, no multiple client IDs to multiply rate limits.
- Rate limiter with a hard ceiling (default 60 QPM) and header-driven backoff.
- Descriptive User-Agent.
- **No vote actions** are implemented. The `vote` OAuth scope is never requested.
- **No bulk/unattended posting.** Publishing (L) is one item per explicit click, only for `approved` drafts, server-side throttled (≥ 10 min between posts, ≤ 5/day default), and logged.
- Deletion compliance and retention per [REDDIT_API.md](REDDIT_API.md).
- No model training on Reddit data.
- NSFW (`over_18`) posts are **always** dropped at ingestion and never stored (ADR-014).

## Privacy

- Reddit usernames are stored only as salted hashes (`AUTHOR_HASH_SALT`). Opinion mining never profiles individual users.
- Subreddit profiles describe observed *content* characteristics, not people.
- Excerpts in the UI are short (≤ 280 chars) and always link to the source.

## Audit

`approval_logs` records approve/reject/edit/copy/publish/link actions with timestamp and details. It is append-only.

## Secrets list (`.env.example`)

`DATABASE_URL`, `REDIS_URL`, `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USERNAME`, `REDDIT_PASSWORD` (script app, read-only use) , `REDDIT_USER_AGENT`, `GROQ_API_KEY`, `APP_SECRET_KEY`, `APP_ENCRYPTION_KEY`, `AUTHOR_HASH_SALT`, `ADMIN_EMAIL`, `ADMIN_PASSWORD` (bootstrap only).

> ⚠️ The script-app flow uses the account password. Use a dedicated Reddit account for **read-only** collection if possible, separate from the account you post from. Publishing (L) uses the auth-code flow with your main account's refresh token instead of its password.
