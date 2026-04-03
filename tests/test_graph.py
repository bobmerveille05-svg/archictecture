import importlib
from pathlib import Path

import pytest


def test_network_commands_blocked_when_allow_network_false(monkeypatch):
    monkeypatch.setenv("ALLOW_NETWORK", "false")
    from sandbox.permissions import check_permission

    assert check_permission("execute", "curl https://example.com") is False
    assert check_permission("execute", "wget https://example.com") is False
    assert check_permission("execute", "echo hello") is True


def test_network_commands_allowed_when_allow_network_true(monkeypatch):
    monkeypatch.setenv("ALLOW_NETWORK", "true")
    from sandbox.permissions import check_permission

    assert check_permission("execute", "curl https://example.com") is True
    assert check_permission("execute", "wget https://example.com") is True


def test_memory_db_path_is_resolved_at_runtime(monkeypatch):
    temp_dir = Path(".tmp-tests")
    temp_dir.mkdir(exist_ok=True)
    db_file = temp_dir / "runtime.db"
    monkeypatch.setenv("MEMORY_DB_PATH", str(db_file))

    import memory.db as db

    importlib.reload(db)
    db.init_db()

    assert db_file.exists()
    db_file.unlink(missing_ok=True)


def test_record_result_node_returns_only_delta():
    pytest.importorskip("langchain_openai")
    pytest.importorskip("langgraph")

    from core.nodes import record_result_node

    state = {
        "tool_results": [{"tool_name": "old", "success": True, "output": "old"}],
        "last_result": {
            "tool_name": "new",
            "success": True,
            "input": {},
            "output": "ok",
            "error": None,
            "metadata": {},
            "recoverable": False,
        },
    }
    result = record_result_node(state)

    assert result["tool_results"] == [state["last_result"]]


def test_cli_uses_current_runtime_node_names():
    cli_path = Path("channels/cli.py")
    content = cli_path.read_text(encoding="utf-8")
    assert "record_result" in content
    assert "if node_name == \"observe\"" not in content
