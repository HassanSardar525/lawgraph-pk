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
        for raw_line in text.splitlines():
            line = raw_line.strip().lstrip("- ")
            parts = [part.strip() for part in line.split("|")]
            if len(parts) != 3 or not all(parts):
                continue
            subject, predicate, obj = parts
            claims.append(
                ExtractedClaim(
                    subject=subject,
                    predicate=predicate.lower().replace(" ", "_"),
                    object=obj,
                    evidence=line,
                    subject_type=_entity_type(subject),
                    object_type=_entity_type(obj),
                )
            )
        return claims
