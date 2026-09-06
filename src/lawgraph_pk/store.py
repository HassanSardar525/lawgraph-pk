from __future__ import annotations

import json
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from .text import canonicalize


SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS documents (
  id INTEGER PRIMARY KEY,
  title TEXT NOT NULL,
  source_uri TEXT,
  published_at TEXT NOT NULL,
  checksum TEXT NOT NULL UNIQUE,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS chunks (
  id INTEGER PRIMARY KEY,
  document_id INTEGER NOT NULL REFERENCES documents(id),
  position INTEGER NOT NULL,
  text TEXT NOT NULL,
  embedding TEXT NOT NULL,
  page_number INTEGER,
  UNIQUE(document_id, position)
);
CREATE TABLE IF NOT EXISTS entities (
  id INTEGER PRIMARY KEY,
  canonical_name TEXT NOT NULL UNIQUE,
  display_name TEXT NOT NULL,
  entity_type TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS claims (
  id INTEGER PRIMARY KEY,
  subject_entity_id INTEGER NOT NULL REFERENCES entities(id),
  predicate TEXT NOT NULL,
  object_entity_id INTEGER NOT NULL REFERENCES entities(id),
  evidence TEXT NOT NULL,
  document_id INTEGER NOT NULL REFERENCES documents(id),
  chunk_id INTEGER NOT NULL REFERENCES chunks(id),
  confidence REAL NOT NULL,
  evidence_start INTEGER,
  evidence_end INTEGER,
  valid_from TEXT NOT NULL,
  valid_to TEXT,
  is_current INTEGER NOT NULL DEFAULT 1,
  supersedes_claim_id INTEGER REFERENCES claims(id),
  created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_claim_subject ON claims(subject_entity_id, predicate);
CREATE INDEX IF NOT EXISTS idx_claim_object ON claims(object_entity_id);
"""


class SQLiteGraphStore:
    def __init__(self, path: str | Path = ":memory:") -> None:
        self.path = str(path)
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.lock = threading.RLock()
        with self.lock:
            self.connection.executescript(SCHEMA)
            self._ensure_legacy_columns()

    def _ensure_legacy_columns(self) -> None:
        """Apply tiny additive migrations for databases created by earlier milestones."""
        for table, column, definition in (
            ("chunks", "page_number", "INTEGER"),
            ("claims", "evidence_start", "INTEGER"),
            ("claims", "evidence_end", "INTEGER"),
        ):
            columns = {row["name"] for row in self.connection.execute(f"PRAGMA table_info({table})")}
            if column not in columns:
                self.connection.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
        self.connection.commit()

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        with self.lock:
            try:
                yield self.connection
                self.connection.commit()
            except Exception:
                self.connection.rollback()
                raise

    def get_document_by_checksum(self, checksum: str) -> sqlite3.Row | None:
        return self.connection.execute(
            "SELECT * FROM documents WHERE checksum = ?", (checksum,)
        ).fetchone()

    def upsert_entity(self, conn: sqlite3.Connection, name: str, entity_type: str) -> int:
        canonical = canonicalize(name)
        now = datetime.now(timezone.utc).isoformat()
        conn.execute(
            """INSERT INTO entities(canonical_name, display_name, entity_type, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(canonical_name) DO UPDATE SET
                 updated_at=excluded.updated_at,
                 entity_type=CASE WHEN entities.entity_type='entity' THEN excluded.entity_type ELSE entities.entity_type END""",
            (canonical, name.strip(), entity_type, now, now),
        )
        row = conn.execute(
            "SELECT id FROM entities WHERE canonical_name = ?", (canonical,)
        ).fetchone()
        assert row is not None
        return int(row["id"])

    def graph_stats(self) -> dict[str, int]:
        with self.lock:
            return {
                table: int(self.connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
                for table in ("documents", "chunks", "entities", "claims")
            }

    def find_entities_in_question(self, question: str) -> list[sqlite3.Row]:
        normalized = canonicalize(question)
        rows = self.connection.execute("SELECT * FROM entities ORDER BY length(canonical_name) DESC").fetchall()
        return [row for row in rows if row["canonical_name"] and row["canonical_name"] in normalized]

    def claims_for_entities(self, entity_ids: list[int], as_of: str | None = None) -> list[sqlite3.Row]:
        if not entity_ids:
            return []
        marks = ",".join("?" for _ in entity_ids)
        params: list[object] = [*entity_ids, *entity_ids]
        time_clause = " AND c.is_current = 1"
        if as_of:
            time_clause = " AND c.valid_from <= ? AND (c.valid_to IS NULL OR c.valid_to > ?)"
            params.extend([as_of, as_of])
        sql = f"""
          SELECT c.*, se.display_name subject_name, oe.display_name object_name,
                 d.title, d.source_uri, ch.page_number
          FROM claims c
          JOIN entities se ON se.id=c.subject_entity_id
          JOIN entities oe ON oe.id=c.object_entity_id
          JOIN documents d ON d.id=c.document_id
          JOIN chunks ch ON ch.id=c.chunk_id
          WHERE (c.subject_entity_id IN ({marks}) OR c.object_entity_id IN ({marks})) {time_clause}
          ORDER BY c.valid_from DESC, c.id DESC
        """
        return self.connection.execute(sql, params).fetchall()

    def all_chunks(self, as_of: str | None = None) -> list[sqlite3.Row]:
        if as_of:
            return self.connection.execute(
                """SELECT ch.*, d.title, d.source_uri, d.published_at FROM chunks ch
                   JOIN documents d ON d.id=ch.document_id
                   WHERE d.published_at <= ?
                   ORDER BY d.published_at DESC, ch.position""",
                (as_of,),
            ).fetchall()
        return self.connection.execute(
            """SELECT ch.*, d.title, d.source_uri, d.published_at FROM chunks ch
               JOIN documents d ON d.id=ch.document_id"""
        ).fetchall()

    def active_chunk_ids(self, as_of: str | None = None) -> set[int]:
        if as_of:
            rows = self.connection.execute(
                """SELECT DISTINCT chunk_id FROM claims
                   WHERE valid_from <= ? AND (valid_to IS NULL OR valid_to > ?)""",
                (as_of, as_of),
            ).fetchall()
        else:
            rows = self.connection.execute(
                "SELECT DISTINCT chunk_id FROM claims WHERE is_current=1"
            ).fetchall()
        return {int(row["chunk_id"]) for row in rows}

    def neighboring_entity_ids(self, entity_ids: list[int]) -> list[int]:
        if not entity_ids:
            return []
        marks = ",".join("?" for _ in entity_ids)
        rows = self.connection.execute(
            f"""SELECT subject_entity_id, object_entity_id FROM claims
                WHERE subject_entity_id IN ({marks}) OR object_entity_id IN ({marks})""",
            [*entity_ids, *entity_ids],
        ).fetchall()
        found = set(entity_ids)
        for row in rows:
            found.add(int(row["subject_entity_id"]))
            found.add(int(row["object_entity_id"]))
        return sorted(found)

    @staticmethod
    def decode_embedding(row: sqlite3.Row) -> list[float]:
        return list(json.loads(row["embedding"]))
