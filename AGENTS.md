# AGENTS.md — LawGraph-PK continuation guide

## Purpose

LawGraph-PK is a research implementation project, not merely a chatbot. The project studies the combination of **incremental knowledge-graph RAG** and **hierarchical/coarse-to-fine retrieval** for evolving legal knowledge.

The intended research contribution is a small-scale reproduction plus domain extension:

> Can an incrementally maintained temporal knowledge graph answer evolving legal questions more accurately and cheaply than repeatedly rebuilding a graph, while hierarchical fallback retrieval prevents failures when exact graph evidence is missing?

## Current state

Milestone 1 is implemented and tested. It is deliberately local and deterministic:

- SQLite graph/document store
- deterministic hash embeddings
- pipe-delimited claim extractor
- incremental entity/claim insertion
- temporal supersession for selected predicates
- three-floor retrieval
- citation objects and retrieval traces
- vector-only baseline
- basic evaluation harness
- FastAPI API
- minimal browser demo

Do not describe this milestone as a production legal system or as a faithful full reproduction of every LightRAG implementation detail.

## Development rules

1. Use Python 3.11+ and `uv`.
2. Keep core logic behind interfaces so SQLite can later be replaced by Neo4j/PostgreSQL.
3. Keep research baselines reproducible and isolated from the proposed system.
4. Never use model-generated text as verified legal ground truth without human verification.
5. Every experimental claim must have a measurable metric and a reproducible configuration.
6. Preserve source URI, publication date, checksum, chunk ID and evidence span whenever possible.
7. Do not silently overwrite historical legal claims. Prefer versioning, supersession or explicit conflict relationships.
8. Add tests before or alongside non-trivial behavior changes.
9. Keep the README concise; put detailed research material under `docs/`.

## Preferred workflow

Before implementing a feature:

1. Read `PROJECT_CONTEXT.md`.
2. Read `docs/RESEARCH_SPEC.md` and `docs/ARCHITECTURE.md`.
3. Check `docs/STATUS.md` and `docs/EXPERIMENT_PROTOCOL.md`.
4. Inspect existing code rather than replacing working components.
5. Add/update tests.
6. Run `uv run pytest` and the relevant CLI experiment.
7. Update `docs/STATUS.md` and `CHANGELOG.md`.

## Next major milestone

Implement real PDF ingestion and a structured LLM claim extractor while preserving the current `ClaimExtractor` interface. Then add a rebuild-based Graph-RAG baseline and a common evaluation dataset.

## Important research distinction

- **Incremental indexing** answers: “How do we update the knowledge base when new documents arrive?”
- **Hierarchical retrieval** answers: “Where should we search when exact evidence is unavailable?”
- The project combines both, but they must be evaluated independently through ablations.
