import pandas as pd
import streamlit as st

from core.paradigm_monitor_model import (
    VALID_SIGNAL_STRENGTHS,
    VALID_SIGNAL_TYPES,
    VALID_SOURCE_TYPES,
    build_paradigm_summary,
    normalize_paradigm_signal,
    upsert_paradigm_signal,
    validate_paradigm_signal,
)
from core.paradigm_to_basic_bridge import (
    build_basic_industry_from_paradigm,
    can_transfer_paradigm_to_basic,
    upsert_basic_industry,
)
from core.utils import render_section_title, render_status_badge, render_status_card


TABS = [
    "24小时信息流总览",
    "美国政府资金流向",
    "巨头公司科研方向配置",
    "商界领袖关注方向配置",
    "X KOL 发言配置",
    "AI 审核队列",
    "24小时输出详情",
]

DATA_STATUS = "待人工确认 / 数据不足 / 已验证"
AI_DRAFT = "AI草稿 / 待人工确认"


def _init_state():
    if "paradigm_signals" not in st.session_state:
        st.session_state.paradigm_signals = []
    if "basic_research_industries" not in st.session_state:
        st.session_state.basic_research_industries = []


def _table(rows):
    st.dataframe(rows, width="stretch", hide_index=True)
    st.caption(f"数据状态：{DATA_STATUS}")


def _button_row(labels, prefix):
    columns = st.columns(len(labels))
    for index, (column, label) in enumerate(zip(columns, labels), start=1):
        with column:
            st.button(label, key=f"{prefix}_{index}", width="stretch")


def _signal_rows(signals):
    return [
        {
            "theme_name": item.get("theme_name", ""),
            "source_type": item.get("source_type", ""),
            "signal_type": item.get("signal_type", ""),
            "signal_strength": item.get("signal_strength", ""),
            "summary": item.get("summary", ""),
            "evidence_note": item.get("evidence_note", ""),
            "data_status": item.get("data_status", "待人工确认"),
            "updated_at": item.get("updated_at", ""),
        }
        for item in signals
    ]


def _signal_form():
    with st.form("paradigm_signal_form", clear_on_submit=True):
        st.markdown("### 手动添加范式主题")
        columns = st.columns(3)
        with columns[0]:
            theme_name = st.text_input("theme_name", placeholder="例如 AI 光互连、机器人电池、数据中心电力")
            source_type = st.selectbox("source_type", sorted(VALID_SOURCE_TYPES))
        with columns[1]:
            signal_type = st.selectbox("signal_type", sorted(VALID_SIGNAL_TYPES))
            signal_strength = st.selectbox("signal_strength", ["弱", "中", "强"])
        with columns[2]:
            data_status = st.selectbox("data_status", ["待人工确认", "数据不足", "已验证"])
            st.caption("手动主题，待人工确认。")
        summary = st.text_area("summary", placeholder="主题摘要，可为空")
        evidence_note = st.text_area("evidence_note", placeholder="证据备注，可为空")
        submitted = st.form_submit_button("保存范式主题", width="stretch")

    if submitted:
        signal = normalize_paradigm_signal(
            {
                "theme_name": theme_name,
                "source_type": source_type,
                "signal_type": signal_type,
                "signal_strength": signal_strength,
                "summary": summary,
                "evidence_note": evidence_note,
                "data_status": data_status,
            }
        )
        validation = validate_paradigm_signal(signal)
        if validation["ok"]:
            st.session_state.paradigm_signals = upsert_paradigm_signal(st.session_state.paradigm_signals, signal)
            st.success("已保存到会话级范式主题池。")
        else:
            st.error("；".join(validation["errors"]))


def _transfer_signal_ui(prefix):
    signals = st.session_state.paradigm_signals
    if not signals:
        st.info("请先手动添加范式主题。")
        return
    labels = [item["theme_name"] for item in signals]
    selected_label = st.selectbox("选择范式主题", labels, key=f"{prefix}_select_signal")
    signal = signals[labels.index(selected_label)]
    if st.button("转入基础投研", key=f"{prefix}_transfer_to_basic", width="stretch"):
        transfer_check = can_transfer_paradigm_to_basic(signal)
        if not transfer_check["ok"]:
            st.warning(transfer_check["reason"])
        else:
            industry = build_basic_industry_from_paradigm(signal)
            st.session_state.basic_research_industries = upsert_basic_industry(
                st.session_state.basic_research_industries,
                industry,
                max_count=3,
            )
            st.success("已转入基础投研行业/主题池。")
            st.caption(transfer_check["reason"])
            st.caption("已转入基础投研主题池。")


def _render_overview_tab():
    _init_state()
    st.subheader("24小时信息流总览")
    st.write("手动维护新方向 / 新主题，并作为基础投研入口。")
    render_status_badge("会话级数据")
    render_status_badge("研究入口")
    st.caption("手动主题，待人工确认。")

    _signal_form()

    summary = build_paradigm_summary(st.session_state.paradigm_signals)
    st.markdown("### 范式主题汇总")
    columns = st.columns(6)
    cards = [
        ("总主题数", summary["总主题数"], "会话级"),
        ("强信号", summary["强信号数量"], "人工标注"),
        ("中信号", summary["中信号数量"], "人工标注"),
        ("弱信号", summary["弱信号数量"], "人工标注"),
        ("待人工确认", summary["待人工确认数量"], "数据状态"),
        ("数据不足", summary["数据不足数量"], "数据状态"),
    ]
    for column, (title, value, note) in zip(columns, cards):
        with column:
            render_status_card(title, value, note)

    st.markdown("### 范式主题表格")
    signals = st.session_state.paradigm_signals
    _table(_signal_rows(signals) if signals else [{"theme_name": "数据不足", "source_type": "人工输入", "data_status": "数据不足"}])

    _transfer_signal_ui("overview")

    if signals:
        export_df = pd.DataFrame(_signal_rows(signals))
        st.download_button(
            "导出 paradigm_signals 为 CSV",
            data=export_df.to_csv(index=False).encode("utf-8-sig"),
            file_name="paradigm_signals_export.csv",
            mime="text/csv",
            width="stretch",
        )


def _render_government_tab():
    st.subheader("美国政府资金流向")
    st.write("当前阶段不接真实政府数据，仅保留信息源结构和人工确认入口。")
    _table(
        [
            {
                "机构": "待配置",
                "接收方": "数据不足",
                "用途": "数据不足",
                "技术词": "待人工确认",
                "AI标签": AI_DRAFT,
                "人工状态": "待人工确认",
            }
        ]
    )


def _render_company_tab():
    st.subheader("巨头公司科研方向配置")
    st.write("当前阶段不接真实巨头数据，仅保留 15 个手动配置位。")
    for row in range(5):
        columns = st.columns(3)
        for column_index, column in enumerate(columns):
            index = row * 3 + column_index + 1
            with column:
                with st.container(border=True):
                    st.markdown(f"**科技公司：{index}**")
                    value = st.text_input("输入框", key=f"tech_company_{index}", label_visibility="collapsed")
                    st.caption(f"状态：{'已配置' if value else '未配置'}")


def _render_leader_tab():
    st.subheader("商界领袖关注方向配置")
    st.write("当前阶段不接真实商界领袖数据，仅保留 15 个手动配置位。")
    for row in range(5):
        columns = st.columns(3)
        for column_index, column in enumerate(columns):
            index = row * 3 + column_index + 1
            with column:
                with st.container(border=True):
                    st.markdown(f"**商界领袖：{index}**")
                    name = st.text_input("姓名输入框", key=f"leader_name_{index}")
                    company = st.text_input("公司输入框", key=f"leader_company_{index}")
                    st.caption(f"状态：{'已配置' if name or company else '未配置'}")


def _render_kol_tab():
    st.subheader("X KOL 发言配置")
    render_status_badge("线索")
    st.write("当前阶段不接真实 X/KOL 数据，仅保留 15 个手动配置位。")
    st.caption("KOL 信息只能作为线索，不能直接作为事实结论。")
    for row in range(5):
        columns = st.columns(3)
        for column_index, column in enumerate(columns):
            index = row * 3 + column_index + 1
            with column:
                with st.container(border=True):
                    st.markdown(f"**监控KOL账号：{index}**")
                    value = st.text_input("账号输入框", key=f"kol_account_{index}")
                    st.caption(f"状态：{'已配置' if value else '未配置'}")


def _render_ai_queue_tab():
    _init_state()
    st.subheader("AI 审核队列")
    st.write("集中查看手动范式主题，并转入基础投研行业/主题池。")
    render_status_badge("AI草稿 / 待人工确认")
    render_status_badge("研究入口")

    signals = st.session_state.paradigm_signals
    _table(_signal_rows(signals) if signals else [{"theme_name": "数据不足", "signal_strength": "中", "data_status": "数据不足"}])

    left, right = st.columns(2)
    with left:
        with st.container(border=True):
            st.subheader("原始信息")
            st.write("当前为手动范式主题池。")
            st.write("真实外部数据源尚未接入。")
            st.caption(f"数据状态：{DATA_STATUS}")
    with right:
        with st.container(border=True):
            st.subheader("AI审核结果")
            st.write(AI_DRAFT)
            st.write("主题是否进入基础投研，必须人工确认。")
            st.caption(f"数据状态：{DATA_STATUS}")

    _transfer_signal_ui("ai_queue")


def _render_output_tab():
    st.subheader("24小时输出详情")
    for title in ["美国政府监控输出", "巨头公司监控输出", "商界领袖监控输出", "KOL监控输出"]:
        with st.container(border=True):
            st.subheader(title)
            columns = st.columns(3)
            with columns[0]:
                render_status_card("重点关注", "__ 条", "数据不足")
            with columns[1]:
                render_status_card("待审核", "__ 条", "待人工确认")
            with columns[2]:
                render_status_card("忽略", "__ 条", "待人工确认")
            if "KOL" in title:
                st.caption("KOL信息只能作为线索，不能直接作为事实。")
            _button_row(["查看详情", "只看重点关注", "只看待审核"], f"output_{title}")


def render():
    render_section_title(
        "范式创新监控模块",
        "手动维护新方向 / 新主题，并作为基础投研入口。",
    )
    render_status_badge("会话级数据")
    render_status_badge("待人工确认")
    render_status_badge("数据不足")
    st.caption(f"全局数据状态：{DATA_STATUS}")

    tabs = st.tabs(TABS)
    renderers = [
        _render_overview_tab,
        _render_government_tab,
        _render_company_tab,
        _render_leader_tab,
        _render_kol_tab,
        _render_ai_queue_tab,
        _render_output_tab,
    ]
    for tab, renderer in zip(tabs, renderers):
        with tab:
            renderer()
