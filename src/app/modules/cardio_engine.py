import joblib
import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MODEL_PATH = ROOT / "models" / "classifiers" / "cardio_best.pkl"


# ======================================================
# 1. Funções de conversão REAL → CATEGORIA (clínico)
# ======================================================

def convert_cholesterol_category(value_mgdl: float) -> int:
    """
    Colesterol total (mg/dL) -> categoria de risco
    1 = normal (<200)
    2 = limítrofe (200–239)
    3 = alto (>=240)
    """
    if value_mgdl < 200:
        return 1
    if value_mgdl < 240:
        return 2
    return 3  # >=240


def convert_glucose_category(value_mgdl: float) -> int:
    """
    Glicemia em jejum (mg/dL) -> categoria
    1 = normal (<100)
    2 = pré-diabetes (100–125)
    3 = diabetes (>=126)
    """
    if value_mgdl < 100:
        return 1
    if value_mgdl < 126:
        return 2
    return 3  # >=126


# ======================================================
# 2. Carregamento do modelo
# ======================================================

def load_cardio_model():
    if not MODEL_PATH.exists():
        return None
    return joblib.load(MODEL_PATH)


# ======================================================
# 3. Vetor de Features Para o Modelo
# ======================================================

def build_feature_vector(
    age,
    gender_label,
    height_cm,
    weight_kg,
    ap_hi,
    ap_lo,
    chol_category,
    gluc_category,
    smoking_label,
    alcohol_label,
    active_label,
):
    """
    Monta o vetor de features exatamente no mesmo formato
    usado no treinamento.
    """

    gender = 2 if gender_label == "Masculino" else 1
    smoking = 1 if smoking_label == "Sim" else 0
    alcohol = 1 if alcohol_label == "Sim" else 0
    active = 1 if active_label == "Sim" else 0

    height_m = height_cm / 100.0
    bmi = weight_kg / (height_m ** 2)

    data = {
        "age": [age],
        "gender": [gender],
        "bmi": [bmi],
        "ap_hi": [ap_hi],
        "ap_lo": [ap_lo],
        "chol": [chol_category],
        "glucose": [gluc_category],
        "smoking": [smoking],
        "alcohol": [alcohol],
        "active_lifestyle": [active],
    }

    cols = [
        "age",
        "gender",
        "bmi",
        "ap_hi",
        "ap_lo",
        "chol",
        "glucose",
        "smoking",
        "alcohol",
        "active_lifestyle",
    ]

    return pd.DataFrame(data)[cols]


# ======================================================
# 4. Camada clínica em cima da probabilidade
# ======================================================

def apply_clinical_overrides(df_features: pd.DataFrame, prob: float) -> float:
    """
    Ajuste suave da probabilidade — sem travamentos, sem explosões.
    Mantém o modelo como principal e apenas faz correções pequenas.
    """

    row = df_features.iloc[0]

    age = row["age"]
    bmi = row["bmi"]
    ap_hi = row["ap_hi"]
    ap_lo = row["ap_lo"]
    chol_cat = row["chol"]
    gluc_cat = row["glucose"]
    smoking = row["smoking"]
    alcohol = row["alcohol"]
    active = row["active_lifestyle"]

    # ================================
    # 1. Contagem de fatores de risco
    # ================================
    risk_flags = 0
    if age >= 55: risk_flags += 1
    if bmi >= 30: risk_flags += 1
    if ap_hi >= 140 or ap_lo >= 90: risk_flags += 1
    if chol_cat >= 2: risk_flags += 1
    if gluc_cat >= 2: risk_flags += 1
    if smoking == 1: risk_flags += 1
    if alcohol == 1: risk_flags += 1
    if active == 0: risk_flags += 1

    # ================================
    # 2. Ajustes suaves
    # ================================

    # Caso claramente baixo risco → reduzir levemente
    if risk_flags == 0:
        prob = prob * 0.85   # -15%
        prob = max(prob, 0.02)

    # Poucos fatores → não trava mais em 40%
    elif risk_flags in (1, 2):
        prob = prob  # sem intervenção

    # Moderado/Alto risco → pequeno reforço
    elif 3 <= risk_flags <= 4:
        prob = prob + 0.10   # +10%
        prob = min(prob, 0.90)

    # Muito alto risco
    elif risk_flags >= 5:
        prob = prob + 0.20   # +20%
        prob = min(prob, 0.95)

    # Clip suave para garantir limites
    prob = float(np.clip(prob, 0.01, 0.99))
    return prob


# ======================================================
# 5. Cálculo do Risco
# ======================================================

def compute_cardio_risk(model, df_features: pd.DataFrame):
    if model is None:
        return {"prob": 0.0, "level": "Erro", "color": "#808080", "emoji": "⚠️"}

    # Probabilidade bruta (modelo já está calibrado no treinamento)
    raw_prob = model.predict_proba(df_features)[0][1]

    # Aplica camada clínica
    prob = apply_clinical_overrides(df_features, raw_prob)

    # Classificação em faixas
    if prob < 0.25:
        meta = {"level": "Baixo", "color": "#28a745", "emoji": "🟢"}
    elif prob < 0.50:
        meta = {"level": "Moderado", "color": "#ffc107", "emoji": "🟡"}
    elif prob < 0.75:
        meta = {"level": "Alto", "color": "#fd7e14", "emoji": "🟠"}
    else:
        meta = {"level": "Muito Alto", "color": "#dc3545", "emoji": "🔴"}

    meta["prob"] = float(prob)
    meta["bmi"] = float(df_features["bmi"].iloc[0])

    return meta
