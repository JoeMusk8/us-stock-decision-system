import os
import sys


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.research_to_tracking_bridge import (
    build_tracking_item_from_research_task,
    can_transfer_to_tracking_pool,
    map_research_decision_to_tracking_status,
    upsert_tracking_item,
)


FORBIDDEN_TERMS = ["建议买入", "建议卖出", "目标价", "自动交易", "自动下单"]


def _task(**overrides):
    base = {
        "ticker": "LITE",
        "company_name": "Example Co",
        "theme": "AI 光互连",
        "final_research_grade": "A",
        "decision": "进入重点跟踪池",
        "evidence_notes": "证据备注",
        "counter_evidence": "核心风险",
        "data_status": "待人工确认",
    }
    base.update(overrides)
    return base


def test_decision_mapping():
    assert map_research_decision_to_tracking_status("进入核心跟踪池") == "核心跟踪"
    assert map_research_decision_to_tracking_status("进入重点跟踪池") == "重点跟踪"
    assert map_research_decision_to_tracking_status("进入观察池") == "观察"
    assert map_research_decision_to_tracking_status("继续观察") == "观察"
    assert map_research_decision_to_tracking_status("剔除") == "剔除"


def test_build_tracking_item_does_not_generate_prices():
    item = build_tracking_item_from_research_task(_task())
    assert item["buy_price"] is None
    assert item["take_profit_price"] is None
    assert item["stop_loss_price"] is None


def test_build_tracking_item_keeps_core_fields():
    item = build_tracking_item_from_research_task(_task())
    assert item["ticker"] == "LITE"
    assert item["theme"] == "AI 光互连"
    assert item["research_grade"] == "A"
    assert item["evidence_note"] == "证据备注"
    assert item["risk"] == "核心风险"


def test_can_transfer_rejects_missing_ticker():
    result = can_transfer_to_tracking_pool(_task(ticker=""))
    assert result["ok"] is False


def test_can_transfer_rejects_missing_theme():
    result = can_transfer_to_tracking_pool(_task(theme=""))
    assert result["ok"] is False


def test_can_transfer_rejects_removed_decision():
    result = can_transfer_to_tracking_pool(_task(decision="剔除"))
    assert result["ok"] is False
    assert result["reason"] == "剔除任务不转入跟踪池"


def test_upsert_updates_same_ticker_theme_without_duplicate():
    existing = [build_tracking_item_from_research_task(_task(research_status="进行中"))]
    new_item = build_tracking_item_from_research_task(_task(final_research_grade="S", decision="进入核心跟踪池"))
    result = upsert_tracking_item(existing, new_item)
    assert len(result) == 1
    assert result[0]["research_grade"] == "S"
    assert result[0]["tracking_status"] == "核心跟踪"


def test_outputs_do_not_include_forbidden_terms():
    item = build_tracking_item_from_research_task(_task())
    result = upsert_tracking_item([], item)
    text = str(item) + str(result) + str(can_transfer_to_tracking_pool(_task()))
    for term in FORBIDDEN_TERMS:
        assert term not in text


def run_tests():
    test_decision_mapping()
    test_build_tracking_item_does_not_generate_prices()
    test_build_tracking_item_keeps_core_fields()
    test_can_transfer_rejects_missing_ticker()
    test_can_transfer_rejects_missing_theme()
    test_can_transfer_rejects_removed_decision()
    test_upsert_updates_same_ticker_theme_without_duplicate()
    test_outputs_do_not_include_forbidden_terms()


if __name__ == "__main__":
    run_tests()
    print("tests/test_research_to_tracking_bridge.py passed")
