from datetime import datetime, timezone

from lawgraph_pk.service import LawGraphService
from lawgraph_pk.evaluation import EvaluationCase, evaluate


def dt(year: int) -> datetime:
    return datetime(year, 1, 1, tzinfo=timezone.utc)


def test_incremental_update_supersedes_current_claim():
    service = LawGraphService()
    first = service.indexer.ingest(
        title="Act", text="Section 10 | requires | annual audit", published_at=dt(2024)
    )
    update = service.indexer.ingest(
        title="Amendment", text="Section 10 | requires | quarterly audit", published_at=dt(2025)
    )
    assert first.claims_added == 1
    assert update.claims_superseded == 1

    current = service.retriever.query("What does Section 10 require?")
    assert "quarterly audit" in current.answer.lower()
    assert "annual audit" not in current.answer.lower()

    historical = service.retriever.query("What did Section 10 require?", as_of=dt(2024))
    assert "annual audit" in historical.answer.lower()


def test_duplicate_document_is_idempotent():
    service = LawGraphService()
    first = service.indexer.ingest(title="Act", text="Act | contains | Section 1", published_at=dt(2024))
    duplicate = service.indexer.ingest(title="Copy", text="Act | contains | Section 1", published_at=dt(2024))
    assert first.status == "inserted"
    assert duplicate.status == "duplicate"
    assert service.store.graph_stats()["documents"] == 1


def test_retrieval_falls_back_to_chunks_for_unknown_entity():
    service = LawGraphService()
    service.indexer.ingest(
        title="Act", text="Section 10 | requires | annual audit", published_at=dt(2024)
    )
    result = service.retriever.query("Tell me about audit obligations")
    assert result.floors_tried == [1, 3]
    assert result.items
    assert result.items[0].floor == 3


def test_api_vertical_slice(tmp_path, monkeypatch):
    monkeypatch.setenv("LAWGRAPH_DB_PATH", str(tmp_path / "api.db"))
    from importlib import reload
    from fastapi.testclient import TestClient
    import lawgraph_pk.api as api_module

    api_module = reload(api_module)
    client = TestClient(api_module.app)
    inserted = client.post(
        "/documents",
        json={
            "title": "Test Act",
            "text": "Section 7 | requires | public notice",
            "published_at": "2024-01-01T00:00:00Z",
        },
    )
    assert inserted.status_code == 200
    result = client.post("/query", json={"question": "What does Section 7 require?"})
    assert result.status_code == 200
    assert "public notice" in result.json()["answer"].lower()


def test_evaluation_reports_retrieval_metrics():
    service = LawGraphService()
    service.indexer.ingest(title="Act", text="Section 3 | requires | registration", published_at=dt(2024))
    report = evaluate(service.retriever, [
        EvaluationCase("q1", "What does Section 3 require?", ("registration",), "factual")
    ])
    assert report["hit_rate_at_k"] == 1.0
    assert report["mrr"] == 1.0
    assert report["citation_rate"] == 1.0
    assert report["answer_accuracy"] == 1.0
