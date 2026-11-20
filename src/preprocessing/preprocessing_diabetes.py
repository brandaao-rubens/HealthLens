import os
import pandas as pd


def load_raw_diabetes(path: str = "data/raw/diabetes_prediction_dataset.csv") -> pd.DataFrame:
    """Carrega o dataset bruto de diabetes."""
    return pd.read_csv(path)


def clean_diabetes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpa o dataset:
    - remove pacientes < 18 anos
    - remove gênero 'Other'
    - corrige outliers de IMC
    - corrige glicemia fora do padrão
    """
    df = df.copy()

    # 1) Apenas adultos
    df = df[df["age"] >= 18]

    # 2) Remover gêneros raros
    df = df[df["gender"].isin(["Male", "Female"])]

    # 3) Corrigir IMC
    df["bmi"] = df["bmi"].clip(15, 60)

    # 4) Corrigir glicemia extrema
    df["blood_glucose_level"] = df["blood_glucose_level"].clip(70, 300)

    df = df.reset_index(drop=True)
    return df


def save_clean(df: pd.DataFrame, path: str = "data/processed/diabetes_clean.csv"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)


def run_preprocessing():
    print("[DIABETES] Carregando dataset...")
    df_raw = load_raw_diabetes()

    print("[DIABETES] Limpando dataset...")
    df_clean = clean_diabetes(df_raw)

    print("[DIABETES] Salvando...")
    save_clean(df_clean)

    print("[DIABETES] Preprocessing concluído!")
    return df_clean


if __name__ == "__main__":
    run_preprocessing()