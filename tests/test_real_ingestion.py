from datetime import datetime, timezone

import pytest

from lawgraph_pk.models import ExtractedClaim, PageText
from lawgraph_pk.service import LawGraphService


def dt(year: int) -> datetime:
    return datetime(year, 1, 1, tzinfo=timezone.utc)


def test_page_aware_ingestion_preserves_page_citation():
    service = LawGraphService()
    result = service.indexer.ingest_pages(
        title="Paged Act",
        pages=[
            PageText(page_number=2, text="Section 7 | requires | public notice"),
            PageText(page_number=5, text="Public notice | applies_to | regulated entities"),
        ],
        source_uri="official://paged-act",
        published_at=dt(2024),
    )
    assert result.chunks_added == 2

    query = service.retriever.query("What does Section 7 require?")
    assert query.items
    assert query.items[0].citation.page_number == 2
    assert query.items[0].citation.source_uri == "official://paged-act"


def test_evidence_span_is_validated():
    service = LawGraphService()
    claim = ExtractedClaim(
        subject="Section 7",
        predicate="requires",
        object="public notice",
        evidence="Section 7 | requires | public notice",
        evidence_start=0,
        evidence_end=len("Section 7 | requires | public notice"),
    )

    class OneClaimExtractor:
        def extract(self, text: str):
            return [claim]

    service.indexer.extractor = OneClaimExtractor()
    result = service.indexer.ingest(
        title="Evidence Act",
        text=claim.evidence,
        published_at=dt(2024),
    )
    assert result.claims_added == 1


def test_invalid_evidence_span_rejects_ingestion():
    service = LawGraphService()
    claim = ExtractedClaim(
        subject="Section 7",
        predicate="requires",
        object="public notice",
        evidence="wrong evidence",
        evidence_start=0,
        evidence_end=5,
    )

    class OneClaimExtractor:
        def extract(self, text: str):
            return [claim]

    service.indexer.extractor = OneClaimExtractor()
    with pytest.raises(ValueError, match="Evidence span"):
        service.indexer.ingest(title="Bad Evidence", text="Section 7 | requires | public notice", published_at=dt(2024))
