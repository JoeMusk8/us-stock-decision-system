import os
import sys


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.deep_research_model import (
    SCORE_FIELDS,
    build_research_summary,
    calculate_total_research_score,
    derive_research_decision,
    derive_research_grade,
    normalize_research_task,
    validate_research_task,
)


FORBIDDEN_TERMS = ["建议买入", "建议卖出", "目标价", "自动交易", "自动下单"]


def _task(**overrides):
    base = {
        "ticker": "lite",
        "company_name": "",
        "theme": "AI 光互连",
        "research_status": "进行中",
        "data_status": "待人工确认",
    }
    for field in SCORE_FIELDS:
        base[field] = 3
    base.update(overrides)
    return base


def test_ticker_is_normalized_to_uppercase():
    normalized = normalize_research_task(_task(ticker=" mu "))
    assert normalized["ticker"] == "MU"


def test_empty_ticker_fails_validation():
    result = validate_research_task(_task(ticker=""))
    assert result["ok"] is False
    assert "ticker 不能为空" in result["errors"]


def test_empty_theme_fails_validation():
    result = validate_research_task(_task(theme=""))
    assert result["ok"] is False
    assert "theme 不能为空" in result["errors"]


def test_score_below_zero_or_above_five_fails_validation():
    result_low = validate_research_task(_task(business_boundary_score=-1))
    result_high = validate_research_task(_task(theme_benefit_score=6))
    assert result_low["ok"] is False
    assert result_high["ok"] is False


def test_high_score_gets_s_grade():
    assert derive_research_grade(40) == "S"
    assert derive_research_grade(34) == "S"


def test_grade_ranges_are_correct():
    assert derive_research_grade(28) == "A"
    assert derive_research_grade(21) == "B"
    assert derive_research_grade(12) == "C"
    assert derive_research_grade(11) == "D"


def test_grade_decisions_are_correct():
    assert derive_research_decision("S") == "进入核心跟踪池"
    assert derive_research_decision("A") == "进入重点跟踪池"
    assert derive_research_decision("D") == "剔除"


def test_total_score_uses_eight_fields():
    task = _task()
    assert calculate_total_research_score(task) == 24


def test_build_research_summary_counts_tasks():
    tasks = [
        _task(ticker="A", research_status="已完成", **{field: 5 for field in SCORE_FIELDS}),
        _task(ticker="B", research_status="进行中", **{field: 4 for field in SCORE_FIELDS}),
        _task(ticker="C", research_status="未开始", **{field: 1 for field in SCORE_FIELDS}),
    ]
    summary = build_research_summary(tasks)
    assert summary["总任务数"] == 3
    assert summary["S 数量"] == 1
    assert summary["A 数量"] == 1
    assert summary["D 数量"] == 1
    assert summary["已完成数量"] == 1
    assert summary["进行中数量"] == 1


def test_outputs_do_not_include_forbidden_terms():
    task = normalize_research_task(_task())
    text = str(task) + str(validate_research_task(task)) + str(build_research_summary([task]))
    for term in FORBIDDEN_TERMS:
        assert term not in text


def run_tests():
    test_ticker_is_normalized_to_uppercase()
    test_empty_ticker_fails_validation()
    test_empty_theme_fails_validation()
    test_score_below_zero_or_above_five_fails_validation()
    test_high_score_gets_s_grade()
    test_grade_ranges_are_correct()
    test_grade_decisions_are_correct()
    test_total_score_uses_eight_fields()
    test_build_research_summary_counts_tasks()
    test_outputs_do_not_include_forbidden_terms()


if __name__ == "__main__":
    run_tests()
    print("tests/test_deep_research_model.py passed")
