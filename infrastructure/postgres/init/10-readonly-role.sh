#!/bin/sh
# Runs once, on first init of the db volume. Creates the SELECT-only role used by the Postgres MCP.
set -e
if [ -z "$KFA_READONLY_PASSWORD" ]; then
  echo "KFA_READONLY_PASSWORD not set; skipping kfa_readonly role"
  exit 0
fi
psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ro_pw="$KFA_READONLY_PASSWORD" <<'SQL'
CREATE ROLE kfa_readonly LOGIN PASSWORD :'ro_pw';
GRANT USAGE ON SCHEMA public TO kfa_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO kfa_readonly;
-- Tables created later by the migration role (this POSTGRES_USER) are readable too.
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO kfa_readonly;
SQL
