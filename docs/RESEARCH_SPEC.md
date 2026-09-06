# Research Specification

## Working title

**LawGraph-PK: Temporal and Conflict-Aware Incremental Hierarchical Graph-RAG for Evolving Legislation**

## Primary research question

Can incremental temporal graph-RAG incorporate evolving legal knowledge faster and more cheaply than rebuilding the knowledge graph after every document batch, while hierarchical retrieval maintains answer quality when exact graph evidence is unavailable?

## Secondary questions

1. Does graph retrieval improve multi-hop legal question answering over flat vector retrieval?
2. Does temporal versioning reduce stale answers after amendments?
3. Does explicit conflict preservation reduce unsafe overwriting of competing claims?
4. Does hierarchical fallback recover answers when entity/relation extraction misses the query entity?
5. What is the quality/cost/latency trade-off of the additional graph machinery?

## Hypotheses

- **H1:** Incremental indexing reduces update time and extraction work relative to full rebuilds.
- **H2:** Graph-aware retrieval improves relational and multi-hop retrieval metrics over vector-only retrieval.
- **H3:** Temporal claim versioning reduces stale-answer rate on update-sensitive questions.
- **H4:** Conflict-aware storage is safer than destructive overwriting when sources disagree.
- **H5:** Hierarchical fallback improves recall over exact-only graph retrieval at acceptable latency cost.

## Systems to compare

| ID | System | Purpose |
|---|---|---|
| B1 | Vector-only RAG | Flat retrieval baseline |
| B2 | Static/Rebuild Graph-RAG | Graph quality without incremental optimization |
| B3 | Incremental Graph-RAG | Tests update efficiency |
| Ours | Temporal + Conflict + Hierarchical Graph-RAG | Proposed extension |

All systems should use the same document corpus, question set, model family where practical, and answer-generation protocol.

## Controlled variables

Record:

- model name and version
- embedding model
- chunk size and overlap
- top-k values
- graph depth
- retrieval thresholds
- extraction prompt/version
- temperature
- dataset commit/version
- software commit SHA
- hardware
- API pricing assumptions

## Dependent variables

### Quality

- answer correctness
- citation correctness
- citation completeness
- faithfulness
- retrieval Recall@K
- MRR
- nDCG
- stale-answer rate
- contradiction-detection precision/recall

### Efficiency

- indexing wall time
- update wall time
- number of documents/chunks reprocessed
- LLM calls
- input/output tokens
- estimated cost
- query latency

## Required ablations

1. Remove temporal metadata.
2. Remove conflict handling.
3. Remove hierarchical fallback.
4. Remove entity canonicalization.
5. Exact graph retrieval only.
6. Graph + vector hybrid retrieval.

## Minimum convincing result

A successful project should not depend on one metric. The report should demonstrate a measurable trade-off, for example:

> The proposed system reduces stale answers and update cost while maintaining or improving retrieval quality, with the cost/latency overhead explicitly reported.

If results do not support the hypothesis, report that honestly and analyze why.
