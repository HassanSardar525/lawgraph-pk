from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ExtractedClaim(BaseModel):
    subject: str
    predicate: str
    object: str
    evidence: str
    subject_type: str = "entity"
    object_type: str = "entity"
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class IngestResult(BaseModel):
    document_id: int
    status: Literal["inserted", "duplicate"]
    chunks_added: int = 0
    entities_touched: int = 0
    claims_added: int = 0
    claims_superseded: int = 0


class Citation(BaseModel):
    document_id: int
    title: str
    source_uri: str | None = None
    chunk_id: int
    evidence: str


class RetrievalItem(BaseModel):
    floor: Literal[1, 2, 3]
    score: float
    text: str
    citation: Citation
    claim_id: int | None = None


class QueryResult(BaseModel):
    question: str
    answer: str
    as_of: datetime | None = None
    items: list[RetrievalItem]
    floors_tried: list[int]
