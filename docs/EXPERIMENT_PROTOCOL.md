# Experiment Protocol

## Goal

Make every research result reproducible and comparable.

## Dataset construction

Use a chronological document stream:

```text
D0 -> initial legislation
D1 -> amendment / update
D2 -> additional amendment
D3 -> related court interpretation
...
```

Each document record should contain:

- stable document ID
- title
- source URI
- publication/effective date when available
- checksum
- page number(s)
- text/evidence spans
- document version or amendment relationship when available

Do not put confidential or unlicensed documents into the public repository.

## Question set

Target at least 150 manually reviewed questions:

- 40 direct factual questions
- 40 relational/multi-hop questions
- 40 temporal/update-sensitive questions
- 30 stale/contradiction questions

Store questions in version-controlled JSONL/CSV with expected evidence IDs, not only expected answer strings.

## Batch experiment

For each system:

1. Start from the same empty database.
2. Insert D0.
3. Evaluate.
4. Insert D1.
5. Evaluate again.
6. Continue through the document stream.
7. Record update time and affected objects.

For rebuild baseline B2, reconstruct the complete graph after each batch.

For incremental systems, only process the newly added batch.

## Retrieval experiment

For every question record:

- system ID
- query
- timestamp/as-of value
- retrieved claim/chunk IDs
- retrieval floors used
- scores
- answer
- citations
- latency
- token/cost metadata

## Metrics

### Retrieval

Recall@5:

```text
# questions where at least one gold evidence item is in top 5
---------------------------------------------------------------
                       # questions
```

MRR:

```text
mean(1 / rank_of_first_gold_evidence)
```

### Freshness

Stale-answer rate:

```text
questions answered using evidence that was no longer valid
----------------------------------------------------------------
                       update-sensitive questions
```

### Update efficiency

Report both absolute time and normalized work:

- seconds/update
- documents processed/update
- chunks processed/update
- claims inserted/update
- estimated LLM tokens/update

## Human evaluation

Automatic LLM judging can be used as a supplementary metric, not the only source of truth. Human review should verify a stratified subset, especially legal correctness and citation support.

## Statistical reporting

When sample size permits:

- report mean and median latency
- report bootstrap confidence intervals for key quality metrics
- compare paired questions across systems
- include effect size where appropriate

Avoid presenting tiny synthetic-demo improvements as statistically meaningful research findings.
