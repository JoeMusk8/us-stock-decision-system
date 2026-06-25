"""Manual paradigm-monitor signal model helpers."""

from __future__ import annotations

from datetime import UTC, datetime


VALID_SOURCE_TYPES = {"政府资金", "巨头科研", "商界领袖", "学术专利", "产业联盟", "投融资", "人工输入"}
VALID_SIGNAL_TYPES = {"新技术词", "资金增加", "重复出现", "关键人物关注", "产业链变化", "其他"}
VALID_SIGNAL_STRENGTHS = {"弱", "中", "强"}
VALID_DATA_STATUSES = {"待人工确认", "数据不足", "已验证"}


def utc_now_iso():
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def normalize_paradigm_signal(signal):
    item = dict(signal)
    item["theme_name"] = str(item.get("theme_name") or "").strip()
    item["source_type"] = item.get("source_type") or "人工输入"
    item["signal_type"] = item.get("signal_type") or "其他"
    item["signal_strength"] = item.get("signal_strength") or "中"
    item["summary"] = str(item.get("summary") or "").strip()
    item["evidence_note"] = str(item.get("evidence_note") or "").strip()
    item["data_status"] = item.get("data_status") or "待人工确认"
    item["updated_at"] = item.get("updated_at") or utc_now_iso()
    return item


def validate_paradigm_signal(signal):
    item = normalize_paradigm_signal(signal)
    errors = []
    if not item["theme_name"]:
        errors.append("theme_name 不能为空")
    if item["source_type"] not in VALID_SOURCE_TYPES:
        errors.append("source_type 不合法")
    if item["signal_type"] not in VALID_SIGNAL_TYPES:
        errors.append("signal_type 不合法")
    if item["signal_strength"] not in VALID_SIGNAL_STRENGTHS:
        errors.append("signal_strength 不合法")
    if item["data_status"] not in VALID_DATA_STATUSES:
        errors.append("data_status 不合法")
    return {"ok": not errors, "errors": errors}


def upsert_paradigm_signal(existing_signals, new_signal):
    signals = [dict(signal) for signal in (existing_signals or [])]
    normalized = normalize_paradigm_signal(new_signal)
    for index, signal in enumerate(signals):
        if str(signal.get("theme_name") or "").strip() == normalized["theme_name"]:
            signals[index] = {**signal, **normalized}
            return signals
    signals.append(normalized)
    return signals


def build_paradigm_summary(signals):
    items = signals or []
    return {
        "总主题数": len(items),
        "强信号数量": sum(1 for item in items if item.get("signal_strength") == "强"),
        "中信号数量": sum(1 for item in items if item.get("signal_strength") == "中"),
        "弱信号数量": sum(1 for item in items if item.get("signal_strength") == "弱"),
        "待人工确认数量": sum(1 for item in items if item.get("data_status") == "待人工确认"),
        "数据不足数量": sum(1 for item in items if item.get("data_status") == "数据不足"),
    }
