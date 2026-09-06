# TODO

## Immediate

- [ ] Add page-aware PDF ingestion.
- [ ] Implement LLM structured extraction behind `ClaimExtractor`.
- [ ] Add extraction schema/version metadata.
- [ ] Add rebuild Graph-RAG baseline.
- [ ] Create versioned evaluation JSONL.

## Research

- [ ] Measure incremental vs rebuild update cost.
- [ ] Measure stale-answer rate after amendments.
- [ ] Test graph vs vector retrieval on multi-hop questions.
- [ ] Test hierarchical fallback under entity-extraction failures.
- [ ] Run temporal/conflict ablations.
- [ ] Add human-verified evidence labels.

## Engineering

- [ ] Neo4j adapter.
- [ ] PostgreSQL/pgvector adapter.
- [ ] Docker Compose.
- [ ] Better configuration and logging.
- [ ] Graph visualization.
- [ ] Evaluation dashboard.

## Presentation

- [ ] Architecture figure.
- [ ] Results table.
- [ ] Update-cost chart.
- [ ] Freshness/stale-answer chart.
- [ ] Error analysis examples.
- [ ] Research report and reproducibility appendix.
