"""SEC EDGAR data helpers.

Small, explicit client for SEC public JSON endpoints. Network reads happen only when
called from the UI; tests can pass fixture data directly and do not require network.
"""

from __future__ import annotations

from datetime import UTC, datetime
import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

SEC_COMPANY_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SEC_SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"
SEC_COMPANYFACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
DEFAULT_USER_AGENT = "us-stock-decision-system contact@example.com"
CORE_FACT_TAGS = (
    "Revenues",
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "NetIncomeLoss",
    "Assets",
    "Liabilities",
    "StockholdersEquity",
    "CashAndCashEquivalentsAtCarryingValue",
    "OperatingIncomeLoss",
)


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def normalize_ticker(ticker: Any) -> str:
    return str(ticker or "").strip().upper()


def normalize_cik(cik: Any) -> str:
    digits = "".join(ch for ch in str(cik or "") if ch.isdigit())
    return digits.zfill(10) if digits else ""


def build_submissions_url(cik: Any) -> str:
    return SEC_SUBMISSIONS_URL.format(cik=normalize_cik(cik))


def build_companyfacts_url(cik: Any) -> str:
    return SEC_COMPANYFACTS_URL.format(cik=normalize_cik(cik))


def fetch_json(url: str, user_agent: str = DEFAULT_USER_AGENT, timeout: int = 20) -> dict:
    request = Request(url, headers={"User-Agent": user_agent, "Accept-Encoding": "gzip, deflate", "Host": url.split("/")[2]})
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_company_tickers(user_agent: str = DEFAULT_USER_AGENT) -> dict:
    return fetch_json(SEC_COMPANY_TICKERS_URL, user_agent=user_agent)


def find_company_by_ticker(ticker: str, company_tickers: dict) -> dict:
    normalized = normalize_ticker(ticker)
    for row in company_tickers.values():
        if normalize_ticker(row.get("ticker")) == normalized:
            return {
                "ticker": normalized,
                "cik": normalize_cik(row.get("cik_str")),
                "company_name": row.get("title", ""),
            }
    return {"ticker": normalized, "cik": "", "company_name": ""}


def summarize_submissions(submissions: dict, limit: int = 8) -> list[dict]:
    recent = submissions.get("filings", {}).get("recent", {}) if isinstance(submissions, dict) else {}
    forms = recent.get("form", []) or []
    filing_dates = recent.get("filingDate", []) or []
    accession_numbers = recent.get("accessionNumber", []) or []
    primary_documents = recent.get("primaryDocument", []) or []
    rows = []
    for index, form in enumerate(forms):
        if form not in {"10-K", "10-Q", "8-K", "20-F", "40-F", "6-K"}:
            continue
        rows.append(
            {
                "form": form,
                "filing_date": filing_dates[index] if index < len(filing_dates) else "",
                "accession_number": accession_numbers[index] if index < len(accession_numbers) else "",
                "primary_document": primary_documents[index] if index < len(primary_documents) else "",
            }
        )
        if len(rows) >= limit:
            break
    return rows


def _latest_usd_fact(tag: str, fact_item: dict) -> dict:
    units = fact_item.get("units", {}) if isinstance(fact_item, dict) else {}
    facts = units.get("USD") or units.get("shares") or []
    if not isinstance(facts, list) or not facts:
        return {"tag": tag, "value": None, "end": "", "filed": "", "form": ""}
    sorted_facts = sorted(facts, key=lambda item: (item.get("filed", ""), item.get("end", "")), reverse=True)
    latest = sorted_facts[0]
    return {
        "tag": tag,
        "value": latest.get("val"),
        "end": latest.get("end", ""),
        "filed": latest.get("filed", ""),
        "form": latest.get("form", ""),
    }


def summarize_companyfacts(companyfacts: dict) -> list[dict]:
    facts = companyfacts.get("facts", {}).get("us-gaap", {}) if isinstance(companyfacts, dict) else {}
    rows = []
    for tag in CORE_FACT_TAGS:
        if tag in facts:
            rows.append(_latest_usd_fact(tag, facts[tag]))
    return rows


def build_company_snapshot(ticker: str, company_row: dict, submissions: dict, companyfacts: dict | None = None) -> dict:
    financial_facts = summarize_companyfacts(companyfacts or {})
    return {
        "ticker": normalize_ticker(ticker),
        "cik": company_row.get("cik", ""),
        "company_name": submissions.get("name") or company_row.get("company_name", ""),
        "sic": submissions.get("sic", ""),
        "sic_description": submissions.get("sicDescription", ""),
        "exchanges": submissions.get("exchanges", []),
        "tickers": submissions.get("tickers", []),
        "recent_filings": summarize_submissions(submissions),
        "financial_facts": financial_facts,
        "data_status": "待人工确认",
        "updated_at": utc_now_iso(),
    }


def fetch_sec_company_snapshot(ticker: str, user_agent: str = DEFAULT_USER_AGENT) -> dict:
    normalized = normalize_ticker(ticker)
    if not normalized:
        return {"ok": False, "error": "ticker 不能为空", "data_status": "数据不足", "updated_at": utc_now_iso()}
    try:
        company_tickers = fetch_company_tickers(user_agent=user_agent)
        company_row = find_company_by_ticker(normalized, company_tickers)
        cik = company_row.get("cik", "")
        if not cik:
            return {"ok": False, "ticker": normalized, "error": "未找到 CIK", "data_status": "数据不足", "updated_at": utc_now_iso()}
        submissions = fetch_json(build_submissions_url(cik), user_agent=user_agent)
        try:
            companyfacts = fetch_json(build_companyfacts_url(cik), user_agent=user_agent)
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
            companyfacts = {}
        snapshot = build_company_snapshot(normalized, company_row, submissions, companyfacts)
        return {"ok": True, "snapshot": snapshot, "error": ""}
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        return {"ok": False, "ticker": normalized, "error": str(exc), "data_status": "数据不足", "updated_at": utc_now_iso()}
