# Reddit API Constraints

Everything here is a **Phase 0 verification item**. Items marked ⚠️ are based on Reddit's published policies as last known. They must be re-checked against the current docs (`https://support.reddithelp.com/hc/en-us/articles/16160319875092`, `https://www.reddit.com/dev/api`, Data API Terms, Developer Terms) before Phase 2 starts. Record the findings in [DECISIONS.md](DECISIONS.md).

## Access

| Item | Assumption | Status |
|---|---|---|
| Auth | OAuth2 is required for every Data API call. "Script" app type works for a single personal account; "web app" type if publishing on behalf of the user via an auth-code flow. | ⚠️ verify |
| App approval | ⚠️ Since late 2025 Reddit's *Responsible Builder Policy* requires new API clients to **request access and be approved**, instead of creating keys self-service at `reddit.com/prefs/apps`. Expect a review with an unknown turnaround. | ⚠️ **blocking** — verify first |
| App naming | A client named "Karma Farming …" may be rejected, because karma farming is a known spam pattern. Register the Reddit app with a neutral name and description (e.g. "Trend research assistant, personal use, read-mostly, human-approved posting"). | Recommendation |
| Commercial use | Free access is for non-commercial/personal use. Any commercial use needs a separate agreement. | ⚠️ verify |
| ML training | Data API terms forbid using Reddit content to train models without permission. **We do not train or fine-tune** on Reddit data. Using it as LLM *inference input* and computing embeddings for retrieval is assumed to be allowed. | ⚠️ verify the embeddings interpretation |

## Rate limits

| Item | Assumption |
|---|---|
| OAuth clients | **100 queries per minute** per client ID, averaged over a 10-minute window |
| Unauthenticated | ~10 QPM, so not used |
| Headers | `X-Ratelimit-Used`, `X-Ratelimit-Remaining`, `X-Ratelimit-Reset`. The client must read them and slow down on its own |
| User-Agent | Required, unique, descriptive: `<platform>:<app_id>:<version> (by /u/<username>)`. Generic UAs get throttled harder |

### Request budget (MVP plan)

Reddit allows 100 QPM ≈ 6,000 req/hour. Our planned usage per 30-minute cycle for 40 subreddits:

| Call | Count / cycle |
|---|---|
| `/r/{sub}/hot`, `/new`, `/rising` (limit=100) | 120 |
| `/api/info?id=t3_…` refresh of tracked posts (100 IDs per call) | ~20 |
| `/comments/{id}` top comments for the top-N trending posts only | ≤ 50 |
| `/r/{sub}/about`, `/about/rules` (daily, not every cycle) | ~3 amortised |
| **Total** | **~195 per 30 min ≈ 6.5 QPM** |

That is under 10% of the limit, which leaves room for on-demand analysis and retries. The client still enforces a hard ceiling of 60 QPM as a safety margin (configurable).

## Data availability

| Field | Source | Notes |
|---|---|---|
| id, subreddit, title, selftext, url, permalink, created_utc | submission | Always present |
| score, num_comments | submission | Vote counts are **fuzzed**, so use them for trends, not exact truth |
| upvote_ratio | submission | Present on submissions |
| author | submission | Store a **salted hash** only; the raw username is shown live via permalink |
| link_flair_text, over_18, spoiler, stickied, is_self, post_hint, domain | submission | `post_hint` is missing on many posts, so content type is derived from several fields |
| media: `preview`, `media_metadata` (galleries), `secure_media` (v.redd.it), `is_gallery`, `is_video` | submission | v.redd.it uses DASH with separate audio. We store **metadata + derived features only** |
| polls: `poll_data` | submission | ⚠️ availability inconsistent, verify |
| comments | `/comments/{id}?sort=top&limit=…&depth=…` | One call per post, so only fetched selectively |
| subreddit rules | `/r/{sub}/about/rules` | Structured short_name + description |
| post requirements | `/api/v1/{sub}/post_requirements` | Title/body regex, flair required, domain allow/block lists. ⚠️ verify |
| deleted/removed state | `/api/info` refresh: `removed_by_category`, author `[deleted]` | Drives deletion compliance |

### Limits that shape the design

- **Listings are capped at ~1,000 items deep** and paginated 100 at a time. There is no historical backfill, so history only exists from the day we start collecting. **Start ingestion early.**
- **No Pushshift-style archive** for general developers.
- **Search API is weak** (relevance-ranked, inconsistent). We rely on listings + our own index.
- **Velocity requires multiple observations.** A single fetch gives score at one moment. Trend metrics need us to re-poll tracked posts (`/api/info`), which is why `post_snapshots` exists.

## Compliance obligations

1. **Honour deletions.** When a refresh shows a post or comment as deleted or removed by its author, purge its text and media features within 48 h (a retention job).
2. **Retention.** Raw post/comment text is kept for 30 days by default (configurable). Aggregates (topic snapshots, metrics) are kept longer because they hold no user content.
3. **No redistribution.** The UI shows excerpts with permalinks back to Reddit. There are no export/download features for raw Reddit content.
4. **NSFW.** `over_18` content is excluded by default (setting).
5. **Posting** (Phase 7+, optional): only via the user's own OAuth token with the `submit` scope, one item per explicit click, after the critic passes and the user approves. It must respect each subreddit's rules, flair requirements and account restrictions (karma/age gates).

## Fallback if API access is delayed

Phases 1, 3–8 can proceed with **clearly labelled mock data** (`source = "mock"` on every row, a red "MOCK DATA" banner in the UI) generated from hand-written fixtures. Phase 2's acceptance criteria require real API access and cannot be marked done on mocks (see [PHASES.md](PHASES.md)).
