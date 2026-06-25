import streamlit as st

from core.styles import apply_global_styles
from modules import (
    basic_research,
    deep_research,
    market_monitor,
    paradigm_monitor,
    tracking_pool,
)


MODULES = {
    "范式创新监控": paradigm_monitor.render,
    "基础投研 / 产业链图谱 / 候选股雷达": basic_research.render,
    "深度投研": deep_research.render,
    "重点跟踪池 / 量化策略标注": tracking_pool.render,
    "市场环境监控": market_monitor.render,
}


def main():
    st.set_page_config(
        page_title="美股交易决策系统",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_global_styles()

    st.sidebar.markdown("### 美股交易决策系统")
    st.sidebar.caption("研究流程工作台")

    selected_module = st.sidebar.radio(
        "模块导航",
        list(MODULES.keys()),
        index=0,
    )

    MODULES[selected_module]()


if __name__ == "__main__":
    main()
