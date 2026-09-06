from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

from .extraction import ClaimExtractor
from .models import IngestResult
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
        published_at = published_at or datetime.now(timezone.utc)
        if published_at.tzinfo is None:
            published_at = published_at.replace(tzinfo=timezone.utc)
        published = published_at.isoformat()
        checksum = hashlib.sha256(text.encode()).hexdigest()
        existing = self.store.get_document_by_checksum(checksum)
        if existing:
            return IngestResult(document_id=int(existing["id"]), status="duplicate")

        chunks = split_text(text)
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
            for position, chunk in enumerate(chunks):
                cursor = conn.execute(
                    "INSERT INTO chunks(document_id, position, text, embedding) VALUES (?, ?, ?, ?)",
                    (document_id, position, chunk, json.dumps(hash_embedding(chunk))),
                )
                chunk_ids.append(int(cursor.lastrowid))

            for position, chunk in enumerate(chunks):
                for claim in self.extractor.extract(chunk):
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
                             document_id, chunk_id, confidence, valid_from,
                             is_current, supersedes_claim_id, created_at
                           ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)""",
                        (
                            subject_id, claim.predicate, object_id, claim.evidence,
                            document_id, chunk_ids[position], claim.confidence,
                            published, supersedes, now,
                        ),
                    )
                    claims_added += 1

        return IngestResult(
            document_id=document_id,
            status="inserted",
            chunks_added=len(chunks),
            entities_touched=len(touched),
            claims_added=claims_added,
            claims_superseded=claims_superseded,
        )
