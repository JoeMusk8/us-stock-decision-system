"""Bridge candidate stocks from basic research into deep research tasks."""

from __future__ import annotations

from datetime import UTC, datetime

from core.deep_research_model import SCORE_FIELDS


def _utc_now_iso():
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def _clean(value):
    return str(value or "").strip()


def can_transfer_candidate_to_deep_research(candidate):
    if not _clean(candidate.get("ticker")):
        return {"ok": False, "reason": "ticker 不能为空"}
    if not _clean(candidate.get("industry")):
        return {"ok": False, "reason": "industry 不能为空"}
    if not _clean(candidate.get("theme")):
        return {"ok": False, "reason": "theme 不能为空"}
    if candidate.get("data_status") == "数据不足":
        return {"ok": True, "reason": "数据不足，可以转入，但需要深度投研验证"}
    if candidate.get("heat_status") == "过热":
        return {"ok": True, "reason": "热度过高，可以转入，但需警惕已被交易"}
    return {"ok": True, "reason": "可以转入深度投研任务池"}


def build_deep_research_task_from_candidate(candidate):
    task = {
        "task_id": f"CANDIDATE-{_clean(candidate.get('ticker')).upper()}-{_utc_now_iso()}",
        "ticker": _clean(candidate.get("ticker")).upper(),
        "company_name": _clean(candidate.get("company_name")),
        "theme": _clean(candidate.get("theme")),
        "research_status": "未开始",
        "key_claims": [],
        "evidence_notes": _clean(candidate.get("evidence_note")),
        "counter_evidence": "",
        "final_research_grade": "",
        "decision": "",
        "data_status": candidate.get("data_status") or "待人工确认",
        "updated_at": _utc_now_iso(),
        "source": "候选股雷达",
        "source_industry": _clean(candidate.get("industry")),
        "candidate_reason": _clean(candidate.get("candidate_reason")),
    }
    for field in SCORE_FIELDS:
        task[field] = 0
    return task


def upsert_deep_research_task(existing_tasks, new_task):
    tasks = [dict(task) for task in (existing_tasks or [])]
    new_ticker = _clean(new_task.get("ticker")).upper()
    new_theme = _clean(new_task.get("theme"))
    for index, task in enumerate(tasks):
        if _clean(task.get("ticker")).upper() == new_ticker and _clean(task.get("theme")) == new_theme:
            tasks[index] = {**task, **new_task, "ticker": new_ticker, "theme": new_theme}
            return tasks
    tasks.append({**new_task, "ticker": new_ticker, "theme": new_theme})
    return tasks
