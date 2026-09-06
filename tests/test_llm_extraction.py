from lawgraph_pk.llm_extraction import ClaimBatch, StructuredLLMClaimExtractor


class FakeStructuredModel:
    def with_structured_output(self, schema):
        assert schema is ClaimBatch
        return self

    def invoke(self, prompt: str):
        evidence = "Section 7 requires public notice."
        start = prompt.index(evidence)
        return {
            "schema_version": "lawgraph-claim-v1",
            "claims": [
                {
                    "subject": "Section 7",
                    "predicate": "requires",
                    "object": "public notice",
                    "evidence": evidence,
                    "subject_type": "section",
                    "object_type": "requirement",
                    "confidence": 0.97,
                    "evidence_start": start,
                    "evidence_end": start + len(evidence),
                }
            ],
        }


def test_structured_extractor_maps_model_output():
    extractor = StructuredLLMClaimExtractor(FakeStructuredModel())
    claims = extractor.extract("Preamble\nSection 7 requires public notice.")
    assert len(claims) == 1
    assert claims[0].predicate == "requires"
    assert claims[0].confidence == 0.97
