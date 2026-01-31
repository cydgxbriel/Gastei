# Guia de Configuração Completo

Este guia detalha a configuração de todos os serviços para o sistema de controle de custos.

## 📋 Índice

1. [Supabase](#1-supabase)
2. [Hugging Face](#2-hugging-face)
3. [n8n Cloud](#3-n8n-cloud)
4. [Evolution API (WhatsApp)](#4-evolution-api-whatsapp)
5. [Conectando Tudo](#5-conectando-tudo)

---

## 1. Supabase

### Criar Projeto

1. Acesse [supabase.com](https://supabase.com) e faça login
2. Clique em **"New Project"**
3. Preencha:
   - **Name**: `controle-custos`
   - **Database Password**: Anote em local seguro!
   - **Region**: South America (São Paulo)
4. Aguarde a criação (~2 min)

### Executar Schema

1. No dashboard, vá em **SQL Editor**
2. Clique em **"New Query"**
3. Cole o conteúdo de `supabase/schema.sql`
4. Clique em **"Run"**

### Obter Credenciais

1. Vá em **Settings > API**
2. Anote:
   - **Project URL**: `https://xxx.supabase.co`
   - **anon public key**: `eyJhbGciOi...`

---

## 2. Hugging Face

### Criar API Key

1. Acesse [huggingface.co](https://huggingface.co) e faça login
2. Vá em **Settings > Access Tokens**
3. Clique em **"New token"**
   - **Name**: `controle-custos`
   - **Type**: `Read`
4. Copie e guarde o token

### Criar Space

1. Vá em **Spaces > Create new Space**
2. Configure:
   - **Space name**: `controle-custos`
   - **SDK**: Gradio
   - **Visibility**: Public (ou Private)
3. Clone o repositório localmente ou use a interface web
4. Faça upload dos arquivos de `huggingface/`:
   - `app.py`
   - `requirements.txt`

### Configurar Variáveis de Ambiente

No Space, vá em **Settings > Variables and secrets**:

| Variable | Value |
|----------|-------|
| `SUPABASE_URL` | `https://xxx.supabase.co` |
| `SUPABASE_KEY` | `eyJhbGciOi...` |

---

## 3. n8n Cloud

### Criar Conta

1. Acesse [n8n.cloud](https://n8n.cloud)
2. Crie uma conta (plano gratuito disponível)
3. Crie um novo workflow

### Configurar Credenciais

Em **Settings > Credentials**, adicione:

#### Supabase
- **Type**: Supabase
- **Host**: `xxx.supabase.co`
- **Service Role Key**: (Settings > API > service_role)

#### Hugging Face
- **Type**: Hugging Face API
- **API Key**: Token criado anteriormente

### Importar Workflow

1. Vá em **Workflows > Import from file**
2. Selecione `n8n/workflows/whatsapp_audio_processor.json`
3. Atualize os nós com suas credenciais
4. Ative o workflow

### Obter URL do Webhook

1. Clique no nó **"Webhook WhatsApp"**
2. Copie a **Production URL**: `https://xxx.app.n8n.cloud/webhook/xxx`

---

## 4. Evolution API (WhatsApp)

### Opção A: Self-Hosted (Gratuito)

#### Requisitos
- VPS com Docker (mínimo 1GB RAM)
- Domínio ou IP público

#### Instalação

```bash
# Clone o repositório
git clone https://github.com/EvolutionAPI/evolution-api.git
cd evolution-api

# Configure o .env
cp .env.example .env
nano .env

# Inicie
docker-compose up -d
```

### Opção B: Z-API (Pago, mais simples)

1. Acesse [z-api.io](https://z-api.io)
2. Crie uma conta (~R$90/mês)
3. Conecte seu número de WhatsApp
4. Configure o webhook para a URL do n8n

### Configurar Webhook

Na Evolution API ou Z-API, configure:

```
Webhook URL: https://xxx.app.n8n.cloud/webhook/whatsapp-webhook
Events: messages.upsert
```

---

## 5. Conectando Tudo

### Fluxo de Dados

```
WhatsApp → Evolution API → n8n → Hugging Face → Supabase
                                                    ↑
                              Gradio Interface ─────┘
```

### Testar

1. **Teste do Webhook**: Envie uma mensagem de teste no WhatsApp
2. **Verifique o n8n**: Vá em "Executions" para ver os logs
3. **Verifique o Supabase**: Table Editor > custos_variaveis

### Solução de Problemas

| Problema | Solução |
|----------|---------|
| Webhook não recebe | Verifique URL e configurações do Evolution API |
| Transcrição falha | Verifique API Key do Hugging Face |
| Não salva no Supabase | Verifique credenciais e permissões |

---

## 🔗 Links Úteis

- [Documentação Evolution API](https://doc.evolution-api.com/)
- [Documentação n8n](https://docs.n8n.io/)
- [Documentação Supabase](https://supabase.com/docs)
- [Documentação Gradio](https://www.gradio.app/docs)
