import streamlit as st


def render_risk_card(
    title: str,
    prob: float,
    risk_level: str,
    risk_emoji: str,
    risk_color: str,
    description: str,
):
    """
    Card padrão para exibir probabilidade de risco.

    prob: probabilidade em [0,1]
    """

    risk_pct = prob * 100.0

    st.markdown(
        f"""
        <div class="health-card" style="border-left: 6px solid {risk_color};">
            <h3 style="color:white; margin:0 0 8px 0;">
                {title}: {risk_pct:.1f}%
            </h3>
            <p style="color:#bbbbbb; margin:0;">
                Nível de risco: {risk_emoji} <b>{risk_level}</b>
            </p>
            <p class="muted" style="margin-top:6px;">
                {description}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
