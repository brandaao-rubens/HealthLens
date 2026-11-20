import streamlit as st
import time
from app.modules.database import create_user, verify_user

class LoginPage:
    def render(self):
        st.markdown(
            """
            <div style="text-align: center; margin-top: 50px;">
                <h1>🩺 HealthLens</h1>
                <p>Acesse seu histórico de saúde inteligente.</p>
            </div>
            """, unsafe_allow_html=True
        )

        cols = st.columns([1, 2, 1])
        with cols[1]:
            tab1, tab2 = st.tabs(["Entrar", "Criar Conta"])

            with tab1:
                username = st.text_input("Usuário", key="login_user")
                password = st.text_input("Senha", type="password", key="login_pass")
                
                if st.button("Acessar Sistema", type="primary", use_container_width=True):
                    if verify_user(username, password):
                        st.session_state["logged_in"] = True
                        st.session_state["username"] = username
                        st.success("Login realizado! Redirecionando...")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Usuário ou senha incorretos.")

            with tab2:
                new_user = st.text_input("Novo Usuário", key="reg_user")
                new_pass = st.text_input("Nova Senha", type="password", key="reg_pass")
                
                if st.button("Registrar", use_container_width=True):
                    if new_user and new_pass:
                        if create_user(new_user, new_pass):
                            st.success("Conta criada! Faça login na aba ao lado.")
                        else:
                            st.error("Esse usuário já existe.")
                    else:
                        st.warning("Preencha todos os campos.")