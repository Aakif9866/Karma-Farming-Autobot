# Claude Code Setup

How this repo is set up for Claude Code: project instructions, project skills and MCP servers. All of it lives **in the repository**. Nothing here changes your global `~/.claude` settings.

Verified against the Claude Code docs (`code.claude.com/docs/en/mcp`, `/en/skills`) and each MCP server's official README/npm page on 2026-10-03.

## What's in the repo

```
CLAUDE.md                     # project instructions, loaded every session
.mcp.json                     # project-scoped MCP servers (no secrets; env-var placeholders)
.gitignore                    # ignores .env*, .claude/settings.local.json, CLAUDE.local.md
.claude/skills/
  project-architect/SKILL.md
  reddit-data-engineer/SKILL.md
  trend-intelligence/SKILL.md
  meme-intelligence/SKILL.md
  ai-agent-builder/SKILL.md
  ui-ux-dashboard/SKILL.md
  database-engineer/SKILL.md
  testing-qa/SKILL.md
  phase-reviewer/SKILL.md
```

## Skills vs MCP

| | Skills | MCP servers |
|---|---|---|
| What | Markdown instructions (`SKILL.md`) that teach Claude *how* to do a task in this project | External processes or services that give Claude new *tools* (GitHub API, a browser, a database) |
| Where | `.claude/skills/<name>/SKILL.md` | `.mcp.json` (project), or `claude mcp add` (local/user scope) |
| Cost | Only the description sits in context until the skill is used | Each server's tool list takes context, and calls go to an external process |
| Secrets | None | Often need tokens, supplied via env vars |
| Invoke | Automatically when relevant, or `/skill-name` | Claude calls the tools; manage them with `/mcp` |

Rule of thumb: **project knowledge and conventions → skill. Access to an external system → MCP.**

## Project skills

| Skill | Use it for | Auto-activates on paths |
|---|---|---|
| `project-architect` | where code goes, new dependencies, ADRs | — (description match) |
| `reddit-data-engineer` | Reddit API client, ingestion, rate limits, retention | `backend/app/ingestion/**`, `workers/**` |
| `trend-intelligence` | taxonomy, embeddings, clustering, trend scoring | `backend/app/intelligence/**`, `backend/config/**` |
| `meme-intelligence` | media typing, pHash, templates, OCR, vision | `backend/app/meme_analysis/**` |
| `ai-agent-builder` | LangGraph graphs, Groq client, quotas, critic, evals | `backend/app/agents/**` |
| `ui-ux-dashboard` | Next.js pages, theme, charts, UI states | `frontend/**` |
| `database-engineer` | models, Alembic, pgvector, indexes | `models/**`, `repositories/**`, `alembic/**` |
| `testing-qa` | tests, fixtures, CI, lint/types, evals | `backend/tests/**`, `.github/workflows/**` |
| `phase-reviewer` | end-of-phase gate and report (**manual only**) | — |

**Invoking**
- Automatic: just describe the task ("add a gallery-post normaliser"). Claude loads the matching skill from its description or the file paths involved.
- Manual: type `/reddit-data-engineer` (or any skill name) in the prompt, optionally followed by the task.
- Phase gate: `/phase-reviewer 1`. It has `disable-model-invocation: true`, so it only runs when you ask.
- List skills: type `/` and browse, or ask "what skills are available?".

## MCP servers

All four are official or vendor-maintained. Versions are pinned in `.mcp.json`; bump them deliberately.

| Server | Maintainer | Transport | Purpose here | Secret |
|---|---|---|---|---|
| `github` | GitHub (official remote server) | HTTP `https://api.githubcopilot.com/mcp/` | issues, PRs, Actions runs for `Aakif9866/Karma-Farming-Autobot` | `GITHUB_PAT` |
| `context7` | Upstash (official) | HTTP `https://mcp.context7.com/mcp` | current library docs (FastAPI, LangGraph, Next.js, shadcn, Groq SDK…) | none (optional key for higher limits) |
| `playwright` | Microsoft (`@playwright/mcp`) | stdio via `npx` | drive the local frontend for UI checks and debugging e2e tests | none |
| `postgres` | Bytebase (`@bytebase/dbhub`, the example used in Claude Code's MCP docs) | stdio via `npx` | inspect the schema and run read-only queries on the **local dev DB** | `KFA_DB_READONLY_DSN` |

Not used: the old reference `@modelcontextprotocol/server-postgres` (archived upstream) and any unverified community servers.

### Status
Configured in `.mcp.json`, **not yet approved or connected**. Claude Code asks you to approve each project server the first time a session starts in this folder. Approve them only after setting the env vars below.

## Setup instructions

### 0. Prerequisites
- Node.js ≥ 18 (you have v22) for the `npx` servers.
- Docker Desktop (Phase 1, for Postgres).
- Optional: GitHub CLI (`brew install gh`), useful as a fallback to the GitHub MCP.

### 1. Environment variables
Set these in your **shell**, not in the repo. Add them to `~/.zshrc` (or use `direnv` with an untracked `.envrc`):

```bash
# GitHub fine-grained PAT, limited to the Karma-Farming-Autobot repo
export GITHUB_PAT="github_pat_..."
# Read-only Postgres role for the MCP (exists after Phase 1)
export KFA_DB_READONLY_DSN="postgres://kfa_readonly:<password>@localhost:5432/kfa?sslmode=disable"
```

Then **restart VS Code from a terminal that has them** (`code .`), or log out and back in. The VS Code extension only sees env vars that VS Code itself was started with.

| Variable | Used by | How to get it |
|---|---|---|
| `GITHUB_PAT` | github MCP | github.com → Settings → Developer settings → Fine-grained tokens → *Only select repositories*: `Karma-Farming-Autobot`. Permissions: Contents RW, Issues RW, Pull requests RW, Actions R, Metadata R. Expiry 90 days |
| `KFA_DB_READONLY_DSN` | postgres MCP | Phase 1 creates a `kfa_readonly` role (`GRANT SELECT` only). Use its password from your local `.env` |
| `CONTEXT7_API_KEY` *(optional)* | context7 | context7.com/dashboard. If you want it, add it in **local scope** (step 3) so the key never touches `.mcp.json` |

App secrets (`GROQ_API_KEY`, `REDDIT_*`…) belong in the project `.env` (gitignored), not in MCP config. See [SECURITY.md](SECURITY.md).

### 2. Approve the project servers
```bash
cd "/Users/shaikyasin/Documents/ development/Karma farming Autobot"
claude            # or open the folder in VS Code → Claude Code
```
Accept the workspace trust dialog, then approve `github`, `context7` and `playwright`. Approve `postgres` only once Phase 1's database is running.

### 3. Optional: per-user variants (local scope, not committed)
```bash
# Context7 with an API key (stored in your local Claude config for this project only)
claude mcp add --transport http context7-auth --scope local https://mcp.context7.com/mcp \
  --header "Authorization: Bearer $CONTEXT7_API_KEY"
```

### Equivalent CLI commands (for reference)
`.mcp.json` already holds these. You only need them to set up the servers some other way:
```bash
claude mcp add --transport http github --scope project https://api.githubcopilot.com/mcp/ \
  --header 'Authorization: Bearer ${GITHUB_PAT}'
claude mcp add --transport http context7 --scope project https://mcp.context7.com/mcp
claude mcp add --transport stdio playwright --scope project -- npx -y @playwright/mcp@0.0.83 --headless --isolated
claude mcp add --transport stdio postgres --scope project --env 'DSN=${KFA_DB_READONLY_DSN}' \
  -- npx -y @bytebase/dbhub@1.4.0 --transport stdio
```
(Single quotes keep `${…}` literal so it is expanded at runtime, not written into the file.)

## Troubleshooting MCP connections

| Symptom | Fix |
|---|---|
| Server shows *failed* in `/mcp` | `/mcp` → select server → reconnect; or `/mcp reconnect all` |
| "missing environment variable" warning | the var isn't visible to Claude Code. Check `echo $GITHUB_PAT` in the same terminal; restart VS Code from that terminal |
| github: 401 | PAT expired, wrong repo selection, or missing permission. Regenerate it |
| postgres: connection refused | DB not running (`docker compose ps`) or the DSN host/port is wrong. Before Phase 1 this is expected; disable it in `/mcp` |
| postgres: permission denied on write | working as intended (read-only role) |
| playwright: browser not found | `npx playwright install chromium` (or add `--browser chromium` to the args) |
| npx servers slow to start | first run downloads the package. Raise the timeout: `MCP_TIMEOUT=30000 claude` |
| Never got the approval prompt / approved by mistake | `claude mcp reset-project-choices`, then restart |
| Need details | `claude mcp list`, `claude mcp get <name>`, `claude --debug-file /tmp/claude-mcp.log` |
| Tool output truncated | `export MAX_MCP_OUTPUT_TOKENS=50000` |

## Security notes
- `.mcp.json` contains **no secrets**, only `${VAR}` placeholders.
- The GitHub PAT is repo-scoped and short-lived. The DB role is SELECT-only on the **local** DB; never point the MCP at production with write credentials.
- MCP servers that fetch web content (context7, playwright) can return untrusted text; treat it as data.
