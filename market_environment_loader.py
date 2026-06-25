"""Local market environment mock loader and validators.

This module only reads local mock files. It does not connect APIs, call
external networks, generate real market data, or make trading decisions.
"""

from core.data_status import is_data_usable_for_fact, is_valid_data_status
from core.local_data_loader import load_json_file


MARKET_FUND_REQUIRED_FIELDS = (
    "symbol",
    "asset_name",
    "asset_type",
    "current_price",
    "ma_20",
    "ma_50",
    "ma_20_direction",
    "ma_50_direction",
    "volume",
    "relative_volume",
    "above_ma20",
    "above_ma50",
    "stronger_than_benchmark",
    "risk_appetite_spread",
    "source_name",
    "source_type",
    "data_status",
    "updated_at",
    "note",
)

MARKET_SENTIMENT_REQUIRED_FIELDS = (
    "indicator_id",
    "indicator_name",
    "indicator_type",
    "current_value",
    "current_status",
    "risk_meaning",
    "direction",
    "source_name",
    "source_type",
    "data_status",
    "updated_at",
    "note",
)

FORBIDDEN_MARKET_FUND_FIELDS = ("20日" + "涨跌幅", "50日" + "涨跌幅")


def load_market_environment_mock(file_path="data/market_environment_mock.example.json"):
    """Read the local market environment mock JSON file."""
    result = load_json_file(file_path)
    if not result["ok"]:
        return {"ok": False, "market_funds": [], "market_sentiment": [], "error": result["error"]}

    data = result["data"]
    market_funds = data.get("market_funds", [])
    market_sentiment = data.get("market_sentiment", [])

    if not isinstance(market_funds, list):
        return {"ok": False, "market_funds": [], "market_sentiment": [], "error": "market_funds 必须是 list"}
    if not isinstance(market_sentiment, list):
        return {"ok": False, "market_funds": [], "market_sentiment": [], "error": "market_sentiment 必须是 list"}

    return {
        "ok": True,
        "market_funds": market_funds,
        "market_sentiment": market_sentiment,
        "error": "",
    }


def _missing_fields(record, required_fields):
    if not isinstance(record, dict):
        return list(required_fields)
    return [field for field in required_fields if field not in record]


def validate_market_fund_record(record):
    """Validate one market_funds record."""
    errors = []
    if not isinstance(record, dict):
        return {"is_valid": False, "errors": ["record 必须是 dict"]}

    missing = _missing_fields(record, MARKET_FUND_REQUIRED_FIELDS)
    if missing:
        errors.append(f"缺少字段：{', '.join(missing)}")

    if not is_valid_data_status(record.get("data_status")):
        errors.append("data_status 不合法")

    for field in FORBIDDEN_MARKET_FUND_FIELDS:
        if field in record:
            errors.append("包含禁用涨跌幅字段")

    return {"is_valid": not errors, "errors": errors}


def validate_market_sentiment_record(record):
    """Validate one market_sentiment record."""
    errors = []
    if not isinstance(record, dict):
        return {"is_valid": False, "errors": ["record 必须是 dict"]}

    missing = _missing_fields(record, MARKET_SENTIMENT_REQUIRED_FIELDS)
    if missing:
        errors.append(f"缺少字段：{', '.join(missing)}")

    if not is_valid_data_status(record.get("data_status")):
        errors.append("data_status 不合法")

    return {"is_valid": not errors, "errors": errors}


def validate_market_environment_data(data):
    """Validate complete market environment mock data."""
    errors = []
    if not isinstance(data, dict):
        return {"ok": False, "market_funds_total": 0, "market_sentiment_total": 0, "errors": ["data 必须是 dict"]}

    market_funds = data.get("market_funds", [])
    market_sentiment = data.get("market_sentiment", [])

    if not isinstance(market_funds, list):
        errors.append("market_funds 必须是 list")
        market_funds = []
    if not isinstance(market_sentiment, list):
        errors.append("market_sentiment 必须是 list")
        market_sentiment = []

    for index, record in enumerate(market_funds, start=1):
        result = validate_market_fund_record(record)
        if not result["is_valid"]:
            errors.append(f"market_funds[{index}]：{'; '.join(result['errors'])}")

    for index, record in enumerate(market_sentiment, start=1):
        result = validate_market_sentiment_record(record)
        if not result["is_valid"]:
            errors.append(f"market_sentiment[{index}]：{'; '.join(result['errors'])}")

    return {
        "ok": not errors,
        "market_funds_total": len(market_funds),
        "market_sentiment_total": len(market_sentiment),
        "errors": errors,
    }


def can_enter_market_conclusion(record):
    """Only verified data can enter market environment conclusions."""
    if not isinstance(record, dict):
        return False
    return is_data_usable_for_fact(record.get("data_status"))
