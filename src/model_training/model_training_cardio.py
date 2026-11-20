import os
import joblib
import numpy as np
import pandas as pd

from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, classification_report
from sklearn.calibration import CalibratedClassifierCV

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "cardiovascular_features.csv")
MODELS_DIR = os.path.join(BASE_DIR, "models", "classifiers")


# ============================================================
# 1. MONOTONIC CONSTRAINTS CLÍNICAS (OTIMIZADAS)
# ============================================================
# Mantemos monotonicidade APENAS onde faz sentido:
#   idade ↑ → risco ↑
#   pressão ↑ → risco ↑
#   IMC ↑ → risco ↑
#   tabagismo ↑ → risco ↑
# NÃO aplicar monotonic em colesterol/glicemia categorizados.
# Isso gera explosões devido ao salto 1→2→3.

def get_monotonic_constraints(columns):
    constraints = []
    for col in columns:

        # NÃO aplicar nos categorizados (chol, glucose)
        if col in ['chol', 'glucose']:
            constraints.append(0)
            continue

        # Váriaveis contínuas — monotônicas
        if col in ["age", "bmi", "ap_hi", "ap_lo", "smoking", "alcohol"]:
            constraints.append(1)

        elif col in ["active_lifestyle"]:
            constraints.append(-1)

        else:
            constraints.append(0)

    return tuple(constraints)


def load_data():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Arquivo não encontrado: {DATA_PATH}")
    return pd.read_csv(DATA_PATH)


# ============================================================
# 2. RE-TREINO CLÍNICO (SEM OPTUNA, ROBUSTO)
# ============================================================
def train_model():
    print("🚀 Re-Treinando Modelo Cardíaco (versão clínica + suave)...")

    df = load_data()
    X = df.drop(columns=["target"])
    y = df["target"]

    # Desbalanceamento — NÃO usar ratio exagerado
    ratio = (y == 0).sum() / (y == 1).sum()
    print(f"[INFO] scale_pos_weight ajustado: {ratio:.2f}")

    constraints = get_monotonic_constraints(X.columns)
    print("[INFO] Constraints:", constraints)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    # ========================================================
    # PARÂMETROS OTIMIZADOS CLINICAMENTE
    # ========================================================
    base_model = XGBClassifier(
        n_estimators=260,
        max_depth=4,
        learning_rate=0.035,
        subsample=0.9,
        colsample_bytree=0.9,

        # regularização (reduz exageros)
        reg_alpha=2.5,
        reg_lambda=8.5,
        min_child_weight=10,

        # constraints clínicos
        monotone_constraints=constraints,

        # desbalanceamento ajustado corretamente
        scale_pos_weight=ratio,

        # performance
        tree_method="hist",
        eval_metric="logloss",
        n_jobs=-1,
        random_state=42,
    )

    # ========================================================
    # CALIBRAÇÃO — SIGMOID (Perfeita para suavizar probabilidades)
    # ========================================================
    calibrated_model = CalibratedClassifierCV(
        base_model, method="sigmoid", cv=5
    )

    calibrated_model.fit(X_train, y_train)

    # ========================================================
    # Avaliação
    # ========================================================
    preds = calibrated_model.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, preds)

    print(f"\n🏆 AUC (modelo final calibrado): {auc:.4f}")
    print("\n📊 Classification Report:")
    print(classification_report(y_test, (preds >= 0.5).astype(int), digits=3))

    os.makedirs(MODELS_DIR, exist_ok=True)
    save_path = os.path.join(MODELS_DIR, "cardio_best.pkl")
    joblib.dump(calibrated_model, save_path)

    print(f"\n✅ Modelo salvo em: {save_path}")


if __name__ == "__main__":
    train_model()
