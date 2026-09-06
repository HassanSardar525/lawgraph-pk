# Development Guide

## Environment

Requirements:

- Python >= 3.11
- `uv`
- Git

Install:

```bash
uv sync --extra dev
```

Run tests:

```bash
uv run pytest
```

Run demo:

```bash
uv run lawgraph demo
```

Run baseline evaluation:

```bash
uv run lawgraph evaluate
```

Run API:

```bash
uv run uvicorn lawgraph_pk.api:app --reload
```

Open `http://127.0.0.1:8000`.

## Code layout

```text
src/lawgraph_pk/
  models.py       # Pydantic domain objects
  text.py         # canonicalization, chunking, deterministic embeddings
  extraction.py   # ClaimExtractor interface + fixture extractor
  store.py        # SQLite graph/document persistence
  ingestion.py    # incremental indexing and temporal updates
  retrieval.py    # hierarchical retrieval
  baselines.py    # vector-only baseline
  evaluation.py   # experiment metrics
  service.py      # dependency wiring
  api.py          # FastAPI endpoints
  cli.py          # demo/evaluation entrypoints
```

## Design principles

### Stable interfaces

`ClaimExtractor` should remain an interface. Real LLM extraction should implement it rather than rewriting indexing logic.

### Provenance first

Every claim should point back to a document and evidence span. Later PDF ingestion should retain page number and offsets.

### Research isolation

Baselines should be independently callable. Do not make B1/B2 accidentally depend on proposed-system features.

### Deterministic tests

Unit tests should not require network access or API keys. External-model experiments should live in explicit integration/evaluation commands.

## Suggested commit structure

Use focused commits:

```text
feat: add pdf ingestion
feat: add structured llm claim extractor
feat: add rebuild graph baseline
feat: add evaluation dataset
feat: add neo4j adapter
feat: add graph explorer
exp: compare incremental and rebuild indexing
exp: run temporal freshness ablation
```

## Before declaring a milestone complete

- tests pass
- demo runs from a clean environment
- docs/status updated
- research assumptions recorded
- experiment configuration saved
- no generated secrets committed
