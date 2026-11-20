import os
import joblib
import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MODEL_PATH = ROOT / "models" / "classifiers" / "diabetes_best.pkl"


def load_diabetes_model():
    if not MODEL_PATH.exists():
        return None
    return joblib.load(MODEL_PATH)


def build_feature_vector(age, gender_label, bmi, hypertension_label,
                         heart_disease_label, hba1c, glucose, smoking_history_label):

    gender = 1 if gender_label == "Masculino" else 0
    hypertension = 1 if hypertension_label == "Sim" else 0
    heart_disease = 1 if heart_disease_label == "Sim" else 0

    # Tabagismo
    smoke_map = {
        "Nunca fumou": 0,
        "Sem informação": 0,
        "Parou de fumar": 2,
        "Fumava, mas não atualmente": 2,
        "Fuma atualmente": 3,
        "Já fumou / fumante crônico": 3,
    }
    smoking_val = smoke_map.get(smoking_history_label, 0)

    # Categorias
    bmi_cat = 2 if bmi >= 30 else 1 if bmi >= 25 else 0
    glucose_hba1c_interaction = glucose * hba1c

    data = {
        "age": [age],
        "gender": [gender],
        "bmi": [bmi],
        "bmi_category": [bmi_cat],
        "hypertension": [hypertension],
        "heart_disease": [heart_disease],
        "smoking_history": [smoking_val],
        "HbA1c_level": [hba1c],
        "blood_glucose_level": [glucose],
        "glucose_hba1c_interaction": [glucose_hba1c_interaction]
    }

    cols = [
        'age', 'gender', 'bmi', 'bmi_category', 'hypertension', 'heart_disease',
        'smoking_history', 'HbA1c_level', 'blood_glucose_level',
        'glucose_hba1c_interaction'
    ]

    return pd.DataFrame(data)[cols]


def compute_diabetes_risk(model, df):
    if model is None:
        return {"prob": 0, "level": "Erro", "color": "#grey", "emoji": "⚠️"}

    raw_prob = float(model.predict_proba(df)[0][1])
    prob = np.clip(raw_prob, 0.01, 0.99)

    # ---------------------------------------------------
    # ✔ Critérios ADA (versão correta)
    # ---------------------------------------------------
    hba1c = df["HbA1c_level"].iloc[0]
    glucose = df["blood_glucose_level"].iloc[0]

    is_diabetic = (hba1c >= 6.5) or (glucose >= 126)
    is_prediabetic = (5.7 <= hba1c < 6.5) or (100 <= glucose < 126)

    # ---------------------------------------------------
    # ✔ Ajustes clínicos leves (não quebram calibração)
    # ---------------------------------------------------

    # Caso diabetes confirmado → probabilidade mínima 60%
    if is_diabetic and prob < 0.60:
        prob = 0.60

    # Caso pré-diabetes → prob mínima 20%, mas NÃO 40–50% (exagerado)
    elif is_prediabetic and prob < 0.20:
        prob = 0.20

    # ---------------------------------------------------
    # Classificação visual
    # ---------------------------------------------------
    if prob < 0.25:
        level = "Baixo"; color = "#28a745"; emoji = "🟢"
    elif prob < 0.50:
        level = "Moderado"; color = "#ffc107"; emoji = "🟡"
    elif prob < 0.75:
        level = "Alto"; color = "#fd7e14"; emoji = "🟠"
    else:
        level = "Muito Alto"; color = "#dc3545"; emoji = "🔴"

    return {
        "prob": float(prob),
        "level": level,
        "emoji": emoji,
        "color": color
    }
