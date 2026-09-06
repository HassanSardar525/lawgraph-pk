from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Any, Iterator

try:
    from langsmith import Client, trace
except ImportError:  # pragma: no cover - exercised when observability extra is not installed
    Client = None  # type: ignore[assignment]
    trace = None  # type: ignore[assignment]


class _NoOpRun:
    id = None

    def end(self, **_: Any) -> None:
        return None


def tracing_configured() -> bool:
    """Return True when LangSmith tracing is explicitly enabled and configured."""
    return (
        os.getenv("LANGSMITH_TRACING", "false").lower() in {"1", "true", "yes", "on"}
        and bool(os.getenv("LANGSMITH_API_KEY"))
        and trace is not None
    )


@contextmanager
def trace_run(
    name: str,
    *,
    run_type: str = "chain",
    inputs: dict[str, Any] | None = None,
    tags: list[str] | None = None,
    metadata: dict[str, Any] | None = None,
) -> Iterator[Any]:
    """Create a LangSmith span when enabled, otherwise behave as a no-op.

    The rest of the application therefore remains runnable without an API key.
    """
    if trace is None:
        yield _NoOpRun()
        return

    with trace(
        name,
        run_type=run_type,
        inputs=inputs or {},
        tags=tags or [],
        metadata=metadata or {},
    ) as run:
        yield run


def finish_trace(run: Any, outputs: Any) -> None:
    """Attach outputs to a trace without making tracing a runtime dependency."""
    if hasattr(run, "end"):
        run.end(outputs=outputs)


def flush_traces() -> None:
    """Best-effort flush for short-lived CLI processes."""
    if not tracing_configured() or Client is None:
        return
    try:
        Client().flush()
    except Exception:
        # Observability must never make the research application fail.
        return
