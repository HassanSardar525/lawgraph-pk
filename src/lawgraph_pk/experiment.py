from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from time import perf_counter

from .baselines import StaticGraphRetriever, VectorOnlyRetriever
from .evaluation import EvaluationCase, evaluate
from .service import LawGraphService


@dataclass(frozen=True)
class BenchmarkDocument:
    title: str
    text: str
    published_at: datetime
    source_uri: str


@dataclass(frozen=True)
class BenchmarkSuite:
    documents: tuple[BenchmarkDocument, ...]
    cases: tuple[EvaluationCase, ...]


def _dt(year: int, month: int = 1, day: int = 1) -> datetime:
    return datetime(year, month, day, tzinfo=timezone.utc)


def build_benchmark_suite() -> BenchmarkSuite:
    """Small deterministic benchmark designed to test the research hypotheses.

    It deliberately includes updates, temporal questions, relational questions,
    and questions that omit exact entity names so hierarchical fallback matters.
    The corpus is synthetic and must not be presented as real law.
    """
    documents = (
        BenchmarkDocument(
            "Data Services Act 2024",
            "Data Services Act | contains | Section 10\n"
            "Section 10 | requires | annual audit\n"
            "Annual audit | applies_to | registered platforms",
            _dt(2024), "demo://data-services-2024",
        ),
        BenchmarkDocument(
            "Consumer Data Act 2024",
            "Consumer Data Act | contains | Section 4\n"
            "Section 4 | requires | annual disclosure\n"
            "Annual disclosure | applies_to | data controllers",
            _dt(2024, 2), "demo://consumer-data-2024",
        ),
        BenchmarkDocument(
            "Digital Safety Act 2024",
            "Digital Safety Act | contains | Section 7\n"
            "Section 7 | requires | incident report\n"
            "Incident report | applies_to | hosting providers",
            _dt(2024, 3), "demo://digital-safety-2024",
        ),
        BenchmarkDocument(
            "Data Services Amendment 2025",
            "Data Services Amendment 2025 | modifies | Section 10\n"
            "Section 10 | requires | quarterly audit\n"
            "Quarterly audit | applies_to | registered platforms",
            _dt(2025), "demo://data-services-2025",
        ),
        BenchmarkDocument(
            "Consumer Data Amendment 2025",
            "Consumer Data Amendment 2025 | modifies | Section 4\n"
            "Section 4 | requires | semiannual disclosure\n"
            "Semiannual disclosure | applies_to | data controllers",
            _dt(2025, 2), "demo://consumer-data-2025",
        ),
        BenchmarkDocument(
            "Digital Safety Amendment 2025",
            "Digital Safety Amendment 2025 | modifies | Section 7\n"
            "Section 7 | requires | 72-hour incident report\n"
            "72-hour incident report | applies_to | hosting providers",
            _dt(2025, 3), "demo://digital-safety-2025",
        ),
        BenchmarkDocument(
            "Platform Guidance 2025",
            "Platform Guidance | covers | registered platforms\n"
            "Platform Guidance | discusses | audit obligations",
            _dt(2025, 4), "demo://platform-guidance-2025",
        ),
        BenchmarkDocument(
            "Compliance Notes 2025",
            "Compliance Notes | covers | data controllers\n"
            "Compliance Notes | discusses | disclosure obligations",
            _dt(2025, 5), "demo://compliance-notes-2025",
        ),
    )

    cases = (
        EvaluationCase(
            "current-section-10",
            "What does Section 10 require?",
            ("quarterly audit",), "temporal_current", forbidden_terms=("annual audit",),
        ),
        EvaluationCase(
            "history-section-10",
            "What did Section 10 require in 2024?",
            ("annual audit",), "temporal_history", as_of=_dt(2024, 6),
        ),
        EvaluationCase(
            "current-section-4",
            "What does Section 4 require?",
            ("semiannual disclosure",), "temporal_current", forbidden_terms=("annual disclosure",),
        ),
        EvaluationCase(
            "history-section-4",
            "What did Section 4 require in 2024?",
            ("annual disclosure",), "temporal_history", as_of=_dt(2024, 6),
        ),
        EvaluationCase(
            "relation-10",
            "Which amendment modifies Section 10?",
            ("Data Services Amendment 2025",), "relational",
        ),
        EvaluationCase(
            "relation-7",
            "Which amendment modifies Section 7?",
            ("Digital Safety Amendment 2025",), "relational",
        ),
        EvaluationCase(
            "fallback-audit",
            "How often must platforms be audited?",
            ("quarterly audit",), "hierarchical_fallback", forbidden_terms=("annual audit",),
        ),
        EvaluationCase(
            "fallback-disclosure",
            "What is the current disclosure frequency for controllers?",
            ("semiannual disclosure",), "hierarchical_fallback", forbidden_terms=("annual disclosure",),
        ),
        EvaluationCase(
            "fallback-incident",
            "How quickly must a hosting provider report an incident?",
            ("72-hour incident report",), "hierarchical_fallback", forbidden_terms=("incident report",),
        ),
    )
    return BenchmarkSuite(documents=documents, cases=cases)


def _ingest(service: LawGraphService, documents: tuple[BenchmarkDocument, ...]) -> dict:
    started = perf_counter()
    chunks = claims = 0
    for document in documents:
        result = service.indexer.ingest(
            title=document.title,
            text=document.text,
            source_uri=document.source_uri,
            published_at=document.published_at,
        )
        chunks += result.chunks_added
        claims += result.claims_added
    return {
        "documents": len(documents),
        "chunks_processed": chunks,
        "claims_processed": claims,
        "wall_time_ms": round((perf_counter() - started) * 1000, 3),
    }


def measure_update_work(documents: tuple[BenchmarkDocument, ...]) -> dict:
    """Compare one-pass incremental updates with full rebuild after every batch."""
    incremental_service = LawGraphService()
    inc_started = perf_counter()
    inc_chunks = inc_claims = 0
    for document in documents:
        result = incremental_service.indexer.ingest(
            title=document.title,
            text=document.text,
            source_uri=document.source_uri,
            published_at=document.published_at,
        )
        inc_chunks += result.chunks_added
        inc_claims += result.claims_added
    incremental_time = (perf_counter() - inc_started) * 1000

    rebuild_started = perf_counter()
    rebuild_chunks = rebuild_claims = 0
    for index in range(1, len(documents) + 1):
        service = LawGraphService()
        work = _ingest(service, documents[:index])
        rebuild_chunks += work["chunks_processed"]
        rebuild_claims += work["claims_processed"]
    rebuild_time = (perf_counter() - rebuild_started) * 1000

    return {
        "incremental": {
            "batches": len(documents),
            "chunks_processed": inc_chunks,
            "claims_processed": inc_claims,
            "wall_time_ms": round(incremental_time, 3),
        },
        "rebuild_after_each_batch": {
            "batches": len(documents),
            "chunks_processed": rebuild_chunks,
            "claims_processed": rebuild_claims,
            "wall_time_ms": round(rebuild_time, 3),
        },
        "work_reduction": {
            "chunk_reduction_pct": round((1 - inc_chunks / rebuild_chunks) * 100, 2) if rebuild_chunks else 0.0,
            "claim_reduction_pct": round((1 - inc_claims / rebuild_claims) * 100, 2) if rebuild_claims else 0.0,
            "wall_time_reduction_pct": round((1 - incremental_time / rebuild_time) * 100, 2) if rebuild_time else 0.0,
        },
    }


def run_comparison() -> dict:
    suite = build_benchmark_suite()
    service = LawGraphService()
    _ingest(service, suite.documents)

    graph_report = evaluate(StaticGraphRetriever(service.store), list(suite.cases))
    reports = {
        "vector_only": evaluate(VectorOnlyRetriever(service.store), list(suite.cases)),
        "rebuild_graph": graph_report,
        "incremental_graph": graph_report,
        "temporal_hierarchical": evaluate(service.retriever, list(suite.cases)),
    }
    return {
        "benchmark": {
            "documents": len(suite.documents),
            "questions": len(suite.cases),
            "note": "Synthetic legal-like data; not legal advice and not real law.",
        },
        "retrieval": reports,
        "update_efficiency": measure_update_work(suite.documents),
    }
