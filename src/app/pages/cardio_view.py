from pathlib import Path
import streamlit as st

from app.modules.database import save_assessment
from app.ui.cards import render_risk_card
from app.modules.cardio_engine import (
    load_cardio_model,
    build_feature_vector,
    compute_cardio_risk,
    convert_cholesterol_category,
    convert_glucose_category,
)
from app.modules.cardio_recommendations import (
    generate_recommendations,
    generate_adaptive_questions,
)

BASE_DIR = Path(__file__).resolve().parents[2]


class CardioPage:
    def __init__(self):
        self.title = "Probabilidade estimada de risco cardíaco"

    def _sidebar_inputs(self):
        st.sidebar.subheader("📥 Entradas Clínicas – Risco Cardíaco")

        # Recupera dados de PDF e dados manuais persistentes
        pdf_data = st.session_state.get("lab_data_cardio", {})
        manual_data = st.session_state.get("manual_data_cardio", {})

        def get_initial_value(key, pdf_key, default):
            if manual_data and key in manual_data:
                return manual_data[key]
            if pdf_data and pdf_key in pdf_data:
                return pdf_data[pdf_key]
            return default

        # ----------------------------
        # DADOS CLÍNICOS
        # ----------------------------

        # Idade
        age = st.sidebar.number_input(
            "Idade (anos)", 20, 100,
            int(get_initial_value("age", "age", 50)),
            key="cardio_age"
        )

        # Sexo
        gender_label = st.sidebar.selectbox(
            "Sexo biológico",
            ["Masculino", "Feminino"],
            key="cardio_gender"
        )

        # Medidas físicas
        height_cm = st.sidebar.number_input(
            "Altura (cm)", 140, 210,
            int(get_initial_value("height_cm", "height", 170)),
            key="cardio_height"
        )

        weight_kg = st.sidebar.number_input(
            "Peso (kg)", 40.0, 200.0,
            float(get_initial_value("weight_kg", "weight", 75.0)),
            key="cardio_weight"
        )

        st.sidebar.markdown("### Pressão arterial")
        ap_hi = st.sidebar.number_input(
            "Pressão Sistólica (mmHg)", 80, 240,
            int(get_initial_value("ap_hi", "ap_hi", 130)),
            key="cardio_ap_hi"
        )
        ap_lo = st.sidebar.number_input(
            "Pressão Diastólica (mmHg)", 40, 180,
            int(get_initial_value("ap_lo", "ap_lo", 85)),
            key="cardio_ap_lo"
        )

        # ---------- VALORES REAIS DE EXAMES ----------
        st.sidebar.markdown("### Exames laboratoriais")

        chol_real = st.sidebar.number_input(
            "Colesterol total (mg/dL)", 100, 400,
            int(get_initial_value("chol_real", "cholesterol", 190)),
            key="cardio_chol_real"
        )

        gluc_real = st.sidebar.number_input(
            "Glicemia em jejum (mg/dL)", 60, 300,
            int(get_initial_value("gluc_real", "glucose", 90)),
            key="cardio_gluc_real"
        )

        # -------- CONVERSÃO REAL → CATEGORIA --------
        chol_category = convert_cholesterol_category(chol_real)
        gluc_category = convert_glucose_category(gluc_real)

        st.sidebar.caption(f"Categoria colesterol: {chol_category}")
        st.sidebar.caption(f"Categoria glicemia: {gluc_category}")

        # Estilo de vida
        smoking_label = st.sidebar.selectbox(
            "Fuma atualmente?", ["Não", "Sim"],
            key="cardio_smoke"
        )
        alcohol_label = st.sidebar.selectbox(
            "Consumo frequente de álcool?", ["Não", "Sim"],
            key="cardio_alc"
        )
        active_label = st.sidebar.selectbox(
            "Pratica atividade física?", ["Não", "Sim"],
            key="cardio_act"
        )

        # Botão para limpar dados importados
        if pdf_data or manual_data:
            if st.sidebar.button("Limpar dados importados"):
                for k in list(st.session_state.keys()):
                    if k.startswith("cardio_") or k.startswith("lab_data_cardio"):
                        del st.session_state[k]
                st.rerun()

        return dict(
            age=age,
            gender_label=gender_label,
            height_cm=height_cm,
            weight_kg=weight_kg,
            ap_hi=ap_hi,
            ap_lo=ap_lo,
            chol_real=chol_real,
            gluc_real=gluc_real,
            chol_category=chol_category,
            gluc_category=gluc_category,
            smoking_label=smoking_label,
            alcohol_label=alcohol_label,
            active_label=active_label,
        )

    def render(self):
        inputs = self._sidebar_inputs()
        st.session_state["manual_data_cardio"] = inputs

        model = load_cardio_model()
        if model is None:
            st.error("Modelo cardíaco não encontrado.")
            return

        # O modelo usa APENAS categorias — enviamos as convertidas
        df_features = build_feature_vector(
            age=inputs["age"],
            gender_label=inputs["gender_label"],
            height_cm=inputs["height_cm"],
            weight_kg=inputs["weight_kg"],
            ap_hi=inputs["ap_hi"],
            ap_lo=inputs["ap_lo"],
            chol_category=inputs["chol_category"],
            gluc_category=inputs["gluc_category"],
            smoking_label=inputs["smoking_label"],
            alcohol_label=inputs["alcohol_label"],
            active_label=inputs["active_label"],
        )

        risk = compute_cardio_risk(model, df_features)

        render_risk_card(
            title=self.title,
            prob=risk["prob"],
            risk_level=risk["level"],
            risk_emoji=risk["emoji"],
            risk_color=risk["color"],
            description=(
                "Modelo baseado em 70 mil pacientes, ajustado por fatores clássicos de risco "
                "(pressão, IMC, glicemia, colesterol, tabagismo e estilo de vida)."
            ),
        )

        st.progress(risk["prob"])

        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("IMC", f"{risk['bmi']:.1f}")
        with c2:
            st.metric("Colesterol (mg/dL)", f"{inputs['chol_real']} ({inputs['chol_category']})")
        with c3:
            st.metric("Glicemia (mg/dL)", f"{inputs['gluc_real']} ({inputs['gluc_category']})")

        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        st.subheader("🩺 Recomendações Personalizadas")
        for r in generate_recommendations(df_features, risk["prob"]):
            st.markdown(f"<div class='recommendation'>{r}</div>", unsafe_allow_html=True)

        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        st.markdown(
            "<p class='muted'>⚠️ Este sistema não substitui consulta médica.</p>",
            unsafe_allow_html=True,
        )

        if st.button("💾 Salvar Resultado no Histórico"):
            save_assessment(
                username=st.session_state.get("username", "Visitante"),
                module="cardio",
                risk_prob=risk["prob"],
                risk_level=risk["level"],
                inputs_dict=inputs
            )
            st.success("Resultado salvo!")
