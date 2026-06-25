"""Read-only real data source client draft.

This module only reads the local draft config and reports disabled status. It
does not connect to external services, fetch market data, or make trading
decisions.
"""

import json
from pathlib import Path

from core.runtime_flags import (
    can_auto_mark_verified,
    is_external_network_allowed,
    is_real_data_to_ui_allowed,
    is_real_market_data_allowed,
    load_runtime_flags,
)


DISABLED_FETCH_ERROR = "真实数据源尚未启用，当前阶段禁止外部网络调用。"
ALLOWED_EMPTY_SECRET_VALUES = ("", None, "待配置")
ALLOWED_EMPTY_ENDPOINT_VALUES = ("", None, "待人工确认")


def load_real_data_source_draft_config(file_path="config/real_data_sources.draft.json"):
    """Load the local real data source draft config without modifying it."""
    path = Path(file_path)
    if not path.exists():
        return {"ok": False, "config": {}, "error": f"文件不存在：{file_path}"}

    try:
        with path.open("r", encoding="utf-8") as file:
            config = json.load(file)
    except json.JSONDecodeError as exc:
        return {"ok": False, "config": {}, "error": f"JSON 格式错误：{exc}"}
    except OSError as exc:
        return {"ok": False, "config": {}, "error": f"读取失败：{exc}"}

    if not isinstance(config, dict):
        return {"ok": False, "config": {}, "error": "配置文件顶层必须是 dict"}

    return {"ok": True, "config": config, "error": ""}


def _get_selected_candidate(config):
    if not isinstance(config, dict):
        return None

    selected_source = config.get("selected_source")
    if selected_source is None:
        return None

    selected_id = selected_source
    if isinstance(selected_source, dict):
        selected_id = selected_source.get("candidate_id")

    for candidate in config.get("candidate_sources", []):
        if isinstance(candidate, dict) and candidate.get("candidate_id") == selected_id:
            return candidate

    return None


def is_real_source_enabled(config):
    """Return True only when a selected candidate is fully enabled."""
    candidate = _get_selected_candidate(config)
    if candidate is None:
        return False

    return (
        candidate.get("enabled") is True
        and candidate.get("endpoint_configured") is True
    )


def precheck_real_source_config(config):
    """Check whether the draft config is still safely disabled."""
    errors = []
    warnings = []

    if not isinstance(config, dict):
        return {"ok": False, "errors": ["config 必须是 dict"], "warnings": []}

    selected_source = config.get("selected_source")
    if selected_source is not None:
        errors.append("selected_source 必须保持为 null")
    else:
        warnings.append("selected_source 为 null，真实数据源未选择")

    candidates = config.get("candidate_sources", [])
    if not isinstance(candidates, list):
        errors.append("candidate_sources 必须是 list")
        candidates = []

    for index, candidate in enumerate(candidates, start=1):
        if not isinstance(candidate, dict):
            errors.append(f"candidate_sources[{index}] 必须是 dict")
            continue

        candidate_id = candidate.get("candidate_id", f"candidate_{index}")

        if candidate.get("enabled") is not False:
            errors.append(f"{candidate_id} enabled 必须为 false")

        if candidate.get("endpoint_configured") is not False:
            errors.append(f"{candidate_id} endpoint_configured 必须为 false")

        if candidate.get("api_key_env") not in ALLOWED_EMPTY_SECRET_VALUES:
            errors.append(f"{candidate_id} 不得写入真实 API key")

        if candidate.get("endpoint_placeholder") not in ALLOWED_EMPTY_ENDPOINT_VALUES:
            errors.append(f"{candidate_id} 不得写入真实 endpoint")

        if candidate.get("first_status_after_fetch") != "待人工确认":
            errors.append(f"{candidate_id} first_status_after_fetch 必须为 待人工确认")

        if candidate.get("manual_review_required") is not True:
            errors.append(f"{candidate_id} manual_review_required 必须为 true")

    if not candidates:
        warnings.append("candidate_sources 为空")

    return {"ok": not errors, "errors": errors, "warnings": warnings}


def fetch_real_market_data_readonly(config, runtime_flags_file="config/runtime_flags.example.json"):
    """Return disabled status after checking runtime safety flags."""
    runtime_result = load_runtime_flags(runtime_flags_file)
    if not runtime_result["ok"]:
        return {
            "ok": False,
            "records": [],
            "error": "运行时安全开关加载失败，禁止外部网络调用。",
        }

    flags = runtime_result["flags"]
    if not is_external_network_allowed(flags):
        return {
            "ok": False,
            "records": [],
            "error": "allow_external_network=false，禁止外部网络调用。",
        }

    if not is_real_market_data_allowed(flags):
        return {
            "ok": False,
            "records": [],
            "error": "allow_real_market_data=false，禁止真实行情数据。",
        }

    if not is_real_source_enabled(config):
        return {
            "ok": False,
            "records": [],
            "error": "真实数据源尚未启用。",
        }

    return {
        "ok": False,
        "records": [],
        "error": "当前阶段仍为只读客户端骨架，尚未实现真实外部数据请求。",
    }


def can_real_data_enter_ui(runtime_flags_file="config/runtime_flags.example.json"):
    """Only allow real data into UI when runtime flags explicitly allow it."""
    runtime_result = load_runtime_flags(runtime_flags_file)
    if not runtime_result["ok"]:
        return False
    return is_real_data_to_ui_allowed(runtime_result["flags"])


def can_real_data_auto_verified(runtime_flags_file="config/runtime_flags.example.json"):
    """Real data cannot be automatically marked as verified."""
    runtime_result = load_runtime_flags(runtime_flags_file)
    if not runtime_result["ok"]:
        return False
    return can_auto_mark_verified(runtime_result["flags"])


def explain_real_data_source_status(config):
    """Return a Chinese explanation of the current disabled source status."""
    enabled = is_real_source_enabled(config)
    selected_source = None
    enabled_status = "未启用"
    endpoint_status = "未配置"

    if isinstance(config, dict):
        selected_source = config.get("selected_source")
        selected_candidate = _get_selected_candidate(config)
        if selected_candidate:
            enabled_status = "已启用" if selected_candidate.get("enabled") is True else "未启用"
            endpoint_status = "已配置" if selected_candidate.get("endpoint_configured") is True else "未配置"

    if enabled:
        network_status = "仍需人工确认后才允许联网"
        conclusion_status = "人工确认前不允许进入真实市场结论"
    else:
        network_status = "真实数据源未启用，不允许联网"
        conclusion_status = "不允许进入真实市场结论"

    selected_status = "null" if selected_source is None else str(selected_source)

    return (
        f"当前是否启用真实数据源：{'是' if enabled else '否'}；"
        f"selected_source 状态：{selected_status}；"
        f"enabled 状态：{enabled_status}；"
        f"endpoint_configured 状态：{endpoint_status}；"
        f"当前是否允许联网：{network_status}；"
        f"当前是否允许进入真实市场结论：{conclusion_status}。"
    )
