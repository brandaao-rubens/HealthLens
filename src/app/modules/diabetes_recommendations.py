from typing import List

import pandas as pd


def generate_recommendations(features: pd.DataFrame, prob: float) -> List[str]:
    f = features.iloc[0]
    recs: List[str] = []

    gl = float(f.get("blood_glucose_level", 0.0))
    hba = float(f.get("HbA1c_level", 0.0))
    bmi = float(f.get("bmi", 0.0))
    htn = int(f.get("hypertension", 0))

    if gl >= 126:
        recs.append(
            "🧪 Sua glicemia está em faixa alterada. Discuta com seu médico "
            "a possibilidade de repetir o exame em jejum e/ou curva glicêmica."
        )
    if hba >= 6.5:
        recs.append(
            "📈 HbA1c elevada sugere glicemia alta de forma crônica. "
            "Avalie mudanças de estilo de vida e possível tratamento medicamentoso."
        )
    if bmi >= 30:
        recs.append(
            "⚖️ Redução gradual de peso (5–10% do peso atual) já traz benefícios "
            "importantes para controle glicêmico."
        )
    if htn == 1:
        recs.append(
            "🩸 Controle rigoroso da pressão arterial é fundamental em pacientes "
            "com risco de diabetes."
        )

    if not recs:
        recs.append(
            "✅ Seus marcadores atuais não sugerem alto risco glicêmico. "
            "Mantenha hábitos saudáveis e acompanhamento periódico."
        )

    if prob >= 0.30:
        recs.append(
            "📅 Agende uma consulta com um clínico/endocrinologista para avaliação "
            "mais detalhada do risco de diabetes."
        )

    return recs


def generate_adaptive_questions(prob: float) -> List[str]:
    qs: List[str] = []

    if prob < 0.10:
        qs.append("Você tem histórico familiar de diabetes tipo 2?")
    elif prob < 0.30:
        qs.append(
            "Com que frequência você consome bebidas açucaradas (refrigerantes, sucos prontos)?"
        )
        qs.append("Você pratica atividade física ao menos 150 minutos por semana?")
    else:
        qs.append(
            "Você já apresentou sintomas como muita sede, aumento da urina ou perda de peso sem explicação?"
        )
        qs.append(
            "Você já recebeu orientação de algum profissional de saúde sobre plano alimentar para controle de glicemia?"
        )

    qs.append("Há alguma dificuldade prática que atrapalhe você a manter hábitos saudáveis no dia a dia?")

    return qs
