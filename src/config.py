import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Chave de API do Google Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Modelo padrão do Gemini (rápido e econômico para plano gratuito)
# Modelos modernos recomendados: "gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-3.1-flash-lite"
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

# Identidade
ASSISTANT_NAME = os.getenv("ASSISTANT_NAME", "Naiah")
CANDIDATE_NAME = os.getenv("CANDIDATE_NAME", "André Capela")
CANDIDATE_EMAIL = os.getenv("CANDIDATE_EMAIL", "andr.capela@gmail.com")
CANDIDATE_LINKEDIN = os.getenv("CANDIDATE_LINKEDIN", "https://www.linkedin.com/in/andre-capela")

# Diretório de conhecimento (arquivos .pdf, .md, .txt)
KNOWLEDGE_DIR = BASE_DIR / "data" / "knowledge"

# Configurações de Rate Limit (Proteção de cota gratuita e prevenção de abusos)
RATE_LIMIT_MAX_PER_MINUTE = int(os.getenv("RATE_LIMIT_MAX_PER_MINUTE", "5"))
RATE_LIMIT_MAX_PER_SESSION = int(os.getenv("RATE_LIMIT_MAX_PER_SESSION", "25"))

# Parâmetros de geração
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.3"))
