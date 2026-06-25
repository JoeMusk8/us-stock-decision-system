import streamlit as st

from core.utils import render_demo_notice, render_section_title, render_status_badge, render_status_card


TABS = [
    "24小时信息流总览",
    "美国政府资金流向",
    "巨头公司科研方向配置",
    "商界领袖关注方向配置",
    "X KOL 发言配置",
    "AI 审核队列",
    "24小时输出详情",
]

SOURCE_TYPES = [
    "美国政府资金流向",
    "巨头公司科研方向",
    "商界领袖关注方向",
    "X KOL 发言",
]

DATA_STATUS = "示例数据 / 待配置 / 数据不足"
AI_DRAFT = "AI草稿 / 待人工确认"


def _table(rows):
    st.dataframe(rows, width="stretch", hide_index=True)
    st.caption(f"数据状态：{DATA_STATUS}")


def _button_row(labels, prefix):
    columns = st.columns(len(labels))
    for index, (column, label) in enumerate(zip(columns, labels), start=1):
        with column:
            st.button(label, key=f"{prefix}_{index}", width="stretch")


def _source_entry_cards():
    columns = st.columns(4)
    for index, source_name in enumerate(SOURCE_TYPES):
        with columns[index]:
            with st.container(border=True):
                st.subheader(source_name)
                st.write("数据状态：待配置")
                st.write("审核状态：数据不足")
                st.button("进入配置", key=f"source_entry_{index}", width="stretch")


def _configured_status(value):
    return "已配置" if value else "未配置"


def _company_cards():
    for row_index in range(5):
        columns = st.columns(3)
        for column_index, column in enumerate(columns):
            card_index = row_index * 3 + column_index + 1
            with column:
                with st.container(border=True):
                    st.markdown(f"**科技公司：{card_index}**")
                    value = st.text_input(
                        "输入框",
                        key=f"tech_company_{card_index}",
                        placeholder="待配置",
                        label_visibility="collapsed",
                    )
                    st.caption(f"状态：{_configured_status(value)}")


def _leader_cards():
    for row_index in range(5):
        columns = st.columns(3)
        for column_index, column in enumerate(columns):
            card_index = row_index * 3 + column_index + 1
            with column:
                with st.container(border=True):
                    st.markdown(f"**商界领袖：{card_index}**")
                    name = st.text_input(
                        "姓名输入框",
                        key=f"leader_name_{card_index}",
                        placeholder="姓名待配置",
                    )
                    company = st.text_input(
                        "公司输入框",
                        key=f"leader_company_{card_index}",
                        placeholder="公司待配置",
                    )
                    st.caption(f"状态：{_configured_status(name or company)}")


def _kol_cards():
    for row_index in range(5):
        columns = st.columns(3)
        for column_index, column in enumerate(columns):
            card_index = row_index * 3 + column_index + 1
            with column:
                with st.container(border=True):
                    st.markdown(f"**监控KOL账号：{card_index}**")
                    value = st.text_input(
                        "账号输入框",
                        key=f"kol_account_{card_index}",
                        placeholder="账号待配置",
                    )
                    st.caption(f"状态：{_configured_status(value)}")


def _monitoring_checklist(items, prefix):
    columns = st.columns(3)
    for index, item in enumerate(items):
        with columns[index % 3]:
            st.checkbox(item, value=False, key=f"{prefix}_monitor_item_{index}_{item}")
    st.caption(f"配置状态：{DATA_STATUS}")


def _render_overview_tab():
    st.subheader("24小时信息流总览")
    st.write("汇总四类信息源的 24 小时信息流，并展示 AI 初筛与人工审核状态。")
    _button_row(
        ["刷新24小时信息", "AI审核新增信息", "新增监控对象", "导出24小时摘要"],
        "overview_action",
    )

    status_columns = st.columns(5)
    status_cards = [
        ("24h新增信息", "示例数据", "未接入真实数据源"),
        ("AI标记重点关注", "数据不足", AI_DRAFT),
        ("待人工审核", "示例数据", "需要人工确认"),
        ("已确认重点关注", "数据不足", "仅作研究线索"),
        ("数据源异常", "待配置", "等待数据源配置"),
    ]
    for column, (title, value, note) in zip(status_columns, status_cards):
        with column:
            render_status_card(title, value, note)

    st.markdown("### 筛选区")
    filter_columns = st.columns(5)
    with filter_columns[0]:
        st.selectbox("时间范围", ["24小时", "待配置"], key="overview_time_range")
    with filter_columns[1]:
        st.selectbox("来源类型", ["全部", *SOURCE_TYPES], key="overview_source_type")
    with filter_columns[2]:
        st.selectbox("AI标签", ["全部", AI_DRAFT, "数据不足"], key="overview_ai_label")
    with filter_columns[3]:
        st.selectbox("人工状态", ["全部", "待人工审核", "继续观察", "忽略"], key="overview_human_status")
    with filter_columns[4]:
        st.text_input("搜索关键词", placeholder="待配置", key="overview_keyword")

    st.markdown("### 信息流表格")
    _table(
        [
            {
                "序号": "示例数据",
                "来源类型": source_type,
                "标题/摘要": "示例数据 / 待配置",
                "AI标签": AI_DRAFT,
                "影响行业": "数据不足",
                "人工状态": "待人工审核",
                "操作": "查看 / 审核",
            }
            for source_type in SOURCE_TYPES
        ]
    )

    st.markdown("### 四类信息源入口")
    _source_entry_cards()


def _render_government_tab():
    st.subheader("美国政府资金流向")
    st.write("监控美国政府资金、合同、拨款和科研资助方向。")

    status_columns = st.columns(6)
    sources = ["USAspending", "SAM.gov", "美国防务合同公告", "Grants.gov", "SBIR/STTR", "DARPA"]
    for column, source_name in zip(status_columns, sources):
        with column:
            render_status_card(source_name, "待配置", "数据状态：数据不足")

    st.markdown("### 抓取字段说明")
    field_columns = st.columns(3)
    fields = [
        "谁给钱？",
        "给了谁？",
        "给了多少钱？",
        "合同/拨款名称？",
        "用途？",
        "所属机构？",
        "资金是否连续增加？",
        "是否出现新技术词？",
        "是否有上市公司或子公司参与？",
    ]
    for index, field in enumerate(fields):
        with field_columns[index % 3]:
            st.write(f"* {field}")

    st.markdown("### 24小时政府资金信息流")
    _table(
        [
            {
                "序号": "示例数据",
                "机构": "待配置",
                "接收方": "待配置",
                "金额": "示例数据 / 待配置",
                "用途": "数据不足",
                "技术词": "数据不足",
                "上市公司关联": "数据不足",
                "AI标签": AI_DRAFT,
                "人工状态": "待人工审核",
            }
        ]
    )

    st.markdown("### AI审核结果面板")
    columns = st.columns(5)
    review_items = [
        ("是否具备范式创新机会", "AI草稿 / 待人工确认"),
        ("消息来源可信度", "数据不足"),
        ("数据真伪检查", "待配置"),
        ("可能影响行业", "数据不足"),
        ("缺失信息", "数据不足"),
    ]
    for column, (title, value) in zip(columns, review_items):
        with column:
            render_status_card(title, value, "需人工审核")

    _button_row(["人工确认重点关注", "继续观察", "忽略", "查看原始来源"], "gov_review")


def _render_company_tab():
    st.subheader("巨头公司科研方向配置")
    st.write("配置最多 15 个科技公司监控对象，用于观察科研方向、产品发布和技术路线变化。")
    _company_cards()

    st.markdown("### 监控内容清单")
    _monitoring_checklist(
        [
            "研究博客",
            "技术论文",
            "开发者博客",
            "产品发布",
            "开源项目",
            "专利",
            "招聘方向",
            "财报电话会",
            "投资者日",
            "合作公告",
            "技术路线图",
        ],
        "company",
    )

    st.markdown("### 当前公司 24 小时信息输出")
    _table(
        [
            {
                "序号": "示例数据",
                "科技公司": "待配置",
                "信息类型": "数据不足",
                "标题/摘要": "示例数据 / 待配置",
                "AI标签": AI_DRAFT,
                "人工状态": "待人工审核",
            }
        ]
    )


def _render_leader_tab():
    st.subheader("商界领袖关注方向配置")
    st.write("配置最多 15 位商界领袖，观察其公开表达、产品会议和投资者沟通中的方向变化。")
    _leader_cards()

    st.markdown("### 监控内容清单")
    _monitoring_checklist(
        [
            "X发言",
            "公开演讲",
            "财报电话会发言",
            "开发者大会发言",
            "产品发布会",
            "采访",
            "播客",
            "股东大会",
            "投资者日",
            "监管文件中的管理层描述",
        ],
        "leader",
    )

    st.markdown("### 当前领袖 24 小时信息输出")
    _table(
        [
            {
                "序号": "示例数据",
                "商界领袖": "待配置",
                "公司": "待配置",
                "来源": "数据不足",
                "标题/摘要": "示例数据 / 待配置",
                "AI标签": AI_DRAFT,
                "人工状态": "待人工审核",
            }
        ]
    )


def _render_kol_tab():
    st.subheader("X KOL 发言配置")
    render_status_badge("线索")
    st.write("配置最多 15 个 X KOL 账号，仅用于发现线索，不进入事实结论。")
    _kol_cards()

    st.markdown("### 当前 KOL 24 小时发言输出")
    _table(
        [
            {
                "序号": "示例数据",
                "KOL账号": "待配置",
                "发言摘要": "示例数据 / 待配置",
                "线索标签": "线索",
                "AI标签": AI_DRAFT,
                "人工状态": "待人工审核",
            }
        ]
    )


def _render_ai_queue_tab():
    st.subheader("AI 审核队列")
    st.write("集中处理 AI 初筛、来源可信度、真伪检查和人工审核。")

    st.markdown("### AI审核信息列表")
    _table(
        [
            {
                "序号": "示例数据",
                "来源类型": source_type,
                "标题/摘要": "示例数据 / 待配置",
                "AI标签": AI_DRAFT,
                "来源可信度": "数据不足",
                "人工状态": "待人工审核",
                "操作": "审核",
            }
            for source_type in SOURCE_TYPES
        ]
    )

    left, right = st.columns(2)
    with left:
        st.markdown("### 原始信息")
        with st.container(border=True):
            st.write("来源类型：示例数据 / 待配置")
            st.write("标题/摘要：示例数据 / 待配置")
            st.write("原始来源：待配置")
            st.write("数据状态：数据不足")
    with right:
        st.markdown("### AI审核结果")
        with st.container(border=True):
            result_rows = [
                ("AI标签", AI_DRAFT),
                ("是否可能具备范式创新机会", "AI草稿 / 待人工确认"),
                ("来源可信度", "数据不足"),
                ("数据真伪检查", "待配置"),
                ("可能影响行业", "数据不足"),
                ("缺失信息", "数据不足"),
                ("需要人工核查", "是"),
            ]
            for label, value in result_rows:
                st.write(f"**{label}：** {value}")

    st.markdown("### 人工审核区")
    st.selectbox(
        "审核结论",
        ["待人工审核", "确认重点关注", "继续观察", "忽略", "标记来源不可信"],
        key="ai_queue_review_result",
    )
    st.text_area("人工备注", placeholder="待配置", key="ai_queue_human_note")
    _button_row(
        ["确认重点关注", "继续观察", "忽略", "标记来源不可信", "查看原始来源"],
        "ai_queue_action",
    )


def _output_block(title, prefix, kol_notice=False):
    with st.container(border=True):
        st.subheader(title)
        columns = st.columns(3)
        with columns[0]:
            render_status_card("重点关注", "__ 条", "示例数据 / 待配置")
        with columns[1]:
            render_status_card("待审核", "__ 条", "数据不足")
        with columns[2]:
            render_status_card("忽略", "__ 条", "示例数据 / 待配置")
        if kol_notice:
            render_status_badge("KOL线索")
        _button_row(["查看详情", "只看重点关注", "只看待审核"], prefix)


def _render_output_tab():
    st.subheader("24小时输出详情")
    st.write("按四类信息源汇总 24 小时结构化输出。")
    _output_block("1. 美国政府监控输出", "output_gov")
    _output_block("2. 巨头公司监控输出", "output_company")
    _output_block("3. 商界领袖监控输出", "output_leader")
    _output_block("4. KOL监控输出", "output_kol", kol_notice=True)


def render():
    render_section_title(
        "范式创新监控模块",
        "四类高质量信息源的实时信息流系统 + AI范式创新初筛 + AI来源真伪检测 + AI行业影响分析 + 人工审核。",
    )
    render_demo_notice()
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
