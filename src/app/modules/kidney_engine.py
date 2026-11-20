import os
import joblib
import pandas as pd
import numpy as np # <--- Importante
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MODEL_PATH = ROOT / "models" / "classifiers" / "renal_best.pkl"

def load_renal_model():
    if not MODEL_PATH.exists():
        return None
    return joblib.load(MODEL_PATH)

def build_feature_vector(age, bp, glucose, urea, creatinine, potassium, hemo, hypertension, diabetes):
    """
    Constrói o DataFrame com as colunas EXATAS que o modelo espera.
    """
    # Converter Sim/Não para 1/0
    htn_val = 1 if hypertension == "Sim" else 0
    dm_val = 1 if diabetes == "Sim" else 0

    # Calcular Razão Ureia/Creatinina (Feature derivada usada no treino)
    # Adicionamos um epsilon pequeno para evitar divisão por zero
    ratio = urea / (creatinine + 0.1)

    data = {
        "age": [age],
        "blood_pressure": [bp],
        "glucose": [glucose],
        "urea": [urea],
        "creatinine": [creatinine],
        "potassium": [potassium],
        "hemo": [hemo],
        "hypertension": [htn_val],
        "diabetes": [dm_val],
        "bun_creatinine_ratio": [ratio]
    }
    
    # Ordem exata das colunas
    cols = ['age', 'blood_pressure', 'glucose', 'urea', 'creatinine', 
            'potassium', 'hemo', 'hypertension', 'diabetes', 'bun_creatinine_ratio']
    
    return pd.DataFrame(data)[cols]

def compute_renal_risk(model, df_features):
    if model is None:
        return {"prob": 0, "level": "Erro", "color": "#grey", "emoji": "⚠️"}

    # Probabilidade bruta
    raw_prob = model.predict_proba(df_features)[0][1]
    
    # --- CORREÇÃO DE PROBABILIDADE (CLIPPING) ---
    # Limita entre 1% e 99% para evitar o "100% de certeza"
    prob = float(np.clip(raw_prob, 0.01, 0.99))
    
    # Classificação Clínica
    if prob < 0.30:
        level = "Baixo"
        color = "#28a745" # Verde
        emoji = "🟢"
    elif prob < 0.60:
        level = "Moderado"
        color = "#ffc107" # Amarelo
        emoji = "🟡"
    elif prob < 0.85:
        level = "Alto"
        color = "#fd7e14" # Laranja
        emoji = "🟠"
    else:
        level = "Muito Alto"
        color = "#dc3545" # Vermelho
        emoji = "🔴"

    return {
        "prob": prob,
        "level": level,
        "color": color,
        "emoji": emoji
    }