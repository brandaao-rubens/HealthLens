# Arquivo: src/app/modules/pdf_reader.py

import io
from pypdf import PdfReader

def extract_text_from_pdf(uploaded_file) -> str:
    """
    Recebe um objeto UploadedFile do Streamlit e retorna todo o texto extraído.
    """
    try:
        # Lê o arquivo da memória
        pdf_reader = PdfReader(uploaded_file)
        full_text = []

        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                full_text.append(text)
        
        # Junta tudo em uma string única
        return "\n".join(full_text)
    
    except Exception as e:
        print(f"Erro ao ler PDF: {e}")
        return ""