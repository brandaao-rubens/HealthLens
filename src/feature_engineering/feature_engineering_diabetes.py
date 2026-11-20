import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INPUT_PATH = ROOT / "data" / "processed" / "diabetes_clean.csv"
OUTPUT_PATH = ROOT / "data" / "processed" / "diabetes_features.csv"

def engineer_features():
    print("⚙️ Feature Engineering DIABETES (Monotonic)...")
    
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {INPUT_PATH}")

    df = pd.read_csv(INPUT_PATH)
    
    # 1. Encoding Ordinal para Tabagismo (Para funcionar a restrição monotônica)
    # Quanto maior o número, maior o risco teórico
    smoke_map = {
        'No Info': 0,
        'never': 0,
        'ever': 1,
        'not current': 1,
        'former': 2,
        'current': 3
    }
    # O dataset pode ter variações, normalizamos para string minúscula
    df['smoking_history'] = df['smoking_history'].astype(str).str.lower().map(smoke_map).fillna(0)

    # 2. Encoding Gênero
    gender_map = {'Female': 0, 'Male': 1, 'Other': 0}
    df['gender'] = df['gender'].map(gender_map).fillna(0)

    # 3. Feature de Interação: HbA1c * Glicose
    # (Os dois juntos explodem o risco)
    df['glucose_hba1c_interaction'] = df['blood_glucose_level'] * df['HbA1c_level']
    
    # 4. Feature: BMI Risk Score (Categorização simples para ajudar o modelo)
    # 0=Normal, 1=Sobrepeso, 2=Obeso
    conditions = [
        (df['bmi'] < 25),
        (df['bmi'] >= 25) & (df['bmi'] < 30),
        (df['bmi'] >= 30)
    ]
    choices = [0, 1, 2]
    df['bmi_category'] = np.select(conditions, choices, default=0)

    # Seleção Final
    features = [
        'age', 'gender', 'bmi', 'bmi_category',
        'hypertension', 'heart_disease', 
        'smoking_history', 
        'HbA1c_level', 'blood_glucose_level',
        'glucose_hba1c_interaction',
        'diabetes' # Target (Renomeado no preprocessing ou mantido original)
    ]
    
    # Verifica se a coluna alvo se chama 'diabetes' ou 'target'. Ajuste conforme seu preprocessing.
    # No seu print anterior parecia ser 'diabetes'. Se for 'target', mude aqui.
    if 'diabetes' not in df.columns and 'target' in df.columns:
        df.rename(columns={'target': 'diabetes'}, inplace=True)

    df = df[features]
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"✅ Features Diabetes salvas em: {OUTPUT_PATH}")

if __name__ == "__main__":
    engineer_features()