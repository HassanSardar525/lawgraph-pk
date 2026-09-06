from __future__ import annotations

from typing import Any, Protocol

from pydantic import BaseModel, Field

from .models import ExtractedClaim


class ClaimBatch(BaseModel):
    schema_version: str = "lawgraph-claim-v1"
    claims: list[ExtractedClaim] = Field(default_factory=list)


class StructuredModel(Protocol):
    def with_structured_output(self, schema: type[BaseModel]) -> Any: ...


EXTRACTION_PROMPT = """You extract factual legal relationships from a source chunk.

Return only relationships that are explicitly supported by the source text.
For every claim:
- subject: canonical legal entity name
- predicate: short snake_case relation such as requires, defines, modifies, applies_to
- object: canonical legal entity/value name
- subject_type and object_type when obvious
- confidence from 0 to 1
- evidence: an exact contiguous quote from the source chunk
- evidence_start/evidence_end: character offsets of that exact quote in the source chunk

Do not invent facts. If the chunk does not contain a clear relationship, return no claim.

SOURCE CHUNK:
{chunk}
"""


class StructuredLLMClaimExtractor:
    """Use any LangChain-compatible chat model with structured output.

    The concrete provider is deliberately injected so the project can use
    OpenAI, Anthropic, Gemini, Bedrock, or another supported model without
    changing the indexing interface.
    """

    def __init__(self, model: StructuredModel) -> None:
        self.model = model.with_structured_output(ClaimBatch)

    def extract(self, text: str) -> list[ExtractedClaim]:
        result = self.model.invoke(EXTRACTION_PROMPT.format(chunk=text))
        if isinstance(result, ClaimBatch):
            return result.claims
        if isinstance(result, dict):
            return ClaimBatch.model_validate(result).claims
        return ClaimBatch.model_validate(result).claims
