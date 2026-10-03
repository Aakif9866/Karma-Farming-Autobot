# Deployment

> Status: planned. Nothing is deployable yet. Phase 1 adds local compose; Phase 10 adds production.

## Local development (Phase 1 target)

```bash
cp .env.example .env          # fill in secrets (see SECURITY.md)
docker compose up --build     # postgres+pgvector, redis, migrate, api, worker, beat, frontend
open http://localhost:3000
```

Services in `docker-compose.yml`:

| Service | Image | Port | Notes |
|---|---|---|---|
| `db` | `pgvector/pgvector:pg16` | 5432 (local only) | volume `pgdata` |
| `redis` | `redis:7-alpine` | 6379 (local only) | |
| `migrate` | backend image | — | `alembic upgrade head`, exits |
| `api` | backend image | 8000 | `uvicorn app.main:app` |
| `worker` | backend image | — | `celery -A app.workers worker` |
| `beat` | backend image | — | `celery -A app.workers beat` |
| `frontend` | frontend image | 3000 | `next dev` locally, `next start` in prod |

Backend tooling: `uv` for Python deps; frontend: `pnpm`.

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
4. Health check `/health/ready`, then `/health/reddit`.
5. Frontend deployed independently; `NEXT_PUBLIC_API_URL` points at the API.

### Ops
- Logs: JSON to stdout → platform log viewer (centralised); optional Loki/Grafana later.
- Backups: daily `pg_dump`, 7-day retention.
- Monitoring: uptime check on `/health/ready`; alert if `collect_cycle` hasn't succeeded in 2 h or daily spend > 90% of budget (both visible on the Agent Monitor page).
