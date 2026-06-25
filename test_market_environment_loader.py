import inspect
import os
import sys


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core import market_environment_loader
from core.local_data_loader import load_json_file
from core.market_environment_loader import (
    can_enter_market_conclusion,
    load_market_environment_mock,
    validate_market_environment_data,
)


FORBIDDEN_20 = "20日" + "涨跌幅"
FORBIDDEN_50 = "50日" + "涨跌幅"


def test_can_load_market_environment_mock():
    result = load_market_environment_mock()
    assert result["ok"] is True
    assert result["error"] == ""


def test_market_funds_has_three_records():
    result = load_market_environment_mock()
    assert len(result["market_funds"]) == 3


def test_market_sentiment_has_one_record():
    result = load_market_environment_mock()
    assert len(result["market_sentiment"]) == 1


def test_mock_json_validation_passes():
    data = load_json_file("data/market_environment_mock.example.json")["data"]
    result = validate_market_environment_data(data)
    assert result["ok"] is True
    assert result["market_funds_total"] == 3
    assert result["market_sentiment_total"] == 1
    assert result["errors"] == []


def test_example_data_cannot_enter_real_market_conclusion():
    result = load_market_environment_mock()
    records = result["market_funds"] + result["market_sentiment"]
    assert all(record["data_status"] == "示例数据" for record in records)
    assert all(can_enter_market_conclusion(record) is False for record in records)


def test_market_funds_records_do_not_contain_forbidden_20_field():
    result = load_market_environment_mock()
    assert all(FORBIDDEN_20 not in record for record in result["market_funds"])


def test_market_funds_records_do_not_contain_forbidden_50_field():
    result = load_market_environment_mock()
    assert all(FORBIDDEN_50 not in record for record in result["market_funds"])


def test_missing_file_does_not_crash():
    result = load_market_environment_mock("data/not_exists_market_environment.json")
    assert result["ok"] is False
    assert result["market_funds"] == []
    assert result["market_sentiment"] == []
    assert result["error"]


def test_no_external_network_calls():
    source = inspect.getsource(market_environment_loader)
    forbidden_tokens = ("requests", "urllib", "socket", "aiohttp", "http://", "https://")
    assert not any(token in source for token in forbidden_tokens)


def run_tests():
    test_can_load_market_environment_mock()
    test_market_funds_has_three_records()
    test_market_sentiment_has_one_record()
    test_mock_json_validation_passes()
    test_example_data_cannot_enter_real_market_conclusion()
    test_market_funds_records_do_not_contain_forbidden_20_field()
    test_market_funds_records_do_not_contain_forbidden_50_field()
    test_missing_file_does_not_crash()
    test_no_external_network_calls()


if __name__ == "__main__":
    run_tests()
    print("tests/test_market_environment_loader.py passed")
