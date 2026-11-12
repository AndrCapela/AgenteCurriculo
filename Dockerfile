# ==========================================
# Dockerfile para Naiah - Agente AI (Chainlit)
# ==========================================

FROM python:3.11-slim

# Evita criação de arquivos .pyc e força stdout/stderr sem buffer (logs imediatos)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Instala curl para suporte ao healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala dependências primeiro (aproveita cache do Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia os arquivos de código e configuração
COPY app.py chainlit.md ./
COPY .chainlit/ .chainlit/
COPY src/ src/
COPY data/ data/

# Expõe a porta interna da aplicação Chainlit
EXPOSE 8000

# Healthcheck para monitorar integridade do container
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD curl -f http://localhost:8000/ || exit 1

# Inicializa o Chainlit em modo de produção (headless)
CMD ["chainlit", "run", "app.py", "--host", "0.0.0.0", "--port", "8000", "--headless"]
