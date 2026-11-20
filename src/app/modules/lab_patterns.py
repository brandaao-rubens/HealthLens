"""
Dicionário de padrões Regex para identificar exames laboratoriais e dados do paciente.
"""

LAB_PATTERNS = {
    # --- DADOS DO PACIENTE ---
    "age": [r"(?i)(?:idade|anos)\s*[:.]?\s*(\d{1,3})"],
    "gender": [r"(?i)(?:sexo|gênero)\s*[:.]?\s*(masculino|feminino|masc|fem|m|f)\b"],

    # --- CARDIO / DIABETES ---
    "glucose": [r"(?i)(?:glicemia|glicose)\s*(?:em jejum|basal)?.*?(\d{2,3})"],
    "hba1c": [r"(?i)(?:hba1c|hemoglobina glicada|fração a1c).*?(\d{1,2}[.,]\d{1,2})"],
    "cholesterol": [r"(?i)(?:colesterol total).*?(\d{2,3})"],
    "hdl": [r"(?i)(?:hdl|colesterol de alta densidade).*?(\d{2,3})"],
    "ldl": [r"(?i)(?:ldl|colesterol de baixa densidade).*?(\d{2,3})"],
    "triglycerides": [r"(?i)(?:triglicerídeos|triglicérides).*?(\d{2,4})"],

    # --- RENAL ---
    "creatinine": [r"(?i)(?:creatinina).*?(\d{1,2}[.,]\d{1,2})"],
    "urea": [r"(?i)(?:ureia).*?(\d{2,3})"],
    "potassium": [r"(?i)(?:potássio).*?(\d{1}[.,]\d{1})"],

    # --- HEPÁTICO (NOVOS!) ---
    "bilirubin_total": [r"(?i)(?:bilirrubina total).*?(\d{1,2}[.,]\d{1,2})"],
    "bilirubin_direct": [r"(?i)(?:bilirrubina direta).*?(\d{1,2}[.,]\d{1,2})"],
    "alkaline_phosphatase": [r"(?i)(?:fosfatase alcalina).*?(\d{2,4})"],
    "sgpt": [r"(?i)(?:tgp|alt|alanina aminotransferase).*?(\d{2,3})"], # ALT
    "sgot": [r"(?i)(?:tgo|ast|aspartato aminotransferase).*?(\d{2,3})"], # AST
    "proteins": [r"(?i)(?:proteínas totais).*?(\d{1,2}[.,]\d{1})"],
    "albumin": [r"(?i)(?:albumina).*?(\d{1,2}[.,]\d{1})"],
    "albumin_globulin_ratio": [r"(?i)(?:relação albumina/globulina|índice a/g).*?(\d{1}[.,]\d{1,2})"]
}