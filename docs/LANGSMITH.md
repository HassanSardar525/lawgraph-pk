# LangSmith Observability

LawGraph-PK uses LangSmith as an inspection/evidence layer for the research implementation. The goal is not to make LangSmith part of the retrieval algorithm; it records what the system did so the comparison is inspectable and reproducible.

## What is traced

When tracing is enabled, the application records:

- **Incremental ingestion** — document metadata, checksum, chunks/claims added, entities touched, and claims superseded.
- **LawGraph query** — question, `as_of` timestamp, retrieval strategy, floors tried, retrieved citations, and final grounded answer.
- **Floor 1** — exact entity/claim retrieval.
- **Floor 2** — one-hop related-entity retrieval.
- **Floor 3** — vector/chunk fallback retrieval.
- **Vector-only baseline** — flat retrieval trace.
- **Static Graph-RAG baseline** — graph retrieval trace.

This gives a trace tree that can be inspected when a result is correct or wrong. In particular, the proposed system exposes whether an answer came from exact graph evidence, graph expansion, or fallback retrieval.

## 1. Create a LangSmith account and API key

Create/log into a LangSmith account and open **Settings → API Keys**. Create a key and copy it immediately; LangSmith only displays the key once.

Do **not** send the API key to the assistant or commit it to Git.

## 2. Configure the local environment

The project keeps LangSmith optional so the deterministic benchmark still works without external services.

Install the observability extra:

```bash
uv sync --extra dev --extra observability
```

For PowerShell:

```powershell
$env:LANGSMITH_TRACING="true"
$env:LANGSMITH_API_KEY="YOUR_KEY_HERE"
$env:LANGSMITH_PROJECT="lawgraph-pk"
$env:LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
```

For bash/zsh:

```bash
export LANGSMITH_TRACING=true
export LANGSMITH_API_KEY="YOUR_KEY_HERE"
export LANGSMITH_PROJECT="lawgraph-pk"
export LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
```

Alternatively, copy `.env.example` to `.env` and load those variables through your normal local environment tooling. `.env` is ignored by Git.

If you have a LangSmith key linked to multiple workspaces, also set `LANGSMITH_WORKSPACE_ID` to the workspace ID.

## 3. Run the comparison

```bash
uv run lawgraph compare
```

The benchmark remains deterministic. LangSmith only observes the run; it does not change retrieval or scoring.

Run the API as usual:

```bash
uv run uvicorn lawgraph_pk.api:app --reload
```

Then query the app. Each query produces a trace in the configured project.

## 4. What to inspect in LangSmith

For a query such as:

> What does Section 10 require?

open the trace and inspect:

```text
LawGraph Query
├── Retrieval Floor 1 - Exact Graph
├── Retrieval Floor 2 - Related Graph       (if needed)
└── Retrieval Floor 3 - Vector Fallback     (if needed)
```

The trace metadata shows the retrieval strategy and the retrieved citation metadata. This is useful evidence for the research report because it lets us inspect **why** the proposed system produced an answer instead of only reporting the final metric.

For an amendment update, inspect:

```text
LawGraph Incremental Ingestion
  ├── chunks_added
  ├── claims_added
  └── claims_superseded
```

This provides an auditable record of incremental update behavior.

## 5. Important research rule

LangSmith traces are **observability evidence**, not ground truth. They do not prove that an answer is legally correct.

Correctness still comes from:

1. real source documents,
2. manually verified evidence/question labels,
3. the common evaluation protocol,
4. comparison against the baselines.

LangSmith helps us inspect and debug the mechanism that produced those results.

## Later phase: LLM extraction and answer generation

When the deterministic extractor is replaced by a real structured LLM extractor, the LLM calls will also be traced. We will record the model/provider, prompt/output structure, extraction result, evidence span, and confidence. This will let us compare extraction failures and update costs without changing the core experiment interface.

## Security

Never commit:

- `LANGSMITH_API_KEY`
- provider API keys
- `.env`
- real private/confidential legal documents

Public legal documents should still retain source URLs, publication dates, and provenance in the dataset.
