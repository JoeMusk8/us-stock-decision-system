import os
import sys
import builtins

import pandas as pd


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.yfinance_market_client import (
    DATA_STATUS_INSUFFICIENT,
    DATA_STATUS_PENDING_REVIEW,
    calculate_market_fund_metrics,
    fetch_market_environment_data,
    _market_fund_record,
    _sentiment_record,
)


FORBIDDEN_20 = "20日" + "涨跌幅"
FORBIDDEN_50 = "50日" + "涨跌幅"


def _mock_history(days=60):
    return pd.DataFrame(
        {
            "Close": [float(index) for index in range(1, days + 1)],
            "Volume": [1000.0 + index for index in range(days)],
        }
    )


def test_calculate_market_fund_metrics_from_mock_data():
    metrics = calculate_market_fund_metrics(_mock_history())
    assert metrics.current_price == 60.0
    assert metrics.ma_20 == 50.5
    assert metrics.ma_50 == 35.5
    assert metrics.ma_20_direction == "向上"
    assert metrics.ma_50_direction == "向上"
    assert metrics.volume == 1059.0
    assert metrics.relative_volume is not None
    assert metrics.above_ma20 is True
    assert metrics.above_ma50 is True


def test_market_fund_record_defaults_to_manual_review_when_complete():
    record = _market_fund_record("QQQ", _mock_history())
    assert record["symbol"] == "QQQ"
    assert record["asset_name"] == "QQQ"
    assert record["data_status"] == DATA_STATUS_PENDING_REVIEW


def test_missing_history_returns_insufficient_without_fake_values():
    record = _market_fund_record("QQQ", pd.DataFrame())
    assert record["data_status"] == DATA_STATUS_INSUFFICIENT
    assert record["current_price"] is None
    assert record["ma_20"] is None
    assert record["ma_50"] is None
    assert record["volume"] is None


def test_short_history_returns_insufficient():
    record = _market_fund_record("BTC-USD", _mock_history(days=30))
    assert record["data_status"] == DATA_STATUS_INSUFFICIENT
    assert record["current_price"] is None


def test_vix_sentiment_record_from_mock_data():
    record = _sentiment_record(_mock_history())
    assert record["indicator_id"] == "^VIX"
    assert record["indicator_name"] == "VIX"
    assert record["current_value"] == 60.0
    assert record["data_status"] == DATA_STATUS_PENDING_REVIEW


def test_vix_sentiment_missing_data_is_insufficient():
    record = _sentiment_record(pd.DataFrame())
    assert record["current_value"] is None
    assert record["data_status"] == DATA_STATUS_INSUFFICIENT


def test_yfinance_missing_does_not_crash():
    original_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "yfinance":
            raise ImportError("mock missing dependency")
        return original_import(name, *args, **kwargs)

    builtins.__import__ = fake_import
    try:
        result = fetch_market_environment_data()
    finally:
        builtins.__import__ = original_import

    assert result["ok"] is False
    assert result["market_funds"] == []
    assert result["market_sentiment"] == []
    assert result["error"] == "缺少 yfinance，请运行 python -m pip install -r requirements.txt"


def test_records_do_not_include_forbidden_fields():
    record = _market_fund_record("QQQ", _mock_history())
    sentiment = _sentiment_record(_mock_history())
    assert FORBIDDEN_20 not in record
    assert FORBIDDEN_50 not in record
    assert FORBIDDEN_20 not in sentiment
    assert FORBIDDEN_50 not in sentiment


def run_tests():
    test_calculate_market_fund_metrics_from_mock_data()
    test_market_fund_record_defaults_to_manual_review_when_complete()
    test_missing_history_returns_insufficient_without_fake_values()
    test_short_history_returns_insufficient()
    test_vix_sentiment_record_from_mock_data()
    test_vix_sentiment_missing_data_is_insufficient()
    test_yfinance_missing_does_not_crash()
    test_records_do_not_include_forbidden_fields()


if __name__ == "__main__":
    run_tests()
    print("tests/test_yfinance_market_client.py passed")
