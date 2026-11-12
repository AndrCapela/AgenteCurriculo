import time
from collections import defaultdict, deque
from typing import Dict, Deque, Tuple

from src.config import (
    RATE_LIMIT_MAX_PER_MINUTE,
    RATE_LIMIT_MAX_PER_SESSION,
    CANDIDATE_EMAIL,
    CANDIDATE_LINKEDIN,
)

class RateLimiter:
    """
    Controlador de taxa de requisições por sessão para proteção da cota da API.
    Aplica limites por janela de tempo (ex: máx por minuto) e por volume total de sessão.
    """

    def __init__(
        self,
        max_per_minute: int = RATE_LIMIT_MAX_PER_MINUTE,
        max_per_session: int = RATE_LIMIT_MAX_PER_SESSION,
    ):
        self.max_per_minute = max_per_minute
        self.max_per_session = max_per_session
        # Armazena timestamps das mensagens recentes por session_id
        self._minute_window: Dict[str, Deque[float]] = defaultdict(deque)
        # Armazena a contagem total de mensagens por session_id
        self._session_counts: Dict[str, int] = defaultdict(int)

    def is_allowed(self, session_id: str) -> Tuple[bool, str]:
        """
        Avalia se a nova requisição da sessão é permitida.
        Retorna (True, "") se autorizada, ou (False, mensagem_de_bloqueio) caso atinja o limite.
        """
        now = time.time()
        
        # 1. Verifica limite total da sessão
        current_session_count = self._session_counts[session_id]
        if current_session_count >= self.max_per_session:
            msg = (
                f"⚠️ **Limite de perguntas por sessão atingido** ({self.max_per_session} perguntas).\n\n"
                f"Esta restrição visa manter o agente acessível para todos os visitantes dentro da cota gratuita da API.\n\n"
                f"Caso queira conversar diretamente com o André ou agendar uma entrevista:\n"
                f"- **E-mail:** [{CANDIDATE_EMAIL}](mailto:{CANDIDATE_EMAIL})\n"
                f"- **LinkedIn:** [Perfil no LinkedIn]({CANDIDATE_LINKEDIN})\n\n"
                f"*Dica: Você também pode reiniciar a sessão na barra lateral para recomeçar.*"
            )
            return False, msg

        # 2. Limpa timestamps mais antigos que 60 segundos
        window = self._minute_window[session_id]
        cutoff = now - 60.0
        while window and window[0] < cutoff:
            window.popleft()

        # 3. Verifica limite por minuto
        if len(window) >= self.max_per_minute:
            wait_seconds = int(60.0 - (now - window[0])) + 1
            msg = (
                f"⏳ **Aguarde um instante:** Você enviou muitas perguntas rapidamente.\n\n"
                f"Por favor, aguarde cerca de **{wait_seconds} segundo(s)** antes de enviar uma nova pergunta."
            )
            return False, msg

        # 4. Registra a requisição
        window.append(now)
        self._session_counts[session_id] += 1
        return True, ""

    def get_remaining_session(self, session_id: str) -> int:
        """Retorna quantas mensagens ainda restam nesta sessão."""
        return max(0, self.max_per_session - self._session_counts[session_id])

    def reset_session(self, session_id: str):
        """Reinicia os limites de uma sessão específica."""
        if session_id in self._minute_window:
            del self._minute_window[session_id]
        if session_id in self._session_counts:
            del self._session_counts[session_id]

# Instância padrão
rate_limiter = RateLimiter()
