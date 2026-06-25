from html import escape

import streamlit as st


def render_status_badge(text):
    st.markdown(f'<span class="app-badge">{escape(str(text))}</span>', unsafe_allow_html=True)


def render_page_header(title, subtitle="", badges=None):
    badge_items = badges or ["示例数据", "待配置", "数据不足"]
    subtitle_html = f"<p>{escape(str(subtitle))}</p>" if subtitle else ""
    badges_html = "".join(f'<span class="app-badge">{escape(str(item))}</span>' for item in badge_items)
    st.markdown(
        f"""
        <div class="app-page-header">
            <h1>{escape(str(title))}</h1>
            {subtitle_html}
            <div class="app-badge-row">{badges_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_card(title, body="", meta=""):
    body_html = f'<div class="app-card-body">{escape(str(body))}</div>' if body != "" else ""
    meta_html = f'<div class="app-card-meta">{escape(str(meta))}</div>' if meta else ""
    st.markdown(
        f"""
        <div class="app-card">
            <div class="app-card-title">{escape(str(title))}</div>
            {body_html}
            {meta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(title, value, note=""):
    st.markdown(
        f"""
        <div class="status-card">
            <div class="status-card-title">{escape(str(title))}</div>
            <div class="status-card-value">{escape(str(value))}</div>
            <div class="status-card-note">{escape(str(note))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_action_bar(buttons):
    if not buttons:
        return
    visible_count = min(len(buttons), 6)
    columns = st.columns([1] * visible_count + [max(1, 6 - visible_count)])
    for index, label in enumerate(buttons[:visible_count]):
        with columns[index]:
            st.button(label, key=f"action_bar_{abs(hash((label, index))) % 100000}", width="stretch")
    for extra_index, label in enumerate(buttons[visible_count:], start=visible_count):
        st.button(label, key=f"action_bar_extra_{abs(hash((label, extra_index))) % 100000}")


def render_clean_table(data):
    st.dataframe(data, width="stretch", hide_index=True)


def render_status_card(title, value, note=""):
    render_metric_card(title, value, note)


def render_section_title(title, subtitle=""):
    render_page_header(title, subtitle)


def render_demo_notice():
    st.markdown(
        """
        <div class="app-badge-row">
            <span class="app-badge">示例数据</span>
            <span class="app-badge">待配置</span>
            <span class="app-badge">数据不足</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_placeholder_table(columns):
    placeholder_row = {column: "待配置" for column in columns}
    placeholder_row["数据状态"] = "数据不足"
    render_clean_table([placeholder_row])
