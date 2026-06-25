import streamlit as st

from core.utils import render_clean_table, render_metric_card, render_page_header
from core.workflow_overview import build_workflow_overview, build_workspace_counts, suggest_next_step


def _render_metric_grid(counts):
    columns = st.columns(5)
    metrics = [
        ("范式主题", counts["paradigm_signals"], "入口"),
        ("行业主题", counts["basic_research_industries"], "基础投研"),
        ("候选股", counts["candidate_stocks"], "候选池"),
        ("投研任务", counts["deep_research_tasks"], "深度验证"),
        ("跟踪标的", counts["tracking_pool"], "跟踪池"),
    ]
    for column, (title, value, note) in zip(columns, metrics):
        with column:
            render_metric_card(title, value, note)


def render():
    render_page_header(
        "首页总览",
        "主链路工作台：范式、基础投研、深度投研、跟踪池。",
        badges=["会话级数据", "云端运行", "JSON备份"],
    )

    counts = build_workspace_counts(st.session_state)
    _render_metric_grid(counts)

    st.markdown("### 主链路进度")
    render_clean_table(build_workflow_overview(st.session_state))

    left, right = st.columns([1.2, 1])
    with left:
        st.markdown("### 下一步")
        st.markdown(f"**{suggest_next_step(st.session_state)}**")
        st.caption("侧边栏可下载或导入工作区 JSON。")

    with right:
        st.markdown("### 工作区统计")
        render_clean_table(
            [
                {"项目": "主链路总记录", "数量": counts["total_records"]},
                {"项目": "已配置价格标注", "数量": counts["strategy_configured"]},
            ]
        )
