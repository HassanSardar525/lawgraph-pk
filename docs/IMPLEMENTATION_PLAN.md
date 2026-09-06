# Implementation and Research Plan

## Working title

**LawGraph-PK: Temporal and Conflict-Aware Incremental Hierarchical Graph-RAG for Evolving Legislation**

## Research question

Can an incrementally maintained knowledge graph incorporate legal updates faster and more cheaply than full graph reconstruction while preserving citation accuracy, reducing stale answers and recovering evidence when exact graph retrieval fails?

## Core idea

The project combines two orthogonal mechanisms:

### Incremental indexing

When a new document arrives:

```text
new document
    -> chunks
    -> claims/entities
    -> canonicalization
    -> affected graph nodes/edges
    -> temporal/conflict update
```

Only new/affected state should be processed. Historical claims remain queryable.

### Hierarchical retrieval

When a question arrives:

```text
Floor 1: exact entity/claim evidence
       ↓ if insufficient
Floor 2: related entities/relations
       ↓ if insufficient
Floor 3: vector/document chunks
       ↓
Evidence fusion + citations
```

These mechanisms must be evaluated separately as well as together.

## Hypotheses

- **H1:** Incremental indexing reduces update time and extraction work relative to complete rebuilding.
- **H2:** Graph-aware retrieval improves relational/multi-hop retrieval over vector-only retrieval.
- **H3:** Temporal claim versioning reduces stale answers after amendments.
- **H4:** Explicit conflict preservation is safer than destructive overwriting.
- **H5:** Hierarchical fallback improves recall over exact-only graph retrieval.

## Research systems

| ID | System | Purpose |
|---|---|---|
| B1 | Vector-only RAG | Flat retrieval baseline |
| B2 | Rebuild Graph-RAG | Rebuild complete graph after each update batch |
| B3 | Incremental Graph-RAG | Update only newly affected graph state |
| Ours | Temporal + Conflict + Hierarchical | Proposed system |

## Milestones

### 1. Local vertical slice — COMPLETE

- deterministic extraction
- SQLite persistence
- entity canonicalization
- incremental insertion
- temporal supersession
- hierarchical retrieval
- citations
- vector baseline
- evaluation harness
- FastAPI/browser demo
- automated tests

### 2. Real ingestion — NEXT

- page-aware PDF parsing
- official-source metadata
- structured LLM extraction
- evidence-span validation
- extraction confidence
- legal entity normalization

### 3. Research baselines

- rebuild Graph-RAG
- common retriever interface
- common answer-generation protocol
- versioned evaluation dataset

### 4. Proposed system

- generalized temporal claim intervals
- explicit contradiction edges
- source priority/provenance
- hierarchical scoring thresholds
- graph/vector evidence fusion
- update-impact accounting

### 5. Storage and deployment

- Neo4j adapter
- PostgreSQL + pgvector adapter
- Docker Compose
- configuration and logging

### 6. Evaluation

- 150+ verified questions
- chronological batch updates
- retrieval benchmark
- freshness benchmark
- cost/latency benchmark
- ablations
- error analysis

### 7. Portfolio presentation

- interactive graph explorer
- update timeline
- citation viewer
- experiment dashboard
- research report
- deployment

## Dataset protocol

Start with a small, source-controlled corpus of legal documents. Ingest chronologically as `D0`, `D1`, `D2`, ...

Each source should preserve:

- source URI
- title
- publication/effective date
- checksum
- page number
- evidence span
- document/amendment relationship

Target question set:

- 40 direct factual questions
- 40 relational/multi-hop questions
- 40 time/update-sensitive questions
- 30 contradiction/stale-information questions

## Metrics

### Quality

- Recall@5
- MRR
- nDCG
- answer correctness
- citation precision/completeness
- faithfulness
- stale-answer rate
- conflict-detection precision/recall

### Efficiency

- update wall time
- chunks processed
- claims inserted/updated
- LLM calls
- input/output tokens
- estimated cost
- query latency

## Required ablations

- no temporal metadata
- no conflict handling
- no hierarchical fallback
- no entity canonicalization
- exact graph only
- graph + vector hybrid

## Research honesty rule

The project should report negative results. If the proposed system is more expensive or does not improve quality on a category, that is a useful research result when the cause is analyzed.
