"""Manual deep research task model helpers.

Research grades are workflow grades, not buy ratings. Decisions describe
research flow, not trading instructions.
"""

from __future__ import annotations

from datetime import UTC, datetime


SCORE_FIELDS = [
    "business_boundary_score",
    "theme_benefit_score",
    "supply_chain_position_score",
    "financial_realization_score",
    "customer_order_capex_score",
    "competition_score",
    "risk_counterevidence_score",
    "claim_evidence_score",
]

VALID_RESEARCH_STATUSES = {"未开始", "进行中", "已完成", "暂停", "剔除"}
VALID_DATA_STATUSES = {"待人工确认", "数据不足", "已验证"}
VALID_GRADES = {"S", "A", "B", "C", "D"}


def utc_now_iso():
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def _clean_text(value):
    return str(value or "").strip()


def _to_score(value):
    if value in (None, ""):
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def normalize_research_task(task):
    normalized = dict(task)
    normalized["ticker"] = _clean_text(normalized.get("ticker")).upper()
    normalized["theme"] = _clean_text(normalized.get("theme"))
    normalized["company_name"] = _clean_text(normalized.get("company_name"))
    normalized["research_status"] = normalized.get("research_status") or "未开始"
    normalized["data_status"] = normalized.get("data_status") or "待人工确认"
    normalized["updated_at"] = normalized.get("updated_at") or utc_now_iso()
    normalized["task_id"] = normalized.get("task_id") or f"TASK-{normalized['ticker'] or 'UNKNOWN'}-{normalized['updated_at']}"
    for field in SCORE_FIELDS:
        score = _to_score(normalized.get(field))
        normalized[field] = 0.0 if score is None else score
    normalized["key_claims"] = normalized.get("key_claims") or []
    normalized["evidence_notes"] = normalized.get("evidence_notes") or ""
    normalized["counter_evidence"] = normalized.get("counter_evidence") or ""
    total_score = calculate_total_research_score(normalized)
    normalized["final_research_grade"] = normalized.get("final_research_grade") or derive_research_grade(total_score)
    normalized["decision"] = normalized.get("decision") or derive_research_decision(normalized["final_research_grade"])
    return normalized


def validate_research_task(task):
    normalized = normalize_research_task(task)
    errors = []

    if not normalized["ticker"]:
        errors.append("ticker 不能为空")
    if not normalized["theme"]:
        errors.append("theme 不能为空")
    if normalized["research_status"] not in VALID_RESEARCH_STATUSES:
        errors.append("research_status 不合法")
    if normalized["data_status"] not in VALID_DATA_STATUSES:
        errors.append("data_status 不合法")

    for field in SCORE_FIELDS:
        score = _to_score(task.get(field, normalized.get(field)))
        if score is None or score < 0 or score > 5:
            errors.append(f"{field} 必须是 0-5 之间的数字")

    grade = normalized.get("final_research_grade")
    if grade and grade not in VALID_GRADES:
        errors.append("final_research_grade 只能是 S/A/B/C/D")

    return {"ok": not errors, "errors": errors}


def calculate_total_research_score(task):
    total = 0.0
    for field in SCORE_FIELDS:
        score = _to_score(task.get(field))
        total += 0.0 if score is None else score
    return round(total, 2)


def derive_research_grade(total_score):
    score = float(total_score)
    if 34 <= score <= 40:
        return "S"
    if 28 <= score <= 33:
        return "A"
    if 21 <= score <= 27:
        return "B"
    if 12 <= score <= 20:
        return "C"
    return "D"


def derive_research_decision(grade):
    mapping = {
        "S": "进入核心跟踪池",
        "A": "进入重点跟踪池",
        "B": "进入观察池",
        "C": "继续观察",
        "D": "剔除",
    }
    return mapping.get(grade, "继续观察")


def build_research_summary(tasks):
    normalized_tasks = [normalize_research_task(task) for task in (tasks or [])]
    return {
        "总任务数": len(normalized_tasks),
        "S 数量": sum(1 for task in normalized_tasks if task.get("final_research_grade") == "S"),
        "A 数量": sum(1 for task in normalized_tasks if task.get("final_research_grade") == "A"),
        "B 数量": sum(1 for task in normalized_tasks if task.get("final_research_grade") == "B"),
        "C 数量": sum(1 for task in normalized_tasks if task.get("final_research_grade") == "C"),
        "D 数量": sum(1 for task in normalized_tasks if task.get("final_research_grade") == "D"),
        "已完成数量": sum(1 for task in normalized_tasks if task.get("research_status") == "已完成"),
        "进行中数量": sum(1 for task in normalized_tasks if task.get("research_status") == "进行中"),
    }
