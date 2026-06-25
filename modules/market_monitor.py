import streamlit as st

from core.market_environment_rules import (
    evaluate_market_funds,
    evaluate_market_sentiment,
    evaluate_overall_market_environment,
)
from core.yfinance_market_client import fetch_market_environment_data
from core.utils import render_section_title, render_status_badge, render_status_card


TABS = [
    "市场环境监控主页面",
    "市场资金监控",
    "市场情绪监控",
    "宏观环境监控",
    "市场环境结论",
    "时间提醒 / 事件日历",
]

DATA_STATUS = "待人工确认 / 数据不足"
AI_DRAFT = "AI草稿 / 待人工确认"

MACRO_VARIABLES = ["核心利率", "核心通胀", "核心就业", "核心GDP", "原油"]
EVENT_CATEGORIES = ["财报", "FOMC", "CPI", "PPI", "非农就业", "GDP", "原油库存", "重要行业会议", "政策事件"]


def _table(rows):
    st.dataframe(rows, width="stretch", hide_index=True)
    st.caption(f"数据状态：{DATA_STATUS}")


def _button_row(labels, prefix):
    columns = st.columns(len(labels))
    for index, (column, label) in enumerate(zip(columns, labels), start=1):
        with column:
            st.button(label, key=f"{prefix}_{index}", width="stretch")


def _display_value(value):
    if value is None or value == "":
        return "数据不足"
    if isinstance(value, bool):
        return "是" if value else "否"
    return value


def _short_error(market_result):
    if not market_result.get("errors"):
        return market_result.get("error", "")
    joined = "；".join(str(item).splitlines()[0] for item in market_result["errors"][:3])
    return joined[:240]


def _latest_updated_at(records):
    values = [record.get("updated_at") for record in records if record.get("updated_at")]
    return max(values) if values else "数据不足"


def _asset_environment_status(record):
    if record.get("data_status") == "数据不足":
        return "数据不足"
    required = [
        record.get("current_price"),
        record.get("ma_20"),
        record.get("ma_50"),
        record.get("above_ma20"),
        record.get("above_ma50"),
        record.get("ma_20_direction"),
        record.get("ma_50_direction"),
    ]
    if any(value is None for value in required):
        return "数据不足"
    if record.get("above_ma20") is True and record.get("above_ma50") is True:
        if record.get("ma_20_direction") != "向下" and record.get("ma_50_direction") != "向下":
            return "支持"
        return "谨慎"
    if record.get("above_ma20") is False or record.get("above_ma50") is False:
        return "不支持"
    return "谨慎"


@st.cache_data(ttl=300, show_spinner=False)
def _load_market_context():
    result = fetch_market_environment_data()
    market_funds = result.get("market_funds", [])
    market_sentiment = result.get("market_sentiment", [])
    return {
        **result,
        "funds_evaluation": evaluate_market_funds(market_funds),
        "sentiment_evaluation": evaluate_market_sentiment(market_sentiment),
        "overall_evaluation": evaluate_overall_market_environment(market_funds, market_sentiment),
    }


def _market_fund_rows(market_funds):
    return [
        {
            "资产": record.get("asset_name", "数据不足"),
            "代码": record.get("symbol", "数据不足"),
            "当前价": _display_value(record.get("current_price")),
            "20日均线": _display_value(record.get("ma_20")),
            "50日均线": _display_value(record.get("ma_50")),
            "20日均线方向": _display_value(record.get("ma_20_direction")),
            "50日均线方向": _display_value(record.get("ma_50_direction")),
            "成交量": _display_value(record.get("volume")),
            "相对成交量": _display_value(record.get("relative_volume")),
            "是否站上20日均线": _display_value(record.get("above_ma20")),
            "是否站上50日均线": _display_value(record.get("above_ma50")),
            "数据状态": record.get("data_status", "数据不足"),
            "更新时间": _display_value(record.get("updated_at")),
        }
        for record in market_funds
    ]


def _market_sentiment_rows(market_sentiment):
    return [
        {
            "指标": record.get("indicator_name", "数据不足"),
            "代码": record.get("indicator_id", "数据不足"),
            "当前值": _display_value(record.get("current_value")),
            "当前状态": _display_value(record.get("current_status")),
            "风险含义": _display_value(record.get("risk_meaning")),
            "变化方向": _display_value(record.get("direction")),
            "数据状态": record.get("data_status", "数据不足"),
            "更新时间": _display_value(record.get("updated_at")),
        }
        for record in market_sentiment
    ]


def _render_error_if_needed(market_result):
    error = _short_error(market_result)
    if error:
        st.caption(f"数据读取状态：{error}")


def _render_main_tab():
    market_result = _load_market_context()
    market_funds = market_result["market_funds"]
    market_sentiment = market_result["market_sentiment"]
    all_records = market_funds + market_sentiment
    pending_count = sum(1 for record in all_records if record.get("data_status") == "待人工确认")
    insufficient_count = sum(1 for record in all_records if record.get("data_status") == "数据不足")
    overall = market_result["overall_evaluation"]

    st.subheader("市场环境监控主页面")
    st.write("汇总市场资金、市场情绪和宏观环境，形成辅助风控判断。")
    _button_row(["刷新市场环境", "AI总结市场状态", "更新风险等级", "导出市场摘要"], "market_main_action")

    st.markdown("### 当前市场环境结论")
    columns = st.columns(5)
    conclusion_cards = [
        ("整体状态", overall["status"], "规则计算"),
        ("资金状态", overall["funds_status"], "QQQ / ^IXIC / BTC-USD"),
        ("情绪状态", overall["sentiment_status"], "^VIX"),
        ("更新时间", _latest_updated_at(all_records), "UTC"),
        ("数据不足", insufficient_count, "缺失或失败"),
    ]
    for column, (title, value, note) in zip(columns, conclusion_cards):
        with column:
            render_status_card(title, value, note)

    with st.container(border=True):
        st.subheader("简短原因")
        st.write(overall["reason"])
        st.caption("市场环境状态需人工确认。")

    st.markdown("### 真实行情数据状态")
    data_columns = st.columns(4)
    data_cards = [
        ("数据来源", "yfinance", "QQQ / ^IXIC / BTC-USD / ^VIX"),
        ("市场资金记录", len(market_funds), "3 个资产"),
        ("市场情绪记录", len(market_sentiment), "^VIX"),
        ("待人工确认", pending_count, "首次真实数据状态"),
    ]
    for column, (title, value, note) in zip(data_columns, data_cards):
        with column:
            render_status_card(title, value, note)
    _render_error_if_needed(market_result)

    st.markdown("### 三类环境摘要")
    left, middle, right = st.columns(3)
    with left:
        with st.container(border=True):
            st.subheader("市场资金摘要")
            render_status_card("资金状态", market_result["funds_evaluation"]["status"], "20日 / 50日均线")
            render_status_card("有效支持数量", market_result["funds_evaluation"]["support_count"], "规则统计")
    with middle:
        with st.container(border=True):
            st.subheader("市场情绪摘要")
            render_status_card("VIX 当前值", _display_value(market_result["sentiment_evaluation"]["vix_value"]), "^VIX")
            render_status_card("情绪状态", market_result["sentiment_evaluation"]["status"], "规则统计")
    with right:
        with st.container(border=True):
            st.subheader("宏观环境摘要")
            render_status_card("利率 / 通胀 / 就业", "待配置", "待配置 / 数据不足")
            render_status_card("宏观压制", "数据不足", "待人工确认")


def _render_funding_tab():
    market_result = _load_market_context()
    funds_eval = market_result["funds_evaluation"]

    st.subheader("市场资金监控")
    st.write("页面回答：当前市场资金环境是否支持风险偏好。")
    render_status_badge("yfinance")
    render_status_badge("待人工确认")
    _render_error_if_needed(market_result)
    _table(_market_fund_rows(market_result["market_funds"]))

    st.markdown("### 资金环境解释")
    columns = st.columns(3)
    for column, record in zip(columns, market_result["market_funds"]):
        with column:
            with st.container(border=True):
                st.subheader(record.get("asset_name", "数据不足"))
                render_status_card("状态", _asset_environment_status(record), record.get("symbol", ""))
                render_status_card("数据状态", record.get("data_status", "数据不足"), _display_value(record.get("updated_at")))

    with st.container(border=True):
        st.subheader("规则解释")
        st.write(funds_eval["reason"])
        st.caption(
            f"支持：{funds_eval['support_count']}；谨慎：{funds_eval['caution_count']}；"
            f"不支持：{funds_eval['weak_count']}；数据不足：{funds_eval['insufficient_count']}"
        )


def _render_sentiment_tab():
    market_result = _load_market_context()
    sentiment_eval = market_result["sentiment_evaluation"]

    st.subheader("市场情绪监控")
    st.write("页面回答：当前市场情绪是否过热或恐慌。")
    render_status_badge("yfinance")
    render_status_badge("待人工确认")
    _render_error_if_needed(market_result)
    _table(_market_sentiment_rows(market_result["market_sentiment"]))

    st.markdown("### 情绪环境解释")
    columns = st.columns(3)
    with columns[0]:
        render_status_card("VIX 当前值", _display_value(sentiment_eval["vix_value"]), "^VIX")
    with columns[1]:
        render_status_card("VIX 状态", sentiment_eval["status"], "内部启发式规则")
    with columns[2]:
        render_status_card("数据状态", market_result["market_sentiment"][0].get("data_status", "数据不足") if market_result["market_sentiment"] else "数据不足", "待人工确认")

    with st.container(border=True):
        st.subheader("规则解释")
        st.write(sentiment_eval["reason"])
        st.caption("VIX 阈值为项目内部市场环境启发式规则。")


def _render_macro_tab():
    st.subheader("宏观环境监控")
    st.write("页面回答：当前宏观环境是否支持风险偏好。")
    _table(
        [
            {
                "宏观变量": variable,
                "当前状态": "待配置 / 数据不足",
                "市场含义": "数据不足",
                "风险方向": "支持 / 中性 / 压制 / 数据不足",
                "数据状态": DATA_STATUS,
                "操作": "查看 / 标记 / 复查",
            }
            for variable in MACRO_VARIABLES
        ]
    )

    st.markdown("### 宏观摘要")
    columns = st.columns(5)
    summary_cards = [
        ("利率环境", "支持 / 中性 / 压制 / 数据不足", "待配置"),
        ("通胀环境", "支持 / 中性 / 压制 / 数据不足", "待配置"),
        ("就业环境", "支持 / 中性 / 压制 / 数据不足", "待配置"),
        ("GDP环境", "支持 / 中性 / 压制 / 数据不足", "待配置"),
        ("能源环境", "支持 / 中性 / 压制 / 数据不足", "待配置"),
    ]
    for column, (title, value, note) in zip(columns, summary_cards):
        with column:
            render_status_card(title, value, note)
    st.caption(f"数据状态：{DATA_STATUS}")


def _render_conclusion_tab():
    market_result = _load_market_context()
    overall = market_result["overall_evaluation"]

    st.subheader("市场环境结论")
    st.write("页面回答：当前市场环境状态如何。")
    render_status_badge("yfinance")
    render_status_badge("待人工确认")

    columns = st.columns(4)
    summary_cards = [
        ("整体状态", overall["status"], "规则计算"),
        ("资金状态", overall["funds_status"], "20日 / 50日均线"),
        ("情绪状态", overall["sentiment_status"], "^VIX"),
        ("更新时间", _latest_updated_at(market_result["market_funds"] + market_result["market_sentiment"]), "UTC"),
    ]
    for column, (title, value, note) in zip(columns, summary_cards):
        with column:
            render_status_card(title, value, note)

    st.markdown("### 分项结论")
    conclusion_columns = st.columns(3)
    for column, title, body in zip(
        conclusion_columns,
        ["市场资金结论", "市场情绪结论", "宏观环境结论"],
        [market_result["funds_evaluation"]["reason"], market_result["sentiment_evaluation"]["reason"], "宏观环境数据仍为待配置 / 数据不足。"],
    ):
        with column:
            with st.container(border=True):
                st.subheader(title)
                st.write(body)
                st.caption(f"数据状态：{DATA_STATUS}")

    with st.container(border=True):
        st.subheader("市场环境综合判断")
        st.write(overall["reason"])
        st.caption("当前结论为市场环境状态，需人工确认。")

    _button_row(["AI生成市场结论", "人工确认结论", "标记数据不足", "导出市场摘要"], "market_conclusion_action")


def _render_calendar_tab():
    st.subheader("时间提醒 / 事件日历")
    st.write("展示可能影响市场环境判断的重要事件。")
    _table(
        [
            {
                "事件": category,
                "日期": "待配置",
                "类别": category,
                "重要性": "高 / 中 / 低",
                "可能影响": "待配置 / 数据不足",
                "数据状态": DATA_STATUS,
                "操作": "查看 / 提醒 / 标记",
            }
            for category in EVENT_CATEGORIES
        ]
    )

    columns = st.columns(4)
    status_cards = [
        ("今日事件", "__", "待配置 / 数据不足"),
        ("本周重要事件", "__", "数据不足"),
        ("高优先级事件", "__", "待配置"),
        ("待人工确认事件", "__", AI_DRAFT),
    ]
    for column, (title, value, note) in zip(columns, status_cards):
        with column:
            render_status_card(title, value, note)

    _button_row(["新增事件", "创建提醒", "标记已处理", "导出事件日历"], "calendar_action")


def render():
    render_section_title(
        "市场资金 / 情绪 / 宏观监控模块",
        "独立市场风控系统，聚合资金、情绪与宏观环境状态。",
    )
    render_status_badge("yfinance")
    render_status_badge("待人工确认")
    render_status_badge("数据不足")
    market_result = _load_market_context()
    if market_result.get("error") and not market_result["market_funds"] and not market_result["market_sentiment"]:
        st.caption(market_result["error"])
    st.caption(f"全局数据状态：{DATA_STATUS}")

    tabs = st.tabs(TABS)
    for index, tab in enumerate(tabs):
        with tab:
            if index == 0:
                _render_main_tab()
            elif index == 1:
                _render_funding_tab()
            elif index == 2:
                _render_sentiment_tab()
            elif index == 3:
                _render_macro_tab()
            elif index == 4:
                _render_conclusion_tab()
            elif index == 5:
                _render_calendar_tab()
