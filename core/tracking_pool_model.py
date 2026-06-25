"""Manual tracking pool model helpers.

This module only validates and summarizes manually entered tracking-pool data.
Strategy prices are manual annotations, not system recommendations.
"""

from __future__ import annotations

from datetime import UTC, datetime


VALID_RESEARCH_GRADES = {"S", "A", "B", "C", "D"}
VALID_TRACKING_STATUSES = {"核心跟踪", "重点跟踪", "观察", "暂停", "剔除"}
VALID_POSITION_STATUSES = {"未持有", "观察中", "已持有", "已卖出"}
VALID_DATA_STATUSES = {"待人工确认", "数据不足", "已验证"}


def utc_now_iso():
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def normalize_ticker(ticker):
    return str(ticker or "").strip().upper()


def _is_blank(value):
    return value is None or str(value).strip() == ""


def _to_positive_float(value):
    if _is_blank(value):
        return None, True
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None, False
    return number, number > 0


def validate_tracking_item(item):
    errors = []
    ticker = normalize_ticker(item.get("ticker"))
    theme = str(item.get("theme") or "").strip()
    research_grade = str(item.get("research_grade") or "").strip().upper()
    tracking_status = str(item.get("tracking_status") or "").strip()
    position_status = str(item.get("position_status") or "").strip()

    if not ticker:
        errors.append("ticker 不能为空")
    if not theme:
        errors.append("theme 不能为空")
    if research_grade not in VALID_RESEARCH_GRADES:
        errors.append("research_grade 只能是 S/A/B/C/D")
    if tracking_status not in VALID_TRACKING_STATUSES:
        errors.append("tracking_status 不合法")
    if position_status not in VALID_POSITION_STATUSES:
        errors.append("position_status 不合法")

    for field in ("buy_price", "take_profit_price", "stop_loss_price"):
        _, ok = _to_positive_float(item.get(field))
        if not ok:
            errors.append(f"{field} 如果填写，必须是正数")

    data_status = str(item.get("data_status") or "待人工确认").strip()
    if data_status not in VALID_DATA_STATUSES:
        errors.append("data_status 不合法")

    return {"ok": not errors, "errors": errors}


def calculate_strategy_risk_label(item):
    buy_price, buy_ok = _to_positive_float(item.get("buy_price"))
    take_profit_price, take_profit_ok = _to_positive_float(item.get("take_profit_price"))
    stop_loss_price, stop_loss_ok = _to_positive_float(item.get("stop_loss_price"))

    if not all([buy_ok, take_profit_ok, stop_loss_ok]) or not all([buy_price, take_profit_price, stop_loss_price]):
        return "未配置"

    upside = take_profit_price - buy_price
    downside = buy_price - stop_loss_price
    if upside <= 0 or downside <= 0:
        return "中性"
    if downside > upside * 1.2:
        return "风险偏高"
    if upside > downside:
        return "结构较好"
    return "中性"


def build_tracking_summary(items):
    normalized_items = items or []
    return {
        "总股票数": len(normalized_items),
        "核心跟踪数量": sum(1 for item in normalized_items if item.get("tracking_status") == "核心跟踪"),
        "重点跟踪数量": sum(1 for item in normalized_items if item.get("tracking_status") == "重点跟踪"),
        "观察数量": sum(1 for item in normalized_items if item.get("tracking_status") == "观察"),
        "已持有数量": sum(1 for item in normalized_items if item.get("position_status") == "已持有"),
        "未配置策略数量": sum(1 for item in normalized_items if calculate_strategy_risk_label(item) == "未配置"),
    }


def build_tracking_item(raw_item):
    item = dict(raw_item)
    item["ticker"] = normalize_ticker(item.get("ticker"))
    item["research_grade"] = str(item.get("research_grade") or "C").strip().upper()
    item["tracking_status"] = item.get("tracking_status") or "观察"
    item["position_status"] = item.get("position_status") or "未持有"
    item["data_status"] = item.get("data_status") or "待人工确认"
    item["updated_at"] = item.get("updated_at") or utc_now_iso()
    return item
