# Content Opportunities, Generation & Critic

## Opportunity types

| Type | Detection (deterministic first) | MVP |
|---|---|---|
| `trending_discussion` | topic `rising`/`emerging`, target sub has no big thread on it yet | ✅ |
| `unanswered_question` | question posts with high views-proxy (score) but few or low-quality replies after 3 h | ✅ |
| `original_opinion` | topic with low opinion diversity (one stance dominates) | ✅ |
| `counterperspective` | strong minority opinion with low representation | ✅ |
| `experience_prompt` | threads where many comments share personal experiences | ✅ |
| `meme_opportunity` | rising meme template or trending topic without memes in a meme-friendly sub | ✅ |
| `cross_community` | topic big in sub A, absent in related sub B (where it is on-topic per rules) | ✅ |
| `technical_discussion` | tech/programming topic with high discussion intensity | ✅ |
| `news_discussion` | news-domain links rising, discussion still shallow | L |
| `image_concept`, `video_concept`, `educational`, `regional` | — | L |

**High engagement + low discussion** is a core signal: `score` high relative to baseline, `discussion_intensity` low. People care, but nobody has started the conversation yet.

## Opportunity score

```yaml
opportunity_score:
  weights:
    topic_trend_score: 0.30
    gap: 0.25            # how under-served the topic is in the target sub
    sub_fit: 0.20        # embedding similarity of topic to sub's recent accepted posts
    format_fit: 0.15     # format's historical performance in that sub
    freshness: 0.10
  penalties:
    rule_risk: -0.30     # parsed-rule conflict likelihood
    controversy: -0.10   # unless type == counterperspective
    recently_suggested: -0.20
```
Stored with a breakdown, the same as trend scores.

## Recommendation fields (all required)

`subreddit`, `category`, `topic`, `why_selected` (generated from the score breakdown, plus an LLM sentence), `source_posts` (≥ 1, linked), `trend_status`, `audience`, `format`, `angle`, `risks[]`, `title_suggestion`, `content_outline`, `confidence` (`0–1`, shown as low/med/high).

## Generation

One LLM call produces all N variants (default 3) for a recommendation:

- **Input**: recommendation, source excerpts (≤ 8, with IDs), subreddit profile (format mix, typical title length, tone notes computed from data), parsed rules, requested style + format.
- **Output schema**:
```json
{"variants": [{"title": "...", "body": "...", "style": "casual",
               "claims": [{"text": "...", "source_ids": ["c_..."]}],
               "placeholders": ["[YOUR EXPERIENCE: when you first...]"],
               "poll_options": null, "meme_concept": null}]}
```
- **Grounding**: any factual claim must cite a source ID. Claims without one are flagged by the critic.
- **No invented experiences**: experience drafts contain explicit `[YOUR EXPERIENCE: …]` placeholders. **A draft with unfilled placeholders cannot be approved** (UI-enforced and server-enforced).
- **Styles**: casual, conversational, humorous, technical, informative, opinionated, short-and-direct.
- **Formats (MVP)**: text post, question, opinion, comment draft, poll (text options), meme concept. **(L)**: infographic/comparison concept, short-video concept.

## Critic

Deterministic checks first (free), then one batched LLM critic call per draft set.

| Check | Method | Fail → |
|---|---|---|
| Rule compliance | parsed constraints (`flair_required`, `no_memes`, `no_self_promo`, title regex, min/max length, domain block-list) | `fail` |
| Duplicate / near-duplicate | cosine ≥ 0.9 vs. posts in target sub, last 30 days | `fail` |
| Spam signals | link count, ALL CAPS ratio, emoji density, call-to-action phrases ("upvote", "follow me") | `warn`/`fail` |
| Repetitiveness | similarity to the user's own last 20 drafts | `warn` |
| Placeholders unfilled | regex | blocks approval |
| Factual grounding | LLM: is each claim supported by its cited excerpt? | `warn`/`fail` |
| Misleading statements | LLM | `fail` |
| Sensitive subjects | LLM + keyword list (politics, religion, caste, communal topics, tragedies) | `warn`, with handling notes |
| Copyright | template/media reuse disclosed? quoting > 2 sentences of an article? | `warn` |
| Authenticity | LLM: does it read as a genuine contribution or as engagement bait? | `warn` |

Output: `critic_verdict` + `critic_report` (one entry per check with reason). `fail` → auto-regenerate once; if it still fails, it is shown to the user as failed, with reasons, and is **not approvable**.

## Draft lifecycle

```mermaid
stateDiagram-v2
  [*] --> generated
  generated --> in_review: critic done (pass/warn)
  generated --> rejected: critic fail (after retry)
  in_review --> in_review: user edits (new version; critic re-runs)
  in_review --> approved: user approves (no fail, no placeholders)
  in_review --> rejected: user rejects
  approved --> posted: user posts manually & links URL (MVP) / publish click (L)
  posted --> [*]
  rejected --> [*]
```

Every transition writes `approval_logs`. User edits re-run the deterministic checks immediately; the LLM critic re-runs on demand (button) to save cost.
