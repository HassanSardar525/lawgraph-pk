# Ready-to-Paste Continuation Prompt

You are taking over an existing research implementation called **LawGraph-PK**.

Before changing code, read these files:

- `AGENTS.md`
- `PROJECT_CONTEXT.md`
- `docs/LLM_HANDOFF.md`
- `docs/STATUS.md`
- `docs/DECISIONS.md`
- `docs/RESEARCH_SPEC.md`
- `docs/ARCHITECTURE.md`
- `docs/EXPERIMENT_PROTOCOL.md`
- `docs/NEXT_SESSION.md`
- `TODO.md`

### Mission

Continue this as a research implementation, not a generic chatbot. The project combines incremental knowledge-graph RAG with hierarchical retrieval for evolving legislation, with temporal versioning and conflict-aware provenance as the proposed extension.

### Current milestone

Milestone 1 is complete. It contains deterministic SQLite storage, entity canonicalization, incremental claim insertion, temporal supersession, three-floor retrieval, citations, a vector-only baseline, a basic evaluation harness, FastAPI and tests.

### Immediate next step

Implement real page-aware PDF ingestion and a structured LLM claim extractor behind the existing `ClaimExtractor` interface. Keep deterministic extraction for unit tests.

Then implement the rebuild Graph-RAG baseline and a common evaluation dataset. Do not skip baselines or jump directly to a polished UI.

### Engineering constraints

- Python 3.11+
- use `uv`
- keep tests deterministic and API-key free
- preserve provenance
- do not silently overwrite historical claims
- do not commit secrets
- keep SQLite as a simple reference backend while adding production adapters later

### Research constraints

Compare:

1. Vector-only RAG
2. Rebuild Graph-RAG
3. Incremental Graph-RAG
4. Temporal + Conflict + Hierarchical Graph-RAG (ours)

Measure retrieval quality, answer/citation quality, stale-answer rate, update time, processed work and estimated LLM cost. Report negative results honestly.

### Validation

After meaningful changes run:

```bash
uv run pytest
uv run lawgraph demo
uv run lawgraph evaluate
```

Update `docs/STATUS.md`, `CHANGELOG.md` and `TODO.md` as milestones change.
