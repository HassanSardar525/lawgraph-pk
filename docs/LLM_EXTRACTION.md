# Structured LLM Extraction

LawGraph-PK now has a provider-agnostic `StructuredLLMClaimExtractor`. It accepts a LangChain-compatible chat model and calls `with_structured_output(ClaimBatch)`.

This keeps the research pipeline independent of a specific provider:

```text
PDF -> pages -> chunks -> StructuredLLMClaimExtractor -> validated claims -> graph
```

## Contract

The model must return:

- `schema_version`: currently `lawgraph-claim-v1`
- `claims`: a list of claims
- each claim contains subject, predicate, object, types, confidence, exact evidence text, and evidence offsets

The ingestion layer then validates the evidence offsets against the actual chunk. If the model invents an evidence span, ingestion rejects the claim rather than silently storing it.

## Provider setup

The repository intentionally does not hard-code a provider yet. The next live step needs one provider/model selected by the project owner.

Examples of LangChain-compatible model integrations include OpenAI, Anthropic, Google Gemini and AWS Bedrock. The provider package and API credentials should be installed/configured locally; secrets must never be committed.

Example shape once a provider is selected:

```python
from lawgraph_pk.llm_extraction import StructuredLLMClaimExtractor

model = ...  # provider-specific LangChain chat model
extractor = StructuredLLMClaimExtractor(model)
service.indexer.extractor = extractor
```

## Why the provider is intentionally injected

The experiment is comparing retrieval/indexing strategies, not model providers. Changing the model should not change the retrieval interface or evaluation protocol. The same extractor contract can therefore be used with different providers while keeping the rest of the experiment fixed.

## LangSmith

When the selected provider uses a LangChain integration and `LANGSMITH_TRACING=true`, the model calls can be inspected in LangSmith as part of the surrounding ingestion/query trace. This gives us visibility into:

- model used,
- extraction input chunk,
- structured extraction output,
- confidence,
- evidence span,
- extraction failures.

## Required live setup before real extraction

Only one project-specific decision is currently blocking the live LLM extraction step:

**Which provider/model should we use?**

Once selected, provide the provider name/model choice. Do **not** paste an API key into chat. Configure the key locally using the provider's environment variable or secret manager, and I will wire the provider adapter and test the real extraction path.
