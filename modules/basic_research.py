import pandas as pd
import streamlit as st

from core.basic_research_model import (
    VALID_CAPITAL_FLOW_STATUSES,
    VALID_CHAIN_LAYERS,
    VALID_HEAT_STATUSES,
    build_candidate_summary,
    normalize_candidate,
    upsert_candidate,
    validate_candidate,
)
from core.basic_to_deep_bridge import (
    build_deep_research_task_from_candidate,
    can_transfer_candidate_to_deep_research,
    upsert_deep_research_task,
)
from core.utils import render_section_title, render_status_badge, render_status_card


TABS = [
    "基础投研主工作台",
    "产业链全景图谱",
    "节点评分 / 瓶颈识别",
    "候选股雷达",
    "证据与AI解释",
    "人工确认 / 状态管理",
]

DATA_STATUS = "待人工确认 / 数据不足 / 已验证"
AI_DRAFT = "AI草稿 / 待人工确认"

INDUSTRY_LAYERS = [
    "上游资源 / 原材料",
    "核心零部件",
    "关键设备",
    "系统集成",
    "基础设施建设",
    "下游应用 / 客户",
]

SCORING_DIMENSIONS = [
    "技术难度",
    "供给稀缺",
    "产能瓶颈",
    "客户认证周期",
    "资本开支强度",
    "替代难度",
    "毛利率潜力",
    "议价能力",
    "交付周期",
    "监管约束",
]


def _init_state():
    if "basic_research_industries" not in st.session_state:
        st.session_state.basic_research_industries = []
    if "candidate_stocks" not in st.session_state:
        st.session_state.candidate_stocks = []
    if "deep_research_tasks" not in st.session_state:
        st.session_state.deep_research_tasks = []


def _table(rows):
    st.dataframe(rows, width="stretch", hide_index=True)
    st.caption(f"数据状态：{DATA_STATUS}")


def _button_row(labels, prefix):
    columns = st.columns(len(labels))
    for index, (column, label) in enumerate(zip(columns, labels), start=1):
        with column:
            st.button(label, key=f"{prefix}_{index}", width="stretch")


def _candidate_rows(items):
    return [
        {
            "ticker": item.get("ticker", ""),
            "company_name": item.get("company_name", ""),
            "industry": item.get("industry", ""),
            "theme": item.get("theme", ""),
            "chain_layer": item.get("chain_layer", ""),
            "bottleneck_score": item.get("bottleneck_score", ""),
            "heat_status": item.get("heat_status", ""),
            "capital_flow_status": item.get("capital_flow_status", ""),
            "candidate_reason": item.get("candidate_reason", ""),
            "evidence_note": item.get("evidence_note", ""),
            "data_status": item.get("data_status", "待人工确认"),
            "updated_at": item.get("updated_at", ""),
        }
        for item in items
    ]


def _render_workspace_tab():
    _init_state()
    st.subheader("基础投研主工作台")
    st.write("手动维护最多 3 个当前研究行业，并将候选股沉淀到候选股雷达。")
    render_status_badge("会话级数据")
    st.caption("会话级数据，可导出保存。")
    st.caption("可从范式创新监控模块转入新行业/主题。")

    with st.form("basic_industries_form"):
        columns = st.columns(3)
        values = []
        existing = st.session_state.basic_research_industries
        for index, column in enumerate(columns):
            with column:
                values.append(
                    st.text_input(
                        f"行业{index + 1}",
                        value=existing[index] if index < len(existing) else "",
                        placeholder="最多 3 个行业",
                    ).strip()
                )
        submitted = st.form_submit_button("保存当前行业", width="stretch")
    if submitted:
        st.session_state.basic_research_industries = [value for value in values if value][:3]
        st.success("已保存到会话级行业列表。")

    st.markdown("### 当前跟踪行业")
    industry_rows = [{"序号": index, "行业": industry, "数据状态": "待人工确认"} for index, industry in enumerate(st.session_state.basic_research_industries, start=1)]
    _table(industry_rows or [{"序号": 1, "行业": "数据不足", "数据状态": "数据不足"}])

    status_columns = st.columns(4)
    cards = [
        ("当前行业数", len(st.session_state.basic_research_industries), "最多 3 个"),
        ("候选股数量", len(st.session_state.candidate_stocks), "会话级"),
        ("产业链图谱", "待人工确认", "手动阶段"),
        ("候选股雷达", "可手动添加", "待人工确认"),
    ]
    for column, (title, value, note) in zip(status_columns, cards):
        with column:
            render_status_card(title, value, note)

    _button_row(["生成产业链图谱", "重新分析", "AI解释评分", "导出报告", "进入深度投研"], "workspace_action")


def _render_chain_tab():
    st.subheader("产业链全景图谱")
    st.write("使用卡片模拟 6 层产业链结构。")
    for index, layer in enumerate(INDUSTRY_LAYERS, start=1):
        st.markdown(f"### {index}. {layer}")
        columns = st.columns(3)
        for node_index, column in enumerate(columns, start=1):
            with column:
                with st.container(border=True):
                    st.subheader(f"节点{node_index}")
                    st.write(f"所属层级：{layer}")
                    st.write("核心等级：待人工确认")
                    st.write("证据数：数据不足")
                    st.caption(f"状态：{AI_DRAFT}")


def _render_scoring_tab():
    st.subheader("节点评分 / 瓶颈识别")
    st.write("按 10 个瓶颈评分维度对产业链节点进行结构化记录。")
    _table(
        [
            {
                "节点": f"节点{index}",
                "所属层级": INDUSTRY_LAYERS[(index - 1) % len(INDUSTRY_LAYERS)],
                **{dimension: "待人工确认" for dimension in SCORING_DIMENSIONS},
                "总分": "数据不足",
                "核心等级": "待人工确认",
                "证据状态": "数据不足",
            }
            for index in range(1, 7)
        ]
    )


def _render_candidate_form():
    with st.form("candidate_stock_form", clear_on_submit=True):
        st.markdown("### 手动添加候选股")
        columns = st.columns(3)
        with columns[0]:
            ticker = st.text_input("ticker", placeholder="例如 LITE、COHR、MU")
            company_name = st.text_input("company_name", placeholder="可为空")
            industry = st.text_input("industry", placeholder="必填")
        with columns[1]:
            theme = st.text_input("theme", placeholder="必填")
            chain_layer = st.selectbox("chain_layer", sorted(VALID_CHAIN_LAYERS))
            bottleneck_score = st.number_input("bottleneck_score", min_value=0.0, max_value=5.0, value=0.0, step=0.5)
        with columns[2]:
            heat_status = st.selectbox("heat_status", ["低热度", "升温中", "高热度", "过热"])
            capital_flow_status = st.selectbox("capital_flow_status", ["未知", "流入", "中性", "流出"])
            data_status = st.selectbox("data_status", ["待人工确认", "数据不足", "已验证"])
        candidate_reason = st.text_area("candidate_reason", placeholder="候选原因，可为空")
        evidence_note = st.text_area("evidence_note", placeholder="证据备注，可为空")
        submitted = st.form_submit_button("保存候选股", width="stretch")

    if submitted:
        candidate = normalize_candidate(
            {
                "ticker": ticker,
                "company_name": company_name,
                "industry": industry,
                "theme": theme,
                "chain_layer": chain_layer,
                "bottleneck_score": bottleneck_score,
                "heat_status": heat_status,
                "capital_flow_status": capital_flow_status,
                "candidate_reason": candidate_reason,
                "evidence_note": evidence_note,
                "data_status": data_status,
            }
        )
        validation = validate_candidate(candidate)
        if validation["ok"]:
            st.session_state.candidate_stocks = upsert_candidate(st.session_state.candidate_stocks, candidate)
            st.success("已保存到候选股雷达。")
        else:
            st.error("；".join(validation["errors"]))


def _render_candidate_tab():
    _init_state()
    st.subheader("候选股雷达")
    render_status_badge("会话级数据")
    render_status_badge("深度投研候选")
    st.caption("手动候选，待人工确认。")

    _render_candidate_form()

    summary = build_candidate_summary(st.session_state.candidate_stocks)
    st.markdown("### 候选股汇总")
    columns = st.columns(6)
    cards = [
        ("总候选数", summary["总候选数"], "会话级"),
        ("高热度", summary["高热度数量"], "人工标注"),
        ("过热", summary["过热数量"], "需警惕"),
        ("资金流入", summary["资金流入数量"], "人工标注"),
        ("待人工确认", summary["待人工确认数量"], "数据状态"),
        ("数据不足", summary["数据不足数量"], "数据状态"),
    ]
    for column, (title, value, note) in zip(columns, cards):
        with column:
            render_status_card(title, value, note)

    st.markdown("### 当前候选股")
    candidates = st.session_state.candidate_stocks
    _table(_candidate_rows(candidates) if candidates else [{"ticker": "数据不足", "theme": "待人工确认", "data_status": "数据不足"}])

    if candidates:
        labels = [f"{item['ticker']} / {item['theme']}" for item in candidates]
        selected_label = st.selectbox("选择候选股", labels, key="candidate_transfer_select")
        selected_index = labels.index(selected_label)
        selected_candidate = candidates[selected_index]
        if st.button("转入深度投研", key="candidate_to_deep", width="stretch"):
            transfer_check = can_transfer_candidate_to_deep_research(selected_candidate)
            if not transfer_check["ok"]:
                st.warning(transfer_check["reason"])
            else:
                deep_task = build_deep_research_task_from_candidate(selected_candidate)
                st.session_state.deep_research_tasks = upsert_deep_research_task(st.session_state.deep_research_tasks, deep_task)
                st.success("已转入深度投研任务池。")
                st.caption(transfer_check["reason"])
                st.caption("已转入深度投研任务池。")

        export_df = pd.DataFrame(_candidate_rows(candidates))
        st.download_button(
            "导出 candidate_stocks 为 CSV",
            data=export_df.to_csv(index=False).encode("utf-8-sig"),
            file_name="candidate_stocks_export.csv",
            mime="text/csv",
            width="stretch",
        )


def _render_evidence_tab():
    st.subheader("证据与AI解释")
    left, right = st.columns([1.2, 1])
    with left:
        _table(
            [
                {
                    "证据ID": f"EVID____-{index}",
                    "等级": "待人工确认",
                    "来源类型": "待配置",
                    "关联节点": "数据不足",
                    "关联股票": "数据不足",
                    "支持内容": AI_DRAFT,
                    "状态": "数据不足",
                    "操作": "查看 / 标记",
                }
                for index in range(1, 6)
            ]
        )
    with right:
        with st.container(border=True):
            st.subheader("AI解释面板")
            st.write(AI_DRAFT)
            st.write("缺失证据：数据不足")
            st.caption(f"数据状态：{DATA_STATUS}")


def _render_confirmation_tab():
    st.subheader("人工确认 / 状态管理")
    checklist_items = [
        "行业名称已输入",
        "产业链六层已生成",
        "核心瓶颈节点已识别",
        "节点评分已生成",
        "候选股雷达已生成",
        "候选股数量不超过5只",
        "候选股均绑定产业链节点",
        "候选股均绑定证据ID",
        "AI解释已生成",
        "人工确认已完成",
    ]
    columns = st.columns(2)
    for index, item in enumerate(checklist_items):
        with columns[index % 2]:
            st.checkbox(item, value=False, key=f"basic_confirm_{index}")
    _button_row(["确认产业链图谱", "确认候选股雷达", "标记证据不足", "退回重新分析", "提交深度投研候选"], "confirmation_action")


def render():
    render_section_title(
        "基础投研 / 产业链图谱 / 候选股雷达模块",
        "手动维护行业、产业链节点和深度投研候选股。",
    )
    render_status_badge("会话级数据")
    render_status_badge("待人工确认")
    render_status_badge("数据不足")
    st.caption(f"全局数据状态：{DATA_STATUS}")

    tabs = st.tabs(TABS)
    renderers = [
        _render_workspace_tab,
        _render_chain_tab,
        _render_scoring_tab,
        _render_candidate_tab,
        _render_evidence_tab,
        _render_confirmation_tab,
    ]
    for tab, renderer in zip(tabs, renderers):
        with tab:
            renderer()
