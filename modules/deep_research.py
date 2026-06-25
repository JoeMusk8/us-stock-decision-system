import streamlit as st

from core.utils import render_demo_notice, render_section_title, render_status_badge, render_status_card


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

DATA_STATUS = "示例数据 / 待配置 / 数据不足"
AI_DRAFT = "AI草稿 / 待人工确认"

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

BUSINESS_BOUNDARY_ITEMS = [
    "公司主营业务",
    "主要产品",
    "收入分部",
    "客户类型",
    "主题相关业务是否核心业务",
    "是否只是边缘业务",
    "公司是否明确披露该方向",
]

THEME_BENEFIT_ITEMS = [
    "业务相关性",
    "收入暴露度",
    "订单 / 客户证据",
    "管理层是否确认该方向",
    "产业链节点匹配度",
    "是否只是概念相关",
]

CHAIN_POSITION_ITEMS = [
    "所属产业链层级",
    "对应产业链节点",
    "是否处于核心瓶颈节点",
    "是否具备稀缺性",
    "是否难以替代",
    "是否具备议价能力",
]

FINANCIAL_REALIZATION_ITEMS = [
    "收入增长",
    "收入分部变化",
    "毛利率变化",
    "订单 / Backlog",
    "管理层指引",
    "现金流",
]

CUSTOMER_ORDER_CAPEX_ITEMS = [
    "客户证据",
    "订单证据",
    "CapEx相关性",
    "公司扩产",
    "客户需求持续性",
]

COMPETITION_ITEMS = [
    "主要竞争对手",
    "技术壁垒",
    "客户认证壁垒",
    "规模优势",
    "替代风险",
    "价格竞争风险",
]

RISK_COUNTER_ITEMS = [
    "主题相关业务可能不是核心业务",
    "公司没有明确披露该方向",
    "订单证据不足",
    "竞争对手更强",
]

CLAIM_ITEMS = [
    "公司主营业务包括____",
    "公司业务与该主题相关",
    "相关业务属于核心业务",
    "公司明确披露该方向",
]

REPORT_SCORE_ITEMS = [
    "公司业务边界清晰度",
    "主题受益验证",
    "产业链位置验证",
    "财务兑现验证",
    "客户/订单/CapEx证据",
    "竞争格局",
    "风险与反证",
]


def _table(rows):
    st.dataframe(rows, width="stretch", hide_index=True)
    st.caption(f"数据状态：{DATA_STATUS}")


def _button_row(labels, prefix):
    columns = st.columns(len(labels))
    for index, (column, label) in enumerate(zip(columns, labels), start=1):
        with column:
            st.button(label, key=f"{prefix}_{index}", width="stretch")


def _verification_rows(items, mode="evidence_status"):
    rows = []
    for index, item in enumerate(items, start=1):
        row = {"验证项": item, "当前判断": "示例数据 / 待配置"}
        if mode == "count":
            row.update(
                {
                    "证据数量": "__",
                    "evidence_id": f"EVID____-{index}",
                    "状态": "数据不足",
                }
            )
        else:
            row.update(
                {
                    "证据状态": "数据不足",
                    "evidence_id": f"EVID____-{index}",
                    "操作": "绑定证据 / 人工确认",
                }
            )
        rows.append(row)
    return rows


def _ai_summary_card(title, items):
    with st.container(border=True):
        st.subheader(title)
        st.write(AI_DRAFT)
        for label, value in items:
            st.write(f"**{label}：** {value}")
        st.caption(f"数据状态：{DATA_STATUS}")


def _task_card(index):
    with st.container(border=True):
        st.markdown(f"**股票任务：{index}**")
        ticker = st.text_input(
            "股票输入框",
            key=f"deep_ticker_{index}",
            placeholder="待配置",
        )
        theme = st.text_input(
            "研究主题输入框",
            key=f"deep_theme_{index}",
            placeholder="待配置",
        )
        source = st.selectbox(
            "来源",
            ["手动", "选股雷达"],
            key=f"deep_source_{index}",
        )
        if not ticker and not theme:
            default_status = "未输入"
        elif ticker and theme:
            default_status = "待创建"
        else:
            default_status = "证据不足"
        status = st.selectbox(
            "状态",
            ["未输入", "待创建", "证据收集中", "验证中", "证据不足", "已完成"],
            index=["未输入", "待创建", "证据收集中", "验证中", "证据不足", "已完成"].index(default_status),
            key=f"deep_status_{index}",
        )
        st.caption(f"来源：{source}；状态：{status}；数据状态：{DATA_STATUS}")
        col_a, col_b = st.columns(2)
        with col_a:
            st.button("进入投研", key=f"deep_enter_{index}", width="stretch")
        with col_b:
            st.button("输入股票", key=f"deep_input_{index}", width="stretch")


def _render_task_pool_tab():
    st.subheader("股票任务池总览")
    st.write("最多支持 15 只股票，所有深度投研任务必须绑定“股票 + 研究主题”。")
    render_status_badge("股票 + 主题")

    _button_row(
        ["从选股雷达导入", "手动新增股票", "批量创建投研任务", "AI收集证据", "生成投研报告", "同步重点跟踪池"],
        "deep_pool_action",
    )

    status_columns = st.columns(5)
    status_cards = [
        ("已输入股票", "__", "示例数据 / 待配置"),
        ("待创建任务", "__", "数据不足"),
        ("证据收集中", "__", AI_DRAFT),
        ("验证中", "__", "待人工确认"),
        ("已完成", "__", "示例数据 / 待配置"),
    ]
    for column, (title, value, note) in zip(status_columns, status_cards):
        with column:
            render_status_card(title, value, note)

    st.markdown("### 股票任务卡片")
    for row_index in range(5):
        columns = st.columns(3)
        for column_index, column in enumerate(columns):
            task_index = row_index * 3 + column_index + 1
            with column:
                _task_card(task_index)


def _render_single_stock_tab():
    st.subheader("单股投研工作台总览")
    st.write("围绕单一“股票 + 研究主题”任务，集中查看证据、Claim 与研究状态。")

    info_columns = st.columns(3)
    with info_columns[0]:
        render_status_card("当前股票", "____", "示例数据 / 待配置")
    with info_columns[1]:
        render_status_card("研究主题", "____", "示例数据 / 待配置")
    with info_columns[2]:
        render_status_card("来源", "选股雷达 / 手动输入", "数据不足")

    _button_row(
        ["AI收集证据", "AI提取Claim", "生成投研报告", "保存当前任务", "进入重点跟踪池", "剔除", "回写上游"],
        "single_stock_action",
    )

    status_columns = st.columns(5)
    status_cards = [
        ("证据数量", "__", "数据不足"),
        ("A/B级证据", "__", "待配置"),
        ("Claim数量", "__", AI_DRAFT),
        ("待确认Claim", "__", "待人工确认"),
        ("当前等级", "未评级", "不代表交易建议"),
    ]
    for column, (title, value, note) in zip(status_columns, status_cards):
        with column:
            render_status_card(title, value, note)

    left, right = st.columns([1.35, 1])
    with left:
        st.markdown("### 本次深度投研需要验证的问题")
        _table(
            [
                {
                    "序号": index,
                    "验证问题": question,
                    "当前状态": "数据不足",
                    "操作": "收集证据 / 人工确认",
                }
                for index, question in enumerate(RESEARCH_QUESTIONS, start=1)
            ]
        )
    with right:
        st.markdown("### 投研结论面板")
        with st.container(border=True):
            conclusion_rows = [
                ("当前股票", "____"),
                ("当前主题", "____"),
                ("当前状态", "数据不足"),
                ("当前研究等级", "未评级"),
                ("证据状态", "待配置"),
                ("Claim状态", AI_DRAFT),
                ("核心结论", "待生成 / AI草稿 / 待人工确认"),
            ]
            for label, value in conclusion_rows:
                st.write(f"**{label}：** {value}")
            st.caption(f"数据状态：{DATA_STATUS}")
        _button_row(
            ["生成研究等级", "生成研究报告", "进入重点跟踪池", "标记证据不足", "剔除", "回写上游模块"],
            "single_stock_panel_action",
        )


def _render_business_boundary_tab():
    st.subheader("公司业务边界验证")
    st.write("验证公司主营业务、产品、收入分部、客户类型和主题相关业务边界。")
    _table(_verification_rows(BUSINESS_BOUNDARY_ITEMS))
    _ai_summary_card(
        "AI业务边界摘要",
        [
            ("业务边界判断", "AI草稿 / 待人工确认"),
            ("证据缺口", "数据不足"),
            ("人工确认状态", "待配置"),
        ],
    )
    _button_row(["AI总结业务边界", "绑定证据", "确认业务边界", "标记证据不足"], "business_boundary_action")


def _render_theme_benefit_tab():
    st.subheader("主题受益验证")
    st.write("验证公司是否真实受益于当前研究主题，并区分业务受益与概念相关。")
    _table(_verification_rows(THEME_BENEFIT_ITEMS, mode="count"))
    _ai_summary_card(
        "AI受益逻辑草稿",
        [
            ("受益逻辑", "AI草稿 / 待人工确认"),
            ("是否需要继续验证", "数据不足"),
            ("人工确认状态", "待配置"),
        ],
    )
    _button_row(["AI生成受益逻辑", "确认受益成立", "标记部分成立", "标记不成立"], "theme_benefit_action")


def _render_chain_position_tab():
    st.subheader("产业链位置验证")
    st.write("验证公司对应的产业链层级、节点、稀缺性、替代难度和议价能力。")
    _table(_verification_rows(CHAIN_POSITION_ITEMS))
    with st.container(border=True):
        st.subheader("产业链位置摘要")
        summary_columns = st.columns(2)
        with summary_columns[0]:
            render_status_card("当前产业链层级", "____", "示例数据 / 待配置")
            render_status_card("对应节点", "____", "数据不足")
            render_status_card("节点等级", "核心瓶颈 / 重要受益 / 普通节点", "待人工确认")
        with summary_columns[1]:
            render_status_card("证据数量", "__", "示例数据 / 待配置")
            render_status_card("证据ID", "EVID____", "待配置")
            render_status_card("AI说明", AI_DRAFT, "需要人工确认")
    _button_row(["绑定产业链节点", "AI解释产业链位置", "确认产业链位置", "标记待验证"], "chain_position_action")


def _render_financial_realization_tab():
    st.subheader("财务兑现验证")
    st.write("验证主题相关业务是否已经在收入、毛利率、订单、指引和现金流中体现。")
    _table(_verification_rows(FINANCIAL_REALIZATION_ITEMS))
    with st.container(border=True):
        st.subheader("财务兑现摘要")
        columns = st.columns(3)
        with columns[0]:
            render_status_card("财务证据状态", "待验证 / 部分 / 充足", "示例数据 / 待配置")
        with columns[1]:
            render_status_card("是否已兑现", "是 / 否 / 无法判断", "数据不足")
        with columns[2]:
            render_status_card("缺失信息", "____", AI_DRAFT)
        st.caption(f"数据状态：{DATA_STATUS}")
    _button_row(["导入财务证据", "AI总结财务兑现", "确认财务支持", "标记尚未兑现"], "financial_realization_action")


def _render_customer_order_capex_tab():
    st.subheader("客户 / 订单 / CapEx 验证")
    st.write("验证客户、订单、CapEx、扩产和需求持续性的证据状态。")
    _table(_verification_rows(CUSTOMER_ORDER_CAPEX_ITEMS, mode="count"))
    with st.container(border=True):
        st.subheader("客户 / 订单 / CapEx 摘要")
        columns = st.columns(4)
        summary_items = [
            ("客户证据", "____", "数据不足"),
            ("订单证据", "____", "待配置"),
            ("CapEx证据", "____", "示例数据 / 待配置"),
            ("缺失证据", "____", AI_DRAFT),
        ]
        for column, (title, value, note) in zip(columns, summary_items):
            with column:
                render_status_card(title, value, note)
        st.caption(f"数据状态：{DATA_STATUS}")
    _button_row(["AI查找客户/订单证据", "绑定证据", "确认支持", "标记证据不足"], "customer_order_capex_action")


def _render_competition_tab():
    st.subheader("竞争格局验证")
    st.write("验证主要竞争对手、技术壁垒、客户认证壁垒、规模优势和替代风险。")
    _table(_verification_rows(COMPETITION_ITEMS, mode="count"))
    with st.container(border=True):
        st.subheader("竞争格局摘要")
        columns = st.columns(4)
        summary_items = [
            ("竞争优势", "待验证", "示例数据 / 待配置"),
            ("替代风险", "待验证", "数据不足"),
            ("价格压力", "待验证", "待配置"),
            ("证据状态", "部分 / 不足 / 充足", AI_DRAFT),
        ]
        for column, (title, value, note) in zip(columns, summary_items):
            with column:
                render_status_card(title, value, note)
        st.caption(f"数据状态：{DATA_STATUS}")
    _button_row(["AI总结竞争格局", "确认竞争优势", "标记无法判断", "新增竞争对手"], "competition_action")


def _render_risk_counter_tab():
    st.subheader("风险与反证验证")
    st.write("验证主题受益假设中的风险、反证和未解决问题。")
    _table(
        [
            {
                "编号": index,
                "风险 / 反证": item,
                "严重程度": ["高", "中", "低", "中"][index - 1],
                "状态": ["待验证", "未解决", "已解决", "待验证"][index - 1],
                "evidence_id": f"EVID____-{index}",
                "操作": "查看证据 / 人工确认",
            }
            for index, item in enumerate(RISK_COUNTER_ITEMS, start=1)
        ]
    )
    with st.container(border=True):
        st.subheader("重大反证摘要")
        columns = st.columns(3)
        with columns[0]:
            render_status_card("是否存在重大反证", "是 / 否 / 待验证", "示例数据 / 待配置")
        with columns[1]:
            render_status_card("最高风险等级", "____", "数据不足")
        with columns[2]:
            render_status_card("需要补充证据", "____", AI_DRAFT)
        st.caption(f"数据状态：{DATA_STATUS}")
    _button_row(["AI查找反证", "新增风险", "风险已解决", "标记重大反证"], "risk_counter_action")


def _render_claim_tab():
    st.subheader("Claim 验证")
    render_status_badge("evidence_id 必需")
    st.write("验证 Claim 的标签、证据绑定和支持状态。")
    _table(
        [
            {
                "编号": index,
                "Claim": claim,
                "标签": ["事实", "推断", "待验证", "假设"][index - 1],
                "支持状态": ["已证实", "部分支持", "证据不足", "被反证"][index - 1],
                "证据ID": f"evidence_id：EVID____-{index}",
                "操作": "绑定证据 / 人工确认",
            }
            for index, claim in enumerate(CLAIM_ITEMS, start=1)
        ]
    )
    st.markdown("### Claim 审核状态")
    columns = st.columns(5)
    status_cards = [
        ("Claim总数", "__", "示例数据 / 待配置"),
        ("已证实", "__", "待配置"),
        ("部分支持", "__", "数据不足"),
        ("证据不足", "__", AI_DRAFT),
        ("被反证", "__", "待人工确认"),
    ]
    for column, (title, value, note) in zip(columns, status_cards):
        with column:
            render_status_card(title, value, note)
    _button_row(["AI提取Claim", "批量确认事实", "批量标记待验证", "删除无证据Claim", "绑定证据"], "claim_action")


def _render_report_grade_tab():
    st.subheader("研究报告与等级")
    render_status_badge("研究等级")
    st.write("汇总证据、Claim、风险与人工确认状态，生成研究报告草稿和研究等级。")
    _table(
        [
            {
                "评分项": item,
                "分数": "示例数据 / 待配置",
                "状态": "数据不足",
            }
            for item in REPORT_SCORE_ITEMS
        ]
    )

    st.markdown("### 最终研究等级")
    grade_columns = st.columns(5)
    grades = [
        ("S", "进入核心跟踪池"),
        ("A", "进入重点跟踪池"),
        ("B", "进入观察池"),
        ("C", "证据不足，继续观察"),
        ("D", "剔除"),
    ]
    for column, (grade, description) in zip(grade_columns, grades):
        with column:
            render_status_card(grade, description, "不代表交易建议")

    st.markdown("### 研究报告草稿")
    with st.container(border=True):
        st.write("AI草稿 / 待人工确认")
        st.write("AI生成报告草稿，必须人工确认后才能进入重点跟踪池。")
        st.write("核心结论：待生成 / AI草稿 / 待人工确认")
        st.caption(f"数据状态：{DATA_STATUS}")

    _button_row(["AI生成报告", "人工确认等级", "进入重点跟踪池", "剔除", "回写上游模块"], "report_grade_action")


def _render_placeholder_tab(title):
    st.subheader(title)
    st.write("本页为简洁占位，后续阶段再扩展正式 UI。")
    _table(
        [
            {
                "股票": "示例数据 / 待配置",
                "研究主题": "示例数据 / 待配置",
                "evidence_id": "待配置",
                "Claim状态": AI_DRAFT,
                "人工确认状态": "数据不足",
            }
        ]
    )


def render():
    render_section_title(
        "深度投研模块",
        "对“股票 + 主题”进行证据驱动的公司级验证，判断是否进入重点跟踪池。",
    )
    render_demo_notice()
    st.caption(f"全局数据状态：{DATA_STATUS}")

    tabs = st.tabs(TABS)
    for index, tab in enumerate(tabs):
        with tab:
            if index == 0:
                _render_task_pool_tab()
            elif index == 1:
                _render_single_stock_tab()
            elif index == 2:
                _render_business_boundary_tab()
            elif index == 3:
                _render_theme_benefit_tab()
            elif index == 4:
                _render_chain_position_tab()
            elif index == 5:
                _render_financial_realization_tab()
            elif index == 6:
                _render_customer_order_capex_tab()
            elif index == 7:
                _render_competition_tab()
            elif index == 8:
                _render_risk_counter_tab()
            elif index == 9:
                _render_claim_tab()
            elif index == 10:
                _render_report_grade_tab()
            else:
                _render_placeholder_tab(TABS[index])
