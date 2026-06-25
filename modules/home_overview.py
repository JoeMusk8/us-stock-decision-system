import streamlit as st

from core.sec_edgar_client import fetch_sec_company_snapshot, normalize_ticker
from core.utils import render_clean_table, render_metric_card, render_page_header
from core.workflow_overview import build_workflow_overview, build_workspace_counts, suggest_next_step
from core.workspace_quality import build_quality_checks, build_quality_summary


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


def _render_sec_lookup():
    if "sec_company_snapshots" not in st.session_state:
        st.session_state.sec_company_snapshots = {}
    st.markdown("### SEC 公司事实查询")
    st.caption("读取 submissions / companyfacts，结果待人工确认。")
    with st.form("sec_lookup_form"):
        ticker = st.text_input("ticker", placeholder="例如 AAPL、MSFT、NVDA")
        submitted = st.form_submit_button("读取公司事实", width="stretch")
    if submitted:
        normalized = normalize_ticker(ticker)
        if normalized:
            result = fetch_sec_company_snapshot(normalized)
            if result.get("ok"):
                st.session_state.sec_company_snapshots[normalized] = result["snapshot"]
                st.success("已读取公司事实。")
            else:
                st.session_state.sec_company_snapshots[normalized] = {"ticker": normalized, "data_status": "数据不足", "error": result.get("error", "读取失败")}
                st.caption("数据不足：" + str(result.get("error", "读取失败"))[:120])
    snapshots = st.session_state.sec_company_snapshots
    if not snapshots:
        render_clean_table([{"ticker": "待输入", "CIK": "", "公司名称": "", "最近文件数": 0, "财务字段数": 0, "状态": "数据不足"}])
        return
    rows = []
    for snapshot in snapshots.values():
        rows.append({"ticker": snapshot.get("ticker", ""), "CIK": snapshot.get("cik", ""), "公司名称": snapshot.get("company_name", ""), "最近文件数": len(snapshot.get("recent_filings", []) or []), "财务字段数": len(snapshot.get("financial_facts", []) or []), "状态": snapshot.get("data_status", "待人工确认")})
    render_clean_table(rows)


def render():
    render_page_header(
        "首页总览",
        "主链路工作台：范式、基础投研、深度投研、跟踪池。",
        badges=["会话级数据", "云端运行", "JSON备份"],
    )

    counts = build_workspace_counts(st.session_state)
    quality = build_quality_summary(st.session_state)
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
                {"项目": "质量状态", "数量": quality["status"]},
                {"项目": "待处理项", "数量": quality["issue_count"]},
            ]
        )

    st.markdown("### 工作区质量检查")
    render_clean_table(build_quality_checks(st.session_state))
    _render_sec_lookup()
