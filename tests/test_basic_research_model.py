import os
import sys


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.basic_research_model import build_candidate_summary, normalize_ticker, upsert_candidate, validate_candidate


def _candidate(**overrides):
    item = {
        "ticker": "lite",
        "company_name": "",
        "industry": "AI 光通信",
        "theme": "AI 光互连",
        "chain_layer": "核心零部件",
        "bottleneck_score": 4,
        "heat_status": "升温中",
        "capital_flow_status": "流入",
        "candidate_reason": "人工候选",
        "evidence_note": "待人工确认",
        "data_status": "待人工确认",
    }
    item.update(overrides)
    return item


def test_ticker_normalizes_uppercase():
    assert normalize_ticker(" lite ") == "LITE"


def test_required_fields_validate():
    assert validate_candidate(_candidate(ticker=""))["ok"] is False
    assert validate_candidate(_candidate(industry=""))["ok"] is False
    assert validate_candidate(_candidate(theme=""))["ok"] is False


def test_enum_fields_validate():
    assert validate_candidate(_candidate(chain_layer="错误层级"))["ok"] is False
    assert validate_candidate(_candidate(heat_status="错误热度"))["ok"] is False
    assert validate_candidate(_candidate(capital_flow_status="错误资金"))["ok"] is False
    assert validate_candidate(_candidate(data_status="错误状态"))["ok"] is False


def test_bottleneck_score_must_be_between_zero_and_five():
    assert validate_candidate(_candidate(bottleneck_score=-1))["ok"] is False
    assert validate_candidate(_candidate(bottleneck_score=6))["ok"] is False
    assert validate_candidate(_candidate(bottleneck_score=5))["ok"] is True


def test_upsert_candidate_updates_same_ticker_theme():
    first = _candidate(ticker="lite", theme="AI 光互连", bottleneck_score=3)
    second = _candidate(ticker="LITE", theme="AI 光互连", bottleneck_score=5)
    result = upsert_candidate([first], second)
    assert len(result) == 1
    assert result[0]["bottleneck_score"] == 5


def test_summary_counts_candidates():
    items = [
        _candidate(ticker="A", heat_status="高热度", capital_flow_status="流入"),
        _candidate(ticker="B", heat_status="过热", capital_flow_status="中性", data_status="数据不足"),
    ]
    summary = build_candidate_summary(items)
    assert summary["总候选数"] == 2
    assert summary["高热度数量"] == 1
    assert summary["过热数量"] == 1
    assert summary["资金流入数量"] == 1
    assert summary["数据不足数量"] == 1


def run_tests():
    test_ticker_normalizes_uppercase()
    test_required_fields_validate()
    test_enum_fields_validate()
    test_bottleneck_score_must_be_between_zero_and_five()
    test_upsert_candidate_updates_same_ticker_theme()
    test_summary_counts_candidates()


if __name__ == "__main__":
    run_tests()
    print("tests/test_basic_research_model.py passed")
