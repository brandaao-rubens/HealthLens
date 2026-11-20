import streamlit as st


def inject_global_css():
    css = """
    <style>
    body {
        background-color: #050505;
    }

    .main .block-container{
        padding-top: 1.2rem;
        padding-left: 2.4rem;
        padding-right: 2.4rem;
        max-width: 1200px;
    }

    h1, h2, h3, h4 {
        color: #ffffff !important;
        letter-spacing: 0.02em;
    }

    section[data-testid="stSidebar"] {
        background-color: #101010 !important;
        border-right: 1px solid #222222;
    }

    section[data-testid="stSidebar"] * {
        color: #dddddd !important;
    }

    .health-card {
        padding: 14px 16px;
        border-radius: 14px;
        background: radial-gradient(circle at top left, #202020 0, #111111 55%, #050505 100%);
        border: 1px solid #333;
        margin-bottom: 14px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.45);
    }

    .divider {
        margin-top: 25px;
        margin-bottom: 20px;
        border-bottom: 1px solid #333333;
    }

    .recommendation {
        padding: 10px 12px;
        background: linear-gradient(135deg, #181818 0, #101010 100%);
        border-left: 4px solid #4caf50;
        border-radius: 8px;
        margin-bottom: 8px;
        border: 1px solid #333333;
    }

    .question-card {
        padding: 9px 11px;
        background-color: #131313;
        border-radius: 8px;
        border: 1px solid #2b2b2b;
        margin-bottom: 6px;
    }

    .muted {
        color: #aaaaaa;
        font-size: 0.9rem;
    }

    .stTabs [role="tablist"] {
        gap: 8px;
    }

    .stTabs [role="tablist"] button {
        background-color: #151515 !important;
        color: #cccccc !important;
        border-radius: 999px !important;
        padding: 6px 14px !important;
        border: 1px solid #333333 !important;
    }

    .stTabs [role="tablist"] button[aria-selected="true"] {
        background: linear-gradient(135deg, #2563eb 0, #7c3aed 100%) !important;
        color: #ffffff !important;
        border-color: #2563eb !important;
    }

    .stTabs [role="tablist"] button:hover {
        background-color: #1f1f1f !important;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
