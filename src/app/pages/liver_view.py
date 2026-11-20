from pathlib import Path
import streamlit as st

from app.ui.cards import render_risk_card
from app.modules.liver_engine import (
    load_liver_model,
    build_feature_vector,
    compute_liver_risk,
)
from app.modules.liver_recommendations import (
    generate_recommendations,
    generate_adaptive_questions,
)
from app.modules.database import save_assessment


class LiverPage:
    def __init__(self):
        self.title = "Saúde Hepática (Fígado)"

    def _get_initial(self, field, default):
        manual = st.session_state.get("manual_data_liver", {})
        pdf = st.session_state.get("lab_data_liver", {})

        if field in manual:
            return manual[field]
        if field in pdf:
            return pdf[field]
        return default

    def _sidebar_inputs(self):
        st.sidebar.subheader("📥 Entradas Clínicas – Fígado")

        pdf_defaults = st.session_state.get("lab_data_liver", {})

        # Idade
        default_age = int(self._get_initial("age", 45))
        if "liver_age" not in st.session_state:
            st.session_state["liver_age"] = default_age

        age = st.sidebar.number_input(
            "Idade", 10, 100, key="liver_age"
        )

        # Sexo
        gender_default = self._get_initial("gender_label", "Masculino")
        gender_idx = 0 if gender_default == "Masculino" else 1

        if "liver_gender_label" not in st.session_state:
            st.session_state["liver_gender_label"] = gender_default

        gender_label = st.sidebar.selectbox(
            "Sexo",
            ["Masculino", "Feminino"],
            index=gender_idx,
            key="liver_gender_label"
        )

        # Bilirrubinas
        default_bt = float(self._get_initial("bilirubin_total", 0.8))
        if "liver_bilirubin_total" not in st.session_state:
            st.session_state["liver_bilirubin_total"] = default_bt

        bilirubin_total = st.sidebar.number_input(
            "Bilirrubina Total", 0.1, 30.0, step=0.1, key="liver_bilirubin_total"
        )

        default_bd = float(self._get_initial("bilirubin_direct", 0.2))
        if "liver_bilirubin_direct" not in st.session_state:
            st.session_state["liver_bilirubin_direct"] = default_bd

        bilirubin_direct = st.sidebar.number_input(
            "Bilirrubina Direta", 0.1, 20.0, step=0.1, key="liver_bilirubin_direct"
        )

        # Fosfatase
        default_ap = int(self._get_initial("alkaline_phosphatase", 180))
        if "liver_alk_phos" not in st.session_state:
            st.session_state["liver_alk_phos"] = default_ap

        alkaline_phosphatase = st.sidebar.number_input(
            "Fosfatase Alcalina", 10, 2000, key="liver_alk_phos"
        )

        # ALT/AST
        default_sgpt = int(self._get_initial("sgpt", 30))
        if "liver_sgpt" not in st.session_state:
            st.session_state["liver_sgpt"] = default_sgpt

        sgpt = st.sidebar.number_input(
            "TGP (ALT)", 5, 2000, key="liver_sgpt"
        )

        default_sgot = int(self._get_initial("sgot", 30))
        if "liver_sgot" not in st.session_state:
            st.session_state["liver_sgot"] = default_sgot

        sgot = st.sidebar.number_input(
            "TGO (AST)", 5, 2000, key="liver_sgot"
        )

        # Proteínas
        default_prot = float(self._get_initial("proteins", 6.8))
        if "liver_proteins" not in st.session_state:
            st.session_state["liver_proteins"] = default_prot

        proteins = st.sidebar.number_input(
            "Proteínas Totais", 1.0, 10.0, step=0.1, key="liver_proteins"
        )

        default_albumin = float(self._get_initial("albumin", 3.5))
        if "liver_albumin" not in st.session_state:
            st.session_state["liver_albumin"] = default_albumin

        albumin = st.sidebar.number_input(
            "Albumina", 0.5, 6.0, step=0.1, key="liver_albumin"
        )

        default_ag = float(self._get_initial("ag_ratio", 1.0))
        if "liver_ag_ratio" not in st.session_state:
            st.session_state["liver_ag_ratio"] = default_ag

        ag_ratio = st.sidebar.number_input(
            "Razão A/G", 0.1, 3.0, step=0.1, key="liver_ag_ratio"
        )

        # limpar PDF
        if pdf_defaults:
            if st.sidebar.button("Limpar dados importados"):
                del st.session_state["lab_data_liver"]
                st.rerun()

        inputs = dict(
            age=age,
            gender_label=gender_label,
            bilirubin_total=bilirubin_total,
            bilirubin_direct=bilirubin_direct,
            alkaline_phosphatase=alkaline_phosphatase,
            sgpt=sgpt,
            sgot=sgot,
            proteins=proteins,
            albumin=albumin,
            ag_ratio=ag_ratio,
        )

        st.session_state["manual_data_liver"] = inputs
        return inputs

    def render(self):
        inputs = self._sidebar_inputs()

        model = load_liver_model()
        if model is None:
            st.error("Modelo Hepático não encontrado.")
            return

        df_features = build_feature_vector(**inputs)
        risk = compute_liver_risk(model, df_features)

        render_risk_card(
            title=self.title,
            prob=risk["prob"],
            risk_level=risk["level"],
            risk_emoji=risk["emoji"],
            risk_color=risk["color"],
            description="Avaliação baseada em enzimas hepáticas."
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
                    module="liver",
                    risk_prob=float(risk["prob"]),
                    risk_level=risk["level"],
                    inputs_dict=inputs,
                )
                st.success("Resultado salvo com sucesso!")

        # -----------------------------------------------------
        # RECOMENDAÇÕES PERSONALIZADAS
        # -----------------------------------------------------
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        st.subheader("🩺 Recomendações Personalizadas")

        recs = generate_recommendations(df_features, risk["prob"])
        for r in recs:
            st.markdown(
                f"<div class='recommendation'><span style='color:#f5f5f5;'>{r}</span></div>",
                unsafe_allow_html=True,
            )

        # Aviso final
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        st.markdown(
            """
            <p class="muted">
            ⚠️ Os resultados deste módulo devem ser interpretados por um profissional de saúde.
            </p>
            """,
            unsafe_allow_html=True,
        )
