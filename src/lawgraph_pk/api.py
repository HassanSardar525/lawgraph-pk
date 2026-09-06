from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from .models import IngestResult, QueryResult
from .pdf_ingestion import extract_pdf_pages
from .service import LawGraphService


class DocumentRequest(BaseModel):
    title: str
    text: str
    source_uri: str | None = None
    published_at: datetime | None = None


class QueryRequest(BaseModel):
    question: str
    as_of: datetime | None = None
    top_k: int = Field(default=5, ge=1, le=20)


app = FastAPI(title="LawGraph-PK", version="0.1.0")
service = LawGraphService(os.getenv("LAWGRAPH_DB_PATH", "data/lawgraph.db"))
WEB_INDEX = Path(__file__).resolve().parents[2] / "web" / "index.html"


@app.get("/")
def root():
    return FileResponse(WEB_INDEX)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "stats": service.store.graph_stats()}


@app.post("/documents", response_model=IngestResult)
def add_document(request: DocumentRequest) -> IngestResult:
    return service.indexer.ingest(**request.model_dump())


@app.post("/documents/pdf", response_model=IngestResult)
def add_pdf_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    source_uri: str | None = Form(None),
    published_at: datetime | None = Form(None),
) -> IngestResult:
    pages = extract_pdf_pages(file.file)
    return service.indexer.ingest_pages(
        title=title,
        pages=pages,
        source_uri=source_uri or f"uploaded://{file.filename or 'document.pdf'}",
        published_at=published_at,
    )


@app.post("/query", response_model=QueryResult)
def query(request: QueryRequest) -> QueryResult:
    return service.retriever.query(**request.model_dump())


@app.get("/graph")
def graph() -> dict:
    conn = service.store.connection
    entities = [dict(row) for row in conn.execute("SELECT id, display_name, entity_type FROM entities")]
    claims = [dict(row) for row in conn.execute(
        "SELECT id, subject_entity_id source, object_entity_id target, predicate, is_current, valid_from, valid_to FROM claims"
    )]
    return {"entities": entities, "claims": claims}
