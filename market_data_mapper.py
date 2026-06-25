"""Draft market data field mappers.

This module does not fetch data, call networks, generate market data, or make
trading decisions. It only maps future external records into the local standard
field shape for manual review.
"""

from core.data_status import is_valid_data_status


DEFAULT_MAPPED_STATUS = "待人工确认"
MAPPING_DRAFT_NOTE = "字段映射草案，尚未人工确认。"

MARKET_FUND_STANDARD_FIELDS = (
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

MARKET_SENTIMENT_STANDARD_FIELDS = (
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

FORBIDDEN_MAPPED_FIELDS = ("20日" + "涨跌幅", "50日" + "涨跌幅")


def _safe_get(raw_record, field_name):
    if not isinstance(raw_record, dict):
        return None
    return raw_record.get(field_name)


def _missing_fields(record, required_fields):
    if not isinstance(record, dict):
        return list(required_fields)
    return [field for field in required_fields if field not in record]


def _has_forbidden_fields(record):
    if not isinstance(record, dict):
        return False
    return any(field in record for field in FORBIDDEN_MAPPED_FIELDS)


def map_market_fund_record(raw_record, source_name="", source_type="external_market_data"):
    """Map future external market fund data into standard local fields."""
    return {
        "symbol": _safe_get(raw_record, "symbol"),
        "asset_name": _safe_get(raw_record, "asset_name"),
        "asset_type": _safe_get(raw_record, "asset_type"),
        "current_price": _safe_get(raw_record, "current_price"),
        "ma_20": _safe_get(raw_record, "ma_20"),
        "ma_50": _safe_get(raw_record, "ma_50"),
        "ma_20_direction": _safe_get(raw_record, "ma_20_direction"),
        "ma_50_direction": _safe_get(raw_record, "ma_50_direction"),
        "volume": _safe_get(raw_record, "volume"),
        "relative_volume": _safe_get(raw_record, "relative_volume"),
        "above_ma20": _safe_get(raw_record, "above_ma20"),
        "above_ma50": _safe_get(raw_record, "above_ma50"),
        "stronger_than_benchmark": _safe_get(raw_record, "stronger_than_benchmark"),
        "risk_appetite_spread": _safe_get(raw_record, "risk_appetite_spread"),
        "source_name": source_name,
        "source_type": source_type,
        "data_status": DEFAULT_MAPPED_STATUS,
        "updated_at": _safe_get(raw_record, "updated_at"),
        "note": MAPPING_DRAFT_NOTE,
    }


def map_market_sentiment_record(raw_record, source_name="", source_type="external_market_sentiment"):
    """Map future external market sentiment data into standard local fields."""
    return {
        "indicator_id": _safe_get(raw_record, "indicator_id"),
        "indicator_name": _safe_get(raw_record, "indicator_name"),
        "indicator_type": _safe_get(raw_record, "indicator_type"),
        "current_value": _safe_get(raw_record, "current_value"),
        "current_status": _safe_get(raw_record, "current_status"),
        "risk_meaning": _safe_get(raw_record, "risk_meaning"),
        "direction": _safe_get(raw_record, "direction"),
        "source_name": source_name,
        "source_type": source_type,
        "data_status": DEFAULT_MAPPED_STATUS,
        "updated_at": _safe_get(raw_record, "updated_at"),
        "note": MAPPING_DRAFT_NOTE,
    }


def validate_mapped_market_fund_record(record):
    """Validate a mapped market fund record's local field shape."""
    errors = []
    if not isinstance(record, dict):
        return {"is_valid": False, "errors": ["record 必须是 dict"]}

    missing = _missing_fields(record, MARKET_FUND_STANDARD_FIELDS)
    if missing:
        errors.append(f"缺少字段：{', '.join(missing)}")

    if not is_valid_data_status(record.get("data_status")):
        errors.append("data_status 不合法")

    if _has_forbidden_fields(record):
        errors.append("包含已禁用字段")

    return {"is_valid": not errors, "errors": errors}


def validate_mapped_market_sentiment_record(record):
    """Validate a mapped market sentiment record's local field shape."""
    errors = []
    if not isinstance(record, dict):
        return {"is_valid": False, "errors": ["record 必须是 dict"]}

    missing = _missing_fields(record, MARKET_SENTIMENT_STANDARD_FIELDS)
    if missing:
        errors.append(f"缺少字段：{', '.join(missing)}")

    if not is_valid_data_status(record.get("data_status")):
        errors.append("data_status 不合法")

    if _has_forbidden_fields(record):
        errors.append("包含已禁用字段")

    return {"is_valid": not errors, "errors": errors}


def can_mark_mapped_record_verified(record):
    """Mapped records cannot become verified automatically."""
    return False
