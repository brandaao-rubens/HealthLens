import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW_PATH = ROOT / "data" / "raw" / "indian_liver_patient.csv"
PROCESSED_PATH = ROOT / "data" / "processed" / "liver_clean.csv"

def clean_data():
    print("🔄 Iniciando pré-processamento LIVER...")
    
    # Verifica se arquivo existe
    if not RAW_PATH.exists():
        print(f"❌ Erro: Arquivo não encontrado em {RAW_PATH}")
        print("   Baixe o dataset 'Indian Liver Patient' e salve como indian_liver_patient.csv")
        return

    df = pd.read_csv(RAW_PATH)
    
    # 1. Renomear colunas para padrão interno (snake_case)
    rename_map = {
        'Age': 'age',
        'Gender': 'gender',
        'Total_Bilirubin': 'bilirubin_total',
        'Direct_Bilirubin': 'bilirubin_direct',
        'Alkaline_Phosphotase': 'alkaline_phosphatase',
        'Alamine_Aminotransferase': 'sgpt', # ALT
        'Aspartate_Aminotransferase': 'sgot', # AST
        'Total_Protiens': 'proteins',
        'Albumin': 'albumin',
        'Albumin_and_Globulin_Ratio': 'ag_ratio',
        'Dataset': 'target'
    }
    df.rename(columns=rename_map, inplace=True)
    
    # 2. Tratamento de Gênero
    df['gender'] = df['gender'].map({'Male': 1, 'Female': 0})
    
    # 3. Tratamento de Nulos
    # Apenas a coluna ag_ratio costuma ter nulos nesse dataset
    df['ag_ratio'] = df['ag_ratio'].fillna(df['ag_ratio'].median())
    
    # 4. Tratamento do Target
    # No dataset original: 1 = Doença, 2 = Saudável
    # Vamos converter para: 1 = Doença, 0 = Saudável
    df['target'] = df['target'].map({1: 1, 2: 0})
    
    df.to_csv(PROCESSED_PATH, index=False)
    print(f"✅ Dados limpos salvos em: {PROCESSED_PATH}")

if __name__ == "__main__":
    clean_data()