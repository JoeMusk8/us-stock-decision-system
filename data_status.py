"""Data status helpers for local validation.

These helpers do not fetch data and do not decide investment actions. They only
normalize and validate local data status values.
"""

VALID_DATA_STATUSES = (
    "待配置",
    "示例数据",
    "数据不足",
    "已验证",
    "待人工确认",
)


def is_valid_data_status(status):
    """Return True when status is one of the allowed data_status values."""
    return status in VALID_DATA_STATUSES


def normalize_data_status(status):
    """Return a valid status, falling back to 数据不足 for empty or unknown input."""
    if is_valid_data_status(status):
        return status
    return "数据不足"


def is_data_usable_for_fact(status):
    """Only verified data can enter the fact zone."""
    return normalize_data_status(status) == "已验证"


def get_data_status_label(status):
    """Return the Chinese UI label for a data_status value."""
    return normalize_data_status(status)
