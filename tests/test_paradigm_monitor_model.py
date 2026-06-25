import os
import sys


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.paradigm_monitor_model import (
    build_paradigm_summary,
    normalize_paradigm_signal,
    upsert_paradigm_signal,
    validate_paradigm_signal,
)


def _signal(**overrides):
    item = {
        "theme_name": "AI 光互连",
        "source_type": "人工输入",
        "signal_type": "新技术词",
        "signal_strength": "中",
        "summary": "人工记录",
        "evidence_note": "待人工确认",
        "data_status": "待人工确认",
    }
    item.update(overrides)
    return item


def test_normalize_theme_name_strips_text():
    assert normalize_paradigm_signal(_signal(theme_name=" AI 光互连 "))["theme_name"] == "AI 光互连"


def test_required_theme_name():
    assert validate_paradigm_signal(_signal(theme_name=""))["ok"] is False


def test_enum_fields_validate():
    assert validate_paradigm_signal(_signal(source_type="错误"))["ok"] is False
    assert validate_paradigm_signal(_signal(signal_type="错误"))["ok"] is False
    assert validate_paradigm_signal(_signal(signal_strength="错误"))["ok"] is False
    assert validate_paradigm_signal(_signal(data_status="错误"))["ok"] is False


def test_upsert_same_theme_updates_without_duplicate():
    first = _signal(theme_name="AI 光互连", signal_strength="弱")
    second = _signal(theme_name="AI 光互连", signal_strength="强")
    result = upsert_paradigm_signal([first], second)
    assert len(result) == 1
    assert result[0]["signal_strength"] == "强"


def test_summary_counts_signals():
    summary = build_paradigm_summary([
        _signal(theme_name="A", signal_strength="强"),
        _signal(theme_name="B", signal_strength="弱", data_status="数据不足"),
    ])
    assert summary["总主题数"] == 2
    assert summary["强信号数量"] == 1
    assert summary["弱信号数量"] == 1
    assert summary["数据不足数量"] == 1


def run_tests():
    test_normalize_theme_name_strips_text()
    test_required_theme_name()
    test_enum_fields_validate()
    test_upsert_same_theme_updates_without_duplicate()
    test_summary_counts_signals()


if __name__ == "__main__":
    run_tests()
    print("tests/test_paradigm_monitor_model.py passed")
