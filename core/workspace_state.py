"""Workspace snapshot helpers for Streamlit session-state backup."""

from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
import json
from typing import Any, Mapping

SCHEMA_VERSION = "workspace.v1"
WORKSPACE_KEYS = (
    "paradigm_signals",
    "basic_research_industries",
    "candidate_stocks",
    "deep_research_tasks",
    "tracking_pool",
)


def _session_get(session_data: Mapping[str, Any] | Any, key: str, default: Any):
    if hasattr(session_data, "get"):
        return session_data.get(key, default)
    return default


def _list_or_empty(value: Any) -> list:
    if isinstance(value, list):
        return deepcopy(value)
    return []


def build_workspace_snapshot(session_data: Mapping[str, Any] | Any) -> dict:
    snapshot = {
        "schema_version": SCHEMA_VERSION,
        "exported_at": datetime.now(UTC).isoformat(),
    }
    for key in WORKSPACE_KEYS:
        snapshot[key] = _list_or_empty(_session_get(session_data, key, []))
    return snapshot


def validate_workspace_snapshot(snapshot: Any) -> dict:
    errors: list[str] = []
    if not isinstance(snapshot, dict):
        return {"ok": False, "errors": ["workspace must be a JSON object"]}
    if not snapshot.get("schema_version"):
        errors.append("missing schema_version")
    for key in WORKSPACE_KEYS:
        if key not in snapshot:
            errors.append(f"missing field: {key}")
        elif not isinstance(snapshot.get(key), list):
            errors.append(f"invalid field type: {key}")
    return {"ok": not errors, "errors": errors}


def restore_workspace_snapshot(snapshot: dict) -> dict:
    validation = validate_workspace_snapshot(snapshot)
    if not validation["ok"]:
        return {}
    return {key: _list_or_empty(snapshot.get(key, [])) for key in WORKSPACE_KEYS}


def to_json_bytes(snapshot: dict) -> bytes:
    text = json.dumps(snapshot, ensure_ascii=False, indent=2, sort_keys=True)
    return text.encode("utf-8")


def from_json_text(text: str) -> dict:
    try:
        snapshot = json.loads(text)
    except json.JSONDecodeError as exc:
        return {"ok": False, "snapshot": {}, "errors": [f"JSON parse failed: {exc.msg}"]}
    validation = validate_workspace_snapshot(snapshot)
    if not validation["ok"]:
        return {"ok": False, "snapshot": {}, "errors": validation["errors"]}
    return {"ok": True, "snapshot": snapshot, "errors": []}
