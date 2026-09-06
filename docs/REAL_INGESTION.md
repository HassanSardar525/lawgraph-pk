# Real PDF Ingestion

The first real-data phase now supports page-aware PDF extraction and provenance-preserving ingestion. The LLM extractor is intentionally a separate step so the ingestion pipeline can be tested independently.

## Pipeline

```text
PDF
  -> pypdf page extraction
  -> PageText(page_number, text)
  -> page-aware chunking
  -> ClaimExtractor
  -> evidence-span validation
  -> incremental graph update
  -> page-aware citations
```

## Install

```bash
uv sync --extra dev --extra pdf --extra observability
```

## API upload

Start the API:

```bash
uv run uvicorn lawgraph_pk.api:app --reload
```

Upload a PDF as multipart form data to:

```text
POST /documents/pdf
```

Required field:

- `file`
- `title`

Optional fields:

- `source_uri`
- `published_at`

The ingestion result reports document/chunk/entity/claim counts. Query results now include `page_number` in citations when the source was ingested page-aware.

## Python usage

```python
from lawgraph_pk.pdf_ingestion import extract_pdf_pages

pages = extract_pdf_pages("data/source.pdf")
result = service.indexer.ingest_pages(
    title="Source Act",
    pages=pages,
    source_uri="https://official-source.example/document.pdf",
    published_at=published_at,
)
```

## Evidence spans

`ExtractedClaim` supports optional `evidence_start` and `evidence_end` character offsets relative to the exact chunk supplied to the extractor.

If both offsets are present, ingestion verifies that:

1. the span is inside the chunk,
2. the start/end values are ordered, and
3. the extracted span matches the claim's evidence text.

This is important for later LLM extraction: a model will not be allowed to invent an evidence quote that cannot be located in the source chunk.

## Current limitation

`pypdf` extracts text from text-based PDFs. Scanned/image-only PDFs will need OCR in a later step. Do not silently treat OCR output as authoritative; retain page provenance and mark OCR-derived text in the dataset metadata.

## Initial source strategy

The first real corpus should use a small number of public Pakistani legal documents from official sources, rather than attempting to ingest hundreds of laws immediately.

Good starting sources:

- **Pakistan Code**, the Ministry of Law & Justice's federal-law portal. It provides federal legislation and points users toward Gazette notifications for original sources.
- **National Assembly of Pakistan — Acts of Parliament**, which provides an official chronological list of enacted Acts.
- **Punjab Laws Online**, for Punjab provincial legislation when we expand beyond federal material.

For each document record:

- title
- issuing body
- publication/promulgation date
- source URL
- document checksum
- whether it is an original Act, amendment, ordinance, rule, or consolidated text
- local file name
- license/access note

The Pakistan Code itself warns that its content is for information purposes and that the relevant Gazette notification should be consulted where there is doubt. Therefore the research dataset should preserve the original source/Gazette reference whenever possible.

## Research corpus goal

Start with approximately 10–20 documents containing at least a few amendment/update relationships. Then expand to the 150+ question evaluation set. The objective is to test the architecture, not to build a comprehensive Pakistani legal database.
