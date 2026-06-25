import streamlit as st

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

MARKET_ASSETS = ["QQQ", "^IXIC", "BTC-USD"]
SENTIMENT_INDICATORS = ["^VIX"]
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


@st.cache_data(ttl=300, show_spinner=False)
def _load_market_context():
    return fetch_market_environment_data()


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
            "是否强于基准": _display_value(record.get("stronger_than_benchmark")),
            "风险偏好扩散": _display_value(record.get("risk_appetite_spread")),
            "数据状态": record.get("data_status", "数据不足"),
            "说明": record.get("note", "数据不足"),
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
            "说明": record.get("note", "数据不足"),
        }
        for record in market_sentiment
    ]


def _render_main_tab():
    market_result = _load_market_context()
    market_funds = market_result["market_funds"]
    market_sentiment = market_result["market_sentiment"]
    all_records = market_funds + market_sentiment
    pending_count = sum(1 for record in all_records if record.get("data_status") == "待人工确认")
    insufficient_count = sum(1 for record in all_records if record.get("data_status") == "数据不足")

    st.subheader("市场环境监控主页面")
    st.write("汇总市场资金、市场情绪和宏观环境，形成辅助风控判断。")
    _button_row(["刷新市场环境", "AI总结市场状态", "更新风险等级", "导出市场摘要"], "market_main_action")

    st.markdown("### 真实行情数据状态")
    data_columns = st.columns(5)
    data_cards = [
        ("数据来源", "yfinance", "QQQ / ^IXIC / BTC-USD / ^VIX"),
        ("市场资金记录", len(market_funds), "QQQ / ^IXIC / BTC-USD"),
        ("市场情绪记录", len(market_sentiment), "^VIX"),
        ("待人工确认", pending_count, "首次真实数据状态"),
        ("数据不足", insufficient_count, "失败或缺失时显示"),
    ]
    for column, (title, value, note) in zip(data_columns, data_cards):
        with column:
            render_status_card(title, value, note)

    if market_result["errors"]:
        st.caption("；".join(market_result["errors"]))
    if market_result.get("error") and not market_result["market_funds"] and not market_result["market_sentiment"]:
        st.caption(market_result["error"])

    columns = st.columns(5)
    status_cards = [
        ("市场资金状态", "支持 / 谨慎 / 不支持", "待配置 / 数据不足"),
        ("市场情绪状态", "低风险 / 中性 / 高风险", "数据不足"),
        ("宏观环境状态", "支持 / 中性 / 压制", "待配置"),
        ("综合风险等级", "低 / 中 / 高", AI_DRAFT),
        ("环境支持度", "支持 / 谨慎 / 不支持", "辅助风控判断"),
    ]
    for column, (title, value, note) in zip(columns, status_cards):
        with column:
            render_status_card(title, value, note)

    st.markdown("### 三类环境摘要")
    left, middle, right = st.columns(3)
    with left:
        with st.container(border=True):
            st.subheader("市场资金摘要")
            render_status_card("风险偏好扩散", "数据不足", DATA_STATUS)
            render_status_card("均线结构", "待人工确认", "20日 / 50日均线")
    with middle:
        with st.container(border=True):
            st.subheader("市场情绪摘要")
            render_status_card("恐慌程度", _display_value(market_sentiment[0].get("current_value") if market_sentiment else None), "^VIX")
            render_status_card("数据状态", market_sentiment[0].get("data_status", "数据不足") if market_sentiment else "数据不足", "yfinance")
    with right:
        with st.container(border=True):
            st.subheader("宏观环境摘要")
            render_status_card("利率 / 通胀 / 就业", "待配置", "待配置 / 数据不足")
            render_status_card("宏观压制", "数据不足", "待人工确认")

    st.markdown("### 当前环境状态")
    bottom_columns = st.columns(2)
    with bottom_columns[0]:
        render_status_card("当前风险偏好方向", "上升 / 下降 / 分化", "待配置 / 数据不足")
    with bottom_columns[1]:
        render_status_card("当前结论", "数据不足 / 待配置 / AI草稿 / 待人工确认", "待人工确认")


def _render_funding_tab():
    market_result = _load_market_context()

    st.subheader("市场资金监控")
    st.write("页面回答：当前市场资金是否支持交易？")
    render_status_badge("yfinance")
    render_status_badge("待人工确认")
    if market_result["errors"]:
        st.caption("；".join(market_result["errors"]))
    if market_result.get("error") and not market_result["market_funds"]:
        st.caption(market_result["error"])
    _table(_market_fund_rows(market_result["market_funds"]))

    with st.container(border=True):
        st.subheader("风险偏好判断规则")
        st.write("如果 QQQ、纳斯达克指数、比特币均站上 20日 / 50日均线，且均线方向向上，说明风险偏好较强。")
        st.write("如果只有部分资产站上均线，说明风险偏好分化。")
        st.write("如果多数资产跌破 20日 / 50日均线，说明风险偏好下降。")
        st.caption(f"数据状态：{DATA_STATUS}")


def _render_sentiment_tab():
    market_result = _load_market_context()

    st.subheader("市场情绪监控")
    st.write("页面回答：当前市场情绪是否过热或恐慌？")
    render_status_badge("yfinance")
    render_status_badge("待人工确认")
    if market_result["errors"]:
        st.caption("；".join(market_result["errors"]))
    if market_result.get("error") and not market_result["market_sentiment"]:
        st.caption(market_result["error"])
    _table(_market_sentiment_rows(market_result["market_sentiment"]))

    st.markdown("### 指标解释")
    columns = st.columns(3)
    explanations = [
        ("VIX", "用于观察市场恐慌程度"),
        ("Put / Call", "用于观察期权市场风险偏好"),
        ("数据状态", DATA_STATUS),
    ]
    for column, (title, body) in zip(columns, explanations):
        with column:
            with st.container(border=True):
                st.subheader(title)
                st.write(body)
                st.caption(f"数据状态：{DATA_STATUS}")

    with st.container(border=True):
        st.subheader("AI市场情绪摘要")
        st.write(AI_DRAFT)
        st.write("当前仅展示 ^VIX，结论需人工确认。")
        st.caption(f"数据状态：{DATA_STATUS}")


def _render_macro_tab():
    st.subheader("宏观环境监控")
    st.write("页面回答：当前宏观环境是否支持交易？")
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
    records = market_result["market_funds"] + market_result["market_sentiment"]
    all_insufficient = bool(records) and all(record.get("data_status") == "数据不足" for record in records)

    st.subheader("市场环境结论")
    st.write("页面回答：当前市场是否支持交易？")
    render_status_badge("yfinance")
    render_status_badge("待人工确认")

    columns = st.columns(4)
    if all_insufficient:
        summary_cards = [
            ("风险等级", "数据不足", "yfinance"),
            ("环境支持度", "数据不足", "待人工确认"),
            ("风险偏好方向", "数据不足", "yfinance"),
            ("当前结论", "数据不足", "待人工确认"),
        ]
    else:
        summary_cards = [
            ("风险等级", "数据不足", "待人工确认"),
            ("环境支持度", "数据不足", "待人工确认"),
            ("风险偏好方向", "数据不足", "待人工确认"),
            ("当前结论", "数据不足 / AI草稿 / 待人工确认", "需人工确认"),
        ]
    for column, (title, value, note) in zip(columns, summary_cards):
        with column:
            render_status_card(title, value, note)

    st.markdown("### 分项结论")
    conclusion_columns = st.columns(3)
    for column, title in zip(conclusion_columns, ["市场资金结论", "市场情绪结论", "宏观环境结论"]):
        with column:
            with st.container(border=True):
                st.subheader(title)
                st.write(AI_DRAFT)
                st.write("当前结论需人工确认。")
                st.caption(f"数据状态：{DATA_STATUS}")

    with st.container(border=True):
        st.subheader("市场环境综合判断")
        st.write(AI_DRAFT)
        st.write("综合判断需人工确认。")
        st.caption(f"数据状态：{DATA_STATUS}")

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


def _render_placeholder_tab(title):
    st.subheader(title)
    st.write("本页为 Phase 2B-5A 简洁占位，后续阶段再扩展正式 UI。")
    _table(
        [
            {
                "分类": title,
                "指标": "待配置 / 数据不足",
                "当前状态": "数据不足",
                "数据状态": DATA_STATUS,
                "evidence_id": "待配置",
            }
        ]
    )


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
            else:
                _render_placeholder_tab(TABS[index])
