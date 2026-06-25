"""Workflow overview helpers for the session-based MVP."""

from __future__ import annotations

from typing import Any, Mapping


WORKFLOW_STEPS = (
    ("范式创新", "paradigm_signals"),
    ("基础投研行业池", "basic_research_industries"),
    ("候选股雷达", "candidate_stocks"),
    ("深度投研", "deep_research_tasks"),
    ("重点跟踪池", "tracking_pool"),
)


def _get(session_data: Mapping[str, Any] | Any, key: str, default: Any):
    if hasattr(session_data, "get"):
        return session_data.get(key, default)
    return default


def count_items(value: Any) -> int:
    if isinstance(value, list):
        return len(value)
    return 0


def count_strategy_configured(tracking_pool: Any) -> int:
    if not isinstance(tracking_pool, list):
        return 0
    count = 0
    for item in tracking_pool:
        if not isinstance(item, dict):
            continue
        if item.get("buy_price") or item.get("take_profit_price") or item.get("stop_loss_price"):
            count += 1
    return count


def build_workspace_counts(session_data: Mapping[str, Any] | Any) -> dict:
    counts = {key: count_items(_get(session_data, key, [])) for _, key in WORKFLOW_STEPS}
    counts["strategy_configured"] = count_strategy_configured(_get(session_data, "tracking_pool", []))
    counts["total_records"] = sum(counts[key] for _, key in WORKFLOW_STEPS)
    return counts


def build_workflow_overview(session_data: Mapping[str, Any] | Any) -> list[dict]:
    counts = build_workspace_counts(session_data)
    rows = []
    for index, (label, key) in enumerate(WORKFLOW_STEPS, start=1):
        count = counts[key]
        rows.append(
            {
                "顺序": index,
                "环节": label,
                "记录数": count,
                "状态": "已有数据" if count else "待补充",
            }
        )
    rows.append(
        {
            "顺序": len(rows) + 1,
            "环节": "策略标注",
            "记录数": counts["strategy_configured"],
            "状态": "已有标注" if counts["strategy_configured"] else "待补充",
        }
    )
    return rows


def suggest_next_step(session_data: Mapping[str, Any] | Any) -> str:
    counts = build_workspace_counts(session_data)
    if counts["paradigm_signals"] == 0:
        return "先在范式创新监控中添加一个新方向 / 新主题。"
    if counts["basic_research_industries"] == 0:
        return "将范式主题转入基础投研行业/主题池。"
    if counts["candidate_stocks"] == 0:
        return "在候选股雷达中添加候选股。"
    if counts["deep_research_tasks"] == 0:
        return "将候选股转入深度投研任务池。"
    if counts["tracking_pool"] == 0:
        return "完成研究等级后，将任务转入重点跟踪池。"
    if counts["strategy_configured"] == 0:
        return "在重点跟踪池中补充策略价格标注。"
    return "主链路已有完整记录，建议下载工作区 JSON 备份。"
