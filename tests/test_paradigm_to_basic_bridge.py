import os
import sys


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.paradigm_to_basic_bridge import (
    build_basic_industry_from_paradigm,
    can_transfer_paradigm_to_basic,
    upsert_basic_industry,
)


def _signal(**overrides):
    item = {
        "theme_name": "AI 光互连",
        "data_status": "待人工确认",
    }
    item.update(overrides)
    return item


def test_transfer_requires_theme_name():
    assert can_transfer_paradigm_to_basic(_signal(theme_name=""))["ok"] is False


def test_insufficient_data_can_transfer_with_warning():
    result = can_transfer_paradigm_to_basic(_signal(data_status="数据不足"))
    assert result["ok"] is True
    assert "需要基础投研验证" in result["reason"]


def test_build_basic_industry_from_theme():
    assert build_basic_industry_from_paradigm(_signal(theme_name=" AI 光互连 ")) == "AI 光互连"


def test_upsert_basic_industry_limits_to_three_and_dedupes():
    result = upsert_basic_industry(["A", "B", "C"], "A")
    assert result == ["A", "B", "C"]
    result = upsert_basic_industry(["A", "B", "C"], "D")
    assert result == ["A", "B", "C"]
    result = upsert_basic_industry(["A", "B"], "C")
    assert result == ["A", "B", "C"]


def run_tests():
    test_transfer_requires_theme_name()
    test_insufficient_data_can_transfer_with_warning()
    test_build_basic_industry_from_theme()
    test_upsert_basic_industry_limits_to_three_and_dedupes()


if __name__ == "__main__":
    run_tests()
    print("tests/test_paradigm_to_basic_bridge.py passed")
