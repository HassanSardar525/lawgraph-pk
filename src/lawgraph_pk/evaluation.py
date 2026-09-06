from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import log2
import re
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


def _contains_term(text: str, term: str) -> bool:
    pattern = r"(?<!\w)" + re.escape(term.lower()) + r"(?!\w)"
    return re.search(pattern, text.lower()) is not None


def _ranked_relevant(evidence: list[str], expected: tuple[str, ...]) -> list[int]:
    return [
        index
        for index, text in enumerate(evidence, start=1)
        if any(_contains_term(text, term) for term in expected)
    ]


def _ndcg(rank: int | None, k: int) -> float:
    if rank is None or rank > k:
        return 0.0
    return 1.0 / log2(rank + 1)


def _summarize(rows: list[dict]) -> dict:
    if not rows:
        return {
            "cases": 0,
            "hit_rate_at_k": 0.0,
            "mrr": 0.0,
            "ndcg_at_k": 0.0,
            "citation_rate": 0.0,
            "answer_accuracy": 0.0,
            "stale_answer_rate": 0.0,
            "mean_latency_ms": 0.0,
        }
    return {
        "cases": len(rows),
        "hit_rate_at_k": mean(row["hit_at_k"] for row in rows),
        "mrr": mean(row["reciprocal_rank"] for row in rows),
        "ndcg_at_k": mean(row["ndcg_at_k"] for row in rows),
        "citation_rate": mean(row["citation_present"] for row in rows),
        "answer_accuracy": mean(row["answer_correct"] for row in rows),
        "stale_answer_rate": mean(row["stale_answer"] for row in rows),
        "mean_latency_ms": mean(row["latency_ms"] for row in rows),
    }


def evaluate(retriever: Retriever, cases: list[EvaluationCase], top_k: int = 5) -> dict:
    rows: list[dict] = []
    for case in cases:
        started = perf_counter()
        result = retriever.query(case.question, as_of=case.as_of, top_k=top_k)
        latency_ms = (perf_counter() - started) * 1000
        evidence = [item.citation.evidence.lower() for item in result.items]
        expected = tuple(term.lower() for term in case.expected_terms)
        forbidden = tuple(term.lower() for term in case.forbidden_terms)
        ranks = _ranked_relevant(evidence, expected)
        first_rank = min(ranks) if ranks else None
        answer_lower = result.answer.lower()
        stale = any(_contains_term(answer_lower, term) for term in forbidden)
        answer_hit = any(_contains_term(answer_lower, term) for term in expected)
        answer_correct = answer_hit and not stale
        rows.append({
            "id": case.id,
            "category": case.category,
            "hit_at_k": bool(ranks),
            "reciprocal_rank": (1.0 / first_rank) if first_rank else 0.0,
            "ndcg_at_k": _ndcg(first_rank, top_k),
            "citation_present": bool(result.items),
            "answer_hit": answer_hit,
            "answer_correct": answer_correct,
            "stale_answer": stale,
            "latency_ms": round(latency_ms, 3),
            "floors_tried": result.floors_tried,
        })

    by_category: dict[str, dict] = {}
    for category in sorted({row["category"] for row in rows}):
        by_category[category] = _summarize([row for row in rows if row["category"] == category])

    return {
        **_summarize(rows),
        "by_category": by_category,
        "rows": rows,
    }
