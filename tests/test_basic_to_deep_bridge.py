import os
import sys


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.basic_to_deep_bridge import (
    build_deep_research_task_from_candidate,
    can_transfer_candidate_to_deep_research,
    upsert_deep_research_task,
)


FORBIDDEN_TERMS = ["建议买入", "建议卖出", "目标价", "自动交易", "自动下单"]


def _candidate(**overrides):
    item = {
        "ticker": "LITE",
        "company_name": "",
        "industry": "AI 光通信",
        "theme": "AI 光互连",
        "chain_layer": "核心零部件",
        "bottleneck_score": 4,
        "heat_status": "升温中",
        "capital_flow_status": "流入",
        "candidate_reason": "人工候选",
        "evidence_note": "待人工确认",
        "data_status": "待人工确认",
    }
    item.update(overrides)
    return item


def test_transfer_requires_ticker_industry_theme():
    assert can_transfer_candidate_to_deep_research(_candidate(ticker=""))["ok"] is False
    assert can_transfer_candidate_to_deep_research(_candidate(industry=""))["ok"] is False
    assert can_transfer_candidate_to_deep_research(_candidate(theme=""))["ok"] is False


def test_insufficient_data_can_transfer_with_warning():
    result = can_transfer_candidate_to_deep_research(_candidate(data_status="数据不足"))
    assert result["ok"] is True
    assert "需要深度投研验证" in result["reason"]


def test_overheated_candidate_can_transfer_with_warning():
    result = can_transfer_candidate_to_deep_research(_candidate(heat_status="过热"))
    assert result["ok"] is True
    assert "需警惕已被交易" in result["reason"]


def test_build_deep_task_defaults_scores_and_no_grade():
    task = build_deep_research_task_from_candidate(_candidate())
    assert task["ticker"] == "LITE"
    assert task["theme"] == "AI 光互连"
    assert task["business_boundary_score"] == 0
    assert task["final_research_grade"] == ""
    assert task["decision"] == ""
    assert "buy_price" not in task
    assert "take_profit_price" not in task
    assert "stop_loss_price" not in task


def test_upsert_deep_task_updates_same_ticker_theme():
    first = build_deep_research_task_from_candidate(_candidate(company_name="A"))
    second = build_deep_research_task_from_candidate(_candidate(company_name="B"))
    result = upsert_deep_research_task([first], second)
    assert len(result) == 1
    assert result[0]["company_name"] == "B"


def test_outputs_do_not_include_forbidden_terms():
    task = build_deep_research_task_from_candidate(_candidate())
    text = str(task) + str(can_transfer_candidate_to_deep_research(_candidate()))
    for term in FORBIDDEN_TERMS:
        assert term not in text


def run_tests():
    test_transfer_requires_ticker_industry_theme()
    test_insufficient_data_can_transfer_with_warning()
    test_overheated_candidate_can_transfer_with_warning()
    test_build_deep_task_defaults_scores_and_no_grade()
    test_upsert_deep_task_updates_same_ticker_theme()
    test_outputs_do_not_include_forbidden_terms()


if __name__ == "__main__":
    run_tests()
    print("tests/test_basic_to_deep_bridge.py passed")
