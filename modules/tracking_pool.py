import streamlit as st

from core.utils import render_demo_notice, render_section_title, render_status_badge, render_status_card


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

DATA_STATUS = "示例数据 / 待配置 / 数据不足"
AI_DRAFT = "AI草稿 / 待人工确认"

VARIABLE_ENTRIES = [
    "主题变量",
    "公司变量",
    "财务变量",
    "催化剂变量",
    "风险变量",
    "数据新鲜度",
]

THEME_VARIABLES = [
    "主题热度",
    "主题资金流向",
    "主题是否过热",
    "主题是否衰退",
    "是否出现新证据",
    "主题是否被证伪",
]

COMPANY_VARIABLES = [
    "业务边界是否变化",
    "产品路线是否变化",
    "订单是否变化",
    "客户是否变化",
    "管理层表述是否变化",
    "收入暴露度是否变化",
]

FINANCIAL_VARIABLES = [
    "收入增长",
    "毛利率",
    "营业利润率",
    "自由现金流",
    "订单",
    "Backlog",
    "指引",
    "库存",
    "应收账款",
    "资本开支",
]

CATALYST_ITEMS = [
    "财报",
    "投资者日",
    "产品发布",
    "客户公告",
    "政府合同",
    "政策变化",
    "行业会议",
    "管理层讲话",
    "重要订单",
]

RISK_ITEMS = [
    "客户流失",
    "订单取消",
    "毛利率恶化",
    "竞争对手突破",
    "技术路线变化",
    "监管风险",
    "估值过高",
    "主题退潮",
    "管理层下调指引",
]

FRESHNESS_CHECK_ITEMS = [
    "上次投研时间",
    "上次证据更新时间",
    "上次财报更新时间",
    "上次雷达更新时间",
    "上次人工复查时间",
]

ALERT_TYPES = [
    "新证据",
    "新风险",
    "反证",
    "财报更新",
    "管理层表述变化",
    "订单变化",
]

REVIEW_REASONS = [
    "新证据",
    "新风险",
    "数据过期",
    "财报更新",
    "主题退潮",
    "策略标注失效",
]


def _table(rows):
    st.dataframe(rows, width="stretch", hide_index=True)
    st.caption(f"数据状态：{DATA_STATUS}")


def _button_row(labels, prefix):
    columns = st.columns(len(labels))
    for index, (column, label) in enumerate(zip(columns, labels), start=1):
        with column:
            st.button(label, key=f"{prefix}_{index}", width="stretch")


def _variable_rows(items):
    return [
        {
            "变量": item,
            "当前状态": "示例数据 / 待配置",
            "变化方向": "数据不足",
            "证据/数据来源": "待配置",
            "操作": "查看 / 确认 / 复查",
        }
        for item in items
    ]


def _render_main_tab():
    st.subheader("重点跟踪池主页面")
    st.write("集中查看高质量标的、核心变量、风险变化和策略价格标注。")
    _button_row(
        ["同步深度投研", "刷新变量", "AI总结变化", "更新策略标注", "生成复查任务", "导出日报"],
        "tracking_main_action",
    )

    status_columns = st.columns(5)
    status_cards = [
        ("核心跟踪", "__", "示例数据 / 待配置"),
        ("重点跟踪", "__", "数据不足"),
        ("需要复查", "__", AI_DRAFT),
        ("风险预警", "__", "待配置"),
        ("可交易观察", "__", "仅为观察状态"),
    ]
    for column, (title, value, note) in zip(status_columns, status_cards):
        with column:
            render_status_card(title, value, note)

    st.markdown("### 筛选区")
    filters = st.columns([1, 1, 1, 1, 1.2, 0.9, 0.9])
    with filters[0]:
        st.selectbox("跟踪等级", ["全部", "核心跟踪", "重点跟踪", "观察"], key="tracking_filter_level")
    with filters[1]:
        st.selectbox("状态", ["全部", "正常", "需要复查", "风险预警"], key="tracking_filter_status")
    with filters[2]:
        st.text_input("主题", placeholder="待配置", key="tracking_filter_theme")
    with filters[3]:
        st.selectbox("量化状态", ["全部", "未触发", "已触发", "禁止"], key="tracking_filter_quant")
    with filters[4]:
        st.text_input("搜索股票", placeholder="示例数据 / 待配置", key="tracking_filter_search")
    with filters[5]:
        st.button("应用筛选", key="tracking_filter_apply", width="stretch")
    with filters[6]:
        st.button("重置", key="tracking_filter_reset", width="stretch")

    st.markdown("### 跟踪池工作台")
    left, middle, right = st.columns([1.15, 1.2, 1])
    with left:
        with st.container(border=True):
            st.subheader("股票列表")
            _table(
                [
                    {
                        "股票": f"股票{i}",
                        "主题": "示例数据 / 待配置",
                        "等级": "重点跟踪",
                        "状态": "数据不足",
                    }
                    for i in range(1, 6)
                ]
            )
    with middle:
        with st.container(border=True):
            st.subheader("核心变量跟踪")
            variable_columns = st.columns(2)
            for index, variable in enumerate(VARIABLE_ENTRIES):
                with variable_columns[index % 2]:
                    render_status_card(variable, "待配置", "示例数据 / 待配置")
    with right:
        with st.container(border=True):
            st.subheader("策略价格标注")
            st.write("当前股票：股票1")
            st.write("当前状态：示例数据 / 待配置")
            st.write("策略状态：未触发 / 已触发 / 禁止")
            st.write("买入价格：____")
            st.write("止盈价格：____")
            st.write("止损价格：____")
            render_status_badge("策略标注")
            st.caption(f"数据状态：{DATA_STATUS}")
            _button_row(
                ["保存策略标注", "标记可交易观察", "标记不适合交易", "创建复查任务"],
                "strategy_annotation_action",
            )


def _render_theme_tab():
    st.subheader("主题变量")
    st.write("页面回答：这个股票对应的行业叙事还在不在？")
    info_columns = st.columns(4)
    info_cards = [
        ("当前股票", "股票1", "示例数据"),
        ("当前主题", "____", "待配置"),
        ("跟踪等级", "重点跟踪", "示例数据"),
        ("数据状态", DATA_STATUS, "未接入真实数据"),
    ]
    for column, (title, value, note) in zip(info_columns, info_cards):
        with column:
            render_status_card(title, value, note)

    _button_row(["刷新主题变量", "AI总结主题变化", "创建复查任务", "保存变量状态"], "theme_variable_top_action")

    st.markdown("### 主题变量表")
    _table(_variable_rows(THEME_VARIABLES))

    with st.container(border=True):
        st.subheader("主题变量解释")
        st.write(AI_DRAFT)
        st.write("主题变量说明：示例数据 / 待配置。当前没有真实数据源，不能形成事实结论。")
        st.caption(f"数据状态：{DATA_STATUS}")

    _button_row(["确认变量状态", "标记异常", "创建复查任务"], "theme_variable_bottom_action")


def _render_company_tab():
    st.subheader("公司变量")
    st.write("页面回答：这家公司是否还符合原来的投研逻辑？")
    _button_row(["刷新公司变量", "AI总结公司变化", "新增公司证据", "创建复查任务"], "company_variable_top_action")

    st.markdown("### 公司变量表")
    _table(_variable_rows(COMPANY_VARIABLES))

    with st.container(border=True):
        st.subheader("公司变量摘要")
        columns = st.columns(5)
        summary_cards = [
            ("业务边界", "正常 / 变化 / 待验证", "示例数据 / 待配置"),
            ("产品路线", "____", "数据不足"),
            ("订单变化", "____", "待配置"),
            ("客户变化", "____", AI_DRAFT),
            ("管理层表述", "____", "待人工确认"),
        ]
        for column, (title, value, note) in zip(columns, summary_cards):
            with column:
                render_status_card(title, value, note)
        st.caption(f"数据状态：{DATA_STATUS}")

    render_status_badge("复查触发")


def _render_financial_tab():
    st.subheader("财务变量")
    st.write("页面回答：公司是否正在兑现产业逻辑？")
    info_columns = st.columns(4)
    info_cards = [
        ("当前股票", "股票1", "示例数据"),
        ("当前主题", "____", "待配置"),
        ("财务状态", "待验证 / 部分兑现 / 已兑现 / 证据不足", "数据不足"),
        ("数据状态", DATA_STATUS, "未接入真实数据"),
    ]
    for column, (title, value, note) in zip(info_columns, info_cards):
        with column:
            render_status_card(title, value, note)

    _button_row(["刷新财务变量", "AI总结财务变化", "新增财务证据", "创建复查任务"], "financial_variable_action")

    st.markdown("### 财务变量表")
    _table(_variable_rows(FINANCIAL_VARIABLES))

    with st.container(border=True):
        st.subheader("财务变量解释")
        st.write(AI_DRAFT)
        st.write("财务变量说明：示例数据 / 待配置。当前没有真实财务数据源，不能形成公司结论。")
        st.caption(f"数据状态：{DATA_STATUS}")


def _render_catalyst_tab():
    st.subheader("催化剂变量")
    st.write("页面回答：未来有哪些事件可能改变判断？")
    _button_row(["新增催化剂", "刷新事件日历", "AI总结催化剂", "创建提醒"], "catalyst_action")

    st.markdown("### 催化剂表")
    _table(
        [
            {
                "催化剂": item,
                "事件日期": "待配置",
                "影响方向": "数据不足",
                "重要性": "高 / 中 / 低",
                "状态": "示例数据 / 待配置",
                "操作": "查看 / 提醒 / 复查",
            }
            for item in CATALYST_ITEMS
        ]
    )

    with st.container(border=True):
        st.subheader("催化剂摘要")
        columns = st.columns(4)
        summary_cards = [
            ("最近催化剂", "____", "示例数据 / 待配置"),
            ("最高重要性", "高 / 中 / 低", "数据不足"),
            ("是否需要复查", "是 / 否 / 待判断", AI_DRAFT),
            ("数据状态", DATA_STATUS, "未接入真实数据"),
        ]
        for column, (title, value, note) in zip(columns, summary_cards):
            with column:
                render_status_card(title, value, note)


def _render_risk_tab():
    st.subheader("风险变量")
    st.write("页面回答：哪些因素可能推翻原来的逻辑？")
    _button_row(["新增风险", "AI查找反证", "更新风险等级", "创建复查任务"], "risk_variable_action")

    st.markdown("### 风险变量表")
    _table(
        [
            {
                "风险": item,
                "风险等级": "高 / 中 / 低",
                "当前状态": "示例数据 / 待配置",
                "证据/数据来源": "数据不足",
                "操作": "查看 / 标记 / 复查",
            }
            for item in RISK_ITEMS
        ]
    )

    with st.container(border=True):
        st.subheader("风险摘要")
        columns = st.columns(4)
        summary_cards = [
            ("最高风险等级", "高 / 中 / 低", "数据不足"),
            ("是否存在重大反证", "是 / 否 / 待验证", "待配置"),
            ("是否需要重新研究", "是 / 否 / 待判断", AI_DRAFT),
            ("缺失证据", "____", "示例数据 / 待配置"),
        ]
        for column, (title, value, note) in zip(columns, summary_cards):
            with column:
                render_status_card(title, value, note)
        st.caption(f"数据状态：{DATA_STATUS}")

    render_status_badge("风险复查")


def _render_freshness_tab():
    st.subheader("数据新鲜度")
    st.write("页面回答：这份研究是否过期？")
    columns = st.columns(6)
    status_cards = [
        ("上次投研时间", "待配置", "示例数据 / 待配置"),
        ("上次证据更新时间", "待配置", "数据不足"),
        ("上次财报更新时间", "待配置", "示例数据 / 待配置"),
        ("上次雷达更新时间", "待配置", "待配置"),
        ("上次人工复查时间", "待配置", AI_DRAFT),
        ("当前新鲜度状态", "正常 / 接近过期 / 需要复查", "未接入真实数据"),
    ]
    for column, (title, value, note) in zip(columns, status_cards):
        with column:
            render_status_card(title, value, note)

    st.markdown("### 新鲜度检查表")
    _table(
        [
            {
                "检查项": item,
                "上次更新时间": "待配置",
                "有效期": "示例数据 / 待配置",
                "当前状态": "数据不足",
                "操作": "查看 / 标记 / 复查",
            }
            for item in FRESHNESS_CHECK_ITEMS
        ]
    )
    _button_row(["刷新数据新鲜度", "标记已复查", "创建复查任务", "查看过期原因"], "freshness_action")
    render_status_badge("需要复查")


def _render_strategy_detail_tab():
    st.subheader("量化策略标注详情")
    render_status_badge("策略标注")

    left, right = st.columns([1, 1])
    with left:
        with st.container(border=True):
            st.subheader("策略标注表单")
            st.text_input("当前股票", value="股票1", key="strategy_current_stock")
            st.text_input("当前主题", value="____", key="strategy_current_theme")
            st.selectbox("当前跟踪等级", ["核心跟踪", "重点跟踪", "观察"], key="strategy_tracking_level")
            st.selectbox("策略状态", ["未触发", "已触发", "禁止"], key="strategy_status")
            st.text_input("买入价格", value="____", key="strategy_buy_price")
            st.text_input("止盈价格", value="____", key="strategy_take_profit_price")
            st.text_input("止损价格", value="____", key="strategy_stop_loss_price")
            st.text_area("策略失效条件", value="示例数据 / 待配置", key="strategy_invalid_condition")
            st.selectbox("风险等级", ["高", "中", "低", "待配置"], key="strategy_risk_level")
            st.text_area("人工备注", value="数据不足", key="strategy_human_note")
            st.caption(f"数据状态：{DATA_STATUS}")
    with right:
        with st.container(border=True):
            st.subheader("策略检查表")
            checklist_items = [
                "是否来自重点跟踪池",
                "是否完成深度投研",
                "是否有最新证据",
                "是否存在重大风险",
                "是否需要复查",
                "是否允许进入可交易观察",
            ]
            for index, item in enumerate(checklist_items):
                st.checkbox(item, value=False, key=f"strategy_check_{index}")
            st.caption(f"检查状态：{DATA_STATUS}")

    _button_row(["保存策略标注", "标记可交易观察", "标记禁止交易", "创建复查任务"], "strategy_detail_action")


def _render_alert_tab():
    st.subheader("新证据 / 新风险提醒")
    st.write("集中处理新证据、新风险、反证和关键披露变化。")
    columns = st.columns(5)
    status_cards = [
        ("新证据数量", "__", "示例数据 / 待配置"),
        ("新风险数量", "__", "数据不足"),
        ("高优先级提醒", "__", "待配置"),
        ("待人工处理", "__", AI_DRAFT),
        ("已处理", "__", "示例数据 / 待配置"),
    ]
    for column, (title, value, note) in zip(columns, status_cards):
        with column:
            render_status_card(title, value, note)

    st.markdown("### 提醒列表")
    _table(
        [
            {
                "编号": index,
                "类型": item,
                "新内容摘要": "示例数据 / 待配置",
                "关联变量": "数据不足",
                "影响方向": "待配置",
                "优先级": "高 / 中 / 低",
                "evidence_id": f"EVID____-{index}",
                "人工状态": "待人工处理",
                "操作": "查看 / 绑定 / 复查",
            }
            for index, item in enumerate(ALERT_TYPES, start=1)
        ]
    )

    left, right = st.columns(2)
    with left:
        with st.container(border=True):
            st.subheader("新证据 / 新风险原文摘要")
            st.write("示例数据 / 待配置")
            st.write("当前未接入真实来源，不能形成事实结论。")
            st.caption(f"数据状态：{DATA_STATUS}")
    with right:
        with st.container(border=True):
            st.subheader("AI影响判断")
            st.write(AI_DRAFT)
            st.write("影响方向与优先级均需人工确认。")
            st.caption(f"数据状态：{DATA_STATUS}")

    _button_row(["确认重要", "标记忽略", "创建复查任务", "绑定证据", "查看来源"], "alert_action")


def _render_review_task_tab():
    st.subheader("复查任务")
    st.write("管理由新证据、新风险、数据过期、财报更新、主题退潮和策略标注失效触发的复查任务。")
    _button_row(["新建复查任务", "批量标记完成", "按优先级排序", "导出复查清单"], "review_top_action")

    columns = st.columns(4)
    status_cards = [
        ("待复查", "__", "示例数据 / 待配置"),
        ("高优先级", "__", "数据不足"),
        ("已完成", "__", "待配置"),
        ("已逾期", "__", AI_DRAFT),
    ]
    for column, (title, value, note) in zip(columns, status_cards):
        with column:
            render_status_card(title, value, note)

    st.markdown("### 复查任务表")
    _table(
        [
            {
                "任务编号": f"REV____-{index}",
                "股票": "股票1",
                "主题": "示例数据 / 待配置",
                "触发原因": reason,
                "优先级": "高 / 中 / 低",
                "截止时间": "待配置",
                "当前状态": "数据不足",
                "操作": "查看 / 处理 / 完成",
            }
            for index, reason in enumerate(REVIEW_REASONS, start=1)
        ]
    )

    st.markdown("### 复查结论区域")
    with st.container(border=True):
        st.text_area("复查结论", value="示例数据 / 待配置", key="review_conclusion")
        columns = st.columns(4)
        with columns[0]:
            st.selectbox("是否维持重点跟踪", ["待判断", "是", "否"], key="review_keep_tracking")
        with columns[1]:
            st.selectbox("是否降级观察", ["待判断", "是", "否"], key="review_downgrade")
        with columns[2]:
            st.selectbox("是否剔除", ["待判断", "是", "否"], key="review_remove")
        with columns[3]:
            st.selectbox("是否需要重新深度投研", ["待判断", "是", "否"], key="review_deep_research")
        st.text_area("人工备注", value="数据不足", key="review_human_note")
        st.caption(f"数据状态：{DATA_STATUS}")

    _button_row(["保存复查结论", "维持重点跟踪", "降级观察", "剔除", "返回深度投研"], "review_bottom_action")


def _render_placeholder_tab(title):
    st.subheader(title)
    st.write("本页为 Phase 2B-4A 简洁占位，后续阶段再扩展正式 UI。")
    _table(
        [
            {
                "股票": "示例数据 / 待配置",
                "主题": "示例数据 / 待配置",
                "变量类型": title,
                "当前状态": "数据不足",
                "evidence_id": "待配置",
                "复查状态": "待配置",
            }
        ]
    )


def render():
    render_section_title(
        "重点跟踪池 / 量化策略标注模块",
        "保存高质量标的，持续跟踪核心变量，接收新证据和新风险，提醒重新研究，并在重点跟踪个股上标注买入价格、止盈价格、止损价格。",
    )
    render_demo_notice()
    st.caption(f"全局数据状态：{DATA_STATUS}")

    tabs = st.tabs(TABS)
    for index, tab in enumerate(tabs):
        with tab:
            if index == 0:
                _render_main_tab()
            elif index == 1:
                _render_theme_tab()
            elif index == 2:
                _render_company_tab()
            elif index == 3:
                _render_financial_tab()
            elif index == 4:
                _render_catalyst_tab()
            elif index == 5:
                _render_risk_tab()
            elif index == 6:
                _render_freshness_tab()
            elif index == 7:
                _render_strategy_detail_tab()
            elif index == 8:
                _render_alert_tab()
            elif index == 9:
                _render_review_task_tab()
            else:
                _render_placeholder_tab(TABS[index])
