# AI Agent Design

## Core idea

The master prompt's 12-step pipeline is the **logical** flow. It is **not** built as one giant graph. Instead there are **small LangGraph graphs per job**, which share node functions (ADR-004). This gives selective execution for free: a meme request runs the meme graph, not the other eleven agents.

Most "agents" are plain deterministic Python. Only these nodes call an LLM:

| Node | LLM? | Model tier | Why |
|---|---|---|---|
| Research (ingest) | ❌ | — | API calls |
| Data validation | ❌ | — | schema + dedupe |
| Trend detection | ❌ | — | maths |
| Domain classification | ⚠️ fallback only | cheap | keywords + embeddings first; LLM for low-confidence, high-engagement posts |
| Topic labelling | ✅ batched | cheap | name clusters in ≤ 6 words, once per new cluster |
| Opinion mining | ✅ | cheap→strong | needs language understanding |
| Meme intelligence | ✅ top-N only | vision | joke/reference explanation |
| Subreddit intelligence | ⚠️ rule parsing only | cheap | once per rules change |
| Opportunity analysis | ⚠️ ranking is deterministic; rationale text via LLM | cheap | |
| Content generation | ✅ | strong | |
| Quality critic | ✅ + deterministic | cheap | |
| Human approval | ❌ | — | interrupt |
| Performance feedback | ❌ | — | maths |

## Graphs

```mermaid
flowchart TD
  subgraph G1[collect_cycle — every 30 min, no LLM]
    a1[ingest listings] --> a2[validate + dedupe] --> a3[refresh snapshots] --> a4[metrics] --> a5[embed new posts] --> a6[classify] --> a7[cluster topics] --> a8[trend scores]
  end

  subgraph G2[daily_report — daily]
    b1[select top topics<br/>IN + GLOBAL] --> b2[label new clusters] --> b3[opinion mining top-K]
    b1 --> b4[meme explain top-N]
    b3 --> b5[topic summaries]
    b4 --> b5
    b5 --> b6[opportunity analysis] --> b7[write report]
  end

  subgraph G3[generate_drafts — on demand]
    c1[load recommendation + sources + subreddit profile] --> c2[generate N variants] --> c3[deterministic checks] --> c4[LLM critic]
    c4 -->|fail & attempts<2| c2
    c4 --> c5{{interrupt: human review}}
    c5 -->|approve| c6[log + mark approved]
    c5 -->|reject| c7[log + mark rejected]
    c5 -->|regenerate| c2
  end

  subgraph G4[analyze_* — on demand]
    d0{target} -->|topic| b3
    d0 -->|meme| m1[pHash + template match + OCR + vision explain]
    d0 -->|subreddit| s1[rules parse + profile recompute]
  end
```

The full logical chain (research → … → performance feedback) is achieved by chaining jobs: `collect_cycle` → `daily_report` → user picks an opportunity → `generate_drafts` → approval → `track_contributions` → feedback updates opportunity weights (L).

## State

Each graph has a typed state (`TypedDict` / Pydantic). It carries IDs, not blobs; nodes load what they need from the DB. This keeps checkpoints small.

```python
class DraftState(TypedDict):
    run_id: UUID
    recommendation_id: UUID
    variants: int
    style: Style
    draft_ids: list[UUID]
    critic_attempts: int
    human_decision: Literal["approve", "reject", "regenerate"] | None
    errors: list[NodeError]
```

Run status machine (stored in `agent_runs.status`):

```mermaid
stateDiagram-v2
  [*] --> queued
  queued --> deferred_budget: budget exhausted
  deferred_budget --> queued: next budget day
  queued --> running
  running --> waiting_human: interrupt
  waiting_human --> running: user decision
  running --> succeeded
  running --> failed: retries exhausted
  failed --> queued: manual retry
  succeeded --> [*]
```

## LLM client (thin abstraction)

One module `agents/llm.py`, one function used everywhere:

```python
async def structured(task: Task, schema: type[T], messages: list[Msg], *, images: list[ImageRef] = []) -> T
```

- `Task` maps to a model via settings (`cheap`, `strong`, `vision`). Default provider: Anthropic (Haiku for cheap, Sonnet for strong/vision). This is swappable by config; a second provider adapter gets added only when actually needed (ADR-009).
- Structured outputs: Pydantic schema → provider tool/JSON-schema mode → validated. On a validation failure there is 1 repair retry with the error message, then the call fails.
- Every call records `tokens_in/out`, `cost_usd` (price table in config) and `duration_ms` into `agent_run_steps`.
- **Budget gate:** before each call, estimate the cost; if today's spend + estimate > `LLM_DAILY_BUDGET_USD`, raise `BudgetExceeded`. The run goes to `deferred_budget` (scheduled jobs) or returns a clear error to the UI (on-demand jobs).
- Timeouts: 60 s per call (configurable). Retries: 3 with exponential backoff + jitter on 429/5xx/timeouts only.
- Test double: `FakeLLM` returns fixture outputs per schema, so tests never hit the network.

## Prompt-injection posture

Reddit content is untrusted. It is always passed inside clearly delimited data blocks, the system prompt states that content inside them is data and never instructions, outputs are schema-constrained, and no tool use is given to models that read Reddit content. A post saying "ignore previous instructions" can at worst produce a bad summary, never an action.

## Cost controls

| Control | Default |
|---|---|
| Daily LLM budget | $1.00 |
| Opinion mining per daily report | top 10 topics, ≤ 40 sampled comments each |
| Vision meme explanations per day | 20 |
| Classification LLM fallback per day | 200 posts, batched 20/call |
| Cluster labelling | only new/changed clusters, batched |
| Caching | embeddings stored on rows; LLM outputs keyed by `(task, input_hash, model)` in Redis for 24 h |
| Draft generation | on demand only; all N variants in **one** call |

## Observability

`agent_runs` + `agent_run_steps` feed the Agent Execution Monitor: per-run timeline, per-node status/attempts/duration, tokens, cost, errors, plus a "today's spend vs budget" gauge. LangSmith is optional (off by default) and not required.

## Evaluation

Small hand-labelled golden sets in `backend/tests/evals/` (no Reddit text committed; synthetic or paraphrased examples only):
- classification: 100 posts → expected labels (precision/recall per category)
- critic: 30 drafts with known violations → must flag ≥ 90%
- opinion mining: 10 threads → evidence IDs must exist in the input (100%), no fabricated quotes
Evals run via `pytest -m eval` manually or nightly, not on every PR (they cost tokens).
