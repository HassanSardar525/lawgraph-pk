# TODO

## Completed — Observability

- [x] Optional LangSmith integration.
- [x] Trace ingestion/update effects.
- [x] Trace query and retrieval floors.
- [x] Trace vector and static graph baselines.
- [x] Trace benchmark comparison summaries.

## Completed — Page-aware real ingestion foundation

- [x] Page-aware PDF text extraction with `pypdf`.
- [x] Page-level chunk provenance.
- [x] PDF upload endpoint.
- [x] Evidence-span storage and validation.
- [x] Page numbers in retrieval citations.
- [x] Deterministic tests for provenance.

## Next — Real-data validation

- [ ] Add an optional structured LLM extractor behind the existing `ClaimExtractor` interface.
- [ ] Add extraction confidence calibration/schema versioning.
- [ ] Strengthen legal entity/relation normalization.
- [ ] Build a small manually verified legal corpus from official sources.
- [ ] Convert real questions into the existing `EvaluationCase` format.
- [ ] Run vector vs rebuild graph vs incremental graph vs temporal/hierarchical comparisons on real data.
- [ ] Add OCR support for scanned/image-only PDFs.

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
