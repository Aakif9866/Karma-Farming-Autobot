# Trend Detection

All of this is deterministic Python (numpy/scikit-learn) and costs no LLM tokens.

## Inputs
- `posts` (latest values) and `post_snapshots` (time series per post, roughly every 30 min for 48 h)
- Subreddit baselines in `subreddits.profile` (rolling 7-day medians, recomputed daily)
- Post embeddings (384-d, local model)

## Post-level metrics

Let `t` = post age in hours (min 0.25), and `Δ` = the difference between the two latest snapshots spanning ≥ 20 min.

| Metric | Formula | Why |
|---|---|---|
| `engagement_velocity` | `Δscore / Δhours` | momentum *now*, not lifetime |
| `comment_velocity` | `Δcomments / Δhours` | discussion momentum |
| `relative_engagement` | `log1p(score) − log1p(sub_median_score_at_age(t))` | a 500-point post in r/india ≠ a 500-point post in r/pune |
| `discussion_intensity` | `num_comments / max(score, 10)` | high ratio = debate, low = passive consumption |
| `recency` | `exp(−t / 12)` | half-life ≈ 8 h, configurable |
| `controversy` | `1 − |2·upvote_ratio − 1|` | flags divisive topics (used for opportunity risk, not as a positive score) |

`sub_median_score_at_age` uses per-subreddit age buckets (0–1 h, 1–3 h, 3–6 h, 6–12 h, 12–24 h, 24–48 h), so a young post is compared against young posts.

## Topic clustering

1. Embed new posts (title + first 500 chars of body; OCR text for memes when available).
2. **Assign** each new post to the nearest active cluster if cosine similarity ≥ `0.78` (pgvector HNSW lookup).
3. **Discover**: every 6 h, run `sklearn.cluster.HDBSCAN` (min_cluster_size=3) on unassigned posts from the last 48 h, which creates new clusters.
4. Update centroids incrementally (mean of member embeddings).
5. Clusters with no new posts for 7 days become `dormant`. If a dormant cluster matches a new post again, it becomes `recurring`.

Thresholds are in `config/scoring.yaml` and get tuned in Phase 3 on real data.

## Topic-level metrics (per `trend_snapshots` row)

| Metric | Definition |
|---|---|
| `velocity` | sum of member `engagement_velocity` over the last 2 h |
| `comment_velocity` | same for comments |
| `relative_engagement` | mean of member `relative_engagement` |
| `subreddit_count` | distinct subreddits in the last 24 h (cross-subreddit signal) |
| `growth` | `(velocity_now − velocity_6h_ago) / max(velocity_6h_ago, 1)` |
| `novelty` | `1 − max cosine similarity to clusters active in the previous 14 days` |
| `discussion_intensity` | comment-weighted mean of member intensity |

## Trend score

Each component is normalised to `[0,1]` with a robust min-max (5th/95th percentile across today's active topics), then combined:

```yaml
# config/scoring.yaml (version 1)
trend_score:
  weights:
    velocity: 0.25
    comment_velocity: 0.20
    relative_engagement: 0.20
    growth: 0.15
    cross_subreddit: 0.10
    novelty: 0.05
    discussion_intensity: 0.05
  recency_half_life_hours: 8
```

`trend_score = (Σ wᵢ · normᵢ) · recency_factor`, where `recency_factor = 0.5 + 0.5·exp(−hours_since_last_member_post / half_life)`. This keeps stale topics from riding old velocity without zeroing them out. The stored `score_breakdown` looks like:

```json
{"version": 1,
 "components": {"velocity": {"raw": 412.0, "norm": 0.91, "weight": 0.25, "contrib": 0.2275}, "...": {}},
 "top_posts": ["<uuid>", "<uuid>", "<uuid>"]}
```

The UI renders this as a "Why is this trending?" panel, so every score is traceable to its numbers and posts. **Raw upvotes are never the ranking key.**

## Status classification

| Status | Rule (evaluated each snapshot) |
|---|---|
| `emerging` | age < 6 h, `growth > 0.5`, ≥ 3 posts |
| `rising` | `growth > 0.2` and `velocity` above the 60th percentile |
| `peaking` | `velocity` above the 80th percentile and `|growth| ≤ 0.2` |
| `declining` | `growth < −0.3` for 2 consecutive snapshots |
| `recurring` | matched a dormant cluster |
| `dormant` | no new posts for 7 days |

## India vs global

Each post carries `region` from its subreddit (r/india, r/indiasocial, r/bangalore… → `IN`). Topics get `region_mix` = share of IN vs GLOBAL members. The daily report computes:
- top topics per region
- **crossover topics**: present in both regions with ≥ 20% share each
- **IN-only rising** vs **global-only rising**

## Daily diff

The daily report compares today's top-50 topics to yesterday's and last week's snapshots at the same hour: **new entries, rank movers (±10), dropped topics, status changes**.

## Later (L)
- Seasonal detection (needs ≥ 4 weeks): compare against the same weekday and the previous month.
- Unexpected trends: z-score of topic velocity vs. its own history > 3.
- Weight learning from user feedback (ANA-04) instead of hand-set weights.
