import os
import joblib
import pandas as pd
import numpy as np

from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler
from sklearn.calibration import CalibratedClassifierCV
from sklearn.pipeline import Pipeline


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "diabetes_features.csv")
MODELS_DIR = os.path.join(BASE_DIR, "models", "classifiers")


# ----------------------------------------------------------
# MONOTONIC CONSTRAINTS
# ----------------------------------------------------------
def get_monotonic_constraints(columns):
    constraints = []
    positive_features = [
        'age', 'bmi', 'bmi_category',
        'hypertension', 'heart_disease', 'smoking_history',
        'HbA1c_level', 'blood_glucose_level',
        'glucose_hba1c_interaction',
        'gender'
    ]

    for col in columns:
        if col in positive_features:
            constraints.append(1)   # risco aumenta quando a feature aumenta
        else:
            constraints.append(0)   # sem restrição
    return tuple(constraints)



# ----------------------------------------------------------
# TREINO PRINCIPAL (VERSÃO SUAVIZADA + CALIBRADA)
# ----------------------------------------------------------
def train_diabetes_model():
    print("🚀 Treinando DIABETES – versão corrigida e calibrada")

    # -----------------------------
    # 1. Carregar dataset
    # -----------------------------
    df = pd.read_csv(DATA_PATH)
    target = "diabetes"

    X = df.drop(columns=[target])
    y = df[target]

    # -----------------------------
    # 2. Balanceamento leve
    # -----------------------------
    ratio = float(np.sum(y == 0) / np.sum(y == 1))
    scale_pos_weight = ratio * 1.0    # antes = ratio * 2.0 (muito agressivo)
    print(f"[INFO] scale_pos_weight = {scale_pos_weight:.2f}")

    constraints = get_monotonic_constraints(X.columns)

    # -----------------------------
    # 3. Divisão treino/teste
    # -----------------------------
    x_train, x_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    # -----------------------------
    # 4. Modelo XGBoost ajustado
    # -----------------------------
    xgb = XGBClassifier(
        n_estimators=300,
        max_depth=3,               # menor = menos overfitting
        learning_rate=0.03,        # aprendizado suave
        subsample=0.9,
        colsample_bytree=0.9,
        min_child_weight=4,        # suaviza splits
        reg_lambda=2.0,
        scale_pos_weight=scale_pos_weight,
        monotone_constraints=constraints,
        tree_method="hist",
        eval_metric="logloss",
        random_state=42,
        n_jobs=-1,
    )

    # -----------------------------
    # 5. Calibração (ESSENCIAL)
    # compatível com TODAS versões sklearn
    # -----------------------------
    calib = CalibratedClassifierCV(
        xgb, method="isotonic", cv=3
    )

    # -----------------------------
    # 6. Pipeline com normalização
    # -----------------------------
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("calibrated_model", calib)
    ])

    # -----------------------------
    # 7. Treino
    # -----------------------------
    pipeline.fit(x_train, y_train)

    # -----------------------------
    # 8. Avaliação
    # -----------------------------
    probs = pipeline.predict_proba(x_test)[:, 1]
    auc = roc_auc_score(y_test, probs)
    print(f"🏆 AUC Final (calibrado): {auc:.4f}")

    # -----------------------------
    # 9. Salvar modelo
    # -----------------------------
    path = os.path.join(MODELS_DIR, "diabetes_best.pkl")
    joblib.dump(pipeline, path)
    print(f"🎉 Modelo salvo em: {path}")


# ----------------------------------------------------------
# Execução direta
# ----------------------------------------------------------
if __name__ == "__main__":
    train_diabetes_model()
