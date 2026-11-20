import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY") 
# Se estiver usando secrets.toml, copie e cole sua chave aqui direto só pra testar:
# api_key = "SUA_CHAVE_AQUI"

genai.configure(api_key=api_key)

print("Listando modelos disponíveis...")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"- {m.name}")