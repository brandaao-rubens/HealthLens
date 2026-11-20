import os
import joblib
import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MODEL_PATH = ROOT / "models" / "classifiers" / "liver_best.pkl"

def load_liver_model():
    if not MODEL_PATH.exists():
        return None
    return joblib.load(MODEL_PATH)

def build_feature_vector(age, gender_label, bilirubin_total, bilirubin_direct, 
                         alkaline_phosphatase, sgpt, sgot, proteins, albumin, ag_ratio):
    
    # 1. Mapeamento de Gênero (Igual ao treino: Male=1, Female=0)
    gender = 1 if gender_label == "Masculino" else 0
    
    # 2. Cálculo das Features Derivadas (Engenharia de Features)
    # Globulinas = Proteínas - Albumina
    globulin = proteins - albumin
    
    # Bilirrubina Indireta = Total - Direta
    bilirubin_indirect = bilirubin_total - bilirubin_direct
    
    # Razão De Ritis (AST/ALT)
    ast_alt_ratio = sgot / (sgpt + 0.1) # +0.1 para evitar divisão por zero

    data = {
        "age": [age],
        "gender": [gender],
        "bilirubin_total": [bilirubin_total],
        "bilirubin_direct": [bilirubin_direct],
        "alkaline_phosphatase": [alkaline_phosphatase],
        "sgpt": [sgpt], # ALT
        "sgot": [sgot], # AST
        "proteins": [proteins],
        "albumin": [albumin],
        "ag_ratio": [ag_ratio],
        # Derivadas:
        "ast_alt_ratio": [ast_alt_ratio],
        "globulin": [globulin],
        "bilirubin_indirect": [bilirubin_indirect]
    }
    
    # Garante a ordem das colunas conforme o treino
    cols_order = [
        "age", "gender", "bilirubin_total", "bilirubin_direct", 
        "alkaline_phosphatase", "sgpt", "sgot", "proteins", 
        "albumin", "ag_ratio", "ast_alt_ratio", "globulin", "bilirubin_indirect"
    ]
    
    return pd.DataFrame(data)[cols_order]

def compute_liver_risk(model, df_features):
    if model is None:
        return {"prob": 0, "level": "Erro", "color": "#grey", "emoji": "⚠️"}

    # Probabilidade da classe 1 (Doença Hepática)
    prob = model.predict_proba(df_features)[0][1]
    
    if prob < 0.30:
        level = "Baixo"
        color = "#28a745"
        emoji = "🟢"
    elif prob < 0.60:
        level = "Moderado"
        color = "#ffc107"
        emoji = "🟡"
    elif prob < 0.85:
        level = "Alto"
        color = "#fd7e14"
        emoji = "🟠"
    else:
        level = "Muito Alto"
        color = "#dc3545"
        emoji = "🔴"

    return {
        "prob": prob,
        "level": level,
        "color": color,
        "emoji": emoji
    }