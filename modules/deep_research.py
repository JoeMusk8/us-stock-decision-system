import pandas as pd
import streamlit as st

from core.deep_research_model import (
    SCORE_FIELDS,
    build_research_summary,
    calculate_total_research_score,
    derive_research_decision,
    derive_research_grade,
    normalize_research_task,
    validate_research_task,
)
from core.research_to_tracking_bridge import (
    build_tracking_item_from_research_task,
    can_transfer_to_tracking_pool,
    upsert_tracking_item,
)
from core.utils import render_section_title, render_status_badge, render_status_card


TABS = [
    "股票任务池总览",
    "单股投研工作台总览",
    "公司业务边界验证",
    "主题受益验证",
    "产业链位置验证",
    "财务兑现验证",
    "客户 / 订单 / CapEx 验证",
    "竞争格局验证",
    "风险与反证验证",
    "Claim 验证",
    "研究报告与等级",
]

DATA_STATUS = "待人工确认 / 数据不足 / 已验证"
AI_DRAFT = "AI草稿 / 待人工确认"

SCORE_LABELS = {
    "business_boundary_score": "公司业务边界验证",
    "theme_benefit_score": "主题受益验证",
    "supply_chain_position_score": "产业链位置验证",
    "financial_realization_score": "财务兑现验证",
    "customer_order_capex_score": "客户 / 订单 / CapEx 验证",
    "competition_score": "竞争格局验证",
    "risk_counterevidence_score": "风险与反证验证",
    "claim_evidence_score": "Claim / Evidence 验证",
}

RESEARCH_QUESTIONS = [
    "公司主营业务是什么？",
    "主要产品是什么？",
    "收入分部是什么？",
    "客户类型是什么？",
    "该主题相关业务是否属于核心业务？",
    "该业务是否只是边缘业务？",
    "公司是否明确披露过该方向？",
    "这家公司是否真的受益于这个主题？",
]


def _init_tasks():
    if "deep_research_tasks" not in st.session_state:
        st.session_state.deep_research_tasks = []


def _init_tracking_pool():
    if "tracking_pool" not in st.session_state:
        st.session_state.tracking_pool = []


def _tasks():
    _init_tasks()
    return st.session_state.deep_research_tasks


def _table(rows):
    st.dataframe(rows, width="stretch", hide_index=True)
    st.caption(f"数据状态：{DATA_STATUS}")


def _button_row(labels, prefix):
    columns = st.columns(len(labels))
    for index, (column, label) in enumerate(zip(columns, labels), start=1):
        with column:
            st.button(label, key=f"{prefix}_{index}", width="stretch")


def _task_label(task):
    return f"{task.get('ticker', '')} / {task.get('theme', '')}"


def _task_rows(tasks):
    return [
        {
            "ticker": task.get("ticker", ""),
            "company_name": task.get("company_name", ""),
            "theme": task.get("theme", ""),
            "research_status": task.get("research_status", ""),
            "final_research_grade": task.get("final_research_grade", ""),
            "decision": task.get("decision", ""),
            "data_status": task.get("data_status", "待人工确认"),
            "updated_at": task.get("updated_at", ""),
        }
        for task in tasks
    ]


def _selected_task_ui(key_prefix):
    tasks = _tasks()
    if not tasks:
        st.info("请先在“股票任务池总览”手动创建投研任务。")
        return None, None
    labels = [_task_label(task) for task in tasks]
    selected_label = st.selectbox("选择投研任务", labels, key=f"{key_prefix}_selected_task")
    selected_index = labels.index(selected_label)
    return selected_index, tasks[selected_index]


def _render_task_form():
    with st.form("deep_research_add_task_form", clear_on_submit=True):
        st.markdown("### 手动创建投研任务")
        columns = st.columns(3)
        with columns[0]:
            ticker = st.text_input("ticker", placeholder="例如 LITE、COHR、MU")
            company_name = st.text_input("company_name", placeholder="可为空")
            theme = st.text_input("theme", placeholder="例如 AI 光互连、HBM、数据中心电力")
        with columns[1]:
            research_status = st.selectbox("research_status", ["未开始", "进行中", "已完成", "暂停", "剔除"])
            data_status = st.selectbox("data_status", ["待人工确认", "数据不足", "已验证"])
        with columns[2]:
            st.caption("分数和 Claim 可在后续页面补充。")
            st.caption("研究等级不是买入评级。")
        submitted = st.form_submit_button("添加到投研任务池", width="stretch")

    if submitted:
        task = normalize_research_task(
            {
                "ticker": ticker,
                "company_name": company_name,
                "theme": theme,
                "research_status": research_status,
                "data_status": data_status,
            }
        )
        validation = validate_research_task(task)
        if validation["ok"]:
            st.session_state.deep_research_tasks.append(task)
            st.success("已添加到会话级投研任务池。")
        else:
            st.error("；".join(validation["errors"]))


def _render_task_pool_tab():
    tasks = _tasks()
    st.subheader("股票任务池总览")
    st.write("手动创建和维护“股票 + 研究主题”投研任务。")
    render_status_badge("会话级数据")
    render_status_badge("股票 + 主题")
    st.caption("会话级数据，可导出保存。")
    st.caption("可从基础投研 / 候选股雷达模块将候选股转入本深度投研任务池。")

    _render_task_form()

    summary = build_research_summary(tasks)
    st.markdown("### 投研任务汇总")
    columns = st.columns(8)
    cards = [
        ("总任务数", summary["总任务数"], "session_state"),
        ("S", summary["S 数量"], "研究等级"),
        ("A", summary["A 数量"], "研究等级"),
        ("B", summary["B 数量"], "研究等级"),
        ("C", summary["C 数量"], "研究等级"),
        ("D", summary["D 数量"], "研究等级"),
        ("已完成", summary["已完成数量"], "流程状态"),
        ("进行中", summary["进行中数量"], "流程状态"),
    ]
    for column, (title, value, note) in zip(columns, cards):
        with column:
            render_status_card(title, value, note)

    st.markdown("### 当前任务池")
    if tasks:
        _table(_task_rows(tasks))
    else:
        _table(
            [
                {
                    "ticker": "数据不足",
                    "company_name": "",
                    "theme": "待人工确认",
                    "research_status": "未开始",
                    "final_research_grade": "D",
                    "decision": "继续观察",
                    "data_status": "数据不足",
                    "updated_at": "",
                }
            ]
        )


def _render_single_stock_tab():
    st.subheader("单股投研工作台总览")
    selected_index, task = _selected_task_ui("single_stock")
    if task is None:
        return

    total_score = calculate_total_research_score(task)
    grade = derive_research_grade(total_score)
    decision = derive_research_decision(grade)

    columns = st.columns(4)
    cards = [
        ("当前股票", task["ticker"], task.get("company_name", "")),
        ("研究主题", task["theme"], "股票 + 主题绑定"),
        ("总分", total_score, "满分 40"),
        ("研究等级", grade, "不是买入评级"),
    ]
    for column, (title, value, note) in zip(columns, cards):
        with column:
            render_status_card(title, value, note)

    render_status_card("研究流转 decision", decision, "待人工确认")

    st.markdown("### 八项验证分数")
    _table(
        [
            {
                "验证项": SCORE_LABELS[field],
                "分数": task.get(field, 0),
                "状态": "待人工确认",
            }
            for field in SCORE_FIELDS
        ]
    )

    st.markdown("### 核心验证问题")
    _table(
        [
            {
                "序号": index,
                "验证问题": question,
                "当前状态": "待人工确认",
                "操作": "补充证据 / 人工确认",
            }
            for index, question in enumerate(RESEARCH_QUESTIONS, start=1)
        ]
    )


def _render_simple_validation_tab(title, items):
    st.subheader(title)
    st.write("当前页面保留验证边界，支持后续逐项补充证据。")
    _table(
        [
            {
                "验证项": item,
                "当前判断": "待人工确认",
                "证据状态": "数据不足",
                "evidence_id": f"EVID____-{index}",
                "操作": "补充 / 确认",
            }
            for index, item in enumerate(items, start=1)
        ]
    )
    with st.container(border=True):
        st.subheader(f"{title}摘要")
        st.write(AI_DRAFT)
        st.caption(f"数据状态：{DATA_STATUS}")


def _render_claim_tab():
    st.subheader("Claim 验证")
    selected_index, task = _selected_task_ui("claim")
    if task is None:
        return

    st.caption("没有证据备注的 Claim 不能进入事实区。")
    with st.form("claim_evidence_form"):
        claim_text = st.text_area("手动添加 Claim", value="\n".join(task.get("key_claims", [])))
        evidence_note = st.text_area("手动添加 evidence_note", value=task.get("evidence_notes", ""))
        counter_evidence = st.text_area("手动添加 counter_evidence", value=task.get("counter_evidence", ""))
        submitted = st.form_submit_button("保存 Claim / Evidence / Counter Evidence", width="stretch")

    if submitted:
        updated = {
            **task,
            "key_claims": [line.strip() for line in claim_text.splitlines() if line.strip()],
            "evidence_notes": evidence_note.strip(),
            "counter_evidence": counter_evidence.strip(),
        }
        updated = normalize_research_task(updated)
        st.session_state.deep_research_tasks[selected_index] = updated
        task = updated
        st.success("已保存到会话级投研任务。")

    st.markdown("### 当前 Claim 记录")
    claims = task.get("key_claims", [])
    _table(
        [
            {
                "编号": index,
                "Claim": claim,
                "标签": "待验证",
                "支持状态": "待人工确认" if task.get("evidence_notes") else "数据不足",
                "证据备注": task.get("evidence_notes") or "数据不足",
            }
            for index, claim in enumerate(claims or ["数据不足"], start=1)
        ]
    )
    with st.container(border=True):
        st.subheader("反证与风险")
        st.write(task.get("counter_evidence") or "数据不足")
        st.caption(f"数据状态：{task.get('data_status', '待人工确认')}")


def _render_report_grade_tab():
    st.subheader("研究报告与等级")
    selected_index, task = _selected_task_ui("report")
    if task is None:
        return

    st.caption("手动评分，待人工确认。")
    st.markdown("### 当前投研任务")
    task_columns = st.columns(5)
    for column, (title, value, note) in zip(
        task_columns,
        [
            ("ticker", task.get("ticker", ""), "股票代码"),
            ("theme", task.get("theme", ""), "研究主题"),
            ("final_research_grade", task.get("final_research_grade", ""), "研究等级"),
            ("decision", task.get("decision", ""), "研究流转"),
            ("data_status", task.get("data_status", "待人工确认"), "会话级"),
        ],
    ):
        with column:
            render_status_card(title, value or "数据不足", note)

    with st.container(border=True):
        st.subheader("证据与反证摘要")
        st.write(f"evidence_notes：{task.get('evidence_notes') or '数据不足'}")
        st.write(f"counter_evidence：{task.get('counter_evidence') or '数据不足'}")
        st.caption("研究流程流转。")

    with st.form("research_score_form"):
        st.markdown("### 八项验证分数")
        score_columns = st.columns(2)
        score_values = {}
        for index, field in enumerate(SCORE_FIELDS):
            with score_columns[index % 2]:
                score_values[field] = st.number_input(
                    SCORE_LABELS[field],
                    min_value=0.0,
                    max_value=5.0,
                    value=float(task.get(field, 0)),
                    step=0.5,
                    key=f"score_{field}",
                )
        submitted = st.form_submit_button("生成研究等级", width="stretch")

    if submitted:
        updated = {**task, **score_values}
        total_score = calculate_total_research_score(updated)
        grade = derive_research_grade(total_score)
        updated["final_research_grade"] = grade
        updated["decision"] = derive_research_decision(grade)
        updated = normalize_research_task(updated)
        validation = validate_research_task(updated)
        if validation["ok"]:
            st.session_state.deep_research_tasks[selected_index] = updated
            task = updated
            st.success("已生成并保存研究等级。")
        else:
            st.error("；".join(validation["errors"]))

    total_score = calculate_total_research_score(task)
    grade = derive_research_grade(total_score)
    decision = derive_research_decision(grade)
    columns = st.columns(4)
    for column, (title, value, note) in zip(
        columns,
        [
            ("总分", total_score, "满分 40"),
            ("研究等级", grade, "S/A/B/C/D"),
            ("研究流转", decision, "流程流转"),
            ("数据状态", task.get("data_status", "待人工确认"), "会话级"),
        ],
    ):
        with column:
            render_status_card(title, value, note)

    st.markdown("### 研究报告摘要")
    with st.container(border=True):
        st.write(f"股票代码：{task.get('ticker')}")
        st.write(f"研究主题：{task.get('theme')}")
        st.write(f"八项验证分数：{', '.join(f'{SCORE_LABELS[field]}={task.get(field, 0)}' for field in SCORE_FIELDS)}")
        st.write(f"总分：{total_score}")
        st.write(f"研究等级：{grade}")
        st.write(f"研究流转 decision：{decision}")
        st.write(f"核心 Claim：{'；'.join(task.get('key_claims', [])) or '数据不足'}")
        st.write(f"证据备注：{task.get('evidence_notes') or '数据不足'}")
        st.write(f"反证与风险：{task.get('counter_evidence') or '数据不足'}")
        st.caption("研究等级与流转均需人工确认。")

    if st.button("转入重点跟踪池", key="transfer_to_tracking_pool", width="stretch"):
        transfer_check = can_transfer_to_tracking_pool(task)
        if not transfer_check["ok"]:
            st.warning(transfer_check["reason"])
        else:
            _init_tracking_pool()
            tracking_item = build_tracking_item_from_research_task(task)
            st.session_state.tracking_pool = upsert_tracking_item(st.session_state.tracking_pool, tracking_item)
            st.success("已转入重点跟踪池。")
            st.caption("已转入重点跟踪池。")

    export_df = pd.DataFrame(_task_rows(_tasks()))
    csv_data = export_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "导出 deep_research_tasks 为 CSV",
        data=csv_data,
        file_name="deep_research_tasks_export.csv",
        mime="text/csv",
        width="stretch",
    )


def render():
    render_section_title(
        "深度投研模块",
        "对“股票 + 主题”进行证据驱动的公司级验证，判断研究流转方向。",
    )
    render_status_badge("会话级数据")
    render_status_badge("待人工确认")
    render_status_badge("数据不足")
    st.caption(f"全局数据状态：{DATA_STATUS}")

    tabs = st.tabs(TABS)
    validation_items = {
        2: ("公司业务边界验证", ["公司主营业务", "主要产品", "收入分部", "客户类型", "主题相关业务是否核心业务", "是否只是边缘业务"]),
        3: ("主题受益验证", ["业务相关性", "收入暴露度", "订单 / 客户证据", "管理层是否确认该方向", "产业链节点匹配度", "是否只是概念相关"]),
        4: ("产业链位置验证", ["所属产业链层级", "对应产业链节点", "是否处于核心瓶颈节点", "是否具备稀缺性", "是否难以替代", "是否具备议价能力"]),
        5: ("财务兑现验证", ["收入增长", "收入分部变化", "毛利率变化", "订单 / Backlog", "管理层指引", "现金流"]),
        6: ("客户 / 订单 / CapEx 验证", ["客户证据", "订单证据", "CapEx相关性", "公司扩产", "客户需求持续性"]),
        7: ("竞争格局验证", ["主要竞争对手", "技术壁垒", "客户认证壁垒", "规模优势", "替代风险", "价格竞争风险"]),
        8: ("风险与反证验证", ["主题相关业务可能不是核心业务", "公司没有明确披露该方向", "订单证据不足", "竞争对手更强"]),
    }

    for index, tab in enumerate(tabs):
        with tab:
            if index == 0:
                _render_task_pool_tab()
            elif index == 1:
                _render_single_stock_tab()
            elif index == 9:
                _render_claim_tab()
            elif index == 10:
                _render_report_grade_tab()
            elif index in validation_items:
                title, items = validation_items[index]
                _render_simple_validation_tab(title, items)
