from __future__ import annotations

from datetime import datetime

from .models import Citation, QueryResult, RetrievalItem
from .observability import finish_trace, trace_run
from .store import SQLiteGraphStore
from .text import canonicalize, cosine, hash_embedding, tokens


class HierarchicalRetriever:
    def __init__(self, store: SQLiteGraphStore) -> None:
        self.store = store

    def query(self, question: str, *, as_of: datetime | None = None, top_k: int = 5) -> QueryResult:
        as_of_value = as_of.isoformat() if as_of else None
        with trace_run(
            "LawGraph Query",
            run_type="chain",
            inputs={"question": question, "as_of": as_of_value, "top_k": top_k},
            tags=["lawgraph", "retrieval", "temporal-hierarchical"],
            metadata={"retrieval_strategy": "temporal_hierarchical", "top_k": top_k},
        ) as root_run:
            items: list[RetrievalItem] = []
            floors: list[int] = []
            exact = self.store.find_entities_in_question(question)

            floors.append(1)
            exact_ids = [int(row["id"]) for row in exact]
            with trace_run(
                "Retrieval Floor 1 - Exact Graph",
                run_type="retriever",
                inputs={"question": question, "as_of": as_of_value, "entity_matches": [row["display_name"] for row in exact]},
                tags=["lawgraph", "floor-1", "graph"],
                metadata={"floor": 1, "retrieval_mode": "exact_entity"},
            ) as floor_run:
                floor_items = self._claim_items(self.store.claims_for_entities(exact_ids, as_of_value), 1, 1.0)
                items.extend(floor_items)
                finish_trace(floor_run, self._trace_documents(floor_items))

            if len(items) < top_k and exact_ids:
                floors.append(2)
                neighbor_ids = [value for value in self.store.neighboring_entity_ids(exact_ids) if value not in exact_ids]
                with trace_run(
                    "Retrieval Floor 2 - Related Graph",
                    run_type="retriever",
                    inputs={"question": question, "as_of": as_of_value, "neighbor_count": len(neighbor_ids)},
                    tags=["lawgraph", "floor-2", "graph"],
                    metadata={"floor": 2, "retrieval_mode": "one_hop_neighbors"},
                ) as floor_run:
                    floor_items = self._claim_items(self.store.claims_for_entities(neighbor_ids, as_of_value), 2, 0.72)
                    items.extend(floor_items)
                    finish_trace(floor_run, self._trace_documents(floor_items))

            if len(items) < top_k:
                floors.append(3)
                with trace_run(
                    "Retrieval Floor 3 - Vector Fallback",
                    run_type="retriever",
                    inputs={"question": question, "as_of": as_of_value, "remaining_slots": top_k - len(items)},
                    tags=["lawgraph", "floor-3", "vector-fallback"],
                    metadata={"floor": 3, "retrieval_mode": "vector_fallback"},
                ) as floor_run:
                    query_vector = hash_embedding(question)
                    active_chunks = self.store.active_chunk_ids(as_of_value)
                    candidate_rows = self.store.all_chunks(as_of_value)
                    query_tokens = set(tokens(question))
                    relevant_rows = [
                        row for row in candidate_rows
                        if " requires " in f" {row['text'].lower()} "
                        and query_tokens & set(tokens(row["text"]))
                    ]
                    max_relevant_published = max((row["published_at"] for row in relevant_rows), default="")
                    ranked: list[tuple[float, object]] = []
                    for row in candidate_rows:
                        similarity = cosine(query_vector, self.store.decode_embedding(row))
                        row_tokens = set(tokens(row["text"]))
                        lexical_overlap = len(query_tokens & row_tokens)
                        is_structural = " requires " in f" {row['text'].lower()} "
                        freshness_bonus = 0.25 if is_structural and row["published_at"] == max_relevant_published else 0.0
                        structural_bonus = 0.12 if is_structural else 0.0
                        active_bonus = 0.04 if int(row["id"]) in active_chunks else 0.0
                        score = similarity + freshness_bonus + structural_bonus + active_bonus + min(lexical_overlap, 4) * 0.03
                        ranked.append((score, row))
                    ranked.sort(key=lambda pair: pair[0], reverse=True)
                    seen_chunks = {item.citation.chunk_id for item in items}
                    floor_items: list[RetrievalItem] = []
                    for score, row in ranked:
                        if int(row["id"]) in seen_chunks:
                            continue
                        item = RetrievalItem(
                            floor=3,
                            score=round(float(score), 4),
                            text=row["text"],
                            citation=Citation(
                                document_id=int(row["document_id"]), title=row["title"],
                                source_uri=row["source_uri"], chunk_id=int(row["id"]), evidence=row["text"],
                                page_number=row["page_number"],
                            ),
                        )
                        items.append(item)
                        floor_items.append(item)
                        if len(items) >= top_k:
                            break
                    finish_trace(floor_run, self._trace_documents(floor_items))

            items = self._deduplicate(items)[:top_k]
            answer = self._grounded_answer(question, items)
            result = QueryResult(question=question, answer=answer, as_of=as_of, items=items, floors_tried=floors)
            finish_trace(
                root_run,
                {
                    "answer": answer,
                    "retrieved_items": len(items),
                    "floors_tried": floors,
                    "citations": [item.citation.model_dump() for item in items],
                },
            )
            return result

    @staticmethod
    def _trace_documents(items: list[RetrievalItem]) -> list[dict]:
        return [
            {
                "page_content": item.citation.evidence,
                "type": "Document",
                "metadata": {
                    "floor": item.floor,
                    "score": item.score,
                    "document_id": item.citation.document_id,
                    "chunk_id": item.citation.chunk_id,
                    "claim_id": item.claim_id,
                    "page_number": item.citation.page_number,
                    "source_uri": item.citation.source_uri,
                    "title": item.citation.title,
                },
            }
            for item in items
        ]

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
    def _grounded_answer(question: str, items: list[RetrievalItem]) -> str:
        if not items:
            return "The indexed sources do not contain enough evidence to answer this question."

        question_text = canonicalize(question)
        query_terms = set(question_text.split())

        def relevance(item: RetrievalItem) -> tuple[float, float, float]:
            text_terms = set(canonicalize(item.text).split())
            overlap = len(query_terms & text_terms)
            predicate_bonus = 0.0
            if "require" in question_text and "requires" in item.text.lower():
                predicate_bonus = 1.0
            elif "modif" in question_text and "modifies" in item.text.lower():
                predicate_bonus = 1.0
            elif "apply" in question_text and "applies to" in item.text.lower():
                predicate_bonus = 1.0
            return (predicate_bonus, overlap, item.score)

        claim_items = [item for item in items if item.claim_id is not None]
        selected = sorted(claim_items or items, key=relevance, reverse=True)[:2 if claim_items else 1]
        statements = [f"{item.text} [{index}]" for index, item in enumerate(selected, start=1)]
        return "Based on the indexed evidence: " + "; ".join(statements) + "."
