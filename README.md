# 🤖 Naiah - Agente de IA para Portfólio de André Capela

> **Naiah** é uma assistente virtual conversacional desenvolvida para atuar como embaixadora do perfil profissional de **André Capela** perante recrutadores, gestores técnicos (Engineering Managers / Tech Leads) e entrevistadores.

O agente roda sobre o **Chainlit** com orquestração inteligente de prompts, respostas orientadas em 3ª pessoa, guardrails anti-alucinação, filtro de escopo, limitação de taxa (Rate Limiting) para o plano gratuito do **Google Gemini** e base de conhecimento modular em tempo real.

---

## 🏗️ Arquitetura do Projeto

```text
Agente AI Naiah/
├── data/
│   └── knowledge/            # 📂 Base de conhecimento modular (PDFs, Markdown, Texto)
│       ├── Profile.pdf       # Currículo exportado do LinkedIn
│       └── sobre_mim.md      # Biografia, diferenciais, projetos e contato
│
├── src/
│   ├── __init__.py
│   ├── config.py             # Configurações centralizadas (.env)
│   ├── knowledge_loader.py   # Carregador dinâmico de documentos (auto-reload)
│   ├── prompt_manager.py     # Orquestrador do System Prompt, Persona Naiah e Guardrails
│   ├── rate_limiter.py       # Controle de fluxo (janela deslizante + limite de sessão)
│   └── gemini_client.py      # Integração com Google Gemini SDK (google-genai com streaming)
│
├── .chainlit/
│   └── config.toml           # Configurações visuais e temas do Chainlit
├── app.py                    # Ponto de entrada do chat interativo
├── chainlit.md               # Painel de boas-vindas do Chainlit
├── requirements.txt          # Dependências do projeto
├── .env.example              # Modelo de variáveis de ambiente
└── .env                      # Suas configurações e chave de API
```

---

## 🎯 Padrões e Guardrails Pré-estabelecidos

1. **Persona em Terceira Pessoa:** A assistente responde sempre como *Naiah*, falando sobre o André (*"O André possui 12 certificações Salesforce...", "Em sua atuação na GFT, ele liderou..."*).
2. **Fidelidade Factual (Anti-Alucinação):** Respostas estritamente ancoradas nos documentos de `data/knowledge/`. Se algo não constar nos dados, o agente responde com sinceridade e sugere contato direto.
3. **Filtro de Escopo Profissional:** Perguntas fora do escopo profissional (ex: receitas, notícias gerais, códigos não relacionados) são educadamente recusadas, redirecionando o entrevistador para a carreira do André.
4. **Tratamento de Assuntos Sensíveis:** Perguntas sobre pretensão salarial ou confidencialidade (NDA) de clientes anteriores são tratadas com discrição, sugerindo contato formal.
5. **Call To Action (CTA):** Incentivo contínuo para recrutadores agendarem conversas pelo LinkedIn ou E-mail.
6. **Rate Limiting:** Proteção contra abusos e esgotamento da cota gratuita da API do Gemini (máximo de 5 mensagens/minuto e 25 mensagens/sessão).

---

## 📂 Como Adicionar ou Excluir Informações Facilmente

A base de conhecimento foi projetada para ser **100% modular**:

- Para **adicionar** novos dados: basta colocar qualquer arquivo `.pdf`, `.md` ou `.txt` dentro da pasta `data/knowledge/` (ex: `projetos_detalhados.md`, `artigos.txt`, `novo_cv.pdf`).
- Para **excluir** dados: basta remover ou renomear o arquivo da pasta `data/knowledge/`.
- ⚡ **Auto-Reload:** O sistema detecta automaticamente alterações no disco sem necessidade de reiniciar a aplicação!

---

## 🚀 Como Executar Localmente

### 1. Pré-requisitos
- Python 3.10 ou superior instalado.
- Chave de API gratuita do Google Gemini ([Obter no Google AI Studio](https://aistudio.google.com/app/apikey)).

### 2. Configurar a Chave de API
Abra o arquivo `.env` na raiz do projeto e insira a sua chave:
```env
GEMINI_API_KEY=sua_chave_do_gemini_aqui
```

### 3. Instalar Dependências (se ainda não instaladas)
```bash
pip install -r requirements.txt
```

### 4. Executar o Chat
```bash
chainlit run app.py -w
```
> O parâmetro `-w` ativa o *hot-reload* para desenvolvimento. O Chainlit abrirá automaticamente no seu navegador em `http://localhost:8000`.

---

## 🌐 Próxima Etapa: Deploy na VPS (Futuro)

Quando desejar colocar na sua VPS, faremos:
1. Criação do `Dockerfile` e `docker-compose.yml`.
2. Configuração de proxy reverso com **Nginx** ou **Caddy** (para obter certificado SSL HTTPS gratuito automaticamente com Let's Encrypt).
3. Apontamento de um subdomínio (ex: `agente.andrecapela.com.br` ou `ia.andrecapela.dev`).
