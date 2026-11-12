#!/usr/bin/env bash
# ==========================================================
# Script de Deploy e Atualização do Agente AI Naiah
# ==========================================================
set -e

echo "🚀 Iniciando deploy do Agente AI Naiah..."

# 1. Verifica se o arquivo .env existe
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo "⚠️  Arquivo .env não encontrado. Criando a partir de .env.example..."
        cp .env.example .env
        echo "❗ ATENÇÃO: Abra o arquivo .env e configure sua GEMINI_API_KEY antes de continuar!"
        exit 1
    else
        echo "❌ Arquivo .env ou .env.example não encontrado!"
        exit 1
    fi
fi

# 2. Executa build e sobe os containers
echo "📦 Construindo imagem Docker e iniciando container..."
docker compose down || true
docker compose build --pull
docker compose up -d

# 3. Status e logs
echo "✅ Deploy concluído com sucesso!"
echo "📊 Status dos containers:"
docker compose ps

echo ""
echo "🔍 Últimos logs do container (pressione Ctrl+C para sair):"
docker compose logs -f --tail=30
