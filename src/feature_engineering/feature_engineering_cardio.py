import pandas as pd

def select_features(df):
    """
    Seleciona e organiza as features realmente importantes.
    """
    df = df.copy()

    FEATURES = [
        'age',
        'gender',
        'bmi',
        'ap_hi',
        'ap_lo',
        'chol',
        'glucose',
        'smoking',
        'alcohol',
        'active_lifestyle'
    ]

    TARGET = 'target'

    return df[FEATURES], df[TARGET]


# ============================================================
# EXECUÇÃO AUTOMÁTICA
# ============================================================

if __name__ == "__main__":
    print("📥 Carregando dataset limpo...")
    df_clean = pd.read_csv("data/processed/cardiovascular_clean.csv")

    print("⚙️ Selecionando features...")
    X, y = select_features(df_clean)

    print("💾 Salvando features em data/processed/cardiovascular_features.csv ...")
    df_features = pd.concat([X, y], axis=1)
    df_features.to_csv("data/processed/cardiovascular_features.csv", index=False)

    print("✅ Feature engineering concluído!")
