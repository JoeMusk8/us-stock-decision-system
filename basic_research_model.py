"""Manual basic research candidate-stock model helpers."""

from __future__ import annotations

from datetime import UTC, datetime


VALID_CHAIN_LAYERS = {
    "上游资源 / 原材料",
    "核心零部件",
    "关键设备",
    "系统集成",
    "基础设施建设",
    "下游应用 / 客户",
}
VALID_HEAT_STATUSES = {"低热度", "升温中", "高热度", "过热"}
VALID_CAPITAL_FLOW_STATUSES = {"未知", "流入", "中性", "流出"}
VALID_DATA_STATUSES = {"待人工确认", "数据不足", "已验证"}


def utc_now_iso():
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def normalize_ticker(ticker):
    return str(ticker or "").strip().upper()


def normalize_candidate(candidate):
    item = dict(candidate)
    item["ticker"] = normalize_ticker(item.get("ticker"))
    item["company_name"] = str(item.get("company_name") or "").strip()
    item["industry"] = str(item.get("industry") or "").strip()
    item["theme"] = str(item.get("theme") or "").strip()
    item["chain_layer"] = item.get("chain_layer") or "核心零部件"
    item["heat_status"] = item.get("heat_status") or "未知"
    item["capital_flow_status"] = item.get("capital_flow_status") or "未知"
    item["candidate_reason"] = str(item.get("candidate_reason") or "").strip()
    item["evidence_note"] = str(item.get("evidence_note") or "").strip()
    item["data_status"] = item.get("data_status") or "待人工确认"
    item["updated_at"] = item.get("updated_at") or utc_now_iso()
    return item


def _to_score(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def validate_candidate(candidate):
    item = normalize_candidate(candidate)
    errors = []
    if not item["ticker"]:
        errors.append("ticker 不能为空")
    if not item["industry"]:
        errors.append("industry 不能为空")
    if not item["theme"]:
        errors.append("theme 不能为空")
    if item["chain_layer"] not in VALID_CHAIN_LAYERS:
        errors.append("chain_layer 不合法")
    if item["heat_status"] not in VALID_HEAT_STATUSES:
        errors.append("heat_status 不合法")
    if item["capital_flow_status"] not in VALID_CAPITAL_FLOW_STATUSES:
        errors.append("capital_flow_status 不合法")
    if item["data_status"] not in VALID_DATA_STATUSES:
        errors.append("data_status 不合法")
    score = _to_score(item.get("bottleneck_score"))
    if score is None or score < 0 or score > 5:
        errors.append("bottleneck_score 必须是 0-5 之间的数字")
    return {"ok": not errors, "errors": errors}


def upsert_candidate(existing_items, new_item):
    items = [dict(item) for item in (existing_items or [])]
    normalized = normalize_candidate(new_item)
    for index, item in enumerate(items):
        if normalize_ticker(item.get("ticker")) == normalized["ticker"] and str(item.get("theme") or "").strip() == normalized["theme"]:
            items[index] = {**item, **normalized}
            return items
    items.append(normalized)
    return items


def build_candidate_summary(items):
    candidates = items or []
    return {
        "总候选数": len(candidates),
        "高热度数量": sum(1 for item in candidates if item.get("heat_status") == "高热度"),
        "过热数量": sum(1 for item in candidates if item.get("heat_status") == "过热"),
        "资金流入数量": sum(1 for item in candidates if item.get("capital_flow_status") == "流入"),
        "待人工确认数量": sum(1 for item in candidates if item.get("data_status") == "待人工确认"),
        "数据不足数量": sum(1 for item in candidates if item.get("data_status") == "数据不足"),
    }
