"""Workspace quality checks for the session-based workflow."""

from __future__ import annotations

from typing import Any, Mapping


def _get(session_data: Mapping[str, Any] | Any, key: str, default: Any):
    if hasattr(session_data, "get"):
        return session_data.get(key, default)
    return default


def _list(value: Any) -> list:
    return value if isinstance(value, list) else []


def _missing(value: Any) -> bool:
    return value is None or str(value).strip() == ""


def count_missing_candidate_core_fields(candidates: Any) -> int:
    count = 0
    for item in _list(candidates):
        if not isinstance(item, dict):
            count += 1
            continue
        if _missing(item.get("ticker")) or _missing(item.get("industry")) or _missing(item.get("theme")):
            count += 1
    return count


def count_missing_research_core_fields(tasks: Any) -> int:
    count = 0
    for item in _list(tasks):
        if not isinstance(item, dict):
            count += 1
            continue
        if _missing(item.get("ticker")) or _missing(item.get("theme")):
            count += 1
    return count


def count_research_without_grade(tasks: Any) -> int:
    count = 0
    for item in _list(tasks):
        if isinstance(item, dict) and _missing(item.get("final_research_grade")):
            count += 1
    return count


def count_tracking_without_strategy(tracking_pool: Any) -> int:
    count = 0
    for item in _list(tracking_pool):
        if not isinstance(item, dict):
            count += 1
            continue
        has_any_price = item.get("buy_price") or item.get("take_profit_price") or item.get("stop_loss_price")
        if not has_any_price:
            count += 1
    return count


def build_quality_checks(session_data: Mapping[str, Any] | Any) -> list[dict]:
    candidates = _get(session_data, "candidate_stocks", [])
    tasks = _get(session_data, "deep_research_tasks", [])
    tracking_pool = _get(session_data, "tracking_pool", [])

    rows = [
        {
            "检查项": "候选股核心字段",
            "异常数": count_missing_candidate_core_fields(candidates),
            "处理方向": "补齐 ticker / industry / theme",
        },
        {
            "检查项": "投研任务核心字段",
            "异常数": count_missing_research_core_fields(tasks),
            "处理方向": "补齐 ticker / theme",
        },
        {
            "检查项": "研究等级",
            "异常数": count_research_without_grade(tasks),
            "处理方向": "在深度投研中生成等级",
        },
        {
            "检查项": "价格标注",
            "异常数": count_tracking_without_strategy(tracking_pool),
            "处理方向": "在重点跟踪池中补充标注",
        },
    ]
    for row in rows:
        row["状态"] = "正常" if row["异常数"] == 0 else "待处理"
    return rows


def build_quality_summary(session_data: Mapping[str, Any] | Any) -> dict:
    rows = build_quality_checks(session_data)
    issue_count = sum(row["异常数"] for row in rows)
    ok_count = sum(1 for row in rows if row["状态"] == "正常")
    total = len(rows)
    return {
        "total_checks": total,
        "ok_checks": ok_count,
        "issue_count": issue_count,
        "status": "正常" if issue_count == 0 else "待处理",
    }
