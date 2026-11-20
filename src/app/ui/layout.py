import streamlit as st


def render_main_header(icon: str, title: str, subtitle: str):
    st.markdown(
        f"""
        <div style='display:flex; align-items:center; gap:16px;'>
            <div style="
                width:58px; height:58px; border-radius:18px;
                background: radial-gradient(circle at 30% 0%, #38bdf8, #0ea5e9 40%, #0f172a 100%);
                display:flex; align-items:center; justify-content:center;
                box-shadow: 0 10px 20px rgba(0,0,0,0.5);
            ">
                <span style="font-size:32px;">{icon}</span>
            </div>
            <div>
                <h1 style='margin:0; color:white;'>{title}</h1>
                <p class="muted" style='margin:3px 0 0 0;'>
                    {subtitle}
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
