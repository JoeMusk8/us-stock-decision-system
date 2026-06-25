from core.workflow_overview import (
    build_workflow_overview,
    build_workspace_counts,
    count_items,
    count_strategy_configured,
    suggest_next_step,
)


def sample_session():
    return {
        "paradigm_signals": [{"theme_name": "T1"}],
        "basic_research_industries": ["AI 光互连"],
        "candidate_stocks": [{"ticker": "EX1"}],
        "deep_research_tasks": [{"ticker": "EX1"}],
        "tracking_pool": [{"ticker": "EX1", "buy_price": 10}],
    }


def test_count_items_only_counts_lists():
    assert count_items([1, 2]) == 2
    assert count_items({"a": 1}) == 0


def test_count_strategy_configured():
    items = [{"ticker": "A"}, {"ticker": "B", "stop_loss_price": 8}]
    assert count_strategy_configured(items) == 1


def test_build_workspace_counts():
    counts = build_workspace_counts(sample_session())
    assert counts["paradigm_signals"] == 1
    assert counts["basic_research_industries"] == 1
    assert counts["candidate_stocks"] == 1
    assert counts["deep_research_tasks"] == 1
    assert counts["tracking_pool"] == 1
    assert counts["strategy_configured"] == 1
    assert counts["total_records"] == 5


def test_build_workflow_overview_rows():
    rows = build_workflow_overview(sample_session())
    assert len(rows) == 6
    assert rows[0]["状态"] == "已有数据"


def test_suggest_next_step_changes_with_progress():
    assert "范式" in suggest_next_step({})
    assert "JSON" in suggest_next_step(sample_session())
