# Requirements

Scope tags: **MVP** = required for the first end-to-end release · **L** = later phase (see [ROADMAP.md](ROADMAP.md)).
IDs are referenced from [PHASES.md](PHASES.md) and [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md).

## Functional requirements

### ING — Reddit data collection
| ID | Requirement | Scope |
|---|---|---|
| ING-01 | Authenticate to the Reddit Data API via OAuth2 (script app); validate credentials at startup and expose status at `/health/reddit` | MVP |
| ING-02 | Manage monitored subreddits (add/remove/enable, region `IN`/`GLOBAL`, tags, poll interval) | MVP |
| ING-03 | Collect `hot`, `new`, `rising` listings per subreddit on a configurable interval (default 30 min) | MVP |
| ING-04 | Normalise posts into the schema in [DATABASE_DESIGN.md](DATABASE_DESIGN.md), including derived `content_type` | MVP |
| ING-05 | Idempotent upsert keyed on Reddit fullname; duplicates never create new rows | MVP |
| ING-06 | Re-poll tracked posts (age < 48 h) via `/api/info` to record `post_snapshots` | MVP |
| ING-07 | Fetch top comments only for posts that pass a trend pre-filter (top-N per cycle) | MVP |
| ING-08 | Client-side rate limiter honouring `X-Ratelimit-*` headers, with a hard QPM ceiling | MVP |
| ING-09 | Retry with exponential backoff on 429/5xx; failed cycles logged and resumable | MVP |
| ING-10 | Fetch subreddit metadata, rules and post requirements daily | MVP |
| ING-11 | Retention job: purge content older than N days and content deleted on Reddit | MVP |
| ING-12 | Every row carries `source` (`reddit` / `mock`) | MVP |
| ING-13 | Drop NSFW (`over_18`) posts at ingestion; reject NSFW subreddits | MVP |

### CLS — Domain classification
| ID | Requirement | Scope |
|---|---|---|
| CLS-01 | Hierarchical taxonomy (category → subcategory → topic, keywords) loaded from a YAML file into DB; adding categories needs no code change | MVP |
| CLS-02 | Multi-label classification: keyword rules + embedding similarity to category centroids; confidence per label | MVP |
| CLS-03 | LLM fallback only for posts that are low-confidence *and* high-engagement, batched, under budget | MVP |
| CLS-04 | Region dimension (`IN` / `GLOBAL`) from subreddit config + content signals | MVP |

### TRD — Trend detection
| ID | Requirement | Scope |
|---|---|---|
| TRD-01 | Compute engagement velocity, comment velocity, relative engagement vs. subreddit baseline, recency, novelty, discussion intensity | MVP |
| TRD-02 | Configurable weighted scoring model; every score stored with its component breakdown | MVP |
| TRD-03 | Cluster posts into topics using embeddings | MVP |
| TRD-04 | Topic snapshots every cycle; status = emerging / rising / peaking / declining / recurring | MVP |
| TRD-05 | Cross-subreddit detection (same cluster in ≥ 2 subreddits) | MVP |
| TRD-06 | Daily trend report (India vs. global, diff vs. yesterday) | MVP |
| TRD-07 | Seasonal / unexpected trend detection (needs ≥ 4 weeks of history) | L |

### MEM — Meme intelligence
| ID | Requirement | Scope |
|---|---|---|
| MEM-01 | Identify image/GIF/video/gallery posts and extract media metadata | MVP |
| MEM-02 | Perceptual hash (pHash) of the preview image, fetched transiently and never stored | MVP |
| MEM-03 | OCR captions (Tesseract) on trending meme posts only | MVP |
| MEM-04 | Template clustering by pHash distance; label original / template reuse / remix / repost | MVP |
| MEM-05 | Vision-LLM explanation (joke, reference, audience, template, IN/global) for top-N trending memes per day | MVP |
| MEM-06 | Meme lifecycle per template (first seen, peak, spread across subs) | L |
| MEM-07 | CLIP-style visual embeddings for semantic similarity beyond pHash | L |
| MEM-08 | Meme concept generation (caption, image description, template recommendation, punchline variants) — text only, no image generation | MVP |

### OPN — Opinion mining
| ID | Requirement | Scope |
|---|---|---|
| OPN-01 | For a selected topic/post, extract main and minority opinions, arguments, counterarguments, common questions, tone | MVP |
| OPN-02 | Each opinion cites ≥ 1 source comment ID; excerpts are short quotes with permalinks | MVP |
| OPN-03 | Output separates `observed` (quoted/clustered) from `interpretation` (model inference) | MVP |
| OPN-04 | Sample comments by stance diversity, not only top score | MVP |

### SUB — Subreddit intelligence
| ID | Requirement | Scope |
|---|---|---|
| SUB-01 | Profile per subreddit: description, rules, post requirements, format mix, typical engagement baselines, posting windows | MVP |
| SUB-02 | Observed characteristics computed from data (format mix, title length, flair use), not stereotypes about users | MVP |
| SUB-03 | Rules parsed into machine-checkable constraints where possible (flair required, no memes, no self-promo, title regex) | MVP |

### OPP — Content opportunities
| ID | Requirement | Scope |
|---|---|---|
| OPP-01 | Generate recommendations of the types in [CONTENT_GENERATION.md](CONTENT_GENERATION.md) | MVP (subset) |
| OPP-02 | Each recommendation has every field listed there (subreddit, why, sources, risks, confidence…) | MVP |
| OPP-03 | Never invent personal experiences; experience prompts use explicit placeholders | MVP |

### GEN — Content studio
| ID | Requirement | Scope |
|---|---|---|
| GEN-01 | Generate 3 variants per draft by default (configurable 1–5) | MVP |
| GEN-02 | Styles: casual, conversational, humorous, technical, informative, opinionated, short | MVP |
| GEN-03 | Formats: text post, question, opinion, poll, comment draft, meme concept, image/infographic concept, short-video concept | MVP (text, question, opinion, comment, meme concept); L (rest) |
| GEN-04 | Regenerate single variant; edit in place; version history | MVP |

### CRT — Quality & safety critic
| ID | Requirement | Scope |
|---|---|---|
| CRT-01 | Deterministic checks: rule constraints, title regex, banned domains, duplicate/near-duplicate of existing posts, length, link density | MVP |
| CRT-02 | LLM checks: factual grounding vs. sources, misleading claims, sensitive topics, spam tone, authenticity, copyright | MVP |
| CRT-03 | Verdict `pass` / `warn` / `fail` with reasons; `fail` drafts cannot be approved | MVP |

### APR — Approval & publishing
| ID | Requirement | Scope |
|---|---|---|
| APR-01 | Draft states: generated → in_review → approved/rejected → posted | MVP |
| APR-02 | View sources and subreddit rules alongside the draft; copy to clipboard; open target subreddit submit page | MVP |
| APR-03 | Audit log of every approval/rejection/publish action | MVP |
| APR-04 | Publish via Reddit API with user OAuth, one item per explicit click, rate-limited (≤ 1 post / 10 min) | L |

### ANA — Performance analytics
| ID | Requirement | Scope |
|---|---|---|
| ANA-01 | User links a posted Reddit URL to a draft (manual in MVP) | MVP |
| ANA-02 | Track score, comments, upvote ratio over time for linked posts | MVP |
| ANA-03 | Discussion quality: comment depth, unique commenters, OP reply count | L |
| ANA-04 | Acceptance rate of recommendations; feedback loop into opportunity scoring weights | L |

### AGT — Agent runtime
| ID | Requirement | Scope |
|---|---|---|
| AGT-01 | Per-job LangGraph workflows with selective execution | MVP |
| AGT-02 | Every run persisted (`agent_runs`): status, node timings, errors, tokens, cost | MVP |
| AGT-03 | Per-model daily token cap + per-minute token limiter (Groq free tier); runs that would exceed it are deferred, not truncated silently | MVP |
| AGT-04 | Human-approval interrupt with persisted state | MVP |

### UI — Frontend
See [SYSTEM_ARCHITECTURE.md § Frontend](SYSTEM_ARCHITECTURE.md#frontend). MVP pages: Dashboard, Daily Trends, Trend Explorer (with IN/global filter, which replaces separate Indian/Global pages in MVP), Meme Intelligence, Opinion Explorer, Subreddit Explorer, Content Opportunities, Content Studio + Draft Manager, Agent Monitor, Settings. Analytics page: L.

## Non-functional requirements

| ID | Requirement |
|---|---|
| NFR-01 Cost | **$0 paid APIs.** Groq free tier only, with per-model daily token caps under the free limits. Embeddings and OCR run locally |
| NFR-02 Rate limits | Never exceed 60 QPM to Reddit (configurable ceiling below the 100 QPM limit) |
| NFR-03 Explainability | Every score/recommendation stores its inputs and component breakdown |
| NFR-04 Security | No secrets in code; OAuth tokens encrypted at rest; app behind auth. See [SECURITY.md](SECURITY.md) |
| NFR-05 Prompt injection | Reddit text is untrusted data; never executed as instructions; structured outputs only |
| NFR-06 Performance | Dashboard API p95 < 500 ms on 100k posts; ingestion cycle for 40 subs < 5 min |
| NFR-07 Reliability | Failed jobs retried; a failure in one subreddit never blocks the others |
| NFR-08 Observability | Structured JSON logs with run/job IDs; agent runs visible in UI |
| NFR-09 Portability | `docker compose up` brings up the full stack locally |
| NFR-10 Quality | Typed (mypy strict on backend, TS strict), linted (ruff, eslint), tested in CI |

## Constraints & assumptions

- Reddit API approval may be slow or denied → mock-data fallback ([REDDIT_API.md](REDDIT_API.md)).
- No historical backfill → trend history starts on day 1 of ingestion.
- Single user, single deployment.
- One LLM provider at a time (configurable), with model per task in config.
