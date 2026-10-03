# Deployment

> Status: local compose implemented (Phase 1). Production comes in Phase 10.

## Local development

```bash
cp .env.example .env          # fill in secrets (see SECURITY.md); generate with the command in the file
docker compose up --build     # postgres+pgvector, redis, migrate, api, worker, beat, frontend
open http://localhost:3000    # log in with ADMIN_EMAIL / ADMIN_PASSWORD from .env
curl localhost:8000/api/v1/health/ready
```

Services in `docker-compose.yml`:

| Service | Image | Port | Notes |
|---|---|---|---|
| `db` | `pgvector/pgvector:pg16` | 5432 (local only) | volume `pgdata` |
| `redis` | `redis:7-alpine` | 6379 (local only) | |
| `migrate` | backend image | — | `alembic upgrade head` + admin bootstrap, exits |
| `api` | backend image | 8000 | `uvicorn app.main:app` |
| `worker` | backend image | — | `celery -A app.workers.celery_app worker` |
| `beat` | backend image | — | `celery -A app.workers.celery_app beat` (one instance only) |
| `frontend` | frontend image | 3000 | Next.js standalone server; `API_INTERNAL_URL` (runtime) points at the API |

Backend tooling: `uv` for Python deps; frontend: `pnpm`. All ports bind to `127.0.0.1` only.

The `kfa_readonly` role (for the Postgres MCP) is created by `infrastructure/postgres/init/` **only on first init of the `pgdata` volume**. To recreate it: `docker compose down -v` (wipes local data).

### Running outside Docker
```bash
docker compose up -d db redis                     # infra only
cd backend && uv sync && uv run alembic upgrade head && uv run python -m app.bootstrap
uv run uvicorn app.main:app --reload              # :8000 (reads backend/.env or exported vars)
cd frontend && pnpm install && pnpm dev           # :3000, proxies /api to localhost:8000
```
Backend tests: `uv run pytest` (integration tests create and use a separate `<db>_test` database).
API types: `pnpm gen:api` after any backend schema change (CI fails on drift).

## Environments

| Env | Config source | Data |
|---|---|---|
| `local` | `.env` | real Reddit (if approved) or mock seed |
| `ci` | GitHub Actions env + secrets | fixtures only |
| `prod` | platform secret manager | real |

`APP_ENV` switches logging format (pretty vs JSON), CORS origins and cookie `Secure` flag.

## Production (Phase 10, target TBD)

Requirements: one Postgres with pgvector, one Redis, 3 backend processes, 1 frontend. Cheapest reasonable options for one developer:

1. **Single VPS (e.g. 2 vCPU / 4 GB)** running the same compose file with a `docker-compose.prod.yml` override + Caddy for TLS. Cheapest, but you operate it yourself.
2. **Managed PaaS** (e.g. Railway / Render / Fly): backend image deployed as 3 services, managed Postgres (must support pgvector) + Redis; frontend on Vercel or the same platform.

Decision deferred to Phase 10 (open question in [ROADMAP.md](ROADMAP.md)).

### Deploy procedure (any target)
1. CI builds and tags images on `main`.
2. Run `migrate` as a one-off job; abort the deploy on failure.
3. Roll out `api`, `worker`, `beat` (beat: exactly **one** instance).
4. Health check `/api/v1/health/ready`, then `/api/v1/health/reddit`.
5. Frontend deployed independently; `API_INTERNAL_URL` points at the API (read at runtime by `proxy.ts`).

### Ops
- Logs: JSON to stdout → platform log viewer (centralised); optional Loki/Grafana later.
- Backups: daily `pg_dump`, 7-day retention.
- Monitoring: uptime check on `/api/v1/health/ready`; alert if `collect_cycle` hasn't succeeded in 2 h or daily spend > 90% of budget (both visible on the Agent Monitor page).
