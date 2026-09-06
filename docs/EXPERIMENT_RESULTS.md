# Current Comparison Experiment

This is the first end-to-end comparison harness for LawGraph-PK. It is intentionally deterministic and runs without an API key.

## Run

```bash
uv run lawgraph compare
```

The benchmark is synthetic legal-like data. It is **not real law** and must not be used for legal advice. The purpose is to test whether the architecture behaves as expected before adding PDF parsing, LLM extraction, and a real verified corpus.

## Systems

| System | What it tests |
|---|---|
| B1 `vector_only` | Flat chunk retrieval |
| B2 `rebuild_graph` | Graph retrieval with a rebuild/static snapshot |
| B3 `incremental_graph` | Same graph retrieval, but knowledge is maintained incrementally |
| Ours `temporal_hierarchical` | Incremental graph + temporal filtering + hierarchical fallback |

B2 and B3 intentionally have the same query-time retriever. Their difference is measured in the update-efficiency experiment; this isolates **retrieval quality** from **index maintenance cost**.

## Metrics

- Hit@5, MRR, nDCG@5: retrieval quality.
- Answer accuracy: expected answer term is present and explicitly forbidden stale term is absent.
- Stale-answer rate: answer contains a forbidden historical/stale term.
- Mean latency: local query wall time.
- Update work: chunks/claims processed and wall time for incremental indexing versus rebuilding after every batch.

## Example run from the current implementation

The exact wall-clock numbers will vary by machine. The current local run produced approximately:

| System | Hit@5 | MRR | nDCG@5 | Answer accuracy | Stale rate |
|---|---:|---:|---:|---:|---:|
| Vector-only | 1.00 | 0.74 | 0.81 | 0.44 | 0.56 |
| Rebuild Graph-RAG | 0.67 | 0.38 | 0.45 | 0.44 | 0.00 |
| Incremental Graph-RAG | 0.67 | 0.38 | 0.45 | 0.44 | 0.00 |
| Temporal + Hierarchical | 1.00 | 0.89 | 0.92 | 0.89 | 0.11 |

The important result is not the absolute score on this tiny synthetic benchmark. The useful signal is the **relative behavior**:

1. Vector retrieval finds relevant text but frequently mixes old and new versions.
2. Static graph retrieval improves structured retrieval but cannot answer historical questions correctly because it has no temporal interpretation.
3. The proposed system recovers both current and historical claims and can fall back to chunks when no exact graph entity is present.
4. The incremental indexer avoids repeatedly processing old documents.

## Update-efficiency result

For the current 8-document stream:

| Strategy | Chunks processed | Claims processed |
|---|---:|---:|
| Incremental | 8 | 22 |
| Rebuild after every batch | 36 | 105 |

That is approximately **77.8% fewer chunks** and **79.1% fewer claims** processed by the incremental strategy on this stream.

This directly tests the update-efficiency hypothesis, but it is still a small deterministic workload. Real legal PDF ingestion and LLM extraction costs will dominate later experiments.

## Interpretation

The experiment is now useful enough to validate the architecture, but **not enough to make a research claim**. The next step is to replace the synthetic extractor/corpus with a small, manually verified set of real legal documents and run the same harness unchanged.
