"""Bridge paradigm-monitor themes into basic research industry/theme pool."""


def _clean(value):
    return str(value or "").strip()


def can_transfer_paradigm_to_basic(signal):
    if not _clean(signal.get("theme_name")):
        return {"ok": False, "reason": "theme_name 不能为空"}
    if signal.get("data_status") == "数据不足":
        return {"ok": True, "reason": "数据不足，可以转入，但需要基础投研验证"}
    return {"ok": True, "reason": "可以转入基础投研行业/主题池"}


def build_basic_industry_from_paradigm(signal):
    return _clean(signal.get("theme_name"))


def upsert_basic_industry(existing_industries, new_industry, max_count=3):
    industries = [_clean(item) for item in (existing_industries or []) if _clean(item)]
    value = _clean(new_industry)
    if not value:
        return industries[:max_count]
    if value in industries:
        return industries[:max_count]
    return (industries + [value])[:max_count]
