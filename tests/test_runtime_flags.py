import os
import sys


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.runtime_flags import (
    can_auto_mark_verified,
    is_external_network_allowed,
    is_real_data_to_ui_allowed,
    is_real_market_data_allowed,
    load_runtime_flags,
    validate_runtime_flags,
)


def _load_flags():
    result = load_runtime_flags()
    assert result["ok"] is True
    return result["flags"]


def test_can_load_runtime_flags():
    result = load_runtime_flags()
    assert result["ok"] is True
    assert result["error"] == ""
    assert isinstance(result["flags"], dict)
    assert isinstance(result["rules"], dict)


def test_allow_external_network_default_false():
    flags = _load_flags()
    assert flags["allow_external_network"] is False
    assert is_external_network_allowed(flags) is False


def test_allow_real_market_data_default_false():
    flags = _load_flags()
    assert flags["allow_real_market_data"] is False
    assert is_real_market_data_allowed(flags) is False


def test_allow_real_data_to_ui_default_false():
    flags = _load_flags()
    assert flags["allow_real_data_to_ui"] is False
    assert is_real_data_to_ui_allowed(flags) is False


def test_allow_auto_verified_status_default_false():
    flags = _load_flags()
    assert flags["allow_auto_verified_status"] is False


def test_allow_trading_default_false():
    flags = _load_flags()
    assert flags["allow_trading"] is False


def test_allow_order_execution_default_false():
    flags = _load_flags()
    assert flags["allow_order_execution"] is False


def test_allow_investment_advice_default_false():
    flags = _load_flags()
    assert flags["allow_investment_advice"] is False


def test_can_auto_mark_verified_returns_false():
    flags = _load_flags()
    assert can_auto_mark_verified(flags) is False
    assert can_auto_mark_verified({"allow_auto_verified_status": True}) is False


def test_validate_runtime_flags_passes():
    flags = _load_flags()
    result = validate_runtime_flags(flags)
    assert result["ok"] is True
    assert result["errors"] == []


def test_missing_file_does_not_crash():
    result = load_runtime_flags("config/not_exists_runtime_flags.json")
    assert result["ok"] is False
    assert result["flags"] == {}
    assert result["rules"] == {}
    assert result["error"]


def run_tests():
    test_can_load_runtime_flags()
    test_allow_external_network_default_false()
    test_allow_real_market_data_default_false()
    test_allow_real_data_to_ui_default_false()
    test_allow_auto_verified_status_default_false()
    test_allow_trading_default_false()
    test_allow_order_execution_default_false()
    test_allow_investment_advice_default_false()
    test_can_auto_mark_verified_returns_false()
    test_validate_runtime_flags_passes()
    test_missing_file_does_not_crash()


if __name__ == "__main__":
    run_tests()
    print("tests/test_runtime_flags.py passed")
