from core.workspace_quality import (
    build_quality_checks,
    build_quality_summary,
    count_missing_candidate_core_fields,
    count_missing_research_core_fields,
    count_research_without_grade,
    count_tracking_without_strategy,
)


def test_candidate_core_field_check():
    candidates = [{"ticker": "A", "industry": "AI", "theme": "光互连"}, {"ticker": "B", "industry": "AI"}]
    assert count_missing_candidate_core_fields(candidates) == 1


def test_research_core_field_check():
    tasks = [{"ticker": "A", "theme": "HBM"}, {"ticker": "B"}]
    assert count_missing_research_core_fields(tasks) == 1


def test_research_without_grade_check():
    tasks = [{"final_research_grade": "A"}, {"final_research_grade": ""}]
    assert count_research_without_grade(tasks) == 1


def test_tracking_without_strategy_check():
    pool = [{"ticker": "A", "buy_price": 10}, {"ticker": "B"}]
    assert count_tracking_without_strategy(pool) == 1


def test_quality_checks_and_summary():
    session_data = {
        "candidate_stocks": [{"ticker": "A", "industry": "AI", "theme": "光互连"}],
        "deep_research_tasks": [{"ticker": "A", "theme": "光互连", "final_research_grade": "S"}],
        "tracking_pool": [{"ticker": "A", "buy_price": 10}],
    }
    rows = build_quality_checks(session_data)
    summary = build_quality_summary(session_data)
    assert len(rows) == 4
    assert summary["status"] == "正常"
    assert summary["issue_count"] == 0


def test_quality_summary_detects_issues():
    session_data = {
        "candidate_stocks": [{"ticker": "A"}],
        "deep_research_tasks": [{"ticker": "A", "theme": "光互连", "final_research_grade": ""}],
        "tracking_pool": [{"ticker": "A"}],
    }
    summary = build_quality_summary(session_data)
    assert summary["status"] == "待处理"
    assert summary["issue_count"] >= 1
