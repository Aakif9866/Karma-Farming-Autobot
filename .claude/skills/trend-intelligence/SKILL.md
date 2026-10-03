---
name: trend-intelligence
description: Trend detection and classification specialist. Use for taxonomy (config/taxonomy.yaml), multi-label classification, local embeddings (fastembed), topic clustering (pgvector + HDBSCAN), engagement metrics, configurable explainable trend scoring (config/scoring.yaml), trend statuses, India-vs-global comparison, daily diffs, opportunity scoring maths.
when_to_use: Triggers on "trend score", "velocity", "clustering", "topics", "taxonomy", "classification", "embeddings", "emerging", "India vs global", "scoring weights".
paths: "backend/app/intelligence/**,backend/config/**"
---

# Trend Intelligence

Source of truth: `docs/TREND_DETECTION.md` (formulas, thresholds, statuses) and `docs/CONTENT_GENERATION.md` (opportunity score).

## Responsibilities
- Taxonomy loader (YAML → `content_categories`, versioned), keyword + embedding classifier, LLM fallback only for low-confidence high-engagement posts.
- Post metrics: engagement/comment velocity from snapshots, relative engagement vs the subreddit's age-bucket baseline, discussion intensity, recency, controversy.
- Clustering: assign to the nearest centroid (cosine ≥ threshold), discover new clusters with `sklearn.cluster.HDBSCAN`, track dormant/recurring.
- Topic snapshots, weighted scoring with `score_breakdown`, status rules, region mix, daily diffs.

## Execution
1. Implement each metric as a **pure numpy function** with a docstring giving the formula, plus a unit test with hand-computed values.
2. Read weights and thresholds from `config/scoring.yaml`. Store `scoring_version` on every score row.
3. Store the breakdown: `{"version", "components": {name: {raw, norm, weight, contrib}}, "top_posts": [...]}`.
4. Validate on real data (Phase 3 gate: top-20 topics hand-reviewed ≥ 15/20 sensible) and record the threshold changes in the doc.

## Constraints
- **Never rank by raw upvotes.** Every score must be explainable from its stored components.
- No LLM calls in metrics, scoring or clustering. LLM use is limited to the classification fallback and cluster *labels* (batched, Groq cheap model).
- Embeddings are local (fastembed, 384-d), cached on the row (`embedded_at`), never recomputed needlessly.
- Clustering must be deterministic in tests (fixed seeds, fixed input order).
- New categories are added through YAML only; adding one must never require a code change.

## Examples
- *"Add Cricket under Sports."* → edit `taxonomy.yaml` (category `sports` → subcategory `cricket` → topics/keywords), bump the version, run the loader, check the centroid gets computed, add 3 golden-set examples.
- *"Topic stays 'peaking' forever."* → check the `growth` window uses snapshots 6 h apart and that `recency_factor` decays. Add a test with a flat-then-dropping series expecting `declining`.
