from pathlib import Path
import streamlit as st

from app.ui.cards import render_risk_card
from app.modules.kidney_engine import (
    load_renal_model,
    build_feature_vector,
    compute_renal_risk,
)
from app.modules.kidney_recommendations import (
    generate_recommendations,
    generate_adaptive_questions,
)
from app.modules.database import save_assessment


class RenalPage:
    def __init__(self):
        self.title = "Probabilidade estimada de Doença Renal Crônica"

    def _get_initial(self, field, default):
        manual = st.session_state.get("manual_data_renal", {})
        pdf = st.session_state.get("lab_data_renal", {})

        if field in manual:
            return manual[field]
        if field in pdf:
            return pdf[field]
        return default

    def _sidebar_inputs(self):
        st.sidebar.subheader("📥 Entradas Clínicas – Renal")

        pdf_defaults = st.session_state.get("lab_data_renal", {})

        # Idade
        default_age = int(self._get_initial("age", 55))
        if "renal_age" not in st.session_state:
            st.session_state["renal_age"] = default_age

        age = st.sidebar.number_input(
            "Idade", 18, 100, key="renal_age"
        )

        # Pressão Sistólica
        default_bp = int(self._get_initial("bp", 130))
        if "renal_bp" not in st.session_state:
            st.session_state["renal_bp"] = default_bp

        bp = st.sidebar.number_input(
            "Pressão Sistólica (mmHg)", 80, 220, key="renal_bp"
        )

        # Glicemia
        default_glucose = int(self._get_initial("glucose", 120))
        if "renal_glucose" not in st.session_state:
            st.session_state["renal_glucose"] = default_glucose

        glucose = st.sidebar.number_input(
            "Glicemia Aleatória (mg/dL)", 60, 500, key="renal_glucose"
        )

        # Creatinina
        default_creatinine = float(self._get_initial("creatinine", 1.1))
        if "renal_creatinine" not in st.session_state:
            st.session_state["renal_creatinine"] = default_creatinine

        creatinine = st.sidebar.number_input(
            "Creatinina (mg/dL)", 0.4, 15.0, step=0.1, key="renal_creatinine"
        )

        # Ureia
        default_urea = float(self._get_initial("urea", 40.0))
        if "renal_urea" not in st.session_state:
            st.session_state["renal_urea"] = default_urea

        urea = st.sidebar.number_input(
            "Ureia (mg/dL)", 10.0, 300.0, key="renal_urea"
        )

        # Potássio
        default_k = float(self._get_initial("potassium", 4.5))
        if "renal_potassium" not in st.session_state:
            st.session_state["renal_potassium"] = default_k

        potassium = st.sidebar.number_input(
            "Potássio (mEq/L)", 2.0, 8.0, step=0.1, key="renal_potassium"
        )

        # Hemoglobina
        default_hemo = float(self._get_initial("hemo", 14.0))
        if "renal_hemo" not in st.session_state:
            st.session_state["renal_hemo"] = default_hemo

        hemo = st.sidebar.number_input(
            "Hemoglobina (g/dL)", 3.0, 20.0, key="renal_hemo"
        )

        # Hipertensão
        hyp_default = self._get_initial("hypertension", "Não")
        hyp_idx = 1 if hyp_default == "Sim" else 0

        if "renal_hypertension" not in st.session_state:
            st.session_state["renal_hypertension"] = hyp_default

        hypertension = st.sidebar.selectbox(
            "Hipertensão Diagnosticada?",
            ["Não", "Sim"],
            index=hyp_idx,
            key="renal_hypertension"
        )

        # Diabetes
        diab_default = self._get_initial("diabetes", "Não")
        diab_idx = 1 if diab_default == "Sim" else 0

        if "renal_diabetes" not in st.session_state:
            st.session_state["renal_diabetes"] = diab_default

        diabetes = st.sidebar.selectbox(
            "Diabetes Diagnosticado?",
            ["Não", "Sim"],
            index=diab_idx,
            key="renal_diabetes"
        )

        # Limpar PDF
        if pdf_defaults:
            if st.sidebar.button("Limpar dados importados"):
                del st.session_state["lab_data_renal"]
                st.rerun()

        inputs = dict(
            age=age,
            bp=bp,
            glucose=glucose,
            urea=urea,
            creatinine=creatinine,
            potassium=potassium,
            hemo=hemo,
            hypertension=hypertension,
            diabetes=diabetes
        )

        st.session_state["manual_data_renal"] = inputs
        return inputs

    def render(self):
        inputs = self._sidebar_inputs()

        model = load_renal_model()
        if model is None:
            st.error("Modelo Renal não encontrado.")
            return

        df_features = build_feature_vector(**inputs)
        risk = compute_renal_risk(model, df_features)

        render_risk_card(
            title=self.title,
            prob=risk["prob"],
            risk_level=risk["level"],
            risk_emoji=risk["emoji"],
            risk_color=risk["color"],
            description="Modelo baseado em biomarcadores renais."
        )

        st.markdown("Intensidade do risco:")
        st.progress(min(max(risk["prob"], 0.0), 1.0))

        if st.button("💾 Salvar Resultado no Histórico"):
            user = st.session_state.get("username")

            if not user:
                st.warning("Nenhum usuário logado!")
            else:
                save_assessment(
                    username=user,
                    module="renal",
                    risk_prob=float(risk["prob"]),
                    risk_level=risk["level"],
                    inputs_dict=inputs,
                )
                st.success("Resultado salvo com sucesso!")
        
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        st.subheader("🩺 Recomendações Personalizadas")

        recs = generate_recommendations(df_features, risk["prob"])
        for r in recs:
            st.markdown(
                f"""
                <div class="recommendation">
                    <span style="color:#f5f5f5;">{r}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Aviso clínico final
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        st.markdown(
            """
            <p class="muted">
            ⚠️ Este módulo é apenas de apoio e <b>não substitui</b> conduta clínica profissional.
            </p>
            """,
            unsafe_allow_html=True,
        )
