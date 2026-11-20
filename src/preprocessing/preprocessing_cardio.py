import pandas as pd
import numpy as np

def load_raw_cardio(path):
    """Carrega o dataset bruto"""
    df = pd.read_csv(path, sep=';')  # geralmente vem com ';'
    return df


def clean_cardio(df):
    """Limpeza e padronização do dataset cardiovascular"""

    df = df.copy()

    # -----------------------------------------
    # 1. Remover outliers impossíveis
    # -----------------------------------------

    df = df[(df['age'] > 20*365) & (df['age'] < 120*365)]  # idade em dias
    df['age'] = (df['age'] / 365).astype(int)

    df = df[(df['ap_hi'] > 70) & (df['ap_hi'] < 240)]
    df = df[(df['ap_lo'] > 40) & (df['ap_lo'] < 180)]
    df = df[df['height'] > 120]
    df = df[df['weight'] > 30]

    # -----------------------------------------
    # 2. Criar IMC
    # -----------------------------------------
    df['bmi'] = df['weight'] / ((df['height'] / 100) ** 2)

    # -----------------------------------------
    # 3. Padronizar nomes
    # -----------------------------------------
    df.rename(columns={
        'cholesterol': 'chol',
        'gluc': 'glucose',
        'alco': 'alcohol',
        'smoke': 'smoking',
        'active': 'active_lifestyle',
        'cardio': 'target'
    }, inplace=True)

    # -----------------------------------------
    # 4. Reset index
    # -----------------------------------------
    df.reset_index(drop=True, inplace=True)

    return df


def save_clean(df, path):
    df.to_csv(path, index=False)

if __name__ == "__main__":
    print("📥 Carregando dataset bruto...")
    df_raw = load_raw_cardio("data/raw/cardiovascular_raw.csv")

    print("🧹 Limpando dataset...")
    df_clean = clean_cardio(df_raw)

    print("💾 Salvando dataset limpo em data/processed/cardiovascular_clean.csv ...")
    save_clean(df_clean, "data/processed/cardiovascular_clean.csv")

    print("✅ Preprocessing concluído com sucesso!")