import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INPUT_PATH = ROOT / "data" / "processed" / "kidney_clean.csv"
OUTPUT_PATH = ROOT / "data" / "processed" / "kidney_features.csv"

def engineer_features():
    print("⚙️ Iniciando Feature Engineering RENAL...")
    
    df = pd.read_csv(INPUT_PATH)
    
    # 1. Separação de features numéricas e categóricas
    numeric_cols = ['age', 'blood_pressure', 'glucose', 'urea', 'creatinine', 'potassium', 'hemo']
    # Mantemos apenas as colunas que conseguimos pedir na UI ou extrair do PDF com facilidade
    # Simplificando o modelo para focar no que é preenchível
    
    # Features binárias/textuais importantes
    cat_cols = ['hypertension', 'diabetes']
    
    # Seleção final de colunas para o modelo (Dropamos coisas difíceis de obter como 'pus cell clumps')
    selected_cols = numeric_cols + cat_cols + ['target']
    df = df[selected_cols]
    
    # 2. Imputação de Nulos (Estratégia Simples: Mediana/Moda)
    for col in numeric_cols:
        df[col] = df[col].fillna(df[col].median())
        
    for col in cat_cols:
        mode_val = df[col].mode()[0]
        df[col] = df[col].fillna(mode_val)
    
    # 3. Encoding Binário
    binary_map = {'yes': 1, 'no': 0}
    df['hypertension'] = df['hypertension'].map(binary_map)
    df['diabetes'] = df['diabetes'].map(binary_map)
    
    # Fallback para nulos que sobraram no map
    df = df.fillna(0)
    
    # 4. Feature Derivada: Razão Ureia/Creatinina (BUN/Creatinine Ratio)
    # Importante marcador de função renal aguda vs crônica
    # Adiciona 0.1 para evitar divisão por zero
    df['bun_creatinine_ratio'] = df['urea'] / (df['creatinine'] + 0.1)
    
    # 5. Salvar
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"✅ Features salvas em: {OUTPUT_PATH}")

if __name__ == "__main__":
    engineer_features()