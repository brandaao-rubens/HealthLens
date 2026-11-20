import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

import streamlit as st
from app.modules.database import init_db

# Inicializa o banco ao abrir o app
init_db()

from app.ui.styles import inject_global_css
from app.ui.layout import render_main_header

# PÁGINAS
from app.pages.login_view import LoginPage
from app.pages.history_view import HistoryPage
from app.pages.upload_view import UploadPage
from app.pages.cardio_view import CardioPage
from app.pages.diabetes_view import DiabetesPage
from app.pages.kidney_view import RenalPage
from app.pages.liver_view import LiverPage
from app.pages.agent_view import AgentPage

def main():
    st.set_page_config(page_title="HealthLens", layout="wide", page_icon="⚕️")
    inject_global_css()

    # --- LÓGICA DE LOGIN ---
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        # Se não está logado, mostra APENAS a tela de login
        LoginPage().render()
        return

    # --- SE ESTIVER LOGADO, MOSTRA O APP ---
    
    # Header com botão de Logout
    c1, c2 = st.columns([6, 1])
    with c1:
        render_main_header(icon="⚕️", title="HealthLens", subtitle="Sistema Multidiagnóstico Inteligente")
    with c2:
        if st.button("Sair 🚪"):
            st.session_state["logged_in"] = False
            st.rerun()

    # Sidebar
    st.sidebar.header(f"Olá, {st.session_state.get('username', 'Usuário')}")
    st.sidebar.markdown("---")
    
    selected_page = st.sidebar.radio(
        "Menu:",
        [
            "Central de Diagnóstico (Upload)",
            "Assistente IA",
            "Meu Histórico 📈", # <--- NOVA OPÇÃO
            "Risco Cardíaco",
            "Diabetes",
            "Doença Renal",
            "Saúde Hepática",
        ],
    )

    # Roteamento
    if selected_page == "Central de Diagnóstico (Upload)":
        UploadPage().render()
    elif selected_page == "Assistente IA":
        AgentPage().render()
    elif selected_page == "Meu Histórico 📈":
        HistoryPage().render()
    elif selected_page == "Risco Cardíaco":
        CardioPage().render()
    elif selected_page == "Diabetes":
        DiabetesPage().render()
    elif selected_page == "Doença Renal":
        RenalPage().render()
    elif selected_page == "Saúde Hepática":
        LiverPage().render()

if __name__ == "__main__":
    main()