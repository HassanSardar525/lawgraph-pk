from lawgraph_pk.observability import trace_run, tracing_configured


def test_langsmith_is_optional_by_default(monkeypatch):
    monkeypatch.delenv("LANGSMITH_TRACING", raising=False)
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
    assert tracing_configured() is False


def test_trace_helper_is_safe_without_configuration(monkeypatch):
    monkeypatch.setenv("LANGSMITH_TRACING", "false")
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
    with trace_run("test-run", inputs={"value": 1}) as run:
        run.end(outputs={"ok": True})
