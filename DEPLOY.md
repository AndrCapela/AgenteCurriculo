# 🚀 Guia de Deploy - Naiah na VPS (HostGator + CloudPanel + Docker + nip.io)

Este guia orienta passo a passo o deploy do **Agente AI Naiah** em sua VPS HostGator utilizando **Docker**, **CloudPanel** como gerenciador e proxy reverso Nginx, e **nip.io** para domínio dinâmico com certificado SSL gratuito (Let's Encrypt).

---

## 📋 Pré-requisitos na VPS

1. **VPS HostGator** com Linux (Ubuntu/Debian) e **CloudPanel** instalado.
2. **Docker e Docker Compose** instalados na VPS:
   ```bash
   docker --version
   docker compose version
   ```
   *(Caso não tenha instalado, instale com `curl -fsSL https://get.docker.com | sh`)*.
3. Endereço **IP público da sua VPS** (Exemplo: `198.51.100.25`).
4. Sua chave de API do **Google Gemini** (`GEMINI_API_KEY`).

---

## 🌐 1. Como funciona o nip.io?

O **nip.io** é um serviço de DNS wildcard gratuito que dispensa configurações manuais em zonas de DNS de provedores. Qualquer subdomínio com seu IP resolve automaticamente para o seu servidor:

- Exemplo: se seu IP for `198.51.100.25`:
  - Domínio recomendado: `naiah.198.51.100.25.nip.io`
  - Ou direto: `198.51.100.25.nip.io`

---

## 🖥️ 2. Configurar o Site no CloudPanel

1. Acesse o painel do **CloudPanel** no navegador:  
   `https://SEU_IP_VPS:8443`
2. No menu lateral, clique em **Sites** e depois em **+ Add Site**.
3. Selecione a opção **Create a Reverse Proxy**.
4. Preencha os campos:
   - **Domain Name**: `naiah.SEU_IP_VPS.nip.io` *(substitua pelo seu IP real)*
   - **Reverse Proxy URL**: `http://127.0.0.1:4000`
   - **Site User**: Escolha um usuário existente ou crie um (ex: `andre`).
5. Clique em **Create**.

---

## 🔒 3. Ativar Certificado SSL (HTTPS Let's Encrypt)

Como o `nip.io` aponta diretamente para o IP da sua VPS, o CloudPanel consegue emitir o certificado SSL automaticamente em segundos:

1. Na lista de sites do CloudPanel, clique no site recém-criado (`naiah.SEU_IP_VPS.nip.io`).
2. Vá até a aba **SSL/TLS**.
3. Clique em **New Let's Encrypt Certificate**.
4. Clique em **Create and Install**.
5. Em poucos instantes, seu site estará rodando com HTTPS seguro!

---

## ⚡ 4. Ajustar Vhost do Nginx no CloudPanel (Crucial para WebSockets & Streaming)

O **Chainlit** usa conexões WebSocket persistentes e streaming de tokens em tempo real. Para garantir que a conversa não sofra desconexões após 60 segundos de inatividade e os tokens fluam sem retenção de buffer:

1. No CloudPanel, no seu site, clique na aba **Vhost**.
2. Localize o bloco `location /` e certifique-se de que ele inclua o suporte a WebSockets e desativação de buffer:

```nginx
location / {
    proxy_pass http://127.0.0.1:4000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    # Evita timeout em conversas longas
    proxy_read_timeout 86400s;
    proxy_send_timeout 86400s;

    # Permite streaming imediato de tokens do Gemini
    proxy_buffering off;
}
```

3. Clique em **Save**.

---

## 📁 5. Enviar os Arquivos para a VPS

Você pode colocar o projeto na pasta do site ou em `/home/<usuario>/naiah-agent`:

### Opção A: Via Git (Recomendado)
Acesse a VPS via SSH:
```bash
cd /home/<seu-usuario>/
git clone <URL_DO_SEU_REPOSITORIO> naiah-agent
cd naiah-agent
```

### Opção B: Via SCP / SFTP ou Gerenciador de Arquivos do CloudPanel
1. Compacte o projeto no seu computador (sem a pasta `.venv` ou `__pycache__`).
2. Acesse a VPS via FileZilla / WinSCP ou pelo gerenciador de arquivos do CloudPanel e envie para `/home/<seu-usuario>/naiah-agent`.
3. Descompacte na VPS:
   ```bash
   unzip agente-naiah.zip -d /home/<seu-usuario>/naiah-agent
   cd /home/<seu-usuario>/naiah-agent
   ```

---

## ⚙️ 6. Configurar o `.env` e Iniciar o Docker

1. Crie seu arquivo `.env` na VPS a partir do modelo:
   ```bash
   cp .env.example .env
   nano .env
   ```
2. Adicione sua **`GEMINI_API_KEY`** e salve (`Ctrl+O`, `Enter`, `Ctrl+X`).
3. Inicie a aplicação com o script automatizado ou com o Docker Compose:
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```
   *(Ou manualmente: `docker compose up -d --build`)*.

---

## 🔍 7. Verificação e Comandos Úteis

- **Ver status do container:**
  ```bash
  docker compose ps
  ```
- **Acompanhar logs em tempo real:**
  ```bash
  docker compose logs -f
  ```
- **Reiniciar a aplicação:**
  ```bash
  docker compose restart
  ```
- **Parar o container:**
  ```bash
  docker compose down
  ```
- **Atualizar a base de conhecimento (PDFs e Markdown):**
  Como a pasta `data/` está mapeada como volume, basta enviar o novo arquivo para `data/knowledge/` no servidor. O agente atualizará o conteúdo automaticamente sem precisar reiniciar o container!

---

## 🎉 Pronto!
Acesse `https://naiah.SEU_IP_VPS.nip.io` no seu navegador. O chat do Agente AI Naiah estará no ar com HTTPS, streaming de respostas e total segurança!
