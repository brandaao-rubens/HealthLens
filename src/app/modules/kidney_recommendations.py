def generate_recommendations(features_df, risk_prob):
    recs = []
    
    # Dados do paciente
    creat = features_df["creatinine"].iloc[0]
    bp = features_df["blood_pressure"].iloc[0]
    glucose = features_df["glucose"].iloc[0]

    if risk_prob > 0.5:
        recs.append("Consulte um nefrologista para avaliação da Taxa de Filtração Glomerular (TFG).")
        recs.append("Monitore rigorosamente a pressão arterial, mantendo-a abaixo de 130/80 mmHg.")
    else:
        recs.append("Mantenha hábitos saudáveis e hidratação adequada.")

    if creat > 1.2:
        recs.append("Sua Creatinina está elevada. Evite suplementos proteicos sem orientação e anti-inflamatórios.")

    if bp > 140:
        recs.append("O controle pressórico é fundamental para proteger os rins. Reduza o consumo de sódio.")

    if glucose > 126:
        recs.append("O controle da glicemia é vital para evitar a Nefropatia Diabética.")

    recs.append("Beba água regularmente (aprox. 35ml por kg de peso), salvo contraindicação médica.")
    
    return recs

def generate_adaptive_questions(risk_prob):
    # Perguntas para engajamento (futuro chatbot)
    questions = []
    if risk_prob > 0.4:
        questions.append("Você notou inchaço nas pernas ou ao redor dos olhos recentemente?")
        questions.append("Sua urina tem apresentado espuma ou alteração na cor?")
    else:
        questions.append("Você costuma beber quantos litros de água por dia?")
    return questions