#!/bin/sh
# Regenerate frontend API types from the backend's OpenAPI schema (no running server needed).
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/backend"
APP_SECRET_KEY=openapi-export-only-not-a-real-secret-000 DATABASE_URL=postgresql+psycopg://x@localhost/x \
  uv run python -c "import json; from app.main import create_app; print(json.dumps(create_app().openapi(), indent=2))" \
  > "$ROOT/frontend/openapi.json"
cd "$ROOT/frontend"
pnpm exec openapi-typescript openapi.json -o lib/api/schema.d.ts
