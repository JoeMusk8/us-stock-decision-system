import inspect
import os
import sys


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core import local_data_loader
from core.local_data_loader import (
    get_fact_allowed_records,
    load_evidence_items,
    load_json_file,
    validate_loaded_evidence,
)


def test_can_load_evidence_items_example():
    result = load_json_file("data/evidence_items.example.json")
    assert result["ok"] is True
    assert isinstance(result["data"], dict)
    assert result["error"] == ""


def test_load_evidence_items_returns_records():
    result = load_evidence_items()
    assert result["ok"] is True
    assert isinstance(result["records"], list)
    assert len(result["records"]) >= 1


def test_validate_loaded_evidence_summary_counts():
    records = load_evidence_items()["records"]
    result = validate_loaded_evidence(records)
    assert result["total"] == len(records)
    assert "valid_count" in result
    assert "invalid_count" in result
    assert isinstance(result["items"], list)


def test_example_data_cannot_enter_fact_zone():
    records = load_evidence_items()["records"]
    assert all(record["data_status"] == "示例数据" for record in records)
    assert get_fact_allowed_records(records) == []


def test_social_kol_clue_cannot_enter_fact_zone():
    records = load_evidence_items()["records"]
    social_records = [record for record in records if record.get("source_type") == "social_kol_clue"]
    assert social_records
    assert get_fact_allowed_records(social_records) == []


def test_missing_file_does_not_crash():
    result = load_json_file("data/not_exists.example.json")
    assert result["ok"] is False
    assert result["data"] == {}
    assert result["error"]


def test_no_external_network_calls():
    source = inspect.getsource(local_data_loader)
    forbidden_tokens = ("requests", "urllib", "http://", "https://", "socket", "aiohttp")
    assert not any(token in source for token in forbidden_tokens)


def run_tests():
    test_can_load_evidence_items_example()
    test_load_evidence_items_returns_records()
    test_validate_loaded_evidence_summary_counts()
    test_example_data_cannot_enter_fact_zone()
    test_social_kol_clue_cannot_enter_fact_zone()
    test_missing_file_does_not_crash()
    test_no_external_network_calls()


if __name__ == "__main__":
    run_tests()
    print("tests/test_local_data_loader.py passed")
