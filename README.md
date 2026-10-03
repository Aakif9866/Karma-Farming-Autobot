# Karma Farming Autobot

A personal **Reddit trend intelligence and content-assistance** platform for Indian and global communities. It finds what is gaining attention (text, memes, images, video, news), explains *why* with traceable metrics, surfaces opportunities for genuine contributions, and helps draft original, rule-compliant content that **you review and post yourself**.

> Despite the name, this is not a karma farm: no vote manipulation, no automated or bulk posting, no scraping. Authorized Reddit API only, human approval for everything. See [docs/PRODUCT_VISION.md](docs/PRODUCT_VISION.md).

## Status

🏗️ **Phase 1 (foundation) built.** Phase 0 is waiting on Reddit API approval. Live checklist: [docs/IMPLEMENTATION_STATUS.md](docs/IMPLEMENTATION_STATUS.md).

## Stack

Next.js · TypeScript · Tailwind · shadcn/ui · Recharts — FastAPI · Pydantic · SQLAlchemy · Alembic — LangGraph — PostgreSQL + pgvector — Redis + Celery — Docker Compose · GitHub Actions — Pytest · Vitest · Playwright.

## Docs

Start at [docs/README.md](docs/README.md).

## Quickstart

```bash
cp .env.example .env        # fill in the secrets (instructions inside)
docker compose up --build
open http://localhost:3000  # log in with ADMIN_EMAIL / ADMIN_PASSWORD
```
Running without Docker, tests, and type generation: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).
