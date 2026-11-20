import streamlit as st
from app.modules.file_parser import parse_lab_file
from app.ui.cards import render_risk_card

# --- IMPORTS CARDIO ---
from app.modules.cardio_engine import (
    load_cardio_model,
    build_feature_vector as build_cardio_features,
    compute_cardio_risk
)
from app.modules.cardio_recommendations import generate_recommendations as recs_cardio

# --- IMPORTS DIABETES ---
from app.modules.diabetes_engine import (
    load_diabetes_model,
    build_feature_vector as build_diabetes_features,
    compute_diabetes_risk
)
from app.modules.diabetes_recommendations import generate_recommendations as recs_diabetes

# --- IMPORTS RENAL (NOVO) ---
from app.modules.kidney_engine import (
    load_renal_model,
    build_feature_vector as build_renal_features,
    compute_renal_risk
)
from app.modules.kidney_recommendations import generate_recommendations as recs_renal

# --- IMPORTS LIVER (NOVO) ---
from app.modules.liver_engine import (
    load_liver_model,
    build_feature_vector as build_liver_features,
    compute_liver_risk
)
from app.modules.liver_recommendations import generate_recommendations as recs_liver


class UploadPage:
    def __init__(self):
        self.title = "Central de Diagnóstico via Exames"

    # ==========================================
    # 1. FORMULÁRIO CARDIO
    # ==========================================
    def _render_cardio_form(self, extracted_data):
        st.markdown("### ❤️ Complementar Dados - Risco Cardíaco")
        
        def get_val(key, default): return extracted_data.get(key, default)

        # Lógica de conversão: Número -> Categoria
        idx_chol = 1 
        if "cholesterol" in extracted_data:
            val = extracted_data["cholesterol"]
            if val < 200: idx_chol = 0
            elif val < 240: idx_chol = 1
            else: idx_chol = 2
            
        idx_gluc = 0 
        if "glucose" in extracted_data:
            val = extracted_data["glucose"]
            if val < 100: idx_gluc = 0
            elif val < 126: idx_gluc = 1
            else: idx_gluc = 2

        idx_gender = 0
        if extracted_data.get("gender") == "Feminino": idx_gender = 1

        with st.form("form_cardio"):
            c1, c2, c3 = st.columns(3)
            with c1:
                age = st.number_input("Idade", 20, 100, int(get_val("age", 50)))
                gender_label = st.selectbox("Sexo", ["Masculino", "Feminino"], index=idx_gender)
                height_cm = st.number_input("Altura (cm)", 140, 210, 170)
            
            with c2:
                weight_kg = st.number_input("Peso (kg)", 40.0, 200.0, 75.0)
                ap_hi = st.number_input("P. Sistólica (mmHg)", 80, 240, 130)
                ap_lo = st.number_input("P. Diastólica (mmHg)", 40, 180, 85)

            with c3:
                chol_label = st.selectbox("Colesterol", ["Normal", "Acima do normal", "Muito acima"], index=idx_chol)
                gluc_label = st.selectbox("Glicemia", ["Normal", "Acima do normal", "Muito acima"], index=idx_gluc)
                active_label = st.selectbox("Atividade Física?", ["Não", "Sim"])

            c4, c5 = st.columns(2)
            with c4: smoking_label = st.selectbox("Fuma atualmente?", ["Não", "Sim"])
            with c5: alcohol_label = st.selectbox("Álcool frequente?", ["Não", "Sim"])

            submitted = st.form_submit_button("🩺 Calcular Risco Cardíaco", type="primary")

        if submitted:
            # Converter labels para categorias do engine
            chol_map = {
                "Normal": 1,
                "Acima do normal": 2,
                "Muito acima": 3
            }

            gluc_map = {
                "Normal": 1,
                "Acima do normal": 2,
                "Muito acima": 3
            }

            inputs = dict(
                age=age,
                gender_label=gender_label,
                height_cm=height_cm,
                weight_kg=weight_kg,
                ap_hi=ap_hi,
                ap_lo=ap_lo,
                chol_category=chol_map[chol_label],
                gluc_category=gluc_map[gluc_label],
                smoking_label=smoking_label,
                alcohol_label=alcohol_label,
                active_label=active_label
            )

            model = load_cardio_model()
            if model:
                df = build_cardio_features(**inputs)
                risk = compute_cardio_risk(model, df)
                self._show_results(risk, "Cardíaco", df, recs_cardio)

    # ==========================================
    # 2. FORMULÁRIO DIABETES
    # ==========================================
    def _render_diabetes_form(self, extracted_data):
        st.markdown("### 🩸 Complementar Dados - Diabetes")

        def get_val(key, default): return extracted_data.get(key, default)
        idx_gender = 0
        if extracted_data.get("gender") == "Feminino": idx_gender = 1

        with st.form("form_diabetes"):
            c1, c2, c3 = st.columns(3)
            with c1:
                age = st.number_input("Idade", 18, 100, int(get_val("age", 45)))
                gender_label = st.selectbox("Sexo", ["Masculino", "Feminino"], index=idx_gender)
                bmi = st.number_input("IMC", 15.0, 60.0, 28.0)
            
            with c2:
                hba1c = st.number_input("HbA1c (%)", 4.0, 15.0, float(get_val("hba1c", 5.9)), step=0.1)
                glucose = st.number_input("Glicemia (mg/dL)", 60, 400, int(get_val("glucose", 108)))
                smoking_label = st.selectbox("Tabagismo", ["Nunca fumou", "Fuma atualmente", "Parou", "Sem info"])

            with c3:
                hypertension = st.selectbox("Hipertensão?", ["Não", "Sim"])
                heart_disease = st.selectbox("Doença Cardíaca?", ["Não", "Sim"])

            submitted = st.form_submit_button("🩸 Calcular Risco Diabetes", type="primary")

        if submitted:
            inputs = dict(
                age=age, gender_label=gender_label, bmi=bmi,
                hypertension_label=hypertension, heart_disease_label=heart_disease,
                hba1c=hba1c, glucose=glucose, smoking_history_label=smoking_label
            )
            model = load_diabetes_model()
            if model:
                df = build_diabetes_features(**inputs)
                risk = compute_diabetes_risk(model, df)
                self._show_results(risk, "Diabetes", df, recs_diabetes)

    # ==========================================
    # 3. FORMULÁRIO RENAL (NOVO)
    # ==========================================
    def _render_renal_form(self, extracted_data):
        st.markdown("### 🧬 Complementar Dados - Doença Renal")
        
        def get_val(key, default): return extracted_data.get(key, default)
        
        with st.form("form_renal"):
            c1, c2, c3 = st.columns(3)
            with c1:
                age = st.number_input("Idade", 18, 100, int(get_val("age", 55)))
                bp = st.number_input("Pressão Sistólica", 80, 220, 130) # Dataset usa BP genérico, usamos sistólica
                glucose = st.number_input("Glicemia Aleatória", 60, 500, int(get_val("glucose", 120)))
            
            with c2:
                # Dados específicos renais que vêm do PDF
                creatinine = st.number_input("Creatinina (mg/dL)", 0.4, 15.0, float(get_val("creatinine", 1.1)), step=0.1)
                urea = st.number_input("Ureia (mg/dL)", 10.0, 300.0, float(get_val("urea", 40.0)))
                potassium = st.number_input("Potássio (mEq/L)", 2.0, 8.0, float(get_val("potassium", 4.5)))

            with c3:
                hemo = st.number_input("Hemoglobina", 3.0, 20.0, float(get_val("hemo", 14.0)))
                hypertension = st.selectbox("Hipertensão?", ["Não", "Sim"])
                diabetes = st.selectbox("Diabetes?", ["Não", "Sim"])

            submitted = st.form_submit_button("🧬 Calcular Risco Renal", type="primary")
        
        if submitted:
            inputs = dict(
                age=age, bp=bp, glucose=glucose, urea=urea, 
                creatinine=creatinine, potassium=potassium, hemo=hemo,
                hypertension=hypertension, diabetes=diabetes
            )
            model = load_renal_model()
            if model:
                df = build_renal_features(**inputs)
                risk = compute_renal_risk(model, df)
                self._show_results(risk, "Renal", df, recs_renal)

    # ==========================================
    # 4. FORMULÁRIO HEPÁTICO (NOVO)
    # ==========================================
    def _render_liver_form(self, extracted_data):
        st.markdown("### 🍺 Complementar Dados - Saúde Hepática")
        
        def get_val(key, default): return extracted_data.get(key, default)
        idx_gender = 0
        if extracted_data.get("gender") == "Feminino": idx_gender = 1

        with st.form("form_liver"):
            c1, c2, c3 = st.columns(3)
            with c1:
                age = st.number_input("Idade", 10, 100, int(get_val("age", 45)))
                gender_label = st.selectbox("Sexo", ["Masculino", "Feminino"], index=idx_gender)
                # Albumina e Proteinas
                proteins = st.number_input("Proteínas Totais", 1.0, 10.0, float(get_val("proteins", 6.8)), step=0.1)
                albumin = st.number_input("Albumina", 0.5, 6.0, float(get_val("albumin", 3.5)), step=0.1)
            
            with c2:
                # Bilirrubinas
                bil_tot = st.number_input("Bilirrubina Total", 0.1, 30.0, float(get_val("bilirubin_total", 0.8)), step=0.1)
                bil_dir = st.number_input("Bilirrubina Direta", 0.1, 20.0, float(get_val("bilirubin_direct", 0.2)), step=0.1)
                alk_phos = st.number_input("Fosfatase Alc.", 10, 2000, int(get_val("alkaline_phosphatase", 180)))
            
            with c3:
                # Enzimas
                sgpt = st.number_input("TGP (ALT)", 5, 2000, int(get_val("sgpt", 30)))
                sgot = st.number_input("TGO (AST)", 5, 2000, int(get_val("sgot", 30)))
                ag_ratio = st.number_input("Razão A/G", 0.1, 3.0, float(get_val("ag_ratio", 1.0)), step=0.1)

            submitted = st.form_submit_button("🍺 Calcular Risco Hepático", type="primary")
        
        if submitted:
            inputs = dict(
                age=age, gender_label=gender_label, 
                bilirubin_total=bil_tot, bilirubin_direct=bil_dir,
                alkaline_phosphatase=alk_phos, sgpt=sgpt, sgot=sgot,
                proteins=proteins, albumin=albumin, ag_ratio=ag_ratio
            )
            model = load_liver_model()
            if model:
                df = build_liver_features(**inputs)
                risk = compute_liver_risk(model, df)
                self._show_results(risk, "Hepático", df, recs_liver)

    # ==========================================
    # EXIBIÇÃO DE RESULTADOS COMUM
    # ==========================================
    def _show_results(self, risk, model_name, df_features, rec_func):
        st.markdown("---")
        st.subheader(f"📊 Resultado: {model_name}")
        
        render_risk_card(
            title=f"Probabilidade Calculada ({model_name})",
            prob=risk["prob"],
            risk_level=risk["level"],
            risk_emoji=risk["emoji"],
            risk_color=risk["color"],
            description="Cálculo realizado com base nos dados do exame importado e informações complementares."
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.info("💡 Recomendações Preliminares:")
        
        recs = rec_func(df_features, risk["prob"])
        for r in recs:
            st.markdown(f"- {r}")

    # ==========================================
    # RENDER PRINCIPAL
    # ==========================================
    def render(self):
        st.header(f"📂 {self.title}")
        st.markdown("Faça upload do laudo, verifique os dados e obtenha o resultado na hora.")

        # --- UPLOAD ---
        uploaded_file = st.file_uploader("Arraste seu laudo PDF aqui", type=["pdf"])
        
        extracted_data = {}
        
        if uploaded_file is not None:
            if "last_pdf" not in st.session_state or st.session_state["last_pdf"] != uploaded_file.name:
                with st.spinner("Lendo PDF..."):
                    extracted_data = parse_lab_file(uploaded_file)
                    st.session_state["current_pdf_data"] = extracted_data
                    st.session_state["last_pdf"] = uploaded_file.name
            else:
                extracted_data = st.session_state.get("current_pdf_data", {})
            
            if extracted_data:
                st.success("Dados lidos com sucesso!")
                with st.expander("Ver dados extraídos do PDF"):
                    st.json(extracted_data)
                
                # Botões rápidos para salvar no estado global (caso o usuário queira navegar pelas abas depois)
                cols = st.columns(4)
                if cols[0].button("Salvar p/ Cardio"): st.session_state["lab_data_cardio"] = extracted_data
                if cols[1].button("Salvar p/ Diabetes"): st.session_state["lab_data_diabetes"] = extracted_data
                if cols[2].button("Salvar p/ Renal"): st.session_state["lab_data_renal"] = extracted_data
                if cols[3].button("Salvar p/ Hepático"): st.session_state["lab_data_liver"] = extracted_data

            else:
                st.warning("Nenhum dado estruturado encontrado no PDF. Preencha manualmente abaixo.")

        st.markdown("---")
        
        # --- SELEÇÃO DE MODELO ---
        analysis_type = st.radio(
            "Qual análise deseja realizar agora?",
            ["Risco Cardíaco", "Diabetes", "Doença Renal", "Saúde Hepática"],
            horizontal=True
        )

        # --- ROTEAMENTO DO FORMULÁRIO ---
        if analysis_type == "Risco Cardíaco":
            self._render_cardio_form(extracted_data)
        elif analysis_type == "Diabetes":
            self._render_diabetes_form(extracted_data)
        elif analysis_type == "Doença Renal":
            self._render_renal_form(extracted_data)
        elif analysis_type == "Saúde Hepática":
            self._render_liver_form(extracted_data)