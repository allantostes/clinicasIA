import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
import streamlit as st

# Carrega as variáveis de ambiente
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
  st.error(
      "❌ Chave de API do Gemini não encontrada! Verifique o seu arquivo .env."
  )
  st.stop()

# Inicializa o cliente do Google GenAI
client = genai.Client(api_key=api_key)


# Função para carregar a base de conhecimento em Markdown
@st.cache_data
def carregar_faq():
  try:
    with open("faq_clinica.md", "r", encoding="utf-8") as f:
      return f.read()
  except FileNotFoundError:
    return "Base de conhecimento não encontrada."


faq_content = carregar_faq()

# Configuração da Página em modo largo (wide) para caber os dois lados
st.set_page_config(
    page_title="Recepção Inteligente - Clínica Exemplo Saúde",
    page_icon="🩺",
    layout="wide",
)

# Título Principal do Dashboard Comercial
st.title("🩺 Recepção Inteligente 24h | Demonstração Comercial")
st.write(
    "Solução automatizada por Inteligência Artificial para atendimento e"
    " triagem de pacientes."
)
st.divider()

# Criação de duas colunas: Esquerda (Apresentação/Pitch) e Direita (Chat Rodando)
col1, col2 = st.columns([1, 1.2], gap="large")

# --- COLUNA 1: APRESENTAÇÃO / PITCH COMERCIAL ---
with col1:
  st.subheader("📊 Clinica Virtual Inteligente")

  # Card visual estilo Slide
  st.markdown("""
        <div style="background-color: #1e293b; padding: 22px; border-radius: 12px; border: 1px solid #334155; color: #f8fafc; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
            <span style="background-color: rgba(20, 184, 166, 0.1); color: #2dd4bf; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 600; text-transform: uppercase; border: 1px solid rgba(20, 184, 166, 0.2);">Tecnologia Exclusiva</span>
            <h3 style="margin-top: 14px; font-size: 22px; font-weight: bold; color: #f1f5f9;">Recepção Inteligente 24h</h3>
            <p style="font-size: 13px; color: #94a3b8; margin-top: 8px; line-height: 1.5;">
                Elimine a fila de espera no WhatsApp e responda pacientes em segundos, a qualquer hora do dia ou da noite, com total precisão.
            </p>
            <hr style="border-color: #334155; margin: 18px 0;">
            <ul style="font-size: 13px; color: #cbd5e1; padding-left: 18px; line-height: 1.6;">
                <li><b>Zero Fila:</b> Respostas instantâneas para horários e convênios.</li>
                <li><b>Zero Alucinação:</b> Treinado estritamente com as regras da clínica.</li>
                <li><b>Foco Humano:</b> Equipe livre para o atendimento presencial.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

  st.markdown("<br>", unsafe_allow_html=True)
  st.info(
      "💡 **Dica para a Demonstração:** Apresente os benefícios ao gestor no"
      " painel ao lado e peça para ele testar o assistente digitando uma dúvida"
      " real da clínica dele na caixa de chat."
  )

# --- COLUNA 2: O CHATBOT INTERATIVO ---
with col2:
  st.subheader("💬 Atendimento 24 horas por dia.")

  system_instruction = f"""
    Você é um recepcionista virtual educado, empático e prestativo da "Clínica Exemplo Saúde".
    Sua única função é responder às dúvidas dos pacientes com base estritamente nas informações da base de conhecimento abaixo.
    REGRAS:
    1. Se a resposta exata não estiver na base de conhecimento, diga educadamente que não possui essa informação e oriente o paciente a ligar para a recepção.
    2. Nunca invente valores, nomes de médicos ou horários que não estejam escritos aqui.
    3. Mantenha as respostas curtas e diretas, em formato de chat.

    --- BASE DE CONHECIMENTO ---
    {faq_content}
    ----------------------------
    """

  if "chat_client" not in st.session_state:
    st.session_state.chat_client = client.chats.create(
        model="gemini-3.8-flash",
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.2,
        ),
    )

  if "messages" not in st.session_state:
    st.session_state.messages = []

  # Container de chat com altura fixa e rolagem interna
  chat_container = st.container(height=380)

  with chat_container:
    for message in st.session_state.messages:
      with st.chat_message(message["role"]):
        st.markdown(message["content"])

  # Caixa de digitação do chat
  if prompt := st.chat_input(
      "Digite uma dúvida (ex: Quais convênios aceitam?):", key="user_prompt"
  ):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with chat_container:
      with st.chat_message("user"):
        st.markdown(prompt)

    with chat_container:
      with st.chat_message("assistant"):
        with st.spinner("Digitando..."):
          resposta_texto = None
          max_tentativas = 3
          for tentativa in range(max_tentativas):
            try:
              response = st.session_state.chat_client.send_message(prompt)
              resposta_texto = response.text
              break
            except Exception as e:
              if "503" in str(e) and tentativa < max_tentativas - 1:
                time.sleep(2)
                continue
              else:
                resposta_texto = (
                    f"Desculpe, ocorreu um erro ao gerar a resposta: {e}"
                )

          st.markdown(resposta_texto)
          st.session_state.messages.append(
              {"role": "assistant", "content": resposta_texto}
          )