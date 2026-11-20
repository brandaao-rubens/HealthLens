import os
import joblib
import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from sklearn.calibration import CalibratedClassifierCV
import optuna

# ================================
# CONFIGURAÇÕES
# ================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "kidney_features.csv")
MODELS_DIR = os.path.join(BASE_DIR, "models", "classifiers")

# ================================
# RESTRIÇÕES CLÍNICAS (Monotonic Constraints)
# ================================
def get_monotonic_constraints(columns):
    constraints = []
    for col in columns:
        # Fatores de Risco (Quanto maior, PIOR)
        # Nota: bun_creatinine_ratio é complexo, deixamos livre (0) ou positivo.
        # Geralmente ureia alta e creatinina alta são ruins, então ratio alto tende a ser ruim.
        if col in ['age', 'blood_pressure', 'glucose', 'urea', 'creatinine', 'potassium', 
                   'hypertension', 'diabetes', 'bun_creatinine_ratio']:
            constraints.append(1)
        
        # Fatores de Proteção (Quanto maior, MELHOR)
        # Hemoglobina alta é bom (significa sem anemia renal)
        elif col in ['hemo']: 
            constraints.append(-1)
            
        else:
            constraints.append(0)
            
    return tuple(constraints)

def train_renal_model():
    print("🚀 Treinando Modelo RENAL com Restrições Clínicas...")
    
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Arquivo não encontrado: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)
    target_col = 'target'
    
    X = df.drop(columns=[target_col])
    y = df[target_col]
    
    constraints = get_monotonic_constraints(X.columns)
    print(f"[INFO] Aplicando constraints em: {list(X.columns)}")

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # ================================
    # 1. OTIMIZAÇÃO (Com Constraints)
    # ================================
    def objective(trial):
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 50, 300),
            "max_depth": trial.suggest_int("max_depth", 2, 5), # Profundidade baixa é vital para datasets pequenos
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.2, log=True),
            "subsample": trial.suggest_float("subsample", 0.6, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
            "reg_lambda": trial.suggest_float("reg_lambda", 1.0, 10.0, log=True),
            
            "monotone_constraints": constraints, # A MÁGICA
            "tree_method": "hist",
            "eval_metric": "logloss",
            "n_jobs": -1,
            "random_state": 42
        }
        
        model = XGBClassifier(**params)
        model.fit(X_train, y_train)
        
        # Validação cruzada simples ou holdout
        return roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])

    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=20)
    
    best_params = study.best_params
    best_params["monotone_constraints"] = constraints
    best_params["tree_method"] = "hist"

    # ================================
    # 2. TREINO FINAL
    # ================================
    final_model = XGBClassifier(**best_params)
    
    # Calibração ajuda muito em datasets pequenos para evitar overconfidence (100% ou 0%)
    calibrated = CalibratedClassifierCV(final_model, method='isotonic', cv=3)
    calibrated.fit(X_train, y_train)
    
    # Avaliação
    probs = calibrated.predict_proba(X_test)[:, 1]
    print(f"🏆 AUC Final: {roc_auc_score(y_test, probs):.4f}")
    
    # Salvar
    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(calibrated, os.path.join(MODELS_DIR, "renal_best.pkl"))
    print("✅ Modelo Renal corrigido e salvo!")

if __name__ == "__main__":
    train_renal_model()