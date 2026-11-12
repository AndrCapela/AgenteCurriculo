import logging
from typing import AsyncGenerator, List, Dict
from google import genai
from google.genai import types
from google.genai.errors import APIError

from src.config import GEMINI_API_KEY, GEMINI_MODEL, TEMPERATURE
from src.prompt_manager import prompt_manager

logger = logging.getLogger(__name__)

# Modelos recomendados da série 3.x para plano gratuito
FALLBACK_MODELS = ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite"]

class GeminiService:
    """
    Serviço assíncrono para comunicação com a API do Google Gemini
    utilizando a biblioteca oficial moderna google-genai com streaming e fallback automático.
    """

    def __init__(self):
        self.api_key = GEMINI_API_KEY
        self.model = GEMINI_MODEL
        self.temperature = TEMPERATURE
        self._client = None

    def _get_client(self) -> genai.Client:
        """Obtém ou instancia o cliente Gemini."""
        if not self._client:
            if not self.api_key:
                raise ValueError(
                    "A variável GEMINI_API_KEY não está configurada. "
                    "Por favor, configure sua chave no arquivo .env."
                )
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    async def stream_response(
        self,
        chat_history: List[Dict[str, str]],
        user_message: str
    ) -> AsyncGenerator[str, None]:
        """
        Envia a mensagem e o histórico de conversação com streaming em tempo real.
        chat_history: lista de dicts com formato [{"role": "user"|"model", "content": "..."}]
        """
        if not self.api_key:
            yield (
                "⚠️ **Configuração necessária:**\n\n"
                "A chave da API do Gemini (`GEMINI_API_KEY`) ainda não foi configurada no arquivo `.env`.\n\n"
                "Para configurar:\n"
                "1. Crie ou edite o arquivo `.env` na raiz do projeto;\n"
                "2. Adicione sua chave: `GEMINI_API_KEY=sua_chave_aqui`;\n"
                "3. Você pode obter uma chave gratuita no [Google AI Studio](https://aistudio.google.com/app/apikey)."
            )
            return

        client = self._get_client()
        system_instruction = prompt_manager.build_system_instruction()

        # Constrói o histórico no formato oficial do google-genai
        contents: List[types.Content] = []
        for item in chat_history:
            role = "user" if item["role"] == "user" else "model"
            contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=item["content"])]
                )
            )

        # Adiciona a mensagem atual do usuário
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_message)]
            )
        )

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=self.temperature,
        )

        # Lista de modelos a tentar (modelo configurado primeiro, seguido de fallbacks)
        candidate_models = [self.model]
        for fb in FALLBACK_MODELS:
            if fb not in candidate_models:
                candidate_models.append(fb)

        last_error = None
        for model_name in candidate_models:
            try:
                response_stream = await client.aio.models.generate_content_stream(
                    model=model_name,
                    contents=contents,
                    config=config,
                )

                async for chunk in response_stream:
                    if chunk.text:
                        yield chunk.text
                return  # Sucesso, encerra o gerador

            except APIError as e:
                err_str = str(e)
                logger.warning(f"Tentativa com modelo {model_name} falhou: {err_str}")
                # Se for erro 503 (alta demanda) ou 404 (modelo descontinuado), tenta o próximo
                if "503" in err_str or "UNAVAILABLE" in err_str or "404" in err_str or "NOT_FOUND" in err_str:
                    last_error = e
                    continue
                else:
                    if "RESOURCE_EXHAUSTED" in err_str or "429" in err_str:
                        yield (
                            "⚠️ **Limite de requisições por minuto atingido no plano gratuito do Gemini.**\n\n"
                            "Por favor, aguarde cerca de um minuto e envie sua pergunta novamente."
                        )
                    else:
                        yield f"⚠️ **Erro na API Gemini:** `{getattr(e, 'message', str(e))}`"
                    return
            except Exception as e:
                logger.error(f"Erro inesperado no GeminiService ({model_name}): {e}", exc_info=True)
                yield f"⚠️ **Erro inesperado:** `{str(e)}`"
                return

        # Se todos os modelos candidatos falharam
        if last_error:
            yield (
                "⚠️ **Os servidores do Gemini estão enfrentando pico temporário de demanda.**\n\n"
                "Por favor, tente novamente em alguns instantes."
            )

# Instância padrão
gemini_service = GeminiService()
