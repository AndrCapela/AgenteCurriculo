import uuid
import logging
import chainlit as cl

from src.config import ASSISTANT_NAME, CANDIDATE_NAME
from src.knowledge_loader import knowledge_loader
from src.rate_limiter import rate_limiter
from src.gemini_client import gemini_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_quick_actions():
    """Retorna os botões de ação interativos com perguntas frequentes."""
    return [
        cl.Action(
            name="quick_ask",
            label="🚀 Resumo Profissional",
            payload={"prompt": "Pode me apresentar um resumo sobre a trajetória profissional do André e seus principais diferenciais?"},
            tooltip="Visão geral da carreira e experiência",
        ),
        cl.Action(
            name="quick_ask",
            label="☁️ Experiência Salesforce",
            payload={"prompt": "Quais são as principais certificações e tecnologias do ecossistema Salesforce que o André domina?"},
            tooltip="Certificações, Apex, LWC e integrações",
        ),
        cl.Action(
            name="quick_ask",
            label="🌍 Projetos Globais",
            payload={"prompt": "Como foi a atuação do André em projetos bancários internacionais e liderança técnica?"},
            tooltip="Experiência multinacional 100% em inglês",
        ),
        cl.Action(
            name="quick_ask",
            label="📬 Contato & Entrevista",
            payload={"prompt": "Gostei do perfil dele! Como posso entrar em contato ou agendar uma entrevista técnica com o André?"},
            tooltip="LinkedIn, e-mail e canais diretos",
        ),
    ]

@cl.on_chat_start
async def on_chat_start():
    """Inicialização de cada sessão de conversa com boas-vindas e botões interativos."""
    session_id = str(uuid.uuid4())
    cl.user_session.set("session_id", session_id)
    cl.user_session.set("chat_history", [])

    num_files, num_words = knowledge_loader.get_summary()
    logger.info(f"Nova sessão iniciada: {session_id} | Documentos: {num_files} ({num_words} palavras)")

    welcome_msg = (
        f"👋 Olá! Sou a **{ASSISTANT_NAME}**, assistente virtual de **{CANDIDATE_NAME}**.\n\n"
        f"Fui criada para ajudar recrutadores, líderes técnicos e entrevistadores a tirarem dúvidas sobre "
        f"sua experiência com **Salesforce (12x Certified)**, desenvolvimento em projetos globais (inglês), "
        f"arquitetura de sistemas e liderança técnica.\n\n"
        f"👇 **Clique em uma das opções abaixo para começar ou digite sua pergunta:**"
    )
    
    actions = get_quick_actions()
    await cl.Message(content=welcome_msg, actions=actions).send()

async def process_user_query(user_prompt: str):
    """Processa a pergunta do usuário com controle de taxa e streaming do Gemini."""
    session_id = cl.user_session.get("session_id") or "default_session"
    chat_history = cl.user_session.get("chat_history") or []

    # 1. Verificação de Rate Limit (Proteção da cota gratuita)
    is_allowed, block_reason = rate_limiter.is_allowed(session_id)
    if not is_allowed:
        await cl.Message(content=block_reason).send()
        return

    # 2. Inicia streaming da resposta
    response_msg = cl.Message(content="")
    await response_msg.send()

    accumulated_chunks = []
    async for token in gemini_service.stream_response(
        chat_history=chat_history,
        user_message=user_prompt
    ):
        await response_msg.stream_token(token)
        accumulated_chunks.append(token)

    await response_msg.update()

    # 3. Atualiza o histórico da conversa
    full_response = "".join(accumulated_chunks)
    if full_response:
        chat_history.append({"role": "user", "content": user_prompt})
        chat_history.append({"role": "model", "content": full_response})
        cl.user_session.set("chat_history", chat_history)

@cl.action_callback("quick_ask")
async def on_action_quick_ask(action: cl.Action):
    """Executado quando o visitante clica em um dos botões rápidos."""
    prompt = action.payload.get("prompt", "")
    if prompt:
        # Envia como pergunta selecionada na tela
        await cl.Message(content=f"🔍 *Pergunta rápida selecionada:* **{action.label}**").send()
        await process_user_query(prompt)

@cl.on_message
async def on_message(message: cl.Message):
    """Manipula qualquer pergunta livre digitada no chat."""
    await process_user_query(message.content.strip())
