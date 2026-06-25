import os
import sys


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.market_environment_rules import (
    evaluate_market_funds,
    evaluate_market_sentiment,
    evaluate_overall_market_environment,
)


FORBIDDEN_TERMS = ["买" + "入", "卖" + "出", "目标" + "价", "自动" + "交易", "自动" + "下单"]


def _fund(symbol, above20=True, above50=True, direction="向上", status="待人工确认"):
    return {
        "symbol": symbol,
        "current_price": 100.0,
        "ma_20": 90.0,
        "ma_50": 80.0,
        "above_ma20": above20,
        "above_ma50": above50,
        "ma_20_direction": direction,
        "ma_50_direction": direction,
        "data_status": status,
    }


def _vix(value, status="待人工确认"):
    return [{"current_value": value, "data_status": status}]


def test_funds_support_when_all_assets_above_moving_averages():
    result = evaluate_market_funds([_fund("QQQ"), _fund("^IXIC"), _fund("BTC-USD")])
    assert result["status"] == "支持"
    assert result["support_count"] == 3


def test_funds_weak_when_majority_assets_below_moving_averages():
    result = evaluate_market_funds([
        _fund("QQQ", above20=False),
        _fund("^IXIC", above50=False),
        _fund("BTC-USD"),
    ])
    assert result["status"] == "不支持"
    assert result["weak_count"] == 2


def test_funds_insufficient_when_less_than_two_valid_assets():
    result = evaluate_market_funds([
        _fund("QQQ", status="数据不足"),
        _fund("^IXIC", status="数据不足"),
        _fund("BTC-USD"),
    ])
    assert result["status"] == "数据不足"


def test_sentiment_support_when_vix_below_18():
    result = evaluate_market_sentiment(_vix(17.9))
    assert result["status"] == "支持"


def test_sentiment_caution_when_vix_between_18_and_25():
    result = evaluate_market_sentiment(_vix(20.0))
    assert result["status"] == "谨慎"


def test_sentiment_weak_when_vix_at_or_above_25():
    result = evaluate_market_sentiment(_vix(25.0))
    assert result["status"] == "不支持"


def test_overall_result_has_no_disallowed_trading_terms():
    funds = [_fund("QQQ"), _fund("^IXIC"), _fund("BTC-USD")]
    result = evaluate_overall_market_environment(funds, _vix(16.0))
    text = " ".join(str(value) for value in result.values())
    for term in FORBIDDEN_TERMS:
        assert term not in text


def run_tests():
    test_funds_support_when_all_assets_above_moving_averages()
    test_funds_weak_when_majority_assets_below_moving_averages()
    test_funds_insufficient_when_less_than_two_valid_assets()
    test_sentiment_support_when_vix_below_18()
    test_sentiment_caution_when_vix_between_18_and_25()
    test_sentiment_weak_when_vix_at_or_above_25()
    test_overall_result_has_no_disallowed_trading_terms()


if __name__ == "__main__":
    run_tests()
    print("tests/test_market_environment_rules.py passed")
