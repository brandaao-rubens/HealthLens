def generate_recommendations(features_df, risk_prob):
    recs = []
    
    sgot = features_df["sgot"].iloc[0] # AST
    sgpt = features_df["sgpt"].iloc[0] # ALT
    ratio = features_df["ast_alt_ratio"].iloc[0]
    bili = features_df["bilirubin_total"].iloc[0]

    if risk_prob > 0.5:
        recs.append("Procure um hepatologista. Seus marcadores indicam sobrecarga hepática.")
        
    if ratio > 1.0 and (sgot > 40 or sgpt > 40):
        recs.append("A relação AST/ALT elevada pode indicar dano hepático associado ao consumo de álcool ou cirrose avançada.")
    elif ratio < 1.0 and (sgot > 40 or sgpt > 40):
        recs.append("A relação AST/ALT menor que 1 é comum em esteatose hepática (gordura no fígado). Avalie sua dieta.")

    if bili > 1.2:
        recs.append("Bilirrubina elevada pode indicar problemas no fluxo biliar ou função hepática.")

    recs.append("Evite consumo de álcool e medicamentos hepatotóxicos (como paracetamol em excesso).")
    
    return recs

def generate_adaptive_questions(risk_prob):
    questions = []
    if risk_prob > 0.4:
        questions.append("Você notou amarelamento nos olhos ou na pele (icterícia)?")
        questions.append("Tem sentido dor abdominal no lado direito superior?")
    else:
        questions.append("Você consome bebidas alcoólicas com qual frequência?")
    return questions