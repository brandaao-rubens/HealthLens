import os
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier, StackingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    roc_auc_score,
    classification_report,
    roc_curve,
)
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from xgboost import XGBClassifier
import optuna

# ================================
# CONFIGURAÇÕES DE CAMINHOS
# ================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "liver_features.csv")
MODELS_DIR = os.path.join(BASE_DIR, "models", "classifiers")
EXPLAINER_DIR = os.path.join(BASE_DIR, "models", "explainer")

# ================================
# CARREGAR DATASET
# ================================
def load_liver_features(path: str = DATA_PATH) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Arquivo não encontrado: {path}. Rode o feature engineering primeiro.")
    df = pd.read_csv(path)
    return df

def split_dataset(df: pd.DataFrame):
    X = df.drop(columns=["target"])
    y = df["target"]

    return train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )

# ================================
# OPTUNA XGBOOST TUNING
# ================================
def _optuna_objective(trial, X_train, X_valid, y_train, y_valid):
    # Otimizado para datasets pequenos/médios
    param = {
        "n_estimators": trial.suggest_int("n_estimators", 50, 300),
        "max_depth": trial.suggest_int("max_depth", 2, 6),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
        "subsample": trial.suggest_float("subsample", 0.6, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
        "reg_lambda": trial.suggest_float("reg_lambda", 0.1, 10.0, log=True),
        "scale_pos_weight": trial.suggest_float("scale_pos_weight", 1.0, 5.0), # Importante pois ILPD é desbalanceado
        
        "eval_metric": "logloss",
        "random_state": 42,
        "n_jobs": -1,
    }

    model = XGBClassifier(**param)
    model.fit(X_train, y_train)

    proba = model.predict_proba(X_valid)[:, 1]
    auc = roc_auc_score(y_valid, proba)
    return auc

def tune_xgb_with_optuna(X_train, y_train, n_trials: int = 30):
    print("[INFO] Tuning hyperparameters (Liver) with Optuna...")
    X_t, X_v, y_t, y_v = train_test_split(
        X_train,
        y_train,
        test_size=0.20,
        random_state=42,
        stratify=y_train
    )

    study = optuna.create_study(direction="maximize")
    study.optimize(lambda trial: _optuna_objective(trial, X_t, X_v, y_t, y_v), n_trials=n_trials)

    best_params = study.best_params.copy()
    best_params.update({
        "eval_metric": "logloss",
        "random_state": 42,
        "n_jobs": -1,
    })

    print(f"[OPTUNA] Best AUC: {study.best_value:.4f}")
    return best_params

# ================================
# TREINO INDIVIDUAL
# ================================
def train_individual_models(X_train, y_train, xgb_params: dict):

    print("[INFO] Training RandomForest...")
    rf = RandomForestClassifier(
        n_estimators=200, 
        class_weight="balanced",
        max_depth=8, 
        random_state=42,
        n_jobs=-1
    )
    rf.fit(X_train, y_train)

    print("[INFO] Training GradientBoosting...")
    gb = GradientBoostingClassifier(
        n_estimators=150,
        learning_rate=0.05,
        max_depth=3,
        random_state=42
    )
    gb.fit(X_train, y_train)

    print("[INFO] Training tuned XGBoost...")
    xgb = XGBClassifier(**xgb_params)
    xgb.fit(X_train, y_train)

    print("[INFO] Training Neural Network (MLP)...")
    mlp = MLPClassifier(
        hidden_layer_sizes=(32, 16),
        max_iter=1000,
        random_state=42,
        early_stopping=True,
        validation_fraction=0.2
    )
    mlp.fit(X_train, y_train)

    return rf, gb, xgb, mlp

# ================================
# AVALIAÇÃO
# ================================
def evaluate_model(name: str, model, X_test, y_test):
    preds = model.predict(X_test)

    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X_test)[:, 1]
    else:
        proba = preds

    acc = accuracy_score(y_test, preds)
    f1 = f1_score(y_test, preds)
    
    try:
        auc = roc_auc_score(y_test, proba)
    except ValueError:
        auc = 0.5 

    print(f"\n===== {name} =====")
    print(f"Accuracy: {acc:.4f} | F1: {f1:.4f} | AUC: {auc:.4f}")

    return {
        "name": name,
        "acc": acc,
        "f1": f1,
        "auc": auc,
        "model": model,
    }

# ================================
# ENSEMBLES
# ================================
def build_voting_ensemble(rf, gb, xgb):
    return VotingClassifier(
        estimators=[
            ("rf", rf),
            ("gb", gb),
            ("xgb", xgb)
        ],
        voting="soft",
        n_jobs=-1
    )

def build_stacking_ensemble(rf, gb, xgb):
    meta = LogisticRegression(max_iter=1000, class_weight="balanced")
    return StackingClassifier(
        estimators=[
            ("rf", rf),
            ("gb", gb),
            ("xgb", xgb)
        ],
        final_estimator=meta,
        stack_method="predict_proba",
        n_jobs=-1
    )

# ================================
# CALIBRAÇÃO
# ================================
def calibrate_probabilities(model, X_train, y_train):
    print("[INFO] Calibrating XGB...")
    calibrated = CalibratedClassifierCV(estimator=model, method="isotonic", cv=3)
    calibrated.fit(X_train, y_train)
    return calibrated

# ================================
# DIAGNÓSTICOS (Plots)
# ================================
def generate_diagnostics_plots(model, X_test, y_test, output_dir=EXPLAINER_DIR):
    os.makedirs(output_dir, exist_ok=True)
    proba = model.predict_proba(X_test)[:, 1]

    # ROC Curve
    fpr, tpr, _ = roc_curve(y_test, proba)
    plt.figure()
    plt.plot(fpr, tpr, label="Modelo Hepático")
    plt.plot([0, 1], [0, 1], "k--", label="Aleatório")
    plt.title("Curva ROC - Doença Hepática")
    plt.savefig(os.path.join(output_dir, "roc_liver.png"), dpi=100)
    plt.close()

    # Calibration Curve
    prob_true, prob_pred = calibration_curve(y_test, proba, n_bins=5, strategy="uniform")
    plt.figure()
    plt.plot(prob_pred, prob_true, "o-", label="Modelo Hepático")
    plt.plot([0, 1], [0, 1], "k--")
    plt.title("Calibração - Doença Hepática")
    plt.savefig(os.path.join(output_dir, "calibration_liver.png"), dpi=100)
    plt.close()
    
    print(f"[INFO] Gráficos salvos em {output_dir}")

# ================================
# SALVAMENTO
# ================================
def save_models(best_model, all_models_dict):
    os.makedirs(MODELS_DIR, exist_ok=True)
    
    joblib.dump(best_model, os.path.join(MODELS_DIR, "liver_best.pkl"))
    print(f"[INFO] Melhor modelo salvo: liver_best.pkl")

# ================================
# MAIN PIPELINE
# ================================
def run_training(n_trials_optuna: int = 20):
    print("🚀 [LIVER] Starting training pipeline...")
    
    df = load_liver_features()
    X_train, X_test, y_train, y_test = split_dataset(df)

    # 1. Tuning
    tuned_params = tune_xgb_with_optuna(X_train, y_train, n_trials_optuna)

    # 2. Treino Individual
    rf, gb, xgb_tuned, mlp = train_individual_models(X_train, y_train, tuned_params)

    # 3. Ensembles
    voting = build_voting_ensemble(rf, gb, xgb_tuned)
    voting.fit(X_train, y_train)

    stacking = build_stacking_ensemble(rf, gb, xgb_tuned)
    stacking.fit(X_train, y_train)

    # 4. Calibração
    calibrated_xgb = calibrate_probabilities(xgb_tuned, X_train, y_train)

    # 5. Avaliação
    models_to_eval = [
        ("RandomForest", rf),
        ("GradientBoosting", gb),
        ("XGBoost Tuned", xgb_tuned),
        ("MLP", mlp),
        ("Voting", voting),
        ("Stacking", stacking),
        ("Calibrated XGB", calibrated_xgb)
    ]

    results = []
    model_dict = {}
    
    for name, model in models_to_eval:
        res = evaluate_model(name, model, X_test, y_test)
        results.append(res)
        model_dict[name] = model

    # Escolher o melhor via AUC
    results_sorted = sorted(results, key=lambda x: x["auc"], reverse=True)
    best_result = results_sorted[0]
    
    print(f"\n🏆 MELHOR MODELO: {best_result['name']} (AUC: {best_result['auc']:.4f})")

    # 6. Salvar e Diagnósticos
    save_models(best_result["model"], model_dict)
    generate_diagnostics_plots(best_result["model"], X_test, y_test)

    print("\n✅ [LIVER] Pipeline finalizado com sucesso!")

if __name__ == "__main__":
    run_training()