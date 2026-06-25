"""Bridge deep research tasks into the manual tracking pool.

This is research workflow transfer only. It does not generate strategy prices,
trading instructions, or investment advice.
"""

from __future__ import annotations

from datetime import UTC, datetime


def _utc_now_iso():
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def _clean(value):
    return str(value or "").strip()


def map_research_decision_to_tracking_status(decision):
    mapping = {
        "进入核心跟踪池": "核心跟踪",
        "进入重点跟踪池": "重点跟踪",
        "进入观察池": "观察",
        "继续观察": "观察",
        "剔除": "剔除",
    }
    return mapping.get(_clean(decision), "观察")


def build_tracking_item_from_research_task(task):
    return {
        "ticker": _clean(task.get("ticker")).upper(),
        "company_name": _clean(task.get("company_name")),
        "theme": _clean(task.get("theme")),
        "research_grade": _clean(task.get("final_research_grade")),
        "tracking_status": map_research_decision_to_tracking_status(task.get("decision")),
        "position_status": "未持有",
        "buy_price": None,
        "take_profit_price": None,
        "stop_loss_price": None,
        "catalyst": "",
        "risk": _clean(task.get("counter_evidence")),
        "next_review_date": "",
        "evidence_note": _clean(task.get("evidence_notes")),
        "data_status": _clean(task.get("data_status")) or "待人工确认",
        "updated_at": _utc_now_iso(),
    }


def can_transfer_to_tracking_pool(task):
    ticker = _clean(task.get("ticker"))
    theme = _clean(task.get("theme"))
    grade = _clean(task.get("final_research_grade"))
    decision = _clean(task.get("decision"))

    if not ticker:
        return {"ok": False, "reason": "ticker 不能为空"}
    if not theme:
        return {"ok": False, "reason": "theme 不能为空"}
    if not grade:
        return {"ok": False, "reason": "final_research_grade 不能为空"}
    if not decision:
        return {"ok": False, "reason": "decision 不能为空"}
    if decision == "剔除":
        return {"ok": False, "reason": "剔除任务不转入跟踪池"}
    return {"ok": True, "reason": "可以转入重点跟踪池"}


def upsert_tracking_item(existing_items, new_item):
    items = [dict(item) for item in (existing_items or [])]
    new_ticker = _clean(new_item.get("ticker")).upper()
    new_theme = _clean(new_item.get("theme"))

    for index, item in enumerate(items):
        item_ticker = _clean(item.get("ticker")).upper()
        item_theme = _clean(item.get("theme"))
        if item_ticker == new_ticker and item_theme == new_theme:
            items[index] = {**item, **new_item, "ticker": new_ticker, "theme": new_theme}
            return items

    items.append({**new_item, "ticker": new_ticker, "theme": new_theme})
    return items
