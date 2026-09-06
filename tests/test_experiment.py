from lawgraph_pk.baselines import StaticGraphRetriever
from lawgraph_pk.evaluation import evaluate
from lawgraph_pk.experiment import build_benchmark_suite, measure_update_work, run_comparison
from lawgraph_pk.service import LawGraphService


def build_service():
    suite = build_benchmark_suite()
    service = LawGraphService()
    for document in suite.documents:
        service.indexer.ingest(
            title=document.title,
            text=document.text,
            source_uri=document.source_uri,
            published_at=document.published_at,
        )
    return service, suite


def test_static_graph_baseline_is_available():
    service, suite = build_service()
    report = evaluate(StaticGraphRetriever(service.store), list(suite.cases))
    assert report["cases"] == len(suite.cases)


def test_temporal_hierarchical_beats_static_on_temporal_and_fallback_cases():
    service, suite = build_service()
    proposed = evaluate(service.retriever, list(suite.cases))
    static = evaluate(StaticGraphRetriever(service.store), list(suite.cases))
    assert proposed["by_category"]["temporal_history"]["answer_accuracy"] > static["by_category"]["temporal_history"]["answer_accuracy"]
    assert proposed["by_category"]["hierarchical_fallback"]["answer_accuracy"] > static["by_category"]["hierarchical_fallback"]["answer_accuracy"]


def test_update_work_is_lower_for_incremental_indexing():
    suite = build_benchmark_suite()
    report = measure_update_work(suite.documents)
    assert report["incremental"]["chunks_processed"] < report["rebuild_after_each_batch"]["chunks_processed"]
    assert report["incremental"]["claims_processed"] < report["rebuild_after_each_batch"]["claims_processed"]
    assert report["work_reduction"]["claim_reduction_pct"] > 0


def test_full_comparison_contains_all_required_systems():
    report = run_comparison()
    assert set(report["retrieval"]) == {"vector_only", "rebuild_graph", "incremental_graph", "temporal_hierarchical"}
    assert report["benchmark"]["questions"] >= 9
    assert "update_efficiency" in report
