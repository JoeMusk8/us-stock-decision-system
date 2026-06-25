import streamlit as st

from core.styles import apply_global_styles
from core.workspace_state import build_workspace_snapshot, from_json_text, restore_workspace_snapshot, to_json_bytes
from modules import basic_research, deep_research, home_overview, market_monitor, paradigm_monitor, tracking_pool


MODULES = {
    "\u9996\u9875\u603b\u89c8": home_overview.render,
    "\u8303\u5f0f\u521b\u65b0\u76d1\u63a7": paradigm_monitor.render,
    "\u57fa\u7840\u6295\u7814 / \u4ea7\u4e1a\u94fe\u56fe\u8c31 / \u5019\u9009\u80a1\u96f7\u8fbe": basic_research.render,
    "\u6df1\u5ea6\u6295\u7814": deep_research.render,
    "\u91cd\u70b9\u8ddf\u8e2a\u6c60 / \u91cf\u5316\u7b56\u7565\u6807\u6ce8": tracking_pool.render,
    "\u5e02\u573a\u73af\u5883\u76d1\u63a7": market_monitor.render,
}


def render_workspace_backup():
    st.sidebar.divider()
    with st.sidebar.expander("\u5de5\u4f5c\u533a\u5907\u4efd", expanded=False):
        message = st.session_state.pop("_workspace_backup_message", "")
        if message:
            st.caption(message)
        snapshot = build_workspace_snapshot(st.session_state)
        st.download_button("\u4e0b\u8f7d\u5de5\u4f5c\u533a JSON", data=to_json_bytes(snapshot), file_name="workspace_backup.json", mime="application/json", use_container_width=True)
        uploaded_file = st.file_uploader("\u5bfc\u5165\u5de5\u4f5c\u533a JSON", type=["json"], key="workspace_backup_upload")
        if uploaded_file is not None and st.button("\u6062\u590d\u5de5\u4f5c\u533a", use_container_width=True):
            text = uploaded_file.getvalue().decode("utf-8")
            parsed = from_json_text(text)
            if parsed["ok"]:
                restored = restore_workspace_snapshot(parsed["snapshot"])
                for key, value in restored.items():
                    st.session_state[key] = value
                st.session_state["_workspace_backup_message"] = "\u5df2\u6062\u590d\u5de5\u4f5c\u533a"
                st.rerun()
            else:
                st.caption("\u5bfc\u5165\u5931\u8d25\uff1a" + "\uff1b".join(parsed["errors"][:3]))
        st.caption("\u4fdd\u5b58\u4f1a\u8bdd\u6570\u636e")


def main():
    st.set_page_config(page_title="\u7f8e\u80a1\u4ea4\u6613\u51b3\u7b56\u7cfb\u7edf", layout="wide", initial_sidebar_state="expanded")
    apply_global_styles()
    st.sidebar.markdown("### \u7f8e\u80a1\u4ea4\u6613\u51b3\u7b56\u7cfb\u7edf")
    st.sidebar.caption("\u7814\u7a76\u6d41\u7a0b\u5de5\u4f5c\u53f0")
    selected_module = st.sidebar.radio("\u6a21\u5757\u5bfc\u822a", list(MODULES.keys()), index=0)
    render_workspace_backup()
    MODULES[selected_module]()


if __name__ == "__main__":
    main()
