from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone

from .baselines import VectorOnlyRetriever
from .evaluation import EvaluationCase, evaluate
from .experiment import run_comparison
from .service import LawGraphService


INITIAL = """Digital Services Act | contains | Section 10
Section 10 | requires | annual audit
Annual audit | applies_to | registered platforms"""

AMENDMENT = """Amendment 2025 | modifies | Section 10
Section 10 | requires | quarterly audit
Quarterly audit | applies_to | registered platforms"""


def run_demo() -> None:
    service = LawGraphService()
    first = service.indexer.ingest(
        title="Illustrative Act 2024", text=INITIAL, source_uri="demo://act-2024",
        published_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )
    update = service.indexer.ingest(
        title="Illustrative Amendment 2025", text=AMENDMENT, source_uri="demo://amendment-2025",
        published_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
    )
    result = service.retriever.query("What does Section 10 require?")
    print(json.dumps({"initial": first.model_dump(), "update": update.model_dump(), "query": result.model_dump(mode="json")}, indent=2))


def build_demo_service() -> LawGraphService:
    service = LawGraphService()
    service.indexer.ingest(
        title="Illustrative Act 2024", text=INITIAL, source_uri="demo://act-2024",
        published_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )
    service.indexer.ingest(
        title="Illustrative Amendment 2025", text=AMENDMENT, source_uri="demo://amendment-2025",
        published_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
    )
    return service


def run_evaluation() -> None:
    service = build_demo_service()
    cases = [
        EvaluationCase(
            id="current-1", question="What does Section 10 require?",
            expected_terms=("quarterly audit",), forbidden_terms=("annual audit",), category="update",
        ),
        EvaluationCase(
            id="historical-1", question="What did Section 10 require?",
            expected_terms=("annual audit",), category="temporal",
            as_of=datetime(2024, 6, 1, tzinfo=timezone.utc),
        ),
        EvaluationCase(
            id="relation-1", question="Which amendment modifies Section 10?",
            expected_terms=("amendment 2025",), category="relational",
        ),
    ]
    report = {
        "hierarchical": evaluate(service.retriever, cases),
        "vector_only": evaluate(VectorOnlyRetriever(service.store), cases),
    }
    print(json.dumps(report, indent=2))


def run_compare() -> None:
    print(json.dumps(run_comparison(), indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(prog="lawgraph")
    parser.add_argument("command", choices=["demo", "evaluate", "compare"])
    args = parser.parse_args()
    if args.command == "demo":
        run_demo()
    elif args.command == "evaluate":
        run_evaluation()
    elif args.command == "compare":
        run_compare()


if __name__ == "__main__":
    main()
