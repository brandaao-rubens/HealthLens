from pathlib import Path
import streamlit as st

from app.ui.cards import render_risk_card
from app.modules.diabetes_engine import (
    load_diabetes_model,
    build_feature_vector,
    compute_diabetes_risk,
)
from app.modules.diabetes_recommendations import (
    generate_recommendations,
    generate_adaptive_questions,
)
from app.modules.database import save_assessment


class DiabetesPage:
    def __init__(self):
        self.title = "Probabilidade estimada de diabetes"

    # função de persistência: manual → pdf → default
    def _get_initial(self, field, default):
        manual = st.session_state.get("manual_data_diabetes", {})
        pdf = st.session_state.get("lab_data_diabetes", {})

        if field in manual:
            return manual[field]
        if field in pdf:
            return pdf[field]
        return default

    def _sidebar_inputs(self):
        st.sidebar.subheader("📥 Entradas Clínicas – Diabetes")

        pdf_defaults = st.session_state.get("lab_data_diabetes", {})

        # ------------------------
        # Idade
        # ------------------------
        default_age = int(self._get_initial("age", 45))
        if "diabetes_age" not in st.session_state:
            st.session_state["diabetes_age"] = default_age

        age = st.sidebar.number_input(
            "Idade (anos)", 18, 100, key="diabetes_age"
        )

        # ------------------------
        # Sexo
        # ------------------------
        gender_default = self._get_initial("gender_label", "Masculino")
        gender_idx = 0 if gender_default == "Masculino" else 1

        if "diabetes_gender_label" not in st.session_state:
            st.session_state["diabetes_gender_label"] = gender_default

        gender_label = st.sidebar.selectbox(
            "Sexo biológico",
            ["Masculino", "Feminino"],
            index=gender_idx,
            key="diabetes_gender_label"
        )

        # ------------------------
        # IMC
        # ------------------------
        default_bmi = float(self._get_initial("bmi", 28.0))
        if "diabetes_bmi" not in st.session_state:
            st.session_state["diabetes_bmi"] = default_bmi

        bmi = st.sidebar.number_input(
            "IMC", 15.0, 60.0, step=0.1, key="diabetes_bmi"
        )

        # ------------------------
        # Hipertensão
        # ------------------------
        hyp_default = self._get_initial("hypertension_label", "Não")
        hyp_idx = 1 if hyp_default == "Sim" else 0

        if "diabetes_hypertension_label" not in st.session_state:
            st.session_state["diabetes_hypertension_label"] = hyp_default

        hypertension_label = st.sidebar.selectbox(
            "Hipertensão?",
            ["Não", "Sim"],
            index=hyp_idx,
            key="diabetes_hypertension_label"
        )

        # ------------------------
        # Doença cardíaca
        # ------------------------
        heart_default = self._get_initial("heart_disease_label", "Não")
        heart_idx = 1 if heart_default == "Sim" else 0

        if "diabetes_heart_disease_label" not in st.session_state:
            st.session_state["diabetes_heart_disease_label"] = heart_default

        heart_disease_label = st.sidebar.selectbox(
            "Doença cardíaca?",
            ["Não", "Sim"],
            index=heart_idx,
            key="diabetes_heart_disease_label"
        )

        # ------------------------
        # HbA1c
        # ------------------------
        default_hba1c = float(self._get_initial("hba1c", 5.9))
        if "diabetes_hba1c" not in st.session_state:
            st.session_state["diabetes_hba1c"] = default_hba1c

        hba1c = st.sidebar.number_input(
            "HbA1c (%)", 4.0, 15.0, step=0.1, key="diabetes_hba1c"
        )

        # ------------------------
        # Glicemia
        # ------------------------
        default_glucose = int(self._get_initial("glucose", 108))
        if "diabetes_glucose" not in st.session_state:
            st.session_state["diabetes_glucose"] = default_glucose

        glucose = st.sidebar.number_input(
            "Glicemia (mg/dL)", 60, 400, key="diabetes_glucose"
        )

        # ------------------------
        # Tabagismo
        # ------------------------
        options_smoke = [
            "Nunca fumou",
            "Fuma atualmente",
            "Parou de fumar",
            "Fumava, mas não atualmente",
            "Já fumou / fumante crônico",
            "Sem informação",
        ]

        smoke_default = self._get_initial("smoking_history_label", "Nunca fumou")
        smoke_idx = options_smoke.index(smoke_default)

        if "diabetes_smoking_label" not in st.session_state:
            st.session_state["diabetes_smoking_label"] = smoke_default

        smoking_history_label = st.sidebar.selectbox(
            "Histórico de tabagismo",
            options_smoke,
            index=smoke_idx,
            key="diabetes_smoking_label"
        )

        # botao limpar PDF
        if pdf_defaults:
            if st.sidebar.button("Limpar dados importados"):
                del st.session_state["lab_data_diabetes"]
                st.rerun()

        inputs = dict(
            age=age,
            gender_label=gender_label,
            bmi=bmi,
            hypertension_label=hypertension_label,
            heart_disease_label=heart_disease_label,
            hba1c=hba1c,
            glucose=glucose,
            smoking_history_label=smoking_history_label,
        )

        st.session_state["manual_data_diabetes"] = inputs
        return inputs

    def render(self):
        inputs = self._sidebar_inputs()

        model = load_diabetes_model()
        if model is None:
            st.error("Modelo de Diabetes não encontrado.")
            return

        df_features = build_feature_vector(**inputs)
        risk = compute_diabetes_risk(model, df_features)

        # CARTÃO PRINCIPAL
        render_risk_card(
            title=self.title,
            prob=risk["prob"],
            risk_level=risk["level"],
            risk_emoji=risk["emoji"],
            risk_color=risk["color"],
            description="Modelo baseado em dados clínicos e laboratoriais."
        )

        st.markdown("Intensidade do risco:")
        st.progress(min(max(risk["prob"], 0.0), 1.0))

        # --------------------------
        # SALVAR NO HISTÓRICO
        # --------------------------
        if st.button("💾 Salvar Resultado no Histórico"):
            user = st.session_state.get("username")

            if not user:
                st.warning("Nenhum usuário logado!")
            else:
                save_assessment(
                    username=user,
                    module="diabetes",
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
