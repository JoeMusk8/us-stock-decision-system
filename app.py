import streamlit as st

from core.styles import apply_global_styles
from core.workspace_state import (
    build_workspace_snapshot,
    from_json_text,
    restore_workspace_snapshot,
    to_json_bytes,
)
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


def render_workspace_backup():
    st.sidebar.divider()
    with st.sidebar.expander("工作区备份", expanded=False):
        message = st.session_state.pop("_workspace_backup_message", "")
        if message:
            st.caption(message)

        snapshot = build_workspace_snapshot(st.session_state)
        st.download_button(
            "下载工作区 JSON",
            data=to_json_bytes(snapshot),
            file_name="workspace_backup.json",
            mime="application/json",
            use_container_width=True,
        )

        uploaded_file = st.file_uploader(
            "导入工作区 JSON",
            type=["json"],
            key="workspace_backup_upload",
        )
        if uploaded_file is not None and st.button("恢复工作区", use_container_width=True):
            text = uploaded_file.getvalue().decode("utf-8")
            parsed = from_json_text(text)
            if parsed["ok"]:
                restored = restore_workspace_snapshot(parsed["snapshot"])
                for key, value in restored.items():
                    st.session_state[key] = value
                st.session_state["_workspace_backup_message"] = "已恢复工作区"
                st.rerun()
            else:
                st.caption("导入失败：" + "；".join(parsed["errors"][:3]))

        st.caption("保存会话数据")


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
    render_workspace_backup()

    MODULES[selected_module]()


if __name__ == "__main__":
    main()
