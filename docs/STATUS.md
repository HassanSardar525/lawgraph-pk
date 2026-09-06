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

## Current limitations

- No PDF parser.
- No real LLM extraction.
- Hash embeddings are only a deterministic test substitute.
- SQLite is not the target production graph/vector backend.
- The answer generator is template-based rather than an LLM.
- Conflict handling currently focuses on supersession for selected predicates; generalized contradiction detection is not implemented.
- The evaluation set is synthetic.

## Milestone 2 — Real ingestion

**Status: next**

Tasks:

- [ ] choose and document legal data sources/licensing
- [ ] PDF/text extraction with page-aware provenance
- [ ] structured LLM claim extractor
- [ ] extraction confidence and schema validation
- [ ] entity/relation normalization tests
- [ ] evidence-span validation

## Milestone 3 — Research baselines

- [x] vector-only baseline
- [ ] rebuild/static Graph-RAG baseline
- [ ] common retrieval interface
- [ ] common answer-generation protocol
- [ ] reproducible dataset loader

## Milestone 4 — Proposed system

- [ ] generalized temporal claim model
- [ ] explicit conflict/contradiction edges
- [ ] hierarchical scoring and thresholds
- [ ] hybrid graph/vector retrieval
- [ ] update-impact accounting

## Milestone 5 — Production stores

- [ ] Neo4j adapter
- [ ] PostgreSQL + pgvector adapter
- [ ] Docker Compose
- [ ] configuration management

## Milestone 6 — Research evaluation

- [ ] 150-question verified dataset
- [ ] batch update experiment
- [ ] freshness experiment
- [ ] retrieval experiment
- [ ] ablations
- [ ] error analysis
- [ ] charts and report

## Milestone 7 — Portfolio demo

- [ ] interactive graph explorer
- [ ] document/update timeline
- [ ] citation viewer
- [ ] experiment dashboard
- [ ] deployment
- [ ] research write-up
