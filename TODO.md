# TODO

## Next — Real-data validation

- [ ] Add page-aware PDF ingestion with source/page provenance.
- [ ] Add an optional structured LLM extractor behind the existing `ClaimExtractor` interface.
- [ ] Validate extracted evidence spans against source chunks.
- [ ] Build a small manually verified legal corpus from official sources.
- [ ] Convert real questions into the existing `EvaluationCase` format.
- [ ] Run vector vs rebuild graph vs incremental graph vs temporal/hierarchical comparisons.

## Research extension

- [ ] Generalize temporal intervals beyond replaceable predicates.
- [ ] Add explicit contradiction/conflict edges.
- [ ] Add source-priority/provenance scoring.
- [ ] Add ablations for temporal logic, hierarchical fallback and entity canonicalization.
- [ ] Add update-impact accounting for LLM extraction calls/tokens.

## Engineering later

- [ ] Neo4j adapter.
- [ ] PostgreSQL + pgvector adapter.
- [ ] Docker Compose.
- [ ] Optional real embedding provider.
- [ ] Optional LLM answer generator.

## Portfolio last

- [ ] Graph explorer.
- [ ] Update timeline.
- [ ] Citation viewer.
- [ ] Experiment charts.
- [ ] Research report.
