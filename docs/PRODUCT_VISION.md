# Product Vision — Karma Farming Autobot

## One-liner

A personal Reddit **trend intelligence and content-assistance** platform: it finds what communities are discussing right now, explains *why* it is getting attention, and helps one human write original, rule-compliant contributions — which that human reviews and posts themselves.

## The problem

Keeping up with dozens of subreddits by hand is slow. Raw "top" lists hide the interesting signals: a topic that is small but accelerating, a question nobody has answered well, a meme template spreading from r/IndianDankMemes to r/ProgrammerHumor, a strong minority opinion buried under the top comment. Generic AI writing tools ignore community culture and rules, so their output reads as spam and gets removed.

## Target user

**One individual creator / developer** (the project owner) who participates in Indian and global Reddit communities and wants to contribute content that sparks real discussion. Multi-user SaaS is out of scope until the single-user loop has been shown to work (see [DECISIONS.md](DECISIONS.md) ADR-008).

## Questions the product answers

| Question | Module(s) |
|---|---|
| What is trending on Reddit today, and what changed since yesterday / last week? | Trend Detection, Snapshots |
| Which topics are gaining momentum vs. declining? | Trend Detection |
| What opinions (majority *and* minority) are people expressing? | Opinion Mining |
| Which memes / formats are emerging, and in which communities? | Meme Intelligence |
| Which formats perform well in a given subreddit? | Subreddit Intelligence, Analytics |
| What has high engagement but weak discussion (an opening for a contribution)? | Opportunity Engine |
| What could I contribute, and how should I adapt it to r/X's rules and culture? | Opportunity + Content Studio + Critic |
| How do Indian Reddit trends differ from global ones? | Trend Detection (region dimension) |
| Which of my past contributions led to meaningful conversations? | Performance Analytics |

## Product principles

1. **Genuine engagement over karma.** Success is measured by discussion quality (comment depth, replies, OP engagement), not upvotes alone. The project name is ironic; the product does not farm.
2. **Human in the loop, always.** Nothing is published without explicit per-item approval. No scheduled or bulk posting.
3. **Evidence-grounded.** Every trend, opinion and recommendation links to the source posts or comments behind it. Model interpretations are labelled as interpretations.
4. **Deterministic first, LLM second.** Filtering, metrics and scoring are plain Python. LLMs are only used where language understanding is actually needed, and only on pre-filtered, budgeted batches.
5. **Respect the platform.** Authorized API access only. Rate limits, subreddit rules, user deletions and Reddit's Data API terms are hard constraints, not suggestions.
6. **Never pass off existing work as original.** Reposts, templates and remixes are labelled as such. Users' personal experiences are never invented.
7. **Affordable for one developer.** Runs entirely on free tiers (Groq, Reddit non-commercial) and local models, with per-model daily token caps.

## Explicit non-goals

- Vote manipulation, artificial engagement, sockpuppets, account farming, ban evasion.
- Unattended, scheduled or mass posting/commenting.
- Scraping Reddit HTML, or getting around API limits.
- Rehosting or reproducing copyrighted media.
- Training ML models on Reddit data (forbidden by the Data API terms without a separate agreement; see [REDDIT_API.md](REDDIT_API.md)).
- Multi-tenant SaaS, billing, teams (not in MVP).

## Success metrics (MVP)

| Metric | Target |
|---|---|
| Daily trend report generated without manual intervention | ≥ 6 of 7 days |
| Trend explanations traceable to source posts | 100% |
| Recommendations passing the critic that the user rates "useful" | ≥ 40% |
| Approved drafts removed by moderators | < 10% |
| Paid API spend | **$0**: Groq free tier + free Reddit tier + local embeddings/OCR |
| LLM tokens | ≤ per-model daily cap (default 160K, under Groq's 200K free limit) |
| Median comments per approved contribution vs. the subreddit's median | ≥ 1.0× |
