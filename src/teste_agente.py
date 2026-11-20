import pandas as pd
import joblib
from agent import create_agent
from explainability import compute_shap_values, load_rf
from preprocessing import load_raw_data

# --- LOAD DATA ---
df = pd.read_csv("data/processed/heart_features.csv")
X = df.drop("condition", axis=1)

# --- LOAD RF MODEL (used for SHAP) ---
model = load_rf()

# --- COMPUTE SHAP VALUES ---
shap_values, explainer = compute_shap_values(model, X)

# --- CREATE AGENT ---
agent = create_agent(shap_values, X)

# --- SELECT A RANDOM USER ---
row_index = 10   # you can change this
user_row = df.iloc[row_index]

# --- MODEL PREDICTION ---
proba = model.predict_proba(X.iloc[[row_index]])[0][1]

print("\n===========================")
print("TESTE: EXPLICAÇÃO POR SHAP")
print("===========================")
print(agent.explain_prediction(row_index, proba))


print("\n===========================")
print("TESTE: RECOMENDAÇÕES")
print("===========================")
recs = agent.rule_based_recommendations(user_row)
for r in recs:
    print(" -", r)

print("\n===========================")
print("TESTE: PERGUNTAS DO AGENTE")
print("===========================")
fake_lifestyle = {}  # no info provided yet
questions = agent.follow_up_questions(fake_lifestyle)
for q in questions:
    print(" -", q)
