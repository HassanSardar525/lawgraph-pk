from __future__ import annotations

import hashlib
import math
import re
from collections import Counter


TOKEN_RE = re.compile(r"[a-z0-9]+")


def canonicalize(value: str) -> str:
    return " ".join(TOKEN_RE.findall(value.lower()))


def tokens(value: str) -> list[str]:
    return TOKEN_RE.findall(value.lower())


def hash_embedding(value: str, dimensions: int = 128) -> list[float]:
    vector = [0.0] * dimensions
    counts = Counter(tokens(value))
    for token, count in counts.items():
        digest = hashlib.blake2b(token.encode(), digest_size=8).digest()
        raw = int.from_bytes(digest, "big")
        index = raw % dimensions
        sign = 1.0 if raw & 1 else -1.0
        vector[index] += sign * count
    norm = math.sqrt(sum(x * x for x in vector)) or 1.0
    return [x / norm for x in vector]


def cosine(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right, strict=True))


def split_text(text: str, max_chars: int = 900) -> list[str]:
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        if current and len(current) + len(paragraph) + 2 > max_chars:
            chunks.append(current)
            current = paragraph
        else:
            current = f"{current}\n\n{paragraph}".strip()
    if current:
        chunks.append(current)
    return chunks or ([text.strip()] if text.strip() else [])
