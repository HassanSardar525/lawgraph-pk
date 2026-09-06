from __future__ import annotations

from datetime import datetime

from .models import Citation, QueryResult, RetrievalItem
from .observability import finish_trace, trace_run
from .store import SQLiteGraphStore
from .text import cosine, hash_embedding


class VectorOnlyRetriever:
    """Flat chunk-retrieval baseline used by the experiment harness."""

    def __init__(self, store: SQLiteGraphStore) -> None:
        self.store = store

    def query(self, question: str, *, as_of: datetime | None = None, top_k: int = 5) -> QueryResult:
        with trace_run(
            "Vector-only RAG Query",
            run_type="chain",
            inputs={"question": question, "as_of": as_of.isoformat() if as_of else None, "top_k": top_k},
            tags=["lawgraph", "baseline", "vector-only"],
            metadata={"system": "vector_only"},
        ) as run:
            query_vector = hash_embedding(question)
            ranked = sorted(
                ((cosine(query_vector, self.store.decode_embedding(row)), row) for row in self.store.all_chunks()),
                key=lambda pair: pair[0], reverse=True,
            )[:top_k]
            items = [
                RetrievalItem(
                    floor=3,
                    score=round(float(score), 4),
                    text=row["text"],
                    citation=Citation(
                        document_id=int(row["document_id"]), title=row["title"],
                        source_uri=row["source_uri"], chunk_id=int(row["id"]), evidence=row["text"],
                        page_number=row["page_number"],
                    ),
                )
                for score, row in ranked
            ]
            answer = "Retrieved source text: " + " ".join(item.text for item in items) if items else "No evidence found."
            result = QueryResult(question=question, answer=answer, as_of=as_of, items=items, floors_tried=[3])
            finish_trace(run, {"answer": answer, "retrieved_items": len(items), "citations": [item.citation.model_dump() for item in items]})
            return result


class StaticGraphRetriever:
    """Graph-RAG baseline with no temporal interpretation and no vector fallback.

    It is intentionally simple: retrieve current graph claims for exact entities,
    then one-hop neighbors. This is the retrieval component used for both the
    rebuild and incremental graph baselines; the difference between those
    systems is measured during indexing rather than query execution.
    """

    def __init__(self, store: SQLiteGraphStore) -> None:
        self.store = store

    def query(self, question: str, *, as_of: datetime | None = None, top_k: int = 5) -> QueryResult:
        with trace_run(
            "Static Graph-RAG Query",
            run_type="chain",
            inputs={"question": question, "as_of": as_of.isoformat() if as_of else None, "top_k": top_k},
            tags=["lawgraph", "baseline", "static-graph"],
            metadata={"system": "static_graph"},
        ) as run:
            exact = self.store.find_entities_in_question(question)
            exact_ids = [int(row["id"]) for row in exact]
            items = self._claim_items(self.store.claims_for_entities(exact_ids), floor=1, score=1.0)

            if len(items) < top_k and exact_ids:
                neighbor_ids = [value for value in self.store.neighboring_entity_ids(exact_ids) if value not in exact_ids]
                items.extend(self._claim_items(self.store.claims_for_entities(neighbor_ids), floor=2, score=0.7))

            items = self._deduplicate(items)[:top_k]
            answer = self._grounded_answer(items)
            result = QueryResult(question=question, answer=answer, as_of=as_of, items=items, floors_tried=[1, 2] if exact_ids else [1])
            finish_trace(run, {
                "answer": answer,
                "retrieved_items": len(items),
                "floors_tried": result.floors_tried,
                "citations": [item.citation.model_dump() for item in items],
            })
            return result

    @staticmethod
    def _claim_items(rows: list, floor: int, score: float) -> list[RetrievalItem]:
        return [
            RetrievalItem(
                floor=floor,
                score=score,
                text=f"{row['subject_name']} —{row['predicate'].replace('_', ' ')}→ {row['object_name']}",
                claim_id=int(row["id"]),
                citation=Citation(
                    document_id=int(row["document_id"]), title=row["title"],
                    source_uri=row["source_uri"], chunk_id=int(row["chunk_id"]), evidence=row["evidence"],
                    page_number=row["page_number"], evidence_start=row["evidence_start"], evidence_end=row["evidence_end"],
                ),
            )
            for row in rows
        ]

    @staticmethod
    def _deduplicate(items: list[RetrievalItem]) -> list[RetrievalItem]:
        result: list[RetrievalItem] = []
        seen: set[tuple[int, str]] = set()
        for item in items:
            key = (item.citation.chunk_id, item.text)
            if key not in seen:
                seen.add(key)
                result.append(item)
        return result

    @staticmethod
    def _grounded_answer(items: list[RetrievalItem]) -> str:
        if not items:
            return "The graph does not contain enough evidence to answer this question."
        statements = [f"{item.text} [{index}]" for index, item in enumerate(items[:4], start=1)]
        return "Based on the graph evidence: " + "; ".join(statements) + "."
