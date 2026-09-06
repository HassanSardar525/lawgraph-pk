# Paper Notes

## LightRAG

**Title:** LightRAG: Simple and Fast Retrieval-Augmented Generation

**Publication:** Findings of EMNLP 2025

**Paper:** https://aclanthology.org/2025.findings-emnlp.568/

**Project:** https://lightrag.github.io/

**Code:** https://github.com/HKUDS/LightRAG

## Why it is relevant

LightRAG motivates combining graph structure with vector retrieval and supports incremental insertion/deletion of knowledge. Its retrieval design includes low-level retrieval for specific entities/relations and high-level retrieval for broader concepts/communities.

## What this project borrows conceptually

- graph + vector representations
- entity/relation-oriented retrieval
- broad vs narrow retrieval paths
- incremental knowledge updates

## What this project adds / emphasizes

This implementation is domain-specific and explicitly studies:

- temporal validity of claims
- stale-answer prevention
- conflict/supersession preservation
- hierarchical fallback from exact graph evidence to related graph evidence to chunks
- update-cost measurement

## Reproduction boundary

Do not claim exact reproduction of LightRAG unless the implementation, configuration, datasets and evaluation protocol match the paper. The portfolio project should be described as:

> A small-scale reproduction of key LightRAG ideas with a temporal/conflict-aware legal-domain extension.

## Reading checklist for the next implementation phase

- [ ] map paper architecture to current modules
- [ ] identify which LightRAG components are essential to reproduce
- [ ] record deviations and why they were made
- [ ] reproduce one small paper-style experiment
- [ ] compare against official implementation where practical
