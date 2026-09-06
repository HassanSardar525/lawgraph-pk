from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import BinaryIO

from .models import PageText


def extract_pdf_pages(source: str | Path | bytes | BinaryIO) -> list[PageText]:
    """Extract text page-by-page while preserving the PDF page number.

    `pypdf` is optional. Install the project's `pdf` extra before using this
    function: `uv sync --extra pdf`.
    """
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover - depends on optional extra
        raise RuntimeError("PDF ingestion requires the `pdf` extra: uv sync --extra pdf") from exc

    if isinstance(source, (str, Path)):
        pdf_path = Path(source)
        if not pdf_path.exists():
            raise FileNotFoundError(pdf_path)
        reader = PdfReader(str(pdf_path))
    elif isinstance(source, bytes):
        reader = PdfReader(BytesIO(source))
    else:
        reader = PdfReader(source)

    pages: list[PageText] = []
    for number, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            pages.append(PageText(page_number=number, text=text))
    return pages
