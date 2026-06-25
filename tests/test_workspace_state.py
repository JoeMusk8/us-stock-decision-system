from core.workspace_state import (
    WORKSPACE_KEYS,
    build_workspace_snapshot,
    from_json_text,
    restore_workspace_snapshot,
    to_json_bytes,
    validate_workspace_snapshot,
)


def sample_session():
    return {
        "paradigm_signals": [{"theme_name": "EXAMPLE_THEME"}],
        "basic_research_industries": ["AI 光互连"],
        "candidate_stocks": [{"ticker": "EXAMPLE1"}],
        "deep_research_tasks": [{"ticker": "EXAMPLE1", "theme": "AI 光互连"}],
        "tracking_pool": [{"ticker": "EXAMPLE1", "theme": "AI 光互连"}],
    }


def test_build_workspace_snapshot_keeps_workspace_keys():
    snapshot = build_workspace_snapshot(sample_session())
    assert snapshot["schema_version"]
    assert snapshot["exported_at"]
    for key in WORKSPACE_KEYS:
        assert key in snapshot
        assert snapshot[key] == sample_session()[key]


def test_to_json_bytes_and_from_json_text_roundtrip():
    snapshot = build_workspace_snapshot(sample_session())
    data = to_json_bytes(snapshot)
    assert isinstance(data, bytes)
    parsed = from_json_text(data.decode("utf-8"))
    assert parsed["ok"] is True
    assert parsed["snapshot"]["candidate_stocks"] == snapshot["candidate_stocks"]


def test_invalid_json_returns_error():
    parsed = from_json_text("{not-json")
    assert parsed["ok"] is False
    assert parsed["errors"]


def test_missing_schema_version_fails_validation():
    snapshot = build_workspace_snapshot(sample_session())
    snapshot.pop("schema_version")
    result = validate_workspace_snapshot(snapshot)
    assert result["ok"] is False


def test_restore_only_known_workspace_keys():
    snapshot = build_workspace_snapshot(sample_session())
    snapshot["unknown_key"] = ["ignored"]
    restored = restore_workspace_snapshot(snapshot)
    assert set(restored) == set(WORKSPACE_KEYS)
    assert "unknown_key" not in restored


def test_outputs_do_not_contain_blocked_terms():
    snapshot = build_workspace_snapshot(sample_session())
    text = to_json_bytes(snapshot).decode("utf-8")
    blocked_terms = ["建议" + "买入", "建议" + "卖出", "目标" + "价", "自动" + "交易", "自动" + "下单"]
    for term in blocked_terms:
        assert term not in text
