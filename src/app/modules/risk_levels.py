def classify_risk(prob: float, disease: str = "cardio"):
    """
    Retorna (nível, emoji, cor_hex) dado probabilidade em [0,1].
    Pode ter thresholds diferentes por doença.
    """
    pct = prob * 100

    if disease == "diabetes":
        low_thr = 7.0
        mid_thr = 20.0
    else:  # cardio e demais
        low_thr = 10.0
        mid_thr = 20.0

    if pct < low_thr:
        return "Baixo", "🟢", "#22c55e"
    elif pct < mid_thr:
        return "Moderado", "🟡", "#facc15"
    else:
        return "Alto", "🔴", "#ef4444"
