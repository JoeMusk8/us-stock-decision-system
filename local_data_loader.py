"""Local JSON data loader for low-risk test data.

This module only reads local files. It does not call external networks, connect
APIs, generate real data, or make investment/trading decisions.
"""

import json
from pathlib import Path

from core.evidence_utils import can_enter_fact_zone, validate_evidence_record


def load_json_file(file_path):
    """Read a local JSON file and return a structured result."""
    path = Path(file_path)
    if not path.exists():
        return {"ok": False, "data": {}, "error": f"文件不存在：{file_path}"}

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as exc:
        return {"ok": False, "data": {}, "error": f"JSON 格式错误：{exc}"}
    except OSError as exc:
        return {"ok": False, "data": {}, "error": f"读取文件失败：{exc}"}

    if not isinstance(data, dict):
        return {"ok": False, "data": {}, "error": "JSON 顶层结构必须是 dict"}

    return {"ok": True, "data": data, "error": ""}


def load_evidence_items(file_path="data/evidence_items.example.json"):
    """Load local evidence_items example records."""
    result = load_json_file(file_path)
    if not result["ok"]:
        return {"ok": False, "records": [], "error": result["error"]}

    records = result["data"].get("records", [])
    if not isinstance(records, list):
        return {"ok": False, "records": [], "error": "records 必须是 list"}

    return {"ok": True, "records": records, "error": ""}


def validate_loaded_evidence(records):
    """Validate loaded evidence records with evidence_utils rules."""
    items = []
    for record in records:
        result = validate_evidence_record(record)
        evidence_id = record.get("evidence_id", "") if isinstance(record, dict) else ""
        items.append(
            {
                "evidence_id": evidence_id,
                "is_valid": result["is_valid"],
                "errors": result["errors"],
            }
        )

    valid_count = sum(1 for item in items if item["is_valid"])
    total = len(items)
    return {
        "total": total,
        "valid_count": valid_count,
        "invalid_count": total - valid_count,
        "items": items,
    }


def get_fact_allowed_records(records):
    """Return records that are allowed to enter the fact zone."""
    return [record for record in records if can_enter_fact_zone(record)]
