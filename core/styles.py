import streamlit as st


def apply_global_styles():
    st.markdown(
        """
        <style>
        :root {
            --app-bg: #f8f9fc;
            --surface: #ffffff;
            --surface-soft: #fbfcff;
            --text-main: #172033;
            --text-muted: #667085;
            --text-soft: #8a93a5;
            --line-soft: #e7eaf1;
            --accent-blue: #e8f1ff;
            --accent-purple: #f1ecff;
            --accent-line: rgba(116, 94, 255, 0.18);
            --shadow-soft: 0 16px 42px rgba(34, 42, 64, 0.07);
            --shadow-card: 0 8px 26px rgba(34, 42, 64, 0.06);
            --radius-card: 20px;
            --radius-control: 12px;
            --content-max: 1560px;
            --button-height: 42px;
        }

        .stApp {
            background:
                radial-gradient(circle at 12% -8%, rgba(231, 240, 255, 0.78), transparent 28%),
                radial-gradient(circle at 88% -10%, rgba(241, 236, 255, 0.82), transparent 30%),
                var(--app-bg);
            color: var(--text-main);
            font-size: 15px;
        }

        .block-container {
            max-width: var(--content-max);
            margin-left: auto;
            margin-right: auto;
            padding: 1.35rem 2.2rem 3rem;
        }

        [data-testid="stSidebar"] {
            min-width: 260px !important;
            max-width: 280px !important;
            background: rgba(255, 255, 255, 0.94);
            border-right: 1px solid var(--line-soft);
            box-shadow: 8px 0 28px rgba(34, 42, 64, 0.04);
        }

        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
            gap: 0.7rem;
        }

        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] p {
            font-size: 14px;
        }

        h1, h2, h3, h4 {
            color: var(--text-main);
            letter-spacing: 0;
        }

        h1 {
            font-size: 34px !important;
            line-height: 1.18 !important;
            font-weight: 720 !important;
        }

        h2 {
            font-size: 23px !important;
            line-height: 1.25 !important;
            font-weight: 680 !important;
        }

        h3 {
            font-size: 19px !important;
            line-height: 1.3 !important;
            font-weight: 660 !important;
        }

        p, li, label, .stMarkdown {
            font-size: 15px;
        }

        div[data-testid="stVerticalBlock"] {
            gap: 1rem;
        }

        div[data-testid="stHorizontalBlock"] {
            align-items: stretch;
            gap: 1rem;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            border: 1px solid rgba(231, 234, 241, 0.95);
            border-radius: var(--radius-card);
            box-shadow: var(--shadow-card);
            background: rgba(255, 255, 255, 0.94);
        }

        div[data-testid="stVerticalBlockBorderWrapper"] > div {
            padding: 1.05rem 1.1rem;
        }

        .app-page-header {
            margin: 0 0 1.15rem 0;
            padding: 22px 26px;
            border-radius: 24px;
            background:
                linear-gradient(135deg, rgba(232, 241, 255, 0.92), rgba(241, 236, 255, 0.72)),
                var(--surface);
            border: 1px solid rgba(231, 234, 241, 0.92);
            box-shadow: var(--shadow-soft);
        }

        .app-page-header h1 {
            margin: 0;
        }

        .app-page-header p {
            margin: 9px 0 0;
            max-width: 980px;
            color: var(--text-muted);
            font-size: 15.5px;
            line-height: 1.62;
        }

        .app-badge-row {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 14px;
        }

        .app-badge {
            display: inline-flex;
            align-items: center;
            min-height: 26px;
            padding: 4px 10px;
            border-radius: 999px;
            border: 1px solid rgba(116, 94, 255, 0.16);
            background: rgba(255, 255, 255, 0.74);
            color: #4f5a70;
            font-size: 12.5px;
            font-weight: 620;
            white-space: nowrap;
        }

        .app-card,
        .status-card {
            height: 100%;
            min-height: 118px;
            padding: 20px 22px;
            border-radius: var(--radius-card);
            background: var(--surface);
            box-shadow: var(--shadow-card);
            border: 1px solid rgba(231, 234, 241, 0.96);
        }

        .app-card-title,
        .status-card-title {
            color: var(--text-muted);
            font-size: 13.5px;
            font-weight: 650;
            margin-bottom: 10px;
        }

        .app-card-body,
        .status-card-value {
            color: var(--text-main);
            font-size: 20px;
            line-height: 1.36;
            font-weight: 700;
            margin-bottom: 8px;
        }

        .app-card-meta,
        .status-card-note {
            color: var(--text-muted);
            font-size: 13.5px;
            line-height: 1.5;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            padding: 8px;
            border-radius: 18px;
            background: rgba(255, 255, 255, 0.72);
            border: 1px solid var(--line-soft);
            box-shadow: var(--shadow-card);
            margin-bottom: 1rem;
            overflow-x: auto;
        }

        .stTabs [data-baseweb="tab"] {
            min-height: 42px;
            padding: 10px 16px;
            border-radius: 13px;
            color: var(--text-muted);
            font-size: 14px;
            font-weight: 650;
        }

        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
            color: var(--text-main);
            box-shadow: 0 6px 16px rgba(74, 84, 120, 0.08);
        }

        .stButton > button {
            min-height: var(--button-height);
            border-radius: var(--radius-control);
            border: 1px solid rgba(102, 112, 133, 0.14);
            background: #ffffff;
            color: #26324a;
            font-size: 14px;
            font-weight: 650;
            box-shadow: 0 6px 16px rgba(34, 42, 64, 0.05);
            transition: all 150ms ease;
        }

        .stButton > button:hover {
            border-color: var(--accent-line);
            background: linear-gradient(135deg, #ffffff, #f6f4ff);
            color: #1d2840;
            box-shadow: 0 10px 22px rgba(34, 42, 64, 0.08);
        }

        div[data-testid="stDataFrame"] {
            background: var(--surface);
            border-radius: var(--radius-card);
            box-shadow: var(--shadow-card);
            padding: 10px;
            border: 1px solid rgba(231, 234, 241, 0.96);
        }

        div[data-testid="stDataFrame"] * {
            font-size: 14px;
        }

        div[data-testid="stAlert"] {
            border-radius: 14px;
            padding: 8px 12px;
            font-size: 13px;
            border-width: 1px;
            background: rgba(255, 255, 255, 0.78);
        }

        [data-testid="stTextInput"] input,
        [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
            min-height: 42px;
            border-radius: var(--radius-control);
            font-size: 14px;
        }

        .stCaptionContainer,
        .stCaptionContainer p {
            color: var(--text-soft);
            font-size: 12.5px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
