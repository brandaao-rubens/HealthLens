import pandas as pd
import shap
import joblib
import matplotlib.pyplot as plt
import os


def load_data(path="data/processed/heart_features.csv"):
    return pd.read_csv(path)


def load_rf(path="models/classifiers/random_forest.pkl"):
    return joblib.load(path)


def compute_shap_values(model, X):
    print("[INFO] Creating SHAP TreeExplainer...")
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)

    # Normalize shape:
    # If shap_values is list → multiclass
    # If it's a single array → binary special case
    if isinstance(shap_values, list):
        print("[INFO] SHAP returned list (multiclass) — selecting class 1.")
        shap_values_class = shap_values[1]
    else:
        print("[INFO] SHAP returned array — using as binary shap values.")
        shap_values_class = shap_values

    return shap_values_class, explainer


def save_shap_summary(shap_values, X):
    os.makedirs("models/explainer", exist_ok=True)
    plt.figure(figsize=(10, 6))
    shap.summary_plot(shap_values, X, show=False)
    plt.tight_layout()
    plt.savefig("models/explainer/shap_summary.png")
    print("[INFO] SHAP summary saved!")


def save_shap_bar(shap_values, X):
    plt.figure(figsize=(10, 6))
    shap.summary_plot(shap_values, X, plot_type="bar", show=False)
    plt.tight_layout()
    plt.savefig("models/explainer/shap_bar.png")
    print("[INFO] SHAP bar saved!")


def run_explainability():
    print("[INFO] Loading processed dataset...")
    df = load_data()
    X = df.drop("condition", axis=1)

    print("[INFO] Loading RandomForest model...")
    model = load_rf()

    print("[INFO] Computing SHAP values...")
    shap_values, explainer = compute_shap_values(model, X)

    print("[INFO] Saving SHAP plots...")
    save_shap_summary(shap_values, X)
    save_shap_bar(shap_values, X)

    print("[INFO] Explainability complete!")
    return shap_values, explainer


if __name__ == "__main__":
    run_explainability()
