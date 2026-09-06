# Next Session Checklist

## Start here

Read in this order:

1. `AGENTS.md`
2. `PROJECT_CONTEXT.md`
3. `docs/LLM_HANDOFF.md`
4. `docs/STATUS.md`
5. `docs/DECISIONS.md`
6. `docs/RESEARCH_SPEC.md`
7. `docs/ARCHITECTURE.md`
8. `TODO.md`

## First engineering task

Implement real page-aware PDF ingestion and an LLM-backed structured claim extractor while keeping `DelimitedClaimExtractor` for deterministic tests.

Expected extractor output:

```text
subject
predicate
object
subject_type
object_type
confidence
evidence
source/page metadata when available
```

## Acceptance criteria

- existing unit tests still pass;
- a sample PDF can be parsed into page-aware chunks;
- extracted claims retain evidence spans;
- malformed LLM output is rejected or repaired through schema validation;
- API keys are loaded only from environment variables;
- no secrets enter Git;
- one end-to-end ingestion/query example is documented.

## Second task

Implement B2, the rebuild Graph-RAG baseline, using the same claim representation and evaluation interface. The baseline must intentionally rebuild the graph from all documents after each update batch so update cost can be measured against the incremental system.

## Research task after that

Create a version-controlled evaluation dataset with gold evidence IDs and temporal metadata. Then run:

```text
D0 -> evaluate
D1 -> evaluate
D2 -> evaluate
...
```

for B1, B2, B3 and Ours.

## Do not change the research question casually

If a new idea appears attractive, add it as an ablation or future work unless it directly improves the central comparison. Avoid turning the project into a generic “AI legal assistant.”
