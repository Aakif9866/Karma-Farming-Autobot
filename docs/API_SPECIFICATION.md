# API Specification

REST, JSON, prefix `/api/v1`. FastAPI generates the authoritative OpenAPI at `/api/v1/openapi.json`. This doc is the design intent; the generated schema wins once the code exists.

## Conventions

- **Auth**: session cookie (HTTP-only, SameSite=Lax) from `POST /auth/login`. All routes except `/health*` and `/auth/login` require auth.
- **Pagination**: cursor-based: `?limit=25&cursor=<opaque>` → `{ "items": [...], "next_cursor": "..." | null }`. Max `limit` = 100.
- **Filtering**: query params, e.g. `?region=IN&category=finance&since=2026-10-01T00:00:00Z`.
- **Errors**: `{"error": {"code": "BUDGET_EXCEEDED", "message": "...", "details": {}}}` with the matching HTTP status (400 validation, 401, 404, 409 state conflict, 422, 429 budget/rate, 503 upstream).
- **Long jobs**: return `202 {"run_id": "..."}`; poll `GET /agent-runs/{id}`.
- **Mock data**: every content object includes `"source": "reddit" | "mock"`.

## Endpoints

### Health & auth
| Method | Path | Notes |
|---|---|---|
| GET | `/health` | liveness |
| GET | `/health/ready` | DB + Redis |
| GET | `/health/reddit` | `{authenticated, last_success_at, ratelimit_remaining}` |
| POST | `/auth/login` · `/auth/logout` | |
| GET | `/auth/me` | |

### Subreddits
| Method | Path | Notes |
|---|---|---|
| GET | `/subreddits` | filters: region, enabled, tag |
| POST | `/subreddits` | `{name, region, tags, poll_interval_min}`; validated against Reddit before saving |
| PATCH | `/subreddits/{id}` | enable/disable, interval, tags |
| DELETE | `/subreddits/{id}` | stops collection; data ages out via retention |
| GET | `/subreddits/{id}` | profile, rules, baselines, format mix |
| POST | `/subreddits/{id}/refresh` | 202, `analyze_subreddit` run |

### Posts
| GET | `/posts` | filters: subreddit, region, category, content_type, since, q (full-text) |
| GET | `/posts/{id}` | with snapshots, categories, topic, media, top comments |

### Topics & trends
| GET | `/topics` | filters: region, category, status, sort=`trend_score`\|`growth`\|`novelty`, window |
| GET | `/topics/{id}` | latest snapshot + `score_breakdown`, member posts, time series |
| GET | `/topics/{id}/opinions` | opinions with evidence |
| POST | `/topics/{id}/analyze` | 202, opinion mining on demand |
| GET | `/categories` | taxonomy tree with counts |

### Reports & dashboard
| GET | `/reports/daily` | list of dates |
| GET | `/reports/daily/{date}` | structured report incl. IN vs global, diffs |
| GET | `/dashboard/summary` | widgets: trending topics, emerging, memes, category distribution, IN vs global, recent recs, agent status, collection status |

### Memes
| GET | `/memes/templates` | sort by post_count, recency; filters: region, status |
| GET | `/memes/templates/{id}` | examples (Reddit links), spread across subs |
| GET | `/memes/posts` | meme posts with analysis + originality label |
| POST | `/memes/posts/{post_id}/analyze` | 202, vision analysis (counts toward budget) |

### Opportunities & drafts
| GET | `/opportunities` | filters: type, subreddit, min_confidence, status |
| PATCH | `/opportunities/{id}` | `{status: "dismissed"}` |
| POST | `/opportunities/{id}/drafts` | `{variants, style, format}` → 202 `generate_drafts` run |
| GET | `/drafts` | filters: status, subreddit |
| GET | `/drafts/{id}` | draft + critic report + sources + subreddit rules + version chain |
| PATCH | `/drafts/{id}` | user edit → new version, deterministic critic re-run |
| POST | `/drafts/{id}/critic` | re-run LLM critic |
| POST | `/drafts/{id}/regenerate` | new variant(s) from same recommendation |
| POST | `/drafts/{id}/approve` · `/reject` | 409 if critic `fail` or placeholders unfilled |
| POST | `/drafts/{id}/copy` | logs copy action (the UI does the clipboard) |
| POST | `/drafts/{id}/link-post` | `{reddit_url}` → creates contribution, status `posted` |
| POST | `/drafts/{id}/publish` | **L**: user-OAuth submit, approved drafts only |
| POST | `/feedback` | `{target_type, target_id, rating, comment}` |

### Analytics (L except contributions list)
| GET | `/contributions` | user's linked posts + latest metrics |
| GET | `/analytics/overview` · `/analytics/formats` · `/analytics/subreddits` · `/analytics/topics` | |

### Agent runs & settings
| GET | `/agent-runs` | filters: graph, status |
| GET | `/agent-runs/{id}` | steps, tokens, cost, errors |
| POST | `/agent-runs/{id}/retry` | failed runs only |
| GET | `/usage/today` | spend vs budget, tokens by task |
| GET/PATCH | `/settings` | token caps, models, retention days, intervals (NSFW is always excluded, so there is no toggle) |

## Example: topic detail

```json
GET /api/v1/topics/6f1c...
{
  "id": "6f1c...",
  "label": "Bengaluru metro fare hike",
  "status": "rising",
  "region_mix": {"IN": 0.97, "GLOBAL": 0.03},
  "subreddits": ["bangalore", "india", "indiasocial"],
  "trend_score": 0.82,
  "score_breakdown": {"version": 1, "components": {"velocity": {"raw": 412.0, "norm": 0.91, "weight": 0.25, "contrib": 0.2275}}},
  "series": [{"t": "2026-10-03T06:00:00Z", "trend_score": 0.41}],
  "top_posts": [{"id": "...", "title": "...", "permalink": "https://reddit.com/r/...", "score": 1830, "num_comments": 412, "source": "reddit"}]
}
```
