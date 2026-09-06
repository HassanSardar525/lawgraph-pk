# LLM Handoff — Read This First

This file is a compact continuation packet for a future LLM/agent taking over LawGraph-PK.

## Mission

Continue building a portfolio-quality **research implementation**, not a generic legal chatbot.

The target project is:

> **LawGraph-PK — Temporal and Conflict-Aware Incremental Hierarchical Graph-RAG for Evolving Legislation**

The central experiment compares vector RAG, rebuild Graph-RAG, incremental Graph-RAG and the proposed temporal/conflict-aware hierarchical system.

## Current truth

Milestone 1 is complete. The repository contains a deterministic local prototype and tests. Do not assume real PDFs, LLM extraction, Neo4j or PostgreSQL are implemented yet.

Read `docs/STATUS.md` for the authoritative implementation state.

## Key architectural interfaces

- `ClaimExtractor` in `src/lawgraph_pk/extraction.py`
- `IncrementalIndexer` in `src/lawgraph_pk/ingestion.py`
- `HierarchicalRetriever` in `src/lawgraph_pk/retrieval.py`
- `VectorOnlyRetriever` in `src/lawgraph_pk/baselines.py`
- `SQLiteGraphStore` in `src/lawgraph_pk/store.py`
- `LawGraphService` in `src/lawgraph_pk/service.py`

Preserve these boundaries where practical.

## Immediate next task

Implement **real PDF ingestion + structured LLM extraction** without breaking the deterministic test path.

Desired flow:

```text
PDF
 -> page-aware text extraction
 -> chunks with page metadata
 -> ClaimExtractor implementation
 -> validated entities/relations/claims
 -> IncrementalIndexer
 -> temporal/conflict graph
```

The extractor must return evidence that can be traced back to the source page/chunk.

## Then

1. Implement rebuild Graph-RAG baseline.
2. Define common evaluation dataset format.
3. Add real legal-source ingestion.
4. Add temporal/conflict experiments.
5. Add Neo4j/PostgreSQL adapters.
6. Build graph/timeline UI.
7. Run and record experiments.
8. Write the research report.

## Do not do yet

- Do not optimize for huge datasets.
- Do not train a large model.
- Do not add unnecessary agents.
- Do not replace the deterministic tests with API-dependent tests.
- Do not claim legal correctness without verified sources.
- Do not claim exact reproduction of LightRAG.

## Definition of done

A future milestone is complete only when:

- code works from a clean environment;
- tests pass;
- baseline/proposed systems are comparable;
- experiment configuration is recorded;
- results are saved;
- limitations are documented;
- `docs/STATUS.md` and `CHANGELOG.md` are updated.

## Primary references

- LightRAG paper: https://aclanthology.org/2025.findings-emnlp.568/
- LightRAG project: https://lightrag.github.io/
- LightRAG code: https://github.com/HKUDS/LightRAG
