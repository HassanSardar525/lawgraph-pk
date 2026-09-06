# LawGraph-PK

**Temporal and Conflict-Aware Incremental Hierarchical Graph-RAG for Evolving Legislation**

LawGraph-PK is a research implementation that combines two ideas:

1. **Incremental knowledge-graph RAG:** new documents update only affected graph state instead of rebuilding everything.
2. **Hierarchical retrieval:** a query starts with narrow graph evidence, expands to related graph evidence, and finally falls back to document/vector retrieval when necessary.

The research extension adds **temporal claim versioning, provenance and conflict-aware updates** so that legal amendments do not silently erase history or produce stale answers.

> **Research status:** Milestone 1 is complete. The current code is a deterministic, local prototype. Real PDFs, LLM extraction, Neo4j/PostgreSQL, verified Pakistani legal data and the full experiment suite are next.

## Architecture

```mermaid
flowchart LR
    D[New document] --> C[Chunk]
    C --> E[Extract claims/entities]
    E --> N[Canonicalize]
    N --> U[Incremental update]
    U --> T[Temporal + conflict manager]
    T --> G[(Knowledge Graph)]
    C --> V[(Vector / chunk index)]

    Q[Question] --> R[Query understanding]
    R --> F1{Floor 1\\nExact graph}
    F1 -- insufficient --> F2{Floor 2\\nRelated graph}
    F2 -- insufficient --> F3[Floor 3\\nVector chunks]
    F1 --> X[Evidence fusion]
    F2 --> X
    F3 --> X
    X --> A[Citation-grounded answer]
    G --> F1
    G --> F2
    V --> F3
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full design.

## Research question

> Can an incrementally maintained temporal knowledge graph answer evolving legal questions accurately while reducing update work compared with rebuilding the graph after every document batch, and can hierarchical fallback retrieval recover evidence when exact graph retrieval fails?

The project is anchored in the ideas of **LightRAG: Simple and Fast Retrieval-Augmented Generation** (Findings of EMNLP 2025), but is explicitly a **small-scale reproduction and domain extension**, not a claim of exact reproduction.

- Paper: https://aclanthology.org/2025.findings-emnlp.568/
- Project: https://lightrag.github.io/
- Reference implementation: https://github.com/HKUDS/LightRAG

## Quick start with `uv`

```bash
uv sync --extra dev
uv run pytest
uv run lawgraph demo
uv run lawgraph evaluate
uv run uvicorn lawgraph_pk.api:app --reload
```

Open <http://127.0.0.1:8000>.

## Current prototype

The local milestone intentionally avoids external services:

- Python 3.11+
- FastAPI + Pydantic
- SQLite
- deterministic hash embeddings
- deterministic `subject | predicate | object` extraction
- pytest

This makes the core research logic reproducible without an API key.

## Repository map

```text
src/lawgraph_pk/
  models.py       # domain models
  text.py         # canonicalization/chunking/test embeddings
  extraction.py   # ClaimExtractor interface + fixture extractor
  store.py        # SQLite persistence
  ingestion.py    # incremental indexing + temporal updates
  retrieval.py    # hierarchical retrieval
  baselines.py    # vector-only baseline
  evaluation.py   # experiment metrics
  service.py      # dependency wiring
  api.py          # FastAPI API
  cli.py          # demo/evaluation CLI

docs/
  ARCHITECTURE.md
  EXPERIMENT_PROTOCOL.md
  IMPLEMENTATION_PLAN.md
  PAPER_NOTES.md
  RESEARCH_SPEC.md
  STATUS.md
  DEVELOPMENT.md
  LLM_HANDOFF.md

AGENTS.md           # instructions for future coding agents/LLMs
PROJECT_CONTEXT.md  # project memory and research intent
TODO.md             # active work list
CHANGELOG.md        # implementation history
```

## Research systems

| ID | System | Purpose |
|---|---|---|
| B1 | Vector-only RAG | Flat retrieval baseline |
| B2 | Rebuild Graph-RAG | Tests graph quality without incremental optimization |
| B3 | Incremental Graph-RAG | Tests update efficiency |
| Ours | Temporal + Conflict + Hierarchical Graph-RAG | Proposed extension |

## Important limitation

The included demo data is fictional. Nothing in this repository is legal advice. Real legal documents must be sourced responsibly, with provenance and licensing recorded, and evaluation ground truth must be human-verified.

## Continuing the project with another LLM

Start with:

1. `AGENTS.md`
2. `PROJECT_CONTEXT.md`
3. `docs/LLM_HANDOFF.md`
4. `docs/STATUS.md`
5. `docs/RESEARCH_SPEC.md`
6. `docs/ARCHITECTURE.md`
7. `docs/EXPERIMENT_PROTOCOL.md`
8. `TODO.md`

Those files are intentionally maintained as project handoff documentation.
