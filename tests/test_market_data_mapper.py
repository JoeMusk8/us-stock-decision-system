import inspect
import os
import sys


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core import market_data_mapper
from core.market_data_mapper import (
    MARKET_FUND_STANDARD_FIELDS,
    MARKET_SENTIMENT_STANDARD_FIELDS,
    can_mark_mapped_record_verified,
    map_market_fund_record,
    map_market_sentiment_record,
    validate_mapped_market_fund_record,
    validate_mapped_market_sentiment_record,
)


FORBIDDEN_20 = "20日" + "涨跌幅"
FORBIDDEN_50 = "50日" + "涨跌幅"


def test_can_map_mock_market_fund_record():
    raw_record = {
        "symbol": "MOCK_ASSET",
        "asset_name": "模拟资产",
        "asset_type": "mock_type",
        "current_price": None,
        "ma_20": None,
        "ma_50": None,
        "volume": None,
        "relative_volume": None,
    }
    mapped = map_market_fund_record(raw_record, source_name="mock_source")
    assert mapped["symbol"] == "MOCK_ASSET"
    assert mapped["source_name"] == "mock_source"


def test_mapped_market_fund_record_has_all_standard_fields():
    mapped = map_market_fund_record({})
    assert all(field in mapped for field in MARKET_FUND_STANDARD_FIELDS)
    result = validate_mapped_market_fund_record(mapped)
    assert result["is_valid"] is True


def test_missing_market_fund_fields_stay_none():
    mapped = map_market_fund_record({"symbol": "MOCK_ASSET"})
    assert mapped["asset_name"] is None
    assert mapped["current_price"] is None
    assert mapped["volume"] is None


def test_mapped_market_fund_default_status_is_manual_review():
    mapped = map_market_fund_record({"data_status": "已验证"})
    assert mapped["data_status"] == "待人工确认"


def test_mapped_record_cannot_be_auto_verified():
    mapped = map_market_fund_record({})
    assert can_mark_mapped_record_verified(mapped) is False


def test_can_map_mock_market_sentiment_record():
    raw_record = {
        "indicator_id": "MOCK_SENTIMENT",
        "indicator_name": "模拟情绪指标",
        "indicator_type": "mock_type",
        "current_value": None,
    }
    mapped = map_market_sentiment_record(raw_record, source_name="mock_sentiment_source")
    assert mapped["indicator_id"] == "MOCK_SENTIMENT"
    assert mapped["source_name"] == "mock_sentiment_source"


def test_mapped_market_sentiment_record_has_all_standard_fields():
    mapped = map_market_sentiment_record({})
    assert all(field in mapped for field in MARKET_SENTIMENT_STANDARD_FIELDS)
    result = validate_mapped_market_sentiment_record(mapped)
    assert result["is_valid"] is True


def test_mapper_does_not_call_external_network():
    source = inspect.getsource(market_data_mapper)
    forbidden_tokens = ("requests", "urllib", "socket", "aiohttp", "http://", "https://")
    assert not any(token in source for token in forbidden_tokens)


def test_mapped_records_do_not_contain_forbidden_fields():
    mapped_fund = map_market_fund_record({})
    mapped_sentiment = map_market_sentiment_record({})
    assert FORBIDDEN_20 not in mapped_fund
    assert FORBIDDEN_50 not in mapped_fund
    assert FORBIDDEN_20 not in mapped_sentiment
    assert FORBIDDEN_50 not in mapped_sentiment


def run_tests():
    test_can_map_mock_market_fund_record()
    test_mapped_market_fund_record_has_all_standard_fields()
    test_missing_market_fund_fields_stay_none()
    test_mapped_market_fund_default_status_is_manual_review()
    test_mapped_record_cannot_be_auto_verified()
    test_can_map_mock_market_sentiment_record()
    test_mapped_market_sentiment_record_has_all_standard_fields()
    test_mapper_does_not_call_external_network()
    test_mapped_records_do_not_contain_forbidden_fields()


if __name__ == "__main__":
    run_tests()
    print("tests/test_market_data_mapper.py passed")
