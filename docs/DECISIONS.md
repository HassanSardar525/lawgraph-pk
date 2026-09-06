# Architecture and Research Decisions

## Decision 1 — Combine incremental indexing with hierarchical retrieval

These are complementary rather than competing ideas.

- Incremental indexing controls **how the knowledge base changes**.
- Hierarchical retrieval controls **how the system searches**.

They must also be ablated independently in experiments.

## Decision 2 — Keep a deterministic local implementation

SQLite, hash embeddings and pipe-delimited extraction are intentional for the first milestone. They allow tests and demos to run without API keys, network access or expensive hardware.

Real models/stores should be adapters rather than replacements for the core interfaces.

## Decision 3 — Temporal history must be preserved

A legal amendment should not delete the old claim. Claims should carry validity intervals and/or explicit supersession relationships.

Historical queries use an `as_of` timestamp.

## Decision 4 — Provenance is first-class

Claims point to source documents and evidence spans. Future PDF ingestion must retain page-level provenance.

## Decision 5 — Research claims must be measurable

Do not say the proposed method is “better” without a baseline, dataset, metric and experiment. Negative results should be reported.

## Decision 6 — LightRAG is the paper anchor, not a branding claim

The project uses key LightRAG ideas as a starting point but should be described as a small-scale reproduction plus legal-domain extension unless the paper's complete protocol is reproduced.

## Decision 7 — Avoid unnecessary complexity

No large-model training or multi-agent architecture is required for the research question. Compute should be spent on controlled evaluation, not model size.
