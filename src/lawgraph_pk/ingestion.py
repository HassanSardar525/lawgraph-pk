from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Sequence

from .extraction import ClaimExtractor
from .models import ExtractedClaim, IngestResult, PageText
from .observability import finish_trace, trace_run
from .store import SQLiteGraphStore
from .text import hash_embedding, split_text


class IncrementalIndexer:
    def __init__(
        self,
        store: SQLiteGraphStore,
        extractor: ClaimExtractor,
        replaceable_predicates: set[str] | None = None,
    ) -> None:
        self.store = store
        self.extractor = extractor
        self.replaceable_predicates = replaceable_predicates or {
            "requires", "defines", "sets", "has_status", "applies_to"
        }

    def ingest(
        self,
        *,
        title: str,
        text: str,
        source_uri: str | None = None,
        published_at: datetime | None = None,
    ) -> IngestResult:
        return self.ingest_pages(
            title=title,
            pages=[PageText(page_number=1, text=text)],
            source_uri=source_uri,
            published_at=published_at,
        )

    def ingest_pages(
        self,
        *,
        title: str,
        pages: Sequence[PageText],
        source_uri: str | None = None,
        published_at: datetime | None = None,
    ) -> IngestResult:
        if not pages:
            raise ValueError("At least one page is required")

        published_at = published_at or datetime.now(timezone.utc)
        if published_at.tzinfo is None:
            published_at = published_at.replace(tzinfo=timezone.utc)
        published = published_at.isoformat()
        full_text = "\n\n".join(page.text for page in pages)
        checksum = hashlib.sha256(full_text.encode()).hexdigest()

        with trace_run(
            "LawGraph Incremental Ingestion",
            run_type="chain",
            inputs={
                "title": title,
                "source_uri": source_uri,
                "published_at": published,
                "pages": len(pages),
                "text_length": len(full_text),
                "checksum": checksum,
            },
            tags=["lawgraph", "ingestion", "incremental"],
            metadata={"indexing_strategy": "incremental", "page_aware": True},
        ) as run:
            existing = self.store.get_document_by_checksum(checksum)
            if existing:
                result = IngestResult(document_id=int(existing["id"]), status="duplicate")
                finish_trace(run, result.model_dump())
                return result

            page_chunks: list[tuple[int, str]] = []
            for page in pages:
                for chunk in split_text(page.text):
                    if chunk.strip():
                        page_chunks.append((page.page_number, chunk))
            if not page_chunks:
                raise ValueError("The supplied pages contain no extractable text")

            claims_added = claims_superseded = 0
            touched: set[int] = set()
            now = datetime.now(timezone.utc).isoformat()

            with self.store.transaction() as conn:
                cursor = conn.execute(
                    "INSERT INTO documents(title, source_uri, published_at, checksum, created_at) VALUES (?, ?, ?, ?, ?)",
                    (title, source_uri, published, checksum, now),
                )
                document_id = int(cursor.lastrowid)
                chunk_ids: list[int] = []
                for position, (page_number, chunk) in enumerate(page_chunks):
                    cursor = conn.execute(
                        "INSERT INTO chunks(document_id, position, text, embedding, page_number) VALUES (?, ?, ?, ?, ?)",
                        (document_id, position, chunk, json.dumps(hash_embedding(chunk)), page_number),
                    )
                    chunk_ids.append(int(cursor.lastrowid))

                for position, (_, chunk) in enumerate(page_chunks):
                    for claim in self.extractor.extract(chunk):
                        self._validate_claim_evidence(claim, chunk)
                        subject_id = self.store.upsert_entity(conn, claim.subject, claim.subject_type)
                        object_id = self.store.upsert_entity(conn, claim.object, claim.object_type)
                        touched.update((subject_id, object_id))
                        supersedes: int | None = None
                        if claim.predicate in self.replaceable_predicates:
                            previous = conn.execute(
                                """SELECT id, object_entity_id, valid_from FROM claims
                                   WHERE subject_entity_id=? AND predicate=? AND is_current=1
                                   ORDER BY valid_from DESC LIMIT 1""",
                                (subject_id, claim.predicate),
                            ).fetchone()
                            if previous and int(previous["object_entity_id"]) != object_id and published >= previous["valid_from"]:
                                supersedes = int(previous["id"])
                                conn.execute(
                                    "UPDATE claims SET is_current=0, valid_to=? WHERE id=?",
                                    (published, supersedes),
                                )
                                claims_superseded += 1
                        conn.execute(
                            """INSERT INTO claims(
                                 subject_entity_id, predicate, object_entity_id, evidence,
                                 document_id, chunk_id, confidence, evidence_start, evidence_end,
                                 valid_from, is_current, supersedes_claim_id, created_at
                               ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)""",
                            (
                                subject_id, claim.predicate, object_id, claim.evidence,
                                document_id, chunk_ids[position], claim.confidence,
                                claim.evidence_start, claim.evidence_end,
                                published, supersedes, now,
                            ),
                        )
                        claims_added += 1

            result = IngestResult(
                document_id=document_id,
                status="inserted",
                chunks_added=len(page_chunks),
                entities_touched=len(touched),
                claims_added=claims_added,
                claims_superseded=claims_superseded,
            )
            finish_trace(run, {
                **result.model_dump(),
                "update_effect": "superseded_existing_claims" if claims_superseded else "added_new_claims",
                "pages_indexed": len(pages),
            })
            return result

    @staticmethod
    def _validate_claim_evidence(claim: ExtractedClaim, chunk: str) -> None:
        """Validate optional character offsets against the exact source chunk."""
        if claim.evidence_start is None and claim.evidence_end is None:
            return
        if claim.evidence_start is None or claim.evidence_end is None:
            raise ValueError("evidence_start and evidence_end must be supplied together")
        if claim.evidence_start > claim.evidence_end or claim.evidence_end > len(chunk):
            raise ValueError("Evidence span is outside the source chunk")
        source_span = chunk[claim.evidence_start:claim.evidence_end]
        if source_span.strip() != claim.evidence.strip():
            raise ValueError("Evidence span does not match the supplied evidence text")
