# Arquivo: src/app/modules/file_parser.py

import re
from app.modules.lab_patterns import LAB_PATTERNS
from app.modules.pdf_reader import extract_text_from_pdf

def parse_lab_file(uploaded_file) -> dict:
    raw_text = extract_text_from_pdf(uploaded_file)
    if not raw_text:
        return {}

    clean_text = " ".join(raw_text.split())
    extracted_data = {}

    for key, patterns in LAB_PATTERNS.items():
        for pattern in patterns:
            match = re.search(pattern, clean_text)
            if match:
                value_str = match.group(1)
                
                # LÓGICA ESPECIAL PARA GÊNERO (TEXTO)
                if key == "gender":
                    lower_v = value_str.lower()
                    if "masc" in lower_v or "m" == lower_v:
                        extracted_data[key] = "Masculino"
                    elif "fem" in lower_v or "f" == lower_v:
                        extracted_data[key] = "Feminino"
                    break # Encontrou, para de buscar padrões para esta chave
                
                # LÓGICA PARA NÚMEROS (IDADE E EXAMES)
                else:
                    value_str = value_str.replace(',', '.')
                    try:
                        value = float(value_str)
                        extracted_data[key] = value
                        break
                    except ValueError:
                        continue

    return extracted_data