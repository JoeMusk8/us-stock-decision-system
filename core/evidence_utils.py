"""Evidence validation helpers.

This module only validates local records. It does not connect APIs, fetch data,
generate real data, or produce investment or trading conclusions.
"""

from core.data_status import is_data_usable_for_fact, is_valid_data_status


VALID_EVIDENCE_LEVELS = ("A", "B", "C", "D")


def has_evidence_id(record):
    """Return True when a record has a non-empty evidence_id."""
    if not isinstance(record, dict):
        return False
    evidence_id = record.get("evidence_id")
    return isinstance(evidence_id, str) and bool(evidence_id.strip())


def is_valid_evidence_level(level):
    """Return True when evidence_level is A / B / C / D."""
    return level in VALID_EVIDENCE_LEVELS


def is_social_or_kol_clue(record):
    """Return True for social/KOL clues or records explicitly marked clue_only."""
    if not isinstance(record, dict):
        return False
    return record.get("source_type") == "social_kol_clue" or record.get("clue_only") is True


def can_enter_fact_zone(record):
    """Return True only when an evidence record is allowed into the fact zone."""
    if not isinstance(record, dict):
        return False
    if not has_evidence_id(record):
        return False
    if not is_data_usable_for_fact(record.get("data_status")):
        return False
    if record.get("fact_allowed") is False:
        return False
    if is_social_or_kol_clue(record):
        return False
    return True


def validate_evidence_record(record):
    """Validate an evidence record and return a structured result."""
    errors = []

    if not isinstance(record, dict):
        return {"is_valid": False, "errors": ["record 必须是 dict"]}

    if not has_evidence_id(record):
        errors.append("缺少 evidence_id")

    if not is_valid_data_status(record.get("data_status")):
        errors.append("data_status 不合法")

    if not is_valid_evidence_level(record.get("evidence_level")):
        errors.append("evidence_level 不合法")

    if record.get("source_type") == "social_kol_clue" and record.get("clue_only") is not True:
        errors.append("social_kol_clue 必须设置 clue_only=true")

    if record.get("clue_only") is True and record.get("fact_allowed") is not False:
        errors.append("clue_only=true 时 fact_allowed 必须为 false")

    return {"is_valid": not errors, "errors": errors}


def claim_can_enter_fact_zone(claim):
    """Return True only for evidence-backed factual claims confirmed by support status."""
    if not isinstance(claim, dict):
        return False
    if not has_evidence_id(claim):
        return False
    if claim.get("support_status") != "已证实":
        return False
    if claim.get("claim_label") != "事实":
        return False
    return True
