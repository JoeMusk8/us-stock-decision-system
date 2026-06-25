import pandas as pd
import streamlit as st

from core.tracking_pool_model import (
    build_tracking_item,
    build_tracking_summary,
    calculate_strategy_risk_label,
    normalize_ticker,
    utc_now_iso,
    validate_tracking_item,
)
from core.utils import render_section_title, render_status_badge, render_status_card


TABS = [
    "重点跟踪池主页面",
    "主题变量",
    "公司变量",
    "财务变量",
    "催化剂变量",
    "风险变量",
    "数据新鲜度",
    "量化策略标注详情",
    "新证据 / 新风险提醒",
    "复查任务",
]

DATA_STATUS = "待人工确认 / 数据不足 / 已验证"
AI_DRAFT = "AI草稿 / 待人工确认"

THEME_VARIABLES = ["主题热度", "主题资金流向", "主题是否过热", "主题是否衰退", "是否出现新证据", "主题是否被证伪"]
COMPANY_VARIABLES = ["业务边界是否变化", "产品路线是否变化", "订单是否变化", "客户是否变化", "管理层表述是否变化", "收入暴露度是否变化"]
FINANCIAL_VARIABLES = ["收入增长", "毛利率", "营业利润率", "自由现金流", "订单", "Backlog", "指引", "库存", "应收账款", "资本开支"]
CATALYST_ITEMS = ["财报", "投资者日", "产品发布", "客户公告", "政府合同", "政策变化", "行业会议", "管理层讲话", "重要订单"]
RISK_ITEMS = ["客户流失", "订单取消", "毛利率恶化", "竞争对手突破", "技术路线变化", "监管风险", "估值过高", "主题退潮", "管理层下调指引"]
FRESHNESS_CHECK_ITEMS = ["上次投研时间", "上次证据更新时间", "上次财报更新时间", "上次雷达更新时间", "上次人工复查时间"]
ALERT_TYPES = ["新证据", "新风险", "反证", "财报更新", "管理层表述变化", "订单变化"]
REVIEW_REASONS = ["新证据", "新风险", "数据过期", "财报更新", "主题退潮", "策略标注失效"]


def _init_tracking_pool():
    if "tracking_pool" not in st.session_state:
        st.session_state.tracking_pool = []


def _tracking_pool():
    _init_tracking_pool()
    return st.session_state.tracking_pool


def _table(rows):
    st.dataframe(rows, width="stretch", hide_index=True)
    st.caption(f"数据状态：{DATA_STATUS}")


def _button_row(labels, prefix):
    columns = st.columns(len(labels))
    for index, (column, label) in enumerate(zip(columns, labels), start=1):
        with column:
            st.button(label, key=f"{prefix}_{index}", width="stretch")


def _price_value(value):
    if value in (None, ""):
        return None
    try:
        return float(value)
    except ValueError:
        return value


def _tracking_rows(items):
    return [
        {
            "ticker": item.get("ticker", ""),
            "theme": item.get("theme", ""),
            "research_grade": item.get("research_grade", ""),
            "tracking_status": item.get("tracking_status", ""),
            "position_status": item.get("position_status", ""),
            "catalyst": item.get("catalyst", ""),
            "evidence_note": item.get("evidence_note", ""),
            "risk": item.get("risk", ""),
            "next_review_date": item.get("next_review_date", ""),
            "data_status": item.get("data_status", "待人工确认"),
        }
        for item in items
    ]


def _variable_rows(items):
    return [
        {
            "变量": item,
            "当前状态": "待人工确认 / 数据不足",
            "变化方向": "数据不足",
            "证据/数据来源": "待人工确认",
            "操作": "查看 / 确认 / 复查",
        }
        for item in items
    ]


def _add_tracking_item_form():
    with st.form("add_tracking_item_form", clear_on_submit=True):
        st.markdown("### 手动添加股票")
        columns = st.columns(3)
        with columns[0]:
            ticker = st.text_input("ticker", placeholder="例如 LITE、COHR、MU")
            company_name = st.text_input("company_name", placeholder="可为空")
            theme = st.text_input("theme", placeholder="例如 AI 光互连、HBM、数据中心电力")
        with columns[1]:
            research_grade = st.selectbox("research_grade", ["S", "A", "B", "C", "D"], index=2)
            tracking_status = st.selectbox("tracking_status", ["核心跟踪", "重点跟踪", "观察", "暂停", "剔除"], index=2)
            position_status = st.selectbox("position_status", ["未持有", "观察中", "已持有", "已卖出"], index=0)
        with columns[2]:
            catalyst = st.text_input("catalyst", placeholder="核心催化剂，可为空")
            risk = st.text_input("risk", placeholder="核心风险，可为空")
            next_review_date = st.text_input("next_review_date", placeholder="YYYY-MM-DD，可为空")
        evidence_note = st.text_area("evidence_note", placeholder="证据备注，可为空")
        submitted = st.form_submit_button("添加到跟踪池", width="stretch")

    if submitted:
        item = build_tracking_item(
            {
                "ticker": ticker,
                "company_name": company_name,
                "theme": theme,
                "research_grade": research_grade,
                "tracking_status": tracking_status,
                "position_status": position_status,
                "buy_price": None,
                "take_profit_price": None,
                "stop_loss_price": None,
                "catalyst": catalyst,
                "risk": risk,
                "next_review_date": next_review_date,
                "evidence_note": evidence_note,
                "data_status": "待人工确认",
            }
        )
        validation = validate_tracking_item(item)
        if validation["ok"]:
            st.session_state.tracking_pool.append(item)
            st.success("已添加到会话级跟踪池。")
        else:
            st.error("；".join(validation["errors"]))


def _render_main_tab():
    items = _tracking_pool()

    st.subheader("重点跟踪池主页面")
    st.write("手动维护高质量标的、研究主题、跟踪状态和关键变量。")
    render_status_badge("会话级数据")
    render_status_badge("待人工确认")
    st.caption("会话级数据，可导出保存。")
    st.caption("可从深度投研模块将完成研究等级的任务转入本跟踪池。")

    _add_tracking_item_form()

    summary = build_tracking_summary(items)
    st.markdown("### 跟踪池汇总")
    columns = st.columns(6)
    cards = [
        ("总股票数", summary["总股票数"], "session_state"),
        ("核心跟踪", summary["核心跟踪数量"], "手动维护"),
        ("重点跟踪", summary["重点跟踪数量"], "手动维护"),
        ("观察", summary["观察数量"], "手动维护"),
        ("已持有", summary["已持有数量"], "人工状态"),
        ("未配置策略", summary["未配置策略数量"], "价格字段为空"),
    ]
    for column, (title, value, note) in zip(columns, cards):
        with column:
            render_status_card(title, value, note)

    st.markdown("### 当前跟踪池")
    if items:
        _table(_tracking_rows(items))
    else:
        _table(
            [
                {
                    "ticker": "数据不足",
                    "theme": "待人工确认",
                    "research_grade": "C",
                    "tracking_status": "观察",
                    "position_status": "未持有",
                    "catalyst": "",
                    "evidence_note": "",
                    "risk": "",
                    "next_review_date": "",
                    "data_status": "数据不足",
                }
            ]
        )


def _render_strategy_detail_tab():
    items = _tracking_pool()

    st.subheader("量化策略标注详情")
    render_status_badge("人工策略标注")
    render_status_badge("会话级数据")
    st.caption("手动价格标注。")
    st.caption("会话级数据，可导出保存。")

    if not items:
        st.info("请先在“重点跟踪池主页面”手动添加股票。")
        return

    tickers = [item["ticker"] for item in items]
    selected_ticker = st.selectbox("选择 ticker", tickers)
    selected_index = next(index for index, item in enumerate(items) if item["ticker"] == selected_ticker)
    selected_item = items[selected_index]

    left, right = st.columns([1, 1])
    with left:
        with st.form("strategy_annotation_form"):
            st.markdown("### 手动价格标注")
            st.write(f"当前 ticker：{selected_item['ticker']}")
            st.write(f"研究主题：{selected_item.get('theme', '')}")
            buy_price = st.text_input("buy_price", value="" if selected_item.get("buy_price") is None else str(selected_item.get("buy_price")))
            take_profit_price = st.text_input(
                "take_profit_price",
                value="" if selected_item.get("take_profit_price") is None else str(selected_item.get("take_profit_price")),
            )
            stop_loss_price = st.text_input(
                "stop_loss_price",
                value="" if selected_item.get("stop_loss_price") is None else str(selected_item.get("stop_loss_price")),
            )
            submitted = st.form_submit_button("保存策略标注", width="stretch")

        if submitted:
            updated_item = {
                **selected_item,
                "buy_price": _price_value(buy_price),
                "take_profit_price": _price_value(take_profit_price),
                "stop_loss_price": _price_value(stop_loss_price),
                "updated_at": utc_now_iso(),
            }
            validation = validate_tracking_item(updated_item)
            if validation["ok"]:
                st.session_state.tracking_pool[selected_index] = updated_item
                selected_item = updated_item
                st.success("已保存到会话级跟踪池。")
            else:
                st.error("；".join(validation["errors"]))

    with right:
        risk_label = calculate_strategy_risk_label(selected_item)
        render_status_card("策略风险标签", risk_label, "未配置 / 风险偏高 / 结构较好 / 中性")
        render_status_card("buy_price", selected_item.get("buy_price") or "未配置", "人工填写")
        render_status_card("take_profit_price", selected_item.get("take_profit_price") or "未配置", "人工填写")
        render_status_card("stop_loss_price", selected_item.get("stop_loss_price") or "未配置", "人工填写")

    export_df = pd.DataFrame(_tracking_rows(items))
    csv_data = export_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "导出当前 tracking_pool 为 CSV",
        data=csv_data,
        file_name="tracking_pool_export.csv",
        mime="text/csv",
        width="stretch",
    )


def _render_variable_tab(title, items):
    st.subheader(title)
    st.write("当前页面保留模块边界，后续可继续扩展变量跟踪。")
    _table(_variable_rows(items))
    with st.container(border=True):
        st.subheader(f"{title}摘要")
        st.write(AI_DRAFT)
        st.write("当前为手动工作台阶段，数据不足时不形成事实结论。")
        st.caption(f"数据状态：{DATA_STATUS}")


def _render_freshness_tab():
    st.subheader("数据新鲜度")
    st.write("页面回答：这份研究是否过期？")
    _table(
        [
            {
                "检查项": item,
                "上次更新时间": "数据不足",
                "有效期": "待人工确认",
                "当前状态": "数据不足",
                "操作": "查看 / 标记 / 复查",
            }
            for item in FRESHNESS_CHECK_ITEMS
        ]
    )
    _button_row(["刷新数据新鲜度", "标记已复查", "创建复查任务", "查看过期原因"], "freshness_action")


def _render_alert_tab():
    st.subheader("新证据 / 新风险提醒")
    st.write("当前页面保留提醒处理入口，后续接入证据流后扩展。")
    _table(
        [
            {
                "编号": index,
                "类型": item,
                "新内容摘要": "数据不足",
                "关联变量": "待人工确认",
                "影响方向": "数据不足",
                "优先级": "高 / 中 / 低",
                "evidence_id": f"EVID____-{index}",
                "人工状态": "待人工处理",
                "操作": "查看 / 绑定 / 复查",
            }
            for index, item in enumerate(ALERT_TYPES, start=1)
        ]
    )


def _render_review_task_tab():
    st.subheader("复查任务")
    st.write("管理新证据、新风险、数据过期和策略标注失效触发的复查任务。")
    _button_row(["新建复查任务", "批量标记完成", "按优先级排序", "导出复查清单"], "review_top_action")
    _table(
        [
            {
                "任务编号": f"REV____-{index}",
                "股票": "数据不足",
                "主题": "待人工确认",
                "触发原因": reason,
                "优先级": "高 / 中 / 低",
                "截止时间": "待人工确认",
                "当前状态": "数据不足",
                "操作": "查看 / 处理 / 完成",
            }
            for index, reason in enumerate(REVIEW_REASONS, start=1)
        ]
    )


def render():
    render_section_title(
        "重点跟踪池 / 量化策略标注模块",
        "手动维护跟踪池、变量状态与策略价格标注。",
    )
    render_status_badge("会话级数据")
    render_status_badge("待人工确认")
    render_status_badge("数据不足")
    st.caption(f"全局数据状态：{DATA_STATUS}")

    tabs = st.tabs(TABS)
    for index, tab in enumerate(tabs):
        with tab:
            if index == 0:
                _render_main_tab()
            elif index == 1:
                _render_variable_tab("主题变量", THEME_VARIABLES)
            elif index == 2:
                _render_variable_tab("公司变量", COMPANY_VARIABLES)
            elif index == 3:
                _render_variable_tab("财务变量", FINANCIAL_VARIABLES)
            elif index == 4:
                _render_variable_tab("催化剂变量", CATALYST_ITEMS)
            elif index == 5:
                _render_variable_tab("风险变量", RISK_ITEMS)
            elif index == 6:
                _render_freshness_tab()
            elif index == 7:
                _render_strategy_detail_tab()
            elif index == 8:
                _render_alert_tab()
            elif index == 9:
                _render_review_task_tab()
