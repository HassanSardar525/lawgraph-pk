# Project Context

## Project

**LawGraph-PK** — Temporal and Conflict-Aware Incremental Graph-RAG for Evolving Legislation.

## Why this project exists

The goal is to produce a portfolio-quality implementation of recent AI research. It should demonstrate that the author can:

- read and translate a research paper into an implementation;
- design baselines and controlled experiments;
- build RAG and knowledge-graph infrastructure;
- handle changing knowledge instead of only static documents;
- measure quality, freshness, cost and latency;
- explain engineering trade-offs.

The project should look like a research implementation with an application, not an application with a research paragraph attached to it.

## Core research idea

Combine two concepts:

### 1. Incremental knowledge-graph RAG

When a new legal document or amendment arrives, extract only the new evidence and merge affected entities/relations into the existing graph. Historical claims remain available.

### 2. Hierarchical retrieval

Search progressively broader evidence levels:

- Floor 1 — exact entity/claim evidence
- Floor 2 — neighboring entities and relations
- Floor 3 — vector/document chunks

If a query cannot be answered at a narrow level, the system falls back rather than simply failing.

## Proposed research extension

Add **temporal and conflict-aware claim management**:

- valid-from / valid-to intervals
- supersedes relationships
- explicit contradiction handling
- source and evidence provenance
- current vs historical views

The key research question is whether this combination improves freshness and robustness while reducing update cost.

## Domain

Pakistani legislation is the intended domain because legal documents naturally contain amendments, revisions, cross-references and time-sensitive provisions. The prototype currently uses fictional fixtures. Real legal documents must be sourced from official or otherwise clearly licensed sources and manually verified for the evaluation set.

## Paper anchor

Primary paper:

**LightRAG: Simple and Fast Retrieval-Augmented Generation**

Project page: https://lightrag.github.io/

Paper: https://aclanthology.org/2025.findings-emnlp.568/

Reference implementation: https://github.com/HKUDS/LightRAG

The project is a **small-scale reproduction and domain extension**, not a claim that the entire LightRAG system has been independently reproduced.

## Current implementation

The current prototype is intentionally dependency-light:

- Python 3.11+
- FastAPI
- Pydantic
- SQLite
- deterministic hash embeddings
- deterministic pipe-delimited extraction
- pytest
- uv

Production dependencies are intentionally deferred until interfaces and experiments are stable.
