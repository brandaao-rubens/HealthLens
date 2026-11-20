import pandas as pd
import numpy as np
from pathlib import Path

# Configuração de caminhos
ROOT = Path(__file__).resolve().parents[2]
# Ajuste para o nome do seu arquivo CSV
RAW_PATH = ROOT / "data" / "raw" / "kidney_disease.csv"
PROCESSED_PATH = ROOT / "data" / "processed" / "kidney_clean.csv"

def clean_data():
    print("🔄 Iniciando pré-processamento RENAL (via CSV)...")
    
    # 1. Carregar CSV direto
    df = pd.read_csv(RAW_PATH)
    
    # Remover coluna ID se existir (não é feature médica)
    if 'id' in df.columns:
        df.drop('id', axis=1, inplace=True)
    
    # 2. Limpeza Profunda de Strings (A "faxina")
    # O dataset tem muitos erros de tabulação (\t) e espaços
    obj_cols = df.select_dtypes(include=['object']).columns
    for col in obj_cols:
        df[col] = df[col].str.strip() # Remove espaços nas pontas
        df[col] = df[col].str.replace('\t', '') # Remove tabs escondidos
    
    # 3. Conversão Forçada de Numéricos
    # PCV, WC e RC costumam vir com erros que impedem a leitura automática
    numeric_cols_fix = ['pcv', 'wc', 'rc']
    for col in numeric_cols_fix:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # 4. Renomear para o padrão HealthLens (Inglês Técnico -> Código Limpo)
    rename_map = {
        'age': 'age',
        'bp': 'blood_pressure',
        'sc': 'creatinine',       # Essencial para integração com PDF
        'bu': 'urea',             # Essencial
        'pot': 'potassium',
        'bgr': 'glucose',         # Glicemia aleatória
        'htn': 'hypertension',
        'dm': 'diabetes',
        'cad': 'cad',             # Doença arterial coronariana
        'classification': 'target'
    }
    df.rename(columns=rename_map, inplace=True)
    
    # 5. Tratamento do Target
    # Mapeia 'ckd' para 1 (Doente) e 'notckd' para 0 (Saudável)
    # O replace limpa eventuais erros que tenham sobrado
    df['target'] = df['target'].map({'ckd': 1, 'notckd': 0})
    
    # 6. Salvar
    df.to_csv(PROCESSED_PATH, index=False)
    print(f"✅ Dados limpos salvos em: {PROCESSED_PATH}")
    print(f"   Amostras finais: {len(df)}")
    print(f"   Colunas tratadas: {list(df.columns)}")

if __name__ == "__main__":
    clean_data()