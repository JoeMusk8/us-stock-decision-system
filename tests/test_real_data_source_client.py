import hashlib
import inspect
import os
import sys


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core import real_data_source_client
from core.real_data_source_client import (
    can_real_data_auto_verified,
    can_real_data_enter_ui,
    explain_real_data_source_status,
    fetch_real_market_data_readonly,
    is_real_source_enabled,
    load_real_data_source_draft_config,
    precheck_real_source_config,
)


CONFIG_PATH = "config/real_data_sources.draft.json"
RUNTIME_FLAGS_PATH = "config/runtime_flags.example.json"


def _file_hash(file_path):
    with open(file_path, "rb") as file:
        return hashlib.sha256(file.read()).hexdigest()


def _load_config():
    result = load_real_data_source_draft_config(CONFIG_PATH)
    assert result["ok"] is True
    return result["config"]


def test_can_load_real_data_source_draft_config():
    result = load_real_data_source_draft_config(CONFIG_PATH)
    assert result["ok"] is True
    assert result["error"] == ""
    assert isinstance(result["config"], dict)


def test_selected_source_is_null():
    config = _load_config()
    assert config["selected_source"] is None


def test_all_candidates_are_disabled():
    config = _load_config()
    assert all(candidate["enabled"] is False for candidate in config["candidate_sources"])


def test_all_candidates_have_endpoint_unconfigured():
    config = _load_config()
    assert all(candidate["endpoint_configured"] is False for candidate in config["candidate_sources"])


def test_real_source_is_not_enabled():
    config = _load_config()
    assert is_real_source_enabled(config) is False


def test_readonly_fetch_returns_disabled_status():
    config = _load_config()
    result = fetch_real_market_data_readonly(config)
    assert result["ok"] is False
    assert result["records"] == []
    assert "allow_external_network=false" in result["error"]
    assert "禁止外部网络调用" in result["error"]


def test_default_runtime_flags_block_real_market_data():
    config = _load_config()
    result = fetch_real_market_data_readonly(config)
    assert result["ok"] is False
    assert result["records"] == []


def test_default_runtime_flags_block_real_data_to_ui():
    assert can_real_data_enter_ui(RUNTIME_FLAGS_PATH) is False


def test_default_runtime_flags_block_auto_verified():
    assert can_real_data_auto_verified(RUNTIME_FLAGS_PATH) is False


def test_status_explanation_mentions_network_block():
    config = _load_config()
    explanation = explain_real_data_source_status(config)
    assert "不允许联网" in explanation or "禁止外部网络调用" in explanation
    assert "不允许进入真实市场结论" in explanation


def test_precheck_passes_for_current_disabled_draft():
    config = _load_config()
    result = precheck_real_source_config(config)
    assert result["ok"] is True
    assert result["errors"] == []


def test_no_external_network_calls():
    source = inspect.getsource(real_data_source_client)
    blocked_tokens = ("requests", "yfinance", "pandas_datareader", "urllib", "socket", "aiohttp", "http://", "https://")
    assert not any(token in source for token in blocked_tokens)


def test_does_not_modify_draft_config():
    before = _file_hash(CONFIG_PATH)
    config = _load_config()
    precheck_real_source_config(config)
    is_real_source_enabled(config)
    fetch_real_market_data_readonly(config)
    explain_real_data_source_status(config)
    after = _file_hash(CONFIG_PATH)
    assert before == after


def test_does_not_modify_runtime_flags_config():
    before = _file_hash(RUNTIME_FLAGS_PATH)
    config = _load_config()
    fetch_real_market_data_readonly(config, RUNTIME_FLAGS_PATH)
    can_real_data_enter_ui(RUNTIME_FLAGS_PATH)
    can_real_data_auto_verified(RUNTIME_FLAGS_PATH)
    after = _file_hash(RUNTIME_FLAGS_PATH)
    assert before == after


def test_selected_source_and_candidates_remain_disabled():
    config = _load_config()
    assert config["selected_source"] is None
    assert all(candidate["enabled"] is False for candidate in config["candidate_sources"])


def run_tests():
    test_can_load_real_data_source_draft_config()
    test_selected_source_is_null()
    test_all_candidates_are_disabled()
    test_all_candidates_have_endpoint_unconfigured()
    test_real_source_is_not_enabled()
    test_readonly_fetch_returns_disabled_status()
    test_default_runtime_flags_block_real_market_data()
    test_default_runtime_flags_block_real_data_to_ui()
    test_default_runtime_flags_block_auto_verified()
    test_status_explanation_mentions_network_block()
    test_precheck_passes_for_current_disabled_draft()
    test_no_external_network_calls()
    test_does_not_modify_draft_config()
    test_does_not_modify_runtime_flags_config()
    test_selected_source_and_candidates_remain_disabled()


if __name__ == "__main__":
    run_tests()
    print("tests/test_real_data_source_client.py passed")
