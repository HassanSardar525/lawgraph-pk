from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from statistics import mean
from time import perf_counter
from typing import Protocol

from .models import QueryResult


class Retriever(Protocol):
    def query(self, question: str, *, as_of: datetime | None = None, top_k: int = 5) -> QueryResult: ...


@dataclass(frozen=True)
class EvaluationCase:
    id: str
    question: str
    expected_terms: tuple[str, ...]
    category: str
    as_of: datetime | None = None
    forbidden_terms: tuple[str, ...] = ()


def evaluate(retriever: Retriever, cases: list[EvaluationCase], top_k: int = 5) -> dict:
    rows: list[dict] = []
    for case in cases:
        started = perf_counter()
        result = retriever.query(case.question, as_of=case.as_of, top_k=top_k)
        latency_ms = (perf_counter() - started) * 1000
        evidence = [item.citation.evidence.lower() for item in result.items]
        expected = tuple(term.lower() for term in case.expected_terms)
        forbidden = tuple(term.lower() for term in case.forbidden_terms)
        ranks = [
            index for index, text in enumerate(evidence, start=1)
            if any(term in text for term in expected)
        ]
        hit = bool(ranks)
        stale = any(term in result.answer.lower() for term in forbidden)
        rows.append({
            "id": case.id,
            "category": case.category,
            "hit_at_k": hit,
            "reciprocal_rank": (1.0 / min(ranks)) if ranks else 0.0,
            "citation_present": bool(result.items),
            "stale_answer": stale,
            "latency_ms": round(latency_ms, 3),
            "floors_tried": result.floors_tried,
        })
    return {
        "cases": len(rows),
        "hit_rate_at_k": mean(row["hit_at_k"] for row in rows) if rows else 0.0,
        "mrr": mean(row["reciprocal_rank"] for row in rows) if rows else 0.0,
        "citation_rate": mean(row["citation_present"] for row in rows) if rows else 0.0,
        "stale_answer_rate": mean(row["stale_answer"] for row in rows) if rows else 0.0,
        "mean_latency_ms": mean(row["latency_ms"] for row in rows) if rows else 0.0,
        "rows": rows,
    }
