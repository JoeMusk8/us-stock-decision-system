from core.sec_edgar_client import (
    build_company_snapshot,
    build_companyfacts_url,
    build_submissions_url,
    find_company_by_ticker,
    normalize_cik,
    normalize_ticker,
    summarize_companyfacts,
    summarize_submissions,
)


def test_normalize_ticker_and_cik():
    assert normalize_ticker(" aapl ") == "AAPL"
    assert normalize_cik(320193) == "0000320193"
    assert build_submissions_url(320193).endswith("CIK0000320193.json")
    assert build_companyfacts_url("320193").endswith("CIK0000320193.json")


def test_find_company_by_ticker():
    rows = {"0": {"ticker": "AAPL", "cik_str": 320193, "title": "Apple Inc."}}
    result = find_company_by_ticker("aapl", rows)
    assert result["ticker"] == "AAPL"
    assert result["cik"] == "0000320193"
    assert result["company_name"] == "Apple Inc."


def test_summarize_submissions_filters_core_forms():
    submissions = {
        "filings": {
            "recent": {
                "form": ["4", "10-K", "10-Q"],
                "filingDate": ["2026-01-01", "2026-02-01", "2026-03-01"],
                "accessionNumber": ["a", "b", "c"],
                "primaryDocument": ["a.htm", "b.htm", "c.htm"],
            }
        }
    }
    rows = summarize_submissions(submissions)
    assert [row["form"] for row in rows] == ["10-K", "10-Q"]


def test_summarize_companyfacts_extracts_latest_fact():
    facts = {
        "facts": {
            "us-gaap": {
                "Revenues": {
                    "units": {
                        "USD": [
                            {"val": 100, "end": "2025-12-31", "filed": "2026-01-31", "form": "10-K"},
                            {"val": 90, "end": "2024-12-31", "filed": "2025-01-31", "form": "10-K"},
                        ]
                    }
                }
            }
        }
    }
    rows = summarize_companyfacts(facts)
    assert rows[0]["tag"] == "Revenues"
    assert rows[0]["value"] == 100


def test_build_company_snapshot_shape():
    company_row = {"ticker": "AAPL", "cik": "0000320193", "company_name": "Apple Inc."}
    submissions = {
        "name": "Apple Inc.",
        "sic": "3571",
        "sicDescription": "Electronic Computers",
        "exchanges": ["Nasdaq"],
        "tickers": ["AAPL"],
        "filings": {"recent": {"form": ["10-K"], "filingDate": ["2026-01-01"], "accessionNumber": ["x"], "primaryDocument": ["x.htm"]}},
    }
    snapshot = build_company_snapshot("aapl", company_row, submissions, {})
    assert snapshot["ticker"] == "AAPL"
    assert snapshot["cik"] == "0000320193"
    assert snapshot["recent_filings"][0]["form"] == "10-K"
    assert snapshot["data_status"] == "待人工确认"
