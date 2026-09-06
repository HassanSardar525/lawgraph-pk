from __future__ import annotations

from typing import Protocol

from .models import ExtractedClaim


class ClaimExtractor(Protocol):
    def extract(self, text: str) -> list[ExtractedClaim]: ...


def _entity_type(name: str) -> str:
    lowered = name.lower()
    for marker, label in (
        ("section", "section"),
        ("article", "article"),
        ("act", "law"),
        ("amendment", "amendment"),
        ("court", "court"),
    ):
        if marker in lowered:
            return label
    return "entity"


class DelimitedClaimExtractor:
    """Deterministic extractor for fixtures: subject | predicate | object."""

    def extract(self, text: str) -> list[ExtractedClaim]:
        claims: list[ExtractedClaim] = []
        offset = 0
        for raw_line in text.splitlines(keepends=True):
            line = raw_line.strip().lstrip("- ")
            parts = [part.strip() for part in line.split("|")]
            if len(parts) != 3 or not all(parts):
                offset += len(raw_line)
                continue
            subject, predicate, obj = parts
            start = text.find(line, offset)
            end = start + len(line)
            claims.append(
                ExtractedClaim(
                    subject=subject,
                    predicate=predicate.lower().replace(" ", "_"),
                    object=obj,
                    evidence=line,
                    subject_type=_entity_type(subject),
                    object_type=_entity_type(obj),
                    evidence_start=start,
                    evidence_end=end,
                )
            )
            offset += len(raw_line)
        return claims
