# Changelog

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versioning: SemVer once code ships.

## [Unreleased]

### Added
- 2026-10-03: Phase 1 foundation: FastAPI backend (settings, logging, DB, health, session auth, admin bootstrap, Alembic 0001, Celery), Next.js 16 frontend (dark shell, login, dashboard status, placeholders), Dockerfiles, docker-compose, CI, API type generation. ADR-016, ADR-017.
- 2026-10-03: Claude Code setup: `CLAUDE.md`, 9 project skills in `.claude/skills/`, project `.mcp.json` (GitHub, Context7, Playwright, Postgres/DBHub; pinned, no secrets), `.gitignore`, `docs/CLAUDE_CODE_SETUP.md`.
- 2026-10-03: Plan updated for Groq free tier (ADR-013), NSFW removal (ADR-014), politics included (ADR-015), r/vit added to seed list.
- 2026-10-03: Initial documentation set: product vision, requirements, Reddit API constraints, system architecture, database design + ER diagram, API specification, AI agent design, trend detection, meme intelligence, content generation & critic, security, testing strategy, deployment, roadmap, phased plan, ADRs, implementation status.
