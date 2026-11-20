import numpy as np
import pandas as pd

class HealthAgent:
    def __init__(self, shap_values, feature_names):
        self.shap_values = shap_values
        self.feature_names = feature_names

    # 1. Interpretação técnica baseada em SHAP
    def explain_prediction(self, row_index, prediction_prob):
        shap_row = self.shap_values[row_index]

        # shap_row may be shape (n_trees, n_features)
        # so we average across axis 0:
        if len(shap_row.shape) > 1:
            shap_row = shap_row.mean(axis=0)

        # Now convert each value to float
        feature_contrib = [
            (feat, float(val))
            for feat, val in zip(self.feature_names, shap_row)
        ]

        # Sort by absolute value
        feature_contrib_sorted = sorted(
            feature_contrib,
            key=lambda x: abs(x[1]),
            reverse=True
        )

        explanation = f"Seu risco estimado é de {prediction_prob*100:.1f}%.\n"
        explanation += "Principais fatores que influenciaram esse risco:\n"

        for feat, val in feature_contrib_sorted[:5]:
            direction = "aumentou" if val > 0 else "reduziu"
            explanation += f" - {feat}: {direction} o risco ({val:.3f})\n"

        return explanation

    # 2. Regras médicas básicas
    def rule_based_recommendations(self, df_row):
        recs = []

        if df_row["chol"] > 240:
            recs.append("Seu colesterol está elevado. Reduza gorduras saturadas e aumente fibras.")
        
        if df_row["trestbps"] > 140:
            recs.append("Sua pressão arterial está alta. Considere reduzir sal e medir regularmente.")
        
        if df_row["fbs"] == 1:
            recs.append("Glicemia em jejum elevada pode indicar risco de diabetes. Evite alimentos com alto índice glicêmico.")
        
        if df_row["oldpeak"] > 2:
            recs.append("O valor de Oldpeak sugere possível isquemia durante esforço.")
        
        if len(recs) == 0:
            recs.append("Nenhum marcador crítico identificado. Continue monitorando periodicamente.")

        return recs

    # 3. Conversa adaptativa
    def follow_up_questions(self, lifestyle):
        questions = []

        if lifestyle.get("exercise") is None:
            questions.append("Você pratica atividade física regularmente?")
        
        if lifestyle.get("diet") is None:
            questions.append("Como você descreveria sua alimentação? (ex: saudável, moderada, ruim)")
        
        if lifestyle.get("smoker") is None:
            questions.append("Você fuma?")

        return questions


# Função para uso geral
def create_agent(shap_values, X):
    feature_names = X.columns.tolist()
    return HealthAgent(shap_values, feature_names)
