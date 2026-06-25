"""Runtime safety flags for real data access.

This module only reads local runtime flag files and validates safe defaults. It
does not connect to APIs, call external networks, or enable real market data.
"""

import json
from pathlib import Path


REQUIRED_FLAG_KEYS = (
    "allow_external_network",
    "allow_real_market_data",
    "allow_real_data_to_ui",
    "allow_auto_verified_status",
    "allow_trading",
    "allow_order_execution",
    "allow_investment_advice",
)


def load_runtime_flags(file_path="config/runtime_flags.example.json"):
    """Load local runtime flags from JSON."""
    path = Path(file_path)
    if not path.exists():
        return {"ok": False, "flags": {}, "rules": {}, "error": f"文件不存在：{file_path}"}

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as exc:
        return {"ok": False, "flags": {}, "rules": {}, "error": f"JSON 格式错误：{exc}"}
    except OSError as exc:
        return {"ok": False, "flags": {}, "rules": {}, "error": f"读取失败：{exc}"}

    if not isinstance(data, dict):
        return {"ok": False, "flags": {}, "rules": {}, "error": "配置文件顶层必须是 dict"}

    flags = data.get("flags", {})
    rules = data.get("rules", {})
    if not isinstance(flags, dict):
        return {"ok": False, "flags": {}, "rules": {}, "error": "flags 必须是 dict"}
    if not isinstance(rules, dict):
        return {"ok": False, "flags": {}, "rules": {}, "error": "rules 必须是 dict"}

    return {"ok": True, "flags": flags, "rules": rules, "error": ""}


def is_external_network_allowed(flags):
    """Only allow external network access when explicitly true."""
    return isinstance(flags, dict) and flags.get("allow_external_network") is True


def is_real_market_data_allowed(flags):
    """Only allow real market data when explicitly true."""
    return isinstance(flags, dict) and flags.get("allow_real_market_data") is True


def is_real_data_to_ui_allowed(flags):
    """Only allow real data into UI when explicitly true."""
    return isinstance(flags, dict) and flags.get("allow_real_data_to_ui") is True


def can_auto_mark_verified(flags):
    """Real data cannot be automatically marked as verified."""
    return False


def validate_runtime_flags(flags):
    """Validate safe runtime flag defaults."""
    errors = []
    if not isinstance(flags, dict):
        return {"ok": False, "errors": ["flags 必须是 dict"]}

    for key in REQUIRED_FLAG_KEYS:
        if key not in flags:
            errors.append(f"缺少开关：{key}")
        elif not isinstance(flags[key], bool):
            errors.append(f"{key} 必须是 bool")

    if flags.get("allow_trading") is not False:
        errors.append("allow_trading 必须为 false")

    if flags.get("allow_order_execution") is not False:
        errors.append("allow_order_execution 必须为 false")

    if flags.get("allow_investment_advice") is not False:
        errors.append("allow_investment_advice 必须为 false")

    if is_external_network_allowed(flags):
        errors.append("默认状态不得允许外部网络")

    if is_real_data_to_ui_allowed(flags):
        errors.append("默认状态不得允许真实行情进入 UI")

    if flags.get("allow_auto_verified_status") is not False:
        errors.append("allow_auto_verified_status 必须为 false")

    return {"ok": not errors, "errors": errors}
