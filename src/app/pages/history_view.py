import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from app.modules.database import get_user_history

class HistoryPage:
    def render(self):
        st.header(f"📈 Histórico Clínico de {st.session_state['username']}")

        # ==========================
# BOTÃO PARA APAGAR HISTÓRICO
# ==========================
        with st.expander("⚠️ Opções Avançadas", expanded=False):
            st.markdown("### 🧹 Limpar Histórico Clínico")

            st.info(
                "Esta ação remove **todos os registros de risco** associados ao seu usuário. "
                "Não afeta sua conta, login ou dados de outros usuários."
            )

            if st.button("🗑️ Apagar todo meu histórico", type="secondary"):
                st.session_state["confirm_clear_history"] = True

            # Segunda etapa de confirmação
            if st.session_state.get("confirm_clear_history", False):
                st.warning("Tem certeza? Esta ação **não pode ser desfeita**.")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Sim, apagar tudo"):
                        from app.modules.database import clear_user_history
                        clear_user_history(st.session_state["username"])
                        st.success("Histórico apagado com sucesso!")
                        st.session_state["confirm_clear_history"] = False
                        st.rerun()

                with col2:
                    if st.button("Cancelar"):
                        st.session_state["confirm_clear_history"] = False


        # ==== MAPEAMENTO DOS NOMES ====
        pretty_to_internal = {
            "Todos": None,
            "Cardíaco": "cardio",
            "Diabetes": "diabetes",
            "Renal": "renal",
            "Hepático": "liver",
        }

        internal_to_pretty = {
            "cardio": "Cardíaco",
            "diabetes": "Diabetes",
            "renal": "Renal",
            "liver": "Hepático",
        }

        # ==== SELECTBOX BONITO ====
        pretty_choice = st.selectbox(
            "Filtrar por Módulo",
            list(pretty_to_internal.keys())
        )

        module_filter = pretty_to_internal[pretty_choice]

        # ==== CARREGA HISTÓRICO ====
        data = get_user_history(st.session_state["username"], module_filter)

        if not data:
            st.info("Nenhum registro encontrado. Faça uma avaliação para começar seu histórico!")
            return

        # Converte em DataFrame
        df = pd.DataFrame(data, columns=["date", "module", "risk_prob", "risk_level"])
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")

        # Converte nome interno → bonito
        df["module_pretty"] = df["module"].map(internal_to_pretty)

        # ==== GRÁFICO EVOLUTIVO ====
        st.subheader("📉 Evolução do Risco")

        fig = go.Figure()

        color_map = {
            "Cardíaco": "#4DA8DA",
            "Diabetes": "#2EC4B6",
            "Renal": "#FF6B6B",
            "Hepático": "#FFA600",
        }

        for module in df["module_pretty"].unique():
            temp = df[df["module_pretty"] == module]

            fig.add_trace(go.Scatter(
                x=temp["date"],
                y=temp["risk_prob"],
                mode="lines+markers",
                name=module,
                line=dict(color=color_map.get(module, "#FFFFFF")),
                marker=dict(size=6)
            ))

        fig.update_layout(
            xaxis_title="Data",
            yaxis_title="Probabilidade",
            template="plotly_dark",
            height=450
        )

        st.plotly_chart(fig, use_container_width=True)

        # ==== TABELA DETALHADA ====
        st.subheader("📄 Registros Detalhados")

        df_display = df.copy()
        df_display["risk_prob"] = df_display["risk_prob"].apply(lambda x: f"{x*100:.1f}%")
        df_display.rename(columns={
            "date": "Data",
            "module_pretty": "Módulo",
            "risk_prob": "Probabilidade",
            "risk_level": "Nível"
        }, inplace=True)

        st.dataframe(
            df_display[["Data", "Módulo", "Probabilidade", "Nível"]],
            use_container_width=True
        )
