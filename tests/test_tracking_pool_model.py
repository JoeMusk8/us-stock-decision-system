import os
import sys


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.tracking_pool_model import (
    build_tracking_summary,
    calculate_strategy_risk_label,
    normalize_ticker,
    validate_tracking_item,
)


FORBIDDEN_TERMS = ["建议买入", "建议卖出", "目标价", "自动交易", "自动下单"]


def _item(**overrides):
    base = {
        "ticker": "LITE",
        "company_name": "",
        "theme": "AI 光互连",
        "research_grade": "A",
        "tracking_status": "重点跟踪",
        "position_status": "观察中",
        "buy_price": None,
        "take_profit_price": None,
        "stop_loss_price": None,
        "data_status": "待人工确认",
    }
    base.update(overrides)
    return base


def test_normalize_ticker_uppercases_and_strips():
    assert normalize_ticker(" lite ") == "LITE"


def test_empty_ticker_fails_validation():
    result = validate_tracking_item(_item(ticker=" "))
    assert result["ok"] is False
    assert "ticker 不能为空" in result["errors"]


def test_empty_theme_fails_validation():
    result = validate_tracking_item(_item(theme=""))
    assert result["ok"] is False
    assert "theme 不能为空" in result["errors"]


def test_invalid_research_grade_fails_validation():
    result = validate_tracking_item(_item(research_grade="Z"))
    assert result["ok"] is False
    assert "research_grade 只能是 S/A/B/C/D" in result["errors"]


def test_negative_price_fails_validation():
    result = validate_tracking_item(_item(buy_price="-1"))
    assert result["ok"] is False
    assert "buy_price 如果填写，必须是正数" in result["errors"]


def test_missing_prices_are_unconfigured():
    assert calculate_strategy_risk_label(_item()) == "未配置"


def test_large_downside_returns_high_risk():
    item = _item(buy_price=100, take_profit_price=110, stop_loss_price=80)
    assert calculate_strategy_risk_label(item) == "风险偏高"


def test_larger_upside_returns_good_structure():
    item = _item(buy_price=100, take_profit_price=130, stop_loss_price=90)
    assert calculate_strategy_risk_label(item) == "结构较好"


def test_build_tracking_summary_counts_items():
    items = [
        _item(ticker="A", tracking_status="核心跟踪", position_status="已持有", buy_price=10, take_profit_price=15, stop_loss_price=8),
        _item(ticker="B", tracking_status="重点跟踪", position_status="观察中"),
        _item(ticker="C", tracking_status="观察", position_status="未持有"),
    ]
    summary = build_tracking_summary(items)
    assert summary["总股票数"] == 3
    assert summary["核心跟踪数量"] == 1
    assert summary["重点跟踪数量"] == 1
    assert summary["观察数量"] == 1
    assert summary["已持有数量"] == 1
    assert summary["未配置策略数量"] == 2


def test_outputs_do_not_include_forbidden_terms():
    summary = build_tracking_summary([_item()])
    label = calculate_strategy_risk_label(_item(buy_price=100, take_profit_price=130, stop_loss_price=90))
    text = str(summary) + label + str(validate_tracking_item(_item()))
    for term in FORBIDDEN_TERMS:
        assert term not in text


def run_tests():
    test_normalize_ticker_uppercases_and_strips()
    test_empty_ticker_fails_validation()
    test_empty_theme_fails_validation()
    test_invalid_research_grade_fails_validation()
    test_negative_price_fails_validation()
    test_missing_prices_are_unconfigured()
    test_large_downside_returns_high_risk()
    test_larger_upside_returns_good_structure()
    test_build_tracking_summary_counts_items()
    test_outputs_do_not_include_forbidden_terms()


if __name__ == "__main__":
    run_tests()
    print("tests/test_tracking_pool_model.py passed")
