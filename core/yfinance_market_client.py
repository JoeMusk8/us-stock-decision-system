"""Minimal yfinance client for market environment data.

Only market environment symbols are supported: QQQ, ^IXIC, BTC-USD, and ^VIX.
The first real-data status is 待人工确认. Missing or failed data is reported as
数据不足 without synthetic fallback values.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


MARKET_FUND_SYMBOLS = {
    "QQQ": {"asset_name": "QQQ", "asset_type": "ETF"},
    "^IXIC": {"asset_name": "纳斯达克指数", "asset_type": "指数"},
    "BTC-USD": {"asset_name": "比特币", "asset_type": "加密资产"},
}

VIX_SYMBOL = "^VIX"
DATA_STATUS_PENDING_REVIEW = "待人工确认"
DATA_STATUS_INSUFFICIENT = "数据不足"


@dataclass(frozen=True)
class MovingAverageResult:
    current_price: float | None
    ma_20: float | None
    ma_50: float | None
    ma_20_direction: str | None
    ma_50_direction: str | None
    volume: float | None
    relative_volume: float | None
    above_ma20: bool | None
    above_ma50: bool | None


def _round_number(value):
    if value is None:
        return None
    return round(float(value), 4)


def _last_valid(series):
    cleaned = pd.to_numeric(series, errors="coerce").dropna()
    if cleaned.empty:
        return None
    return float(cleaned.iloc[-1])


def _direction(current_value, previous_value):
    if current_value is None or previous_value is None:
        return None
    if current_value > previous_value:
        return "向上"
    if current_value < previous_value:
        return "向下"
    return "走平"


def _normalize_history(history):
    if history is None or history.empty:
        return pd.DataFrame()

    normalized = history.copy()
    if isinstance(normalized.columns, pd.MultiIndex):
        normalized.columns = normalized.columns.get_level_values(0)

    return normalized


def calculate_market_fund_metrics(history):
    """Calculate market fund metrics from local dataframe data."""
    normalized = _normalize_history(history)
    if normalized.empty or "Close" not in normalized:
        return MovingAverageResult(None, None, None, None, None, None, None, None, None)

    close = pd.to_numeric(normalized["Close"], errors="coerce").dropna()
    if len(close) < 50:
        return MovingAverageResult(None, None, None, None, None, None, None, None, None)

    ma20_series = close.rolling(20).mean().dropna()
    ma50_series = close.rolling(50).mean().dropna()
    current_price = _last_valid(close)
    ma_20 = _last_valid(ma20_series)
    ma_50 = _last_valid(ma50_series)
    previous_ma_20 = float(ma20_series.iloc[-2]) if len(ma20_series) >= 2 else None
    previous_ma_50 = float(ma50_series.iloc[-2]) if len(ma50_series) >= 2 else None

    volume = None
    relative_volume = None
    if "Volume" in normalized:
        volume_series = pd.to_numeric(normalized["Volume"], errors="coerce").dropna()
        if not volume_series.empty:
            volume = float(volume_series.iloc[-1])
            volume_average = volume_series.tail(20).mean() if len(volume_series) >= 20 else None
            if volume_average and volume_average > 0:
                relative_volume = volume / float(volume_average)

    return MovingAverageResult(
        current_price=_round_number(current_price),
        ma_20=_round_number(ma_20),
        ma_50=_round_number(ma_50),
        ma_20_direction=_direction(ma_20, previous_ma_20),
        ma_50_direction=_direction(ma_50, previous_ma_50),
        volume=_round_number(volume),
        relative_volume=_round_number(relative_volume),
        above_ma20=None if current_price is None or ma_20 is None else current_price > ma_20,
        above_ma50=None if current_price is None or ma_50 is None else current_price > ma_50,
    )


def _market_fund_record(symbol, history):
    meta = MARKET_FUND_SYMBOLS[symbol]
    metrics = calculate_market_fund_metrics(history)
    metric_values = (
        metrics.current_price,
        metrics.ma_20,
        metrics.ma_50,
        metrics.ma_20_direction,
        metrics.ma_50_direction,
        metrics.volume,
        metrics.relative_volume,
        metrics.above_ma20,
        metrics.above_ma50,
    )
    has_all_required_values = all(value is not None for value in metric_values)
    data_status = DATA_STATUS_PENDING_REVIEW if has_all_required_values else DATA_STATUS_INSUFFICIENT

    return {
        "symbol": symbol,
        "asset_name": meta["asset_name"],
        "asset_type": meta["asset_type"],
        "current_price": metrics.current_price,
        "ma_20": metrics.ma_20,
        "ma_50": metrics.ma_50,
        "ma_20_direction": metrics.ma_20_direction,
        "ma_50_direction": metrics.ma_50_direction,
        "volume": metrics.volume,
        "relative_volume": metrics.relative_volume,
        "above_ma20": metrics.above_ma20,
        "above_ma50": metrics.above_ma50,
        "stronger_than_benchmark": None,
        "risk_appetite_spread": None,
        "source_name": "yfinance",
        "source_type": "external_market_data",
        "data_status": data_status,
        "updated_at": "",
        "note": "真实行情读取，首次状态需人工确认。" if data_status == DATA_STATUS_PENDING_REVIEW else DATA_STATUS_INSUFFICIENT,
    }


def _sentiment_record(history):
    normalized = _normalize_history(history)
    current_value = None
    if not normalized.empty and "Close" in normalized:
        current_value = _round_number(_last_valid(normalized["Close"]))

    data_status = DATA_STATUS_PENDING_REVIEW if current_value is not None else DATA_STATUS_INSUFFICIENT
    return {
        "indicator_id": VIX_SYMBOL,
        "indicator_name": "VIX",
        "indicator_type": "market_volatility",
        "current_value": current_value,
        "current_status": DATA_STATUS_INSUFFICIENT,
        "risk_meaning": "市场波动率观察",
        "direction": DATA_STATUS_INSUFFICIENT,
        "source_name": "yfinance",
        "source_type": "external_market_sentiment",
        "data_status": data_status,
        "updated_at": "",
        "note": "真实行情读取，首次状态需人工确认。" if data_status == DATA_STATUS_PENDING_REVIEW else DATA_STATUS_INSUFFICIENT,
    }


def _download_history(yf, symbol):
    return yf.download(
        symbol,
        period="90d",
        interval="1d",
        progress=False,
        auto_adjust=False,
        threads=False,
    )


def fetch_market_environment_data():
    """Fetch minimal real market environment data from yfinance."""
    try:
        import yfinance as yf
    except ImportError:
        return {
            "ok": False,
            "market_funds": [],
            "market_sentiment": [],
            "error": "缺少 yfinance，请运行 python -m pip install -r requirements.txt",
            "errors": [],
        }

    market_funds = []
    market_sentiment = []
    errors = []

    for symbol in MARKET_FUND_SYMBOLS:
        try:
            history = _download_history(yf, symbol)
            record = _market_fund_record(symbol, history)
        except Exception as exc:
            record = _market_fund_record(symbol, pd.DataFrame())
            record["note"] = DATA_STATUS_INSUFFICIENT
            errors.append(f"{symbol}: {exc}")
        market_funds.append(record)

    try:
        vix_history = _download_history(yf, VIX_SYMBOL)
        market_sentiment.append(_sentiment_record(vix_history))
    except Exception as exc:
        market_sentiment.append(_sentiment_record(pd.DataFrame()))
        errors.append(f"{VIX_SYMBOL}: {exc}")

    ok = bool(market_funds) and bool(market_sentiment) and not all(
        record.get("data_status") == DATA_STATUS_INSUFFICIENT
        for record in market_funds + market_sentiment
    )

    return {
        "ok": ok,
        "market_funds": market_funds,
        "market_sentiment": market_sentiment,
        "error": "" if ok else DATA_STATUS_INSUFFICIENT,
        "errors": errors,
    }
