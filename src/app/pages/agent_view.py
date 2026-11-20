import streamlit as st
from app.modules.agent_engine import get_agent_response


class AgentPage:
    def __init__(self):
        self.title = "Assistente Inteligente HealthLens"

    def render(self):
        st.header(f"🤖 {self.title}")
        st.caption(
            "Tire dúvidas sobre seus exames, entenda seus riscos e veja seu histórico explicado de forma didática."
        )

        # Inicializa histórico no session_state (apenas conversa, sem contexto técnico)
        if "chat_history" not in st.session_state:
            st.session_state["chat_history"] = []

        # Exibe mensagens anteriores
        for message in st.session_state["chat_history"]:
            role = "user" if message["role"] == "user" else "assistant"
            avatar = "🧑‍💻" if role == "user" else "🤖"
            with st.chat_message(role, avatar=avatar):
                st.markdown(message["parts"][0])

        # Input do usuário
        if prompt := st.chat_input("Digite sua dúvida aqui (ex: 'Meu risco de diabetes aumentou?')"):

            # 1. Mostra msg do usuário
            st.chat_message("user", avatar="🧑‍💻").markdown(prompt)

            # 2. Adiciona ao histórico local
            st.session_state["chat_history"].append(
                {"role": "user", "parts": [prompt]}
            )

            # 3. Pega resposta da IA (com contexto + histórico clínico)
            with st.spinner("Analisando seus dados e histórico..."):
                response_text = get_agent_response(
                    prompt,
                    st.session_state["chat_history"],
                )

            # 4. Mostra resposta da IA
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(response_text)

            # 5. Salva resposta no histórico
            st.session_state["chat_history"].append(
                {"role": "model", "parts": [response_text]}
            )

        # Botão para limpar conversa
        if st.sidebar.button("🗑️ Limpar Conversa"):
            del st.session_state["chat_history"]
            st.rerun()
