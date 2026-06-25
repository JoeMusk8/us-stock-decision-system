"""Market environment heuristic rules.

The rules produce market environment status only. They do not create trading
instructions, individual security recommendations, or price targets.
"""

DATA_STATUS_INSUFFICIENT = "数据不足"
STATUS_SUPPORT = "支持"
STATUS_CAUTION = "谨慎"
STATUS_WEAK = "不支持"


def _is_valid_fund_record(record):
    required_values = [
        record.get("current_price"),
        record.get("ma_20"),
        record.get("ma_50"),
        record.get("above_ma20"),
        record.get("above_ma50"),
        record.get("ma_20_direction"),
        record.get("ma_50_direction"),
    ]
    return record.get("data_status") != DATA_STATUS_INSUFFICIENT and all(value is not None for value in required_values)


def _fund_asset_status(record):
    if not _is_valid_fund_record(record):
        return DATA_STATUS_INSUFFICIENT

    above_both = record.get("above_ma20") is True and record.get("above_ma50") is True
    below_any = record.get("above_ma20") is False or record.get("above_ma50") is False
    weak_direction = record.get("ma_20_direction") == "向下" or record.get("ma_50_direction") == "向下"

    if above_both and not weak_direction:
        return STATUS_SUPPORT
    if below_any:
        return STATUS_WEAK
    return STATUS_CAUTION


def evaluate_market_funds(market_funds):
    asset_statuses = [_fund_asset_status(record) for record in market_funds]
    support_count = asset_statuses.count(STATUS_SUPPORT)
    caution_count = asset_statuses.count(STATUS_CAUTION)
    weak_count = asset_statuses.count(STATUS_WEAK)
    insufficient_count = asset_statuses.count(DATA_STATUS_INSUFFICIENT)
    valid_count = len(asset_statuses) - insufficient_count

    if valid_count < 2:
        status = DATA_STATUS_INSUFFICIENT
        reason = "有效市场资金数据少于 2 个，当前只能判定为市场环境状态：数据不足。"
    elif weak_count >= 2:
        status = STATUS_WEAK
        reason = "多数资产跌破 20日均线或 50日均线，市场环境状态：不支持。"
    elif support_count >= 2 and weak_count == 0:
        status = STATUS_SUPPORT
        reason = "多数资产站上 20日均线和 50日均线，且均线方向没有明显转弱，市场环境状态：支持。"
    else:
        status = STATUS_CAUTION
        reason = "部分资产站上均线或方向不一致，市场环境状态：谨慎。"

    return {
        "status": status,
        "reason": reason,
        "support_count": support_count,
        "caution_count": caution_count,
        "weak_count": weak_count,
        "insufficient_count": insufficient_count,
    }


def evaluate_market_sentiment(market_sentiment):
    record = market_sentiment[0] if market_sentiment else {}
    vix_value = record.get("current_value")

    if vix_value is None or record.get("data_status") == DATA_STATUS_INSUFFICIENT:
        return {
            "status": DATA_STATUS_INSUFFICIENT,
            "reason": "VIX 数据缺失，当前市场情绪状态：数据不足。",
            "vix_value": None,
        }

    if vix_value < 18:
        status = STATUS_SUPPORT
        reason = "VIX 低于 18，市场情绪状态：支持。"
    elif vix_value < 25:
        status = STATUS_CAUTION
        reason = "VIX 位于 18 到 25 区间，市场情绪状态：谨慎。"
    else:
        status = STATUS_WEAK
        reason = "VIX 高于或等于 25，市场情绪状态：不支持。"

    return {
        "status": status,
        "reason": reason,
        "vix_value": vix_value,
    }


def evaluate_overall_market_environment(market_funds, market_sentiment):
    funds_result = evaluate_market_funds(market_funds)
    sentiment_result = evaluate_market_sentiment(market_sentiment)
    funds_status = funds_result["status"]
    sentiment_status = sentiment_result["status"]

    if funds_status == STATUS_SUPPORT and sentiment_status == STATUS_SUPPORT:
        status = STATUS_SUPPORT
        reason = "市场资金和市场情绪均为支持，整体市场环境状态：支持。"
    elif funds_status == STATUS_WEAK or sentiment_status == STATUS_WEAK:
        status = STATUS_WEAK
        reason = "市场资金或市场情绪存在不支持项，整体市场环境状态：不支持。"
    elif funds_status == DATA_STATUS_INSUFFICIENT and sentiment_status == DATA_STATUS_INSUFFICIENT:
        status = DATA_STATUS_INSUFFICIENT
        reason = "市场资金和市场情绪均数据不足，整体市场环境状态：数据不足。"
    elif funds_status == DATA_STATUS_INSUFFICIENT or sentiment_status == DATA_STATUS_INSUFFICIENT:
        status = STATUS_CAUTION
        reason = "市场资金或市场情绪存在数据不足，整体市场环境状态：谨慎，需等待人工确认。"
    else:
        status = STATUS_CAUTION
        reason = "市场资金和市场情绪未形成一致支持，整体市场环境状态：谨慎。"

    return {
        "status": status,
        "reason": reason,
        "funds_status": funds_status,
        "sentiment_status": sentiment_status,
    }
