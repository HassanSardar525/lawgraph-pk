# Project Status

Last updated: 2026-09-06

## Milestone 1 — Local vertical slice

**Status: complete**

Implemented:

- [x] SQLite persistence
- [x] document checksums and idempotent ingestion
- [x] entity canonicalization
- [x] deterministic claim extraction fixture
- [x] incremental claim insertion
- [x] temporal supersession for replaceable predicates
- [x] historical `as_of` retrieval
- [x] three-floor hierarchical retrieval
- [x] citation metadata
- [x] retrieval trace (`floors_tried`)
- [x] vector-only baseline
- [x] basic evaluation metrics
- [x] FastAPI API
- [x] browser demo
- [x] automated tests

## Milestone 2 — Research comparison harness

**Status: complete**

Implemented:

- [x] static/rebuild Graph-RAG baseline
- [x] incremental Graph-RAG indexing-cost comparison
- [x] deterministic benchmark corpus with update/history/relational/fallback cases
- [x] Hit@5, MRR and nDCG@5
- [x] answer accuracy and stale-answer rate
- [x] per-category metrics
- [x] reproducible `lawgraph compare` command
- [x] update work accounting (chunks and claims processed)

Current synthetic run shows the proposed temporal + hierarchical system outperforming the baselines on the benchmark's answer-accuracy metric while incremental indexing substantially reduces repeated processing work. See `docs/EXPERIMENT_RESULTS.md`.

## Milestone 2.5 — LangSmith observability

**Status: implemented**

Implemented:

- [x] optional LangSmith Python SDK integration
- [x] ingestion traces with update/supersession statistics
- [x] end-to-end query traces
- [x] Floor 1/2/3 retrieval spans
- [x] vector-only and static Graph-RAG baseline traces
- [x] citation metadata in retrieval spans
- [x] local no-key fallback so the benchmark remains deterministic
- [x] setup and inspection guide in `docs/LANGSMITH.md`

LangSmith is an inspection/evidence layer only. It does not affect retrieval or evaluation scores.

## Milestone 3 — Real ingestion

**Status: in progress**

Implemented:

- [x] page-aware PDF text extraction with optional `pypdf`
- [x] page-aware chunk provenance
- [x] PDF upload API endpoint
- [x] evidence-span storage and validation
- [x] page numbers in retrieval citations
- [x] deterministic tests for page/evidence provenance
- [x] official-source strategy documented in `docs/REAL_INGESTION.md`

Remaining:

- [ ] structured LLM claim extractor
- [ ] extraction confidence calibration/schema versioning
- [ ] stronger legal entity/relation normalization
- [ ] small manually verified Pakistani legal corpus
- [ ] OCR path for scanned PDFs

## Current limitations

- No real LLM extraction yet.
- Hash embeddings are only a deterministic test substitute.
- SQLite is not the target production graph/vector backend.
- The answer generator is template-based rather than an LLM.
- Conflict handling currently focuses on supersession for selected predicates; generalized contradiction detection is not implemented.
- The evaluation set is synthetic and intentionally small.
- LangSmith tracing is optional and requires a user-provided API key to send remote traces.
- OCR for scanned/image-only PDFs is not implemented.

## Milestone 4 — Research baselines

- [x] vector-only baseline
- [x] rebuild/static Graph-RAG baseline
- [x] common retrieval interface
- [x] common answer-generation protocol
- [x] reproducible dataset loader

## Milestone 5 — Proposed system

- [ ] generalized temporal claim model
- [ ] explicit conflict/contradiction edges
- [x] hierarchical fallback scoring
- [x] graph/vector fallback
- [x] update-impact accounting

## Milestone 6 — Production stores

- [ ] Neo4j adapter
- [ ] PostgreSQL + pgvector adapter
- [ ] Docker Compose
- [ ] configuration management

## Milestone 7 — Research evaluation

- [ ] 150-question verified dataset
- [ ] chronological batch update experiment on real data
- [ ] freshness experiment on real amendments
- [ ] retrieval experiment on real legal questions
- [ ] ablations
- [ ] error analysis
- [ ] charts and report

## Milestone 8 — Portfolio demo

- [ ] interactive graph explorer
- [ ] document/update timeline
- [ ] citation viewer
- [ ] experiment charts
- [ ] deployment
- [ ] research write-up
