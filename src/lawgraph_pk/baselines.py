from __future__ import annotations

from datetime import datetime

from .models import Citation, QueryResult, RetrievalItem
from .store import SQLiteGraphStore
from .text import cosine, hash_embedding


class VectorOnlyRetriever:
    """Flat chunk-retrieval baseline used by the experiment harness."""

    def __init__(self, store: SQLiteGraphStore) -> None:
        self.store = store

    def query(self, question: str, *, as_of: datetime | None = None, top_k: int = 5) -> QueryResult:
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
                ),
            )
            for score, row in ranked
        ]
        answer = "Retrieved source text: " + " ".join(item.text for item in items) if items else "No evidence found."
        return QueryResult(question=question, answer=answer, as_of=as_of, items=items, floors_tried=[3])
