import os
import json
from pathlib import Path

import google.generativeai as genai
import streamlit as st
from dotenv import load_dotenv

from app.modules.database import get_user_history

# Carrega variáveis de ambiente (.env)
load_dotenv()

ROOT = Path(__file__).resolve().parents[3]

# --- API KEY ---
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY and "GOOGLE_API_KEY" in st.secrets:
    API_KEY = st.secrets["GOOGLE_API_KEY"]


# ============================================================
# 1) PROMPT DE SISTEMA (REGRAS FIXAS DO AGENTE)
# ============================================================
def build_system_instruction() -> str:
    """
    Instruções fixas do agente HealthLens AI.
    Aqui NÃO entram dados do paciente, só regras de comportamento.
    """
    return """
Você é o HealthLens AI, um assistente médico de apoio à decisão.
Seu papel é EXPLICAR dados de exames, riscos estimados por modelos de IA
e histórico clínico do usuário, SEM fornecer diagnóstico médico definitivo.

REGRAS GERAIS:
- Responda SEMPRE em Português do Brasil, de forma clara e didática.
- Use linguagem acessível para leigos, mas sem perder precisão.
- NUNCA dê diagnóstico fechado. Prefira expressões como:
  "sugere", "indica risco aumentado", "pode estar associado", etc.
- SEMPRE recomende avaliação com profissional de saúde presencial.
- Se faltar informação para uma conclusão, diga isso abertamente.
- Nunca prescreva medicamentos, doses ou condutas específicas.

SOBRE OS MÓDULOS DO HEALTHLENS:
Você pode receber dados de diferentes módulos:
- Cardíaco
- Diabetes
- Renal
- Hepático

IMPORTANTE SOBRE O MÓDULO CARDÍACO:
- Os campos "colesterol" e "glicemia" NÃO são valores laboratoriais.
- São CATEGORIAS de risco, com o significado:
    Colesterol:
        1 = baixo
        2 = médio
        3 = alto

    Glicemia:
        1 = normal
        2 = pré-alterada
        3 = elevada

- Nunca trate esses números como mg/dL ou valores absolutos.
- Eles são apenas marcadores de risco categóricos dentro do modelo.

NOS OUTROS MÓDULOS:
- Diabetes: HbA1c, glicemia, IMC, etc. são valores contínuos reais (com unidades).
- Renal: creatinina, ureia, potássio, hemoglobina, etc.
- Hepático: bilirrubinas, TGO/TGP (AST/ALT), fosfatase alcalina, proteínas, etc.

SOBRE O HISTÓRICO (BANCO DE DADOS):
- Você pode receber um resumo de avaliações anteriores (módulo, data, risco, nível).
- Use esse histórico para analisar tendências (subida/queda de risco).
- Se o histórico estiver ausente ou muito pequeno, diga isso claramente.

ESTRUTURA RECOMENDADA DA RESPOSTA:
1) Resumo curto (1–2 frases) sobre a situação geral.
2) Explicação detalhada dos achados atuais.
3) Relação com o histórico (se houver): tendência de melhora/piora/estabilidade.
4) Recomendações gerais de estilo de vida (sem conduta médica específica).
5) Aviso de segurança, lembrando que não substitui consulta presencial.
"""


# ============================================================
# 2) CONTEXTO DINÂMICO DO PACIENTE
#    (PDF + Inputs manuais + Histórico do SQLite)
# ============================================================
def _format_dict_block(title: str, data: dict) -> str:
    if not data:
        return ""
    try:
        pretty = json.dumps(data, ensure_ascii=False, indent=2)
    except Exception:
        pretty = str(data)

    return f"--- {title} ---\n{pretty}\n\n"


def _summarize_history_for_user(max_entries_per_module: int = 5) -> str:
    username = st.session_state.get("username")
    if not username:
        return "Nenhum usuário logado. Histórico não disponível.\n"

    try:
        raw = get_user_history(username, module=None)
    except Exception:
        return "Erro ao acessar o histórico no momento.\n"

    if not raw:
        return "Nenhum registro clínico salvo ainda para este usuário.\n"

    # raw: lista de tuplas (date, module, risk_prob, risk_level)
    history_by_module = {}
    for date_str, module, prob, level in raw:
        history_by_module.setdefault(module, []).append((date_str, prob, level))

    lines = [f"Histórico clínico de {username} (últimos registros):"]

    for module, entries in history_by_module.items():
        lines.append(f"\n[Módulo: {module}]")
        # DB já ordenou por data DESC, então pegamos os primeiros
        subset = entries[:max_entries_per_module]
        for date_str, prob, level in subset:
            try:
                prob_pct = f"{prob * 100:.1f}%"
            except Exception:
                prob_pct = str(prob)
            lines.append(f"- {date_str}: risco {prob_pct} ({level})")

        # Trend simples (se houver pelo menos 2 pontos)
        if len(entries) >= 2:
            mais_recente = entries[0][1]
            mais_antigo = entries[-1][1]
            delta = mais_recente - mais_antigo
            if abs(delta) >= 0.05:
                tendencia = "aumentou" if delta > 0 else "diminuiu"
                lines.append(
                    f"  ↳ Tendência aproximada no módulo {module}: risco {tendencia} em relação aos primeiros registros."
                )

    return "\n".join(lines) + "\n"


def build_patient_context() -> str:
    """
    Cria o prontuário dinâmico do paciente, agregando:
    - dados atuais (PDF + inputs dos módulos)
    - resumo do histórico (SQLite)
    Esse texto é enviado como "contexto" junto com a pergunta.
    """
    context_parts = []

    context_parts.append("=== CONTEXTO CLÍNICO ATUAL DO PACIENTE ===\n")

    # 1) Dados extraídos de PDF (upload)
    lab_data = st.session_state.get("current_pdf_data", {})
    block_pdf = _format_dict_block("DADOS EXTRAÍDOS DO PDF (LAUDO)", lab_data)
    if block_pdf:
        context_parts.append(block_pdf)

    # 2) Dados manuais de cada módulo
    cardio_manual = st.session_state.get("manual_data_cardio", {})
    diabetes_manual = st.session_state.get("manual_data_diabetes", {})
    renal_manual = st.session_state.get("manual_data_renal", {})
    liver_manual = st.session_state.get("manual_data_liver", {})

    if cardio_manual:
        context_parts.append(
            _format_dict_block("DADOS DO MÓDULO CARDÍACO (MANUAL)", cardio_manual)
        )
    if diabetes_manual:
        context_parts.append(
            _format_dict_block("DADOS DO MÓDULO DIABETES (MANUAL)", diabetes_manual)
        )
    if renal_manual:
        context_parts.append(
            _format_dict_block("DADOS DO MÓDULO RENAL (MANUAL)", renal_manual)
        )
    if liver_manual:
        context_parts.append(
            _format_dict_block("DADOS DO MÓDULO HEPÁTICO (MANUAL)", liver_manual)
        )

    # 3) Histórico do usuário
    history_text = _summarize_history_for_user()
    context_parts.append("\n=== RESUMO DO HISTÓRICO CLÍNICO ===\n")
    context_parts.append(history_text)

    context_parts.append(
        """
DIRETRIZES PARA USO DESTES DADOS:
- Considere a união de todos os dados acima.
- Em caso de conflito entre histórico antigo e dados atuais, dê preferência aos dados mais recentes.
- Os valores categóricos do módulo cardíaco NÃO são medidas em mg/dL, mas categorias de risco.
"""
    )

    return "\n".join(context_parts)


# ============================================================
# 3) CRIAÇÃO DO MODELO GEMINI
# ============================================================
def get_model():
    """
    Cria o modelo Gemini configurado com instruções de sistema fixas.
    O contexto dinâmico do paciente NÃO entra aqui, e sim por mensagem.
    """
    if not API_KEY:
        return None

    genai.configure(api_key=API_KEY)

    system_instruction = build_system_instruction()
    model = genai.GenerativeModel(
        model_name="models/gemini-2.0-flash",
        system_instruction=system_instruction,
    )
    return model


# ============================================================
# 4) CHAMADA DO AGENTE
# ============================================================
def get_agent_response(user_query: str, chat_history_for_api):
    """
    Gera a resposta do agente Gemini, usando:
    - Instruções fixas de sistema (build_system_instruction)
    - Contexto dinâmico do paciente (build_patient_context)
    - Histórico de chat (chat_history_for_api)
    """

    model = get_model()
    if not model:
        return "⚠️ Erro: API Key do Google Gemini não encontrada."

    # 1) Contexto dinâmico (paciente + histórico do SQLite)
    patient_context = build_patient_context()

    # 2) Historico de chat (apenas o que foi salvo no session_state)
    #    Formato já compatível com a API (role, parts).
    history_for_model = []

    # Injetamos o contexto como uma "mensagem de usuário" que explica os dados disponíveis
    history_for_model.append(
        {
            "role": "user",
            "parts": [
                f"CONTEXT0 CLÍNICO ATUAL (dados e histórico do paciente):\n{patient_context}"
            ],
        }
    )

    # Em seguida, incluímos o histórico real da conversa (perguntas e respostas anteriores)
    if chat_history_for_api:
        history_for_model.extend(chat_history_for_api)

    # 3) Inicia o chat com esse histórico
    chat = model.start_chat(history=history_for_model)

    try:
        response = chat.send_message(user_query)
        return response.text
    except Exception as e:
        return f"⚠️ Erro na IA: {str(e)}"
