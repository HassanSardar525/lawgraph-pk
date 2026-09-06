# Changelog

## 0.2.0 — Research comparison and observability

- Added static/rebuild Graph-RAG baseline.
- Added deterministic comparison benchmark for vector, graph and temporal/hierarchical systems.
- Added Hit@5, MRR, nDCG, answer-accuracy and stale-answer measurements.
- Added incremental-vs-rebuild update-work measurement.
- Added optional LangSmith tracing for ingestion, retrieval floors, baseline queries and benchmark comparisons.
- Added LangSmith setup/inspection documentation and `.env.example`.
- Kept LangSmith optional so deterministic tests and the core benchmark remain API-key free.

## 0.1.0 — Initial research prototype

- Added SQLite-backed incremental knowledge-graph storage.
- Added deterministic pipe-delimited claim extraction for reproducible fixtures.
- Added entity canonicalization and document checksums.
- Added temporal supersession for selected replaceable predicates.
- Added three-floor hierarchical retrieval.
- Added citation metadata and retrieval traces.
- Added vector-only baseline and basic evaluation metrics.
- Added FastAPI endpoints and browser demo.
- Added automated tests for incremental updates, idempotency, fallback retrieval, API behavior and evaluation metrics.
- Added research continuation documentation for future contributors/LLMs.
