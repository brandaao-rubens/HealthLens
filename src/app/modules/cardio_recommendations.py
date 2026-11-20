from typing import List

import pandas as pd


def generate_recommendations(features: pd.DataFrame, prob: float) -> List[str]:
    f = features.iloc[0]
    recs: List[str] = []

    # estilo de vida
    if f["smoking"] == 1:
        recs.append(
            "🚭 Parar de fumar é uma das principais medidas para reduzir o risco "
            "cardiovascular em qualquer faixa etária."
        )
    if f["alcohol"] == 1:
        recs.append(
            "🍺 Reduza o consumo de álcool, priorizando dias sem ingestão e "
            "quantidades moderadas."
        )
    if f["active_lifestyle"] == 0:
        recs.append(
            "🏃‍♂️ Aumente gradualmente o nível de atividade física "
            "(caminhadas, bicicleta, exercícios leves)."
        )

    # pressão
    ap_hi = float(f["ap_hi"])
    ap_lo = float(f["ap_lo"])
    if ap_hi >= 140 or ap_lo >= 90:
        recs.append(
            "🩸 Sua pressão está em faixa elevada. Discuta com um médico sobre "
            "monitorização domiciliar e, se necessário, ajuste de medicamentos."
        )

    # IMC
    bmi = float(f.get("bmi", 0.0))
    if bmi >= 30:
        recs.append(
            "⚖️ Trabalhe em um plano gradual de perda de peso com foco em "
            "alimentação balanceada e atividade física."
        )

    # colesterol / glicemia
    if f["chol"] >= 2:
        recs.append(
            "🥗 Considere reduzir gorduras saturadas e ultraprocessados; "
            "avalie com seu médico a necessidade de tratamento para colesterol."
        )
    if f["glucose"] >= 2:
        recs.append(
            "🧪 Glicemia alterada pode indicar risco metabólico. "
            "Reavalie exames e hábitos alimentares com seu médico."
        )

    if not recs:
        recs.append(
            "✅ Seus fatores de risco parecem bem controlados. "
            "Mantenha acompanhamento regular e hábitos saudáveis."
        )

    # um ajuste geral pelo nível de risco
    if prob >= 0.30:
        recs.append(
            "📅 Agende uma consulta médica em breve para avaliação mais detalhada "
            "de risco cardiovascular."
        )

    return recs


def generate_adaptive_questions(prob: float) -> List[str]:
    qs: List[str] = []

    if prob < 0.10:
        qs.append(
            "Você realiza check-ups regulares (pelo menos uma vez ao ano)?"
        )
    elif prob < 0.25:
        qs.append(
            "Algum familiar de primeiro grau já teve infarto ou AVC antes dos 55 anos (homem) ou 65 anos (mulher)?"
        )
        qs.append(
            "Como está sua rotina de sono (horas por noite, qualidade)?"
        )
    else:
        qs.append(
            "Você já teve sintomas como dor no peito ao esforço, falta de ar ou inchaço nas pernas?"
        )
        qs.append(
            "Você já usa algum medicamento para pressão, colesterol ou diabetes? Como está a adesão?"
        )

    qs.append(
        "Existe algo na sua rotina (trabalho, estresse, alimentação) que você sente que mais impacta sua saúde hoje?"
    )

    return qs
