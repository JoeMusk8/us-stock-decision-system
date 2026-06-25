import streamlit as st

from core.utils import render_demo_notice, render_section_title, render_status_badge, render_status_card


TABS = [
    "基础投研主工作台",
    "产业链全景图谱",
    "节点评分 / 瓶颈识别",
    "候选股雷达",
    "证据与AI解释",
    "人工确认 / 状态管理",
]

DATA_STATUS = "示例数据 / 待配置 / 数据不足"
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


def _table(rows):
    st.dataframe(rows, width="stretch", hide_index=True)
    st.caption(f"数据状态：{DATA_STATUS}")


def _button_row(labels, prefix):
    columns = st.columns(len(labels))
    for index, (column, label) in enumerate(zip(columns, labels), start=1):
        with column:
            st.button(label, key=f"{prefix}_{index}", width="stretch")


def _industry_input_card(index):
    with st.container(border=True):
        st.markdown(f"**行业{index}**")
        value = st.text_input(
            f"行业{index}",
            key=f"basic_industry_{index}",
            placeholder="待配置",
            label_visibility="collapsed",
        )
        st.caption(f"状态：{'已生成' if value else '未输入'}")
        col_a, col_b = st.columns(2)
        with col_a:
            st.button("切换", key=f"industry_switch_{index}", width="stretch")
        with col_b:
            st.button("清空", key=f"industry_clear_{index}", width="stretch")


def _node_card(layer_name, index, level):
    tone = {
        "核心瓶颈": "#dbeafe",
        "重要受益": "#ede9fe",
        "普通节点": "#f8fafc",
    }[level]
    with st.container(border=True):
        st.markdown(
            f"""
            <div style="background:{tone}; border-radius:12px; padding:12px;">
                <strong>{layer_name} - 节点{index}</strong><br>
                节点名称：示例数据 / 待配置<br>
                核心等级：{level}<br>
                证据数：数据不足<br>
                状态：{AI_DRAFT}
            </div>
            """,
            unsafe_allow_html=True,
        )


def _preview_card(title, rows, button_label, key):
    with st.container(border=True):
        st.subheader(title)
        _table(rows)
        st.button(button_label, key=key, width="stretch")


def _render_workspace_tab():
    st.subheader("基础投研主工作台")
    st.write("输入最多 3 个行业，生成产业链全景图谱、瓶颈识别和深度投研候选股。")
    _button_row(
        ["生成产业链图谱", "重新分析", "AI解释评分", "保存当前行业", "导出报告", "进入深度投研"],
        "workspace_action",
    )

    st.markdown("### 行业输入区")
    industry_columns = st.columns(3)
    for index, column in enumerate(industry_columns, start=1):
        with column:
            _industry_input_card(index)

    st.markdown("### 当前行业状态")
    status_columns = st.columns(4)
    cards = [
        ("当前行业", "____", "示例数据 / 待配置"),
        ("当前状态", "产业链图谱已生成 / 候选股雷达待人工确认", "待人工确认"),
        ("节点数量", "__", "数据不足"),
        ("候选股数量", "__", "最多 5 只"),
    ]
    for column, (title, value, note) in zip(status_columns, cards):
        with column:
            render_status_card(title, value, note)

    st.markdown("### 工作台预览")
    left, right = st.columns(2)
    with left:
        _preview_card(
            "产业链图谱预览",
            [
                {
                    "层级": layer,
                    "节点": "示例数据 / 待配置",
                    "核心等级": "数据不足",
                    "证据状态": "待配置",
                }
                for layer in INDUSTRY_LAYERS
            ],
            "查看完整图谱",
            "preview_chain",
        )
    with right:
        _preview_card(
            "候选股雷达预览",
            [
                {
                    "排名": index,
                    "股票": f"股票：{index}",
                    "对应产业链节点": "待配置",
                    "证据状态": "数据不足",
                    "人工状态": "待人工确认",
                }
                for index in range(1, 6)
            ],
            "查看候选雷达",
            "preview_radar",
        )


def _render_chain_tab():
    st.subheader("产业链全景图谱")
    st.write("使用卡片模拟 6 层产业链结构，不生成复杂动态图。")

    with st.container(border=True):
        st.markdown("### 图例")
        legend_columns = st.columns(4)
        legend_items = [
            ("深色 = 核心瓶颈节点", "示例数据"),
            ("中色 = 重要受益节点", "示例数据"),
            ("浅色 = 普通产业节点", "示例数据"),
            ("虚线 = 待验证关系", "数据不足"),
        ]
        for column, (title, note) in zip(legend_columns, legend_items):
            with column:
                render_status_card(title, note, "待验证")

    for layer_index, layer_name in enumerate(INDUSTRY_LAYERS, start=1):
        st.markdown(f"### {layer_index}. {layer_name}")
        columns = st.columns(3)
        levels = ["核心瓶颈", "重要受益", "普通节点"]
        for node_index, column in enumerate(columns, start=1):
            with column:
                _node_card(layer_name, node_index, levels[node_index - 1])
        st.caption("关系状态：虚线 = 待验证关系；数据状态：示例数据 / 待配置 / 数据不足")


def _render_scoring_tab():
    st.subheader("节点评分 / 瓶颈识别")
    st.write("按 10 个瓶颈评分维度对产业链节点进行结构化评分。")

    dimension_columns = st.columns(5)
    for index, dimension in enumerate(SCORING_DIMENSIONS, start=1):
        with dimension_columns[(index - 1) % 5]:
            render_status_card(f"{index}. {dimension}", "待配置", "评分维度")

    rows = []
    for index, layer in enumerate(INDUSTRY_LAYERS, start=1):
        row = {
            "节点": f"节点：{index}",
            "所属层级": layer,
            "技术难度": "示例数据",
            "供给稀缺": "示例数据",
            "产能瓶颈": "示例数据",
            "客户认证周期": "示例数据",
            "资本开支强度": "示例数据",
            "替代难度": "示例数据",
            "毛利率潜力": "示例数据",
            "议价能力": "示例数据",
            "交付周期": "示例数据",
            "监管约束": "示例数据",
            "总分": "数据不足",
            "核心等级": "AI草稿 / 待人工确认",
            "证据状态": "待配置",
        }
        rows.append(row)
    _table(rows)


def _render_candidate_tab():
    st.subheader("候选股雷达")
    render_status_badge("深度投研候选")
    st.write("最多展示 5 只深度投研候选股票。")

    _table(
        [
            {
                "排名": index,
                "股票": f"股票：{index}",
                "对应产业链节点": "待配置",
                "节点核心等级": "AI草稿 / 待人工确认",
                "技术难度": "示例数据",
                "供给稀缺": "示例数据",
                "替代难度": "示例数据",
                "议价能力": "示例数据",
                "总分": "数据不足",
                "证据状态": "待配置",
                "人工状态": "待人工确认",
                "操作": "查看 / 确认",
            }
            for index in range(1, 6)
        ]
    )
    _button_row(["查看评分", "查看证据", "进入深度投研候选", "剔除"], "candidate_action")


def _render_evidence_tab():
    st.subheader("证据与AI解释")
    render_status_badge("AI草稿")
    render_status_badge("待人工确认")

    left, right = st.columns([1.35, 1])
    with left:
        st.markdown("### 证据表格")
        _table(
            [
                {
                    "证据ID": f"evidence_id：{index}",
                    "等级": "数据不足",
                    "来源类型": "待配置",
                    "关联节点": "示例数据 / 待配置",
                    "关联股票": f"股票：{index}",
                    "支持内容": "AI草稿 / 待人工确认",
                    "状态": "待配置",
                    "操作": "查看 / 标记",
                }
                for index in range(1, 6)
            ]
        )
    with right:
        st.markdown("### AI解释面板")
        with st.container(border=True):
            explanation_items = [
                ("AI产业链拆解摘要", AI_DRAFT),
                ("AI认为最可能成为瓶颈的节点", "数据不足"),
                ("AI认为需要继续验证的问题", "数据不足"),
                ("缺失证据", "数据不足"),
                ("可能影响候选股雷达的风险", "待配置"),
            ]
            for label, value in explanation_items:
                st.write(f"**{label}：** {value}")
            st.caption(f"数据状态：{DATA_STATUS}")


def _render_confirmation_tab():
    st.subheader("人工确认 / 状态管理")
    st.write("用于确认产业链图谱、候选股雷达、证据绑定和 AI 解释状态。")

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
    st.caption(f"确认状态：{DATA_STATUS}")

    _button_row(
        ["确认产业链图谱", "确认候选股雷达", "标记证据不足", "退回重新分析", "提交深度投研候选"],
        "confirmation_action",
    )


def render():
    render_section_title(
        "基础投研 / 产业链图谱 / 候选股雷达模块",
        "输入最多 3 个行业，系统生成产业链全景图谱，识别核心瓶颈节点，并输出最多 5 只深度投研候选股。",
    )
    render_demo_notice()
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
