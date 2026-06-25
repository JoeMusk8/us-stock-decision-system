import os
import sys


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.data_status import (
    get_data_status_label,
    is_data_usable_for_fact,
    is_valid_data_status,
    normalize_data_status,
)
from core.evidence_utils import (
    can_enter_fact_zone,
    claim_can_enter_fact_zone,
    validate_evidence_record,
)


def test_verified_record_can_enter_fact_zone():
    record = {
        "evidence_id": "EVID-TEST-001",
        "data_status": "已验证",
        "evidence_level": "A",
        "source_type": "official_disclosure",
        "clue_only": False,
        "fact_allowed": True,
    }
    assert can_enter_fact_zone(record) is True


def test_missing_evidence_id_cannot_enter_fact_zone():
    record = {
        "evidence_id": "",
        "data_status": "已验证",
        "evidence_level": "A",
        "source_type": "official_disclosure",
        "clue_only": False,
        "fact_allowed": True,
    }
    assert can_enter_fact_zone(record) is False


def test_example_data_cannot_enter_fact_zone():
    record = {
        "evidence_id": "EVID-TEST-002",
        "data_status": "示例数据",
        "evidence_level": "B",
        "source_type": "official_disclosure",
        "clue_only": False,
        "fact_allowed": True,
    }
    assert can_enter_fact_zone(record) is False


def test_social_kol_clue_cannot_enter_fact_zone():
    record = {
        "evidence_id": "EVID-TEST-003",
        "data_status": "已验证",
        "evidence_level": "D",
        "source_type": "social_kol_clue",
        "clue_only": True,
        "fact_allowed": False,
    }
    assert can_enter_fact_zone(record) is False


def test_clue_only_requires_fact_allowed_false():
    record = {
        "evidence_id": "EVID-TEST-004",
        "data_status": "已验证",
        "evidence_level": "D",
        "source_type": "social_kol_clue",
        "clue_only": True,
        "fact_allowed": True,
    }
    result = validate_evidence_record(record)
    assert result["is_valid"] is False
    assert "clue_only=true 时 fact_allowed 必须为 false" in result["errors"]


def test_claim_without_evidence_id_cannot_enter_fact_zone():
    claim = {
        "evidence_id": "",
        "claim_label": "事实",
        "support_status": "已证实",
    }
    assert claim_can_enter_fact_zone(claim) is False


def test_non_fact_claim_cannot_enter_fact_zone():
    claim = {
        "evidence_id": "EVID-CLAIM-001",
        "claim_label": "推断",
        "support_status": "已证实",
    }
    assert claim_can_enter_fact_zone(claim) is False


def test_unconfirmed_claim_cannot_enter_fact_zone():
    claim = {
        "evidence_id": "EVID-CLAIM-002",
        "claim_label": "事实",
        "support_status": "部分支持",
    }
    assert claim_can_enter_fact_zone(claim) is False


def test_data_status_helpers():
    assert is_valid_data_status("已验证") is True
    assert is_valid_data_status("未知") is False
    assert normalize_data_status("") == "数据不足"
    assert normalize_data_status("待人工确认") == "待人工确认"
    assert is_data_usable_for_fact("已验证") is True
    assert is_data_usable_for_fact("待人工确认") is False
    assert get_data_status_label("未知") == "数据不足"


def run_tests():
    test_verified_record_can_enter_fact_zone()
    test_missing_evidence_id_cannot_enter_fact_zone()
    test_example_data_cannot_enter_fact_zone()
    test_social_kol_clue_cannot_enter_fact_zone()
    test_clue_only_requires_fact_allowed_false()
    test_claim_without_evidence_id_cannot_enter_fact_zone()
    test_non_fact_claim_cannot_enter_fact_zone()
    test_unconfirmed_claim_cannot_enter_fact_zone()
    test_data_status_helpers()


if __name__ == "__main__":
    run_tests()
    print("tests/test_evidence_utils.py passed")
