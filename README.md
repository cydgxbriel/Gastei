# 💰 Gastei - Controle Financeiro Pessoal

Sistema completo para controle de custos via WhatsApp e interface web, com categorização automática por IA.

## 🎯 Funcionalidades

- ✅ Registro de gastos via WhatsApp (texto ou áudio)
- ✅ Categorização automática de transações
- ✅ Interface web para visualização e gerenciamento
- ✅ Suporte a expense/income/investment
- ✅ Relatórios e dashboards
- ✅ 25 categorias pré-configuradas

## 🛠️ Tecnologias

| Componente | Tecnologia | Função |
|------------|------------|--------|
| **Backend** | n8n Cloud | Automação e processamento |
| **Banco de Dados** | Supabase (PostgreSQL) | Armazenamento com RLS |
| **WhatsApp API** | Evolution API / Z-API | Integração WhatsApp |
| **IA** | Hugging Face (Whisper) | Transcrição de áudio |
| **Frontend** | Gradio (HF Spaces) | Interface web |

## 📁 Estrutura do Projeto

```
Gastei/
├── supabase/
│   └── schema.sql              # Schema completo do banco
├── n8n/
│   ├── workflows/              # Workflows do n8n
│   └── parse_transaction_code.js  # Parser com UUIDs
├── huggingface/
│   ├── app.py                  # Interface Gradio
│   └── requirements.txt        # Dependências Python
├── .env.example                # Template de configuração
└── README.md                   # Este arquivo
```

---

# 🚀 Guia Completo de Setup

## Pré-requisitos

- Conta no [Supabase](https://supabase.com) (gratuita)
- Conta no [n8n Cloud](https://n8n.cloud) (gratuita até 500 execuções/mês)
- Conta no [Hugging Face](https://huggingface.co) (gratuita)
- VPS ou conta na [Z-API](https://z-api.io) para WhatsApp

---

## Passo 1: Configurar Supabase

### 1.1 Criar Projeto

1. Acesse https://supabase.com/dashboard
2. Clique em **"New Project"**
3. Preencha:
   - **Name**: `gastei` (ou nome de sua preferência)
   - **Database Password**: Crie senha forte e anote
   - **Region**: `South America (São Paulo)`
4. Aguarde ~2 minutos

### 1.2 Executar Schema SQL

1. No dashboard, vá em **SQL Editor** → **New query**
2. Copie o conteúdo de `supabase/schema.sql`
3. Cole no editor e clique em **"Run"**
4. Aguarde a execução (~30 segundos)

### 1.3 Obter Credenciais

1. Vá em **Settings → API**
2. Copie e salve:
   - **Project URL**: `https://xxx.supabase.co`
   - **anon public key**: Para uso no frontend
   - **service_role secret**: Para uso no backend (n8n)

### 1.4 Verificar

1. Vá em **Table Editor**
2. Confirme que existem 4 tabelas:
   - `categories` (25 linhas)
   - `transactions` (vazia)
   - `user_preferences` (vazia)
   - `keyword_mappings` (~30 linhas)

---

## Passo 2: Configurar n8n Cloud

### 2.1 Criar Conta

1. Acesse https://n8n.cloud
2. Crie conta (email/GitHub/Google)
3. Confirme email se necessário

### 2.2 Importar Workflow

1. No dashboard, clique em **"New workflow"**
2. Clique nos **3 pontinhos** (⋮) → **"Import from file"**
3. Selecione `n8n/workflows/whatsapp_simple.json` (ou crie manualmente)
4. O workflow será carregado

### 2.3 Configurar Credenciais

#### A) Supabase Credential
1. Clique no nó **"Save to Supabase"**
2. **Create New Credential** → **HTTP Request**
3. Deixe como está (vamos usar headers customizados)

#### B) Configurar Headers do Nó HTTP Request
No nó "Save to Supabase", configure:
- **URL**: `https://xxx.supabase.co/rest/v1/rpc/insert_transaction_from_webhook`
- **Headers**:
  - `apikey`: Cole sua **service_role key**
  - `Authorization`: `Bearer [service_role key]`
  - `Content-Type`: `application/json`

### 2.4 Atualizar Código do Parser

1. Clique no nó **"Parse Transaction"**
2. Copie o código de `n8n/parse_transaction_code.js`
3. Cole no editor de código
4. Salve

### 2.5 Ativar Workflow

1. Toggle **"Inactive" → "Active"** no canto superior direito
2. Copie a **Production URL** do nó Webhook:
   ```
   https://xxx.app.n8n.cloud/webhook/whatsapp-webhook
   ```

---

## Passo 3: Configurar Hugging Face Spaces

### 3.1 Criar Space

1. Acesse https://huggingface.co/spaces
2. Clique em **"Create new Space"**
3. Preencha:
   - **Space name**: `gastei` (ou nome de sua preferência)
   - **SDK**: **Gradio** ⚠️
   - **Hardware**: CPU basic (Free)
   - **Visibility**: Public ou Private

### 3.2 Upload de Arquivos

Via interface web:
1. Clique em **"Files" → "Add file" → "Upload files"**
2. Faça upload de:
   - `huggingface/app.py`
   - `huggingface/requirements.txt`
3. Clique em **"Commit changes to main"**

### 3.3 Configurar Secrets

1. Vá em **"Settings" → "Repository secrets"**
2. Adicione:
   - **SUPABASE_URL**: Sua URL do Supabase
   - **SUPABASE_SERVICE_ROLE_KEY**: Sua service_role key
   - **DEFAULT_USER_ID**: UUID do usuário (obter no Supabase Auth)

### 3.4 Aguardar Build

1. O Space começará a buildar automaticamente (~2-5 min)
2. Quando aparecer **"Running on..."**, está pronto!
3. Acesse a URL do Space para testar

---

## Passo 4: Configurar WhatsApp

Escolha uma das opções:

### Opção A: Evolution API (Gratuito + VPS)

#### A.1 Requisitos
- VPS com Docker (mín. 1GB RAM)
  - **Sugestões**: Contabo (~R$30/mês), DigitalOcean ($6/mês)

#### A.2 Instalar Evolution API

```bash
# Conectar via SSH
ssh root@SEU_IP

# Clonar e configurar
git clone https://github.com/EvolutionAPI/evolution-api.git
cd evolution-api
cp .env.example .env
nano .env

# Configurar variáveis importantes:
# AUTHENTICATION_API_KEY=suasenhasecreta123
# DATABASE_ENABLED=true

# Iniciar
docker-compose up -d

# Verificar logs
docker-compose logs -f
```

#### A.3 Conectar WhatsApp

```bash
# Criar instância
curl -X POST http://SEU_IP:8080/instance/create \
  -H "apikey: suasenhasecreta123" \
  -H "Content-Type: application/json" \
  -d '{
    "instanceName": "gastei",
    "qrcode": true
  }'

# Copie o QR Code exibido e escaneie com WhatsApp
```

#### A.4 Configurar Webhook

```bash
curl -X POST http://SEU_IP:8080/webhook/set/gastei \
  -H "apikey: suasenhasecreta123" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://xxx.app.n8n.cloud/webhook/whatsapp-webhook",
    "webhook_by_events": false,
    "events": ["MESSAGES_UPSERT"]
  }'
```

### Opção B: Z-API (Pago, mais simples)

1. Acesse https://z-api.io
2. Crie conta (~R$90/mês)
3. Conecte seu WhatsApp
4. Configure webhook:
   - **URL**: `https://xxx.app.n8n.cloud/webhook/whatsapp-webhook`
   - **Events**: `messages.upsert`

---

## Passo 5: Testar o Sistema

### 5.1 Teste via WhatsApp

Envie uma mensagem para o número conectado:
```
Gastei 50 reais no almoço
```

### 5.2 Verificar n8n

1. No n8n, vá em **"Executions"**
2. Você deve ver a execução com status **"Success"**
3. Clique para ver os dados processados

### 5.3 Verificar Supabase

1. No Supabase, vá em **Table Editor → transactions**
2. Você deve ver a transação registrada com:
   - `type`: expense
   - `amount_brl`: 50
   - `category`: Alimentação
   - `category_id`: UUID correspondente

### 5.4 Verificar Interface Web

1. Acesse seu Hugging Face Space
2. A transação deve aparecer na lista
3. Teste adicionar uma transação manualmente

---

## 📱 Como Usar

### Via WhatsApp

**Formato simples:**
```
50 mercado
30 uber
100 salário
```

**Com detalhes:**
```
Gastei 50 reais no almoço
Paguei 30 de uber para o trabalho
Recebi 5000 de salário
```

**Via áudio:**
Envie um áudio dizendo: *"Gastei 50 reais no almoço"*

### Via Interface Web

1. Acesse seu Space no Hugging Face
2. Use a aba **"Adicionar Transação"**
3. Preencha os campos e clique em **"Adicionar"**
4. Veja os relatórios nas outras abas

---

## 🔧 Configuração Avançada

### Variáveis de Ambiente (.env)

Crie um arquivo `.env` baseado em `.env.example`:

```env
# Supabase
SUPABASE_URL="https://xxx.supabase.co"
SUPABASE_PUBLISHABLE_KEY="eyJhbGci..."
SUPABASE_SERVICE_ROLE_KEY="eyJhbGci..."
SUPABASE_PROJECT_ID="xxx"

# User
USER_ID="uuid-do-usuario"
DEFAULT_USER_ID="uuid-do-usuario"
```

### Categorias Disponíveis

**Expenses (14):**
Alimentação, Mercado, Casa, Contas, Transporte, Saúde, Roupas & Acessórios, Entretenimento, Assinaturas, Educação, Presentes, Cuidados pessoais, Impostos/Taxas, Outros

**Income (4):**
Salário, Freelance, Rendimentos, Outros

**Investment (7):**
Renda fixa, FII, Ações, ETFs, Crypto, Outros

---

## 🐛 Solução de Problemas

| Problema | Solução |
|----------|---------|
| Webhook não recebe mensagens | Verifique URL no WhatsApp API e se workflow está ativo |
| Transação não salva no Supabase | Verifique service_role key e RLS policies |
| Interface web não carrega | Verifique secrets no HF Spaces e logs do build |
| Categoria errada | Ajuste keywords em `parse_transaction_code.js` |
| n8n retorna erro 401 | Service role key incorreta ou expirada |

### Verificar Logs

**n8n:**
- Executions → Clique na execução → Ver detalhes de cada nó

**Supabase:**
- Logs → API logs

**Hugging Face:**
- Settings → Logs

---

## 📊 Estrutura do Banco de Dados

### Tabelas Principais

- **categories**: 25 categorias pré-definidas
- **transactions**: Todas as transações registradas
- **user_preferences**: Preferências do usuário
- **keyword_mappings**: Mapeamento de keywords para categorias

### RLS (Row Level Security)

Todas as tabelas têm políticas RLS configuradas para:
- Usuários veem apenas seus próprios dados
- Service role tem acesso total (usado pelo n8n)

---

## 🔒 Segurança

### Melhores Práticas

1. ✅ Nunca exponha sua `service_role` key publicamente
2. ✅ Use `.env` para variáveis sensíveis
3. ✅ Mantenha `.env` no `.gitignore`
4. ✅ Rotacione credenciais periodicamente
5. ✅ Use HTTPS em produção

### Credenciais no Git

⚠️ **IMPORTANTE**: O arquivo `.env` está no `.gitignore` e **não deve** ser commitado.

Use `.env.example` como template sem dados sensíveis.

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'feat: adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

---

## 📝 Licença

Este projeto é de código aberto. Use livremente!

---

## 🆘 Suporte

Problemas? Dúvidas?
- Abra uma [issue no GitHub](https://github.com/cydgxbriel/Gastei/issues)
- Consulte a documentação do [Supabase](https://supabase.com/docs), [n8n](https://docs.n8n.io/), [Gradio](https://www.gradio.app/docs)

---

**Versão**: 2.0 (Auditada e Otimizada)
**Última atualização**: 2026-01-31
