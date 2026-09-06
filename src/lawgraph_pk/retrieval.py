from __future__ import annotations

from datetime import datetime

from .models import Citation, QueryResult, RetrievalItem
from .store import SQLiteGraphStore
from .text import cosine, hash_embedding


class HierarchicalRetriever:
    def __init__(self, store: SQLiteGraphStore) -> None:
        self.store = store

    def query(self, question: str, *, as_of: datetime | None = None, top_k: int = 5) -> QueryResult:
        as_of_value = as_of.isoformat() if as_of else None
        items: list[RetrievalItem] = []
        floors: list[int] = []
        exact = self.store.find_entities_in_question(question)

        floors.append(1)
        exact_ids = [int(row["id"]) for row in exact]
        items.extend(self._claim_items(self.store.claims_for_entities(exact_ids, as_of_value), 1, 1.0))

        if len(items) < top_k and exact_ids:
            floors.append(2)
            neighbor_ids = [value for value in self.store.neighboring_entity_ids(exact_ids) if value not in exact_ids]
            items.extend(self._claim_items(self.store.claims_for_entities(neighbor_ids, as_of_value), 2, 0.72))

        if len(items) < top_k:
            floors.append(3)
            query_vector = hash_embedding(question)
            ranked = sorted(
                (
                    (cosine(query_vector, self.store.decode_embedding(row)), row)
                    for row in self.store.all_chunks()
                ),
                key=lambda pair: pair[0], reverse=True,
            )
            seen_chunks = {item.citation.chunk_id for item in items}
            for score, row in ranked:
                if int(row["id"]) in seen_chunks:
                    continue
                items.append(
                    RetrievalItem(
                        floor=3,
                        score=round(float(score), 4),
                        text=row["text"],
                        citation=Citation(
                            document_id=int(row["document_id"]), title=row["title"],
                            source_uri=row["source_uri"], chunk_id=int(row["id"]), evidence=row["text"],
                        ),
                    )
                )
                if len(items) >= top_k:
                    break

        items = self._deduplicate(items)[:top_k]
        answer = self._grounded_answer(question, items)
        return QueryResult(question=question, answer=answer, as_of=as_of, items=items, floors_tried=floors)

    @staticmethod
    def _claim_items(rows: list, floor: int, base_score: float) -> list[RetrievalItem]:
        return [
            RetrievalItem(
                floor=floor,
                score=base_score,
                text=f"{row['subject_name']} —{row['predicate'].replace('_', ' ')}→ {row['object_name']}",
                claim_id=int(row["id"]),
                citation=Citation(
                    document_id=int(row["document_id"]), title=row["title"],
                    source_uri=row["source_uri"], chunk_id=int(row["chunk_id"]), evidence=row["evidence"],
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
    def _grounded_answer(question: str, items: list[RetrievalItem]) -> str:
        if not items:
            return "The indexed sources do not contain enough evidence to answer this question."
        claim_items = [item for item in items if item.claim_id is not None]
        selected = claim_items or items
        statements = [f"{item.text} [{index}]" for index, item in enumerate(selected[:4], start=1)]
        return "Based on the indexed evidence: " + "; ".join(statements) + "."
