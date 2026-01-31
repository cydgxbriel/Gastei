# 💰 Gastei - Controle de Custos Pessoais

Aplicativo para controle de custos fixos e variáveis via WhatsApp e interface web.

## 🛠️ Tecnologias

- **Backend**: n8n Cloud (automações)
- **Banco de Dados**: Supabase (PostgreSQL)
- **WhatsApp API**: Evolution API
- **IA**: Hugging Face (Whisper + LLM)
- **Frontend**: Gradio (Hugging Face Spaces)

## 📁 Estrutura do Projeto

```
Gastei/
├── supabase/
│   └── schema.sql              # Schema do banco de dados
├── n8n/
│   ├── workflows/              # Workflows exportados
│   ├── parse_transaction_code.js  # Parser com mapeamento category_id
│   └── create_workflow.py      # Script para criar workflows via MCP
├── huggingface/
│   ├── app.py                  # Interface Gradio
│   ├── requirements.txt        # Dependências Python
│   └── README.md               # Documentação do app
├── docs/
│   ├── setup.md                # Guia de configuração
│   ├── COMO-TESTAR.md          # Guia de testes
│   └── 06-configurar-huggingface-mcp.md  # Setup MCP
├── .env.example                # Template de variáveis de ambiente
├── ALERTA_SEGURANCA.md         # Análise de segurança
├── ADVISORS_SUPABASE.md        # Problemas de segurança do banco
├── MONITORAMENTO.md            # Guia de monitoramento
└── RESUMO_FINAL.md             # Documentação do processamento
```

## ⚠️ Importante - Segurança

**Antes de usar em produção**:
1. Revise `ALERTA_SEGURANCA.md` - análise de segurança do projeto
2. Revise `ADVISORS_SUPABASE.md` - 23 problemas de segurança/performance no banco
3. Execute correções SQL antes de usar com dados reais
4. Configure `.env` com suas próprias credenciais (use `.env.example` como base)

## 🚀 Setup Rápido

### 1. Supabase
1. Crie um projeto em [supabase.com](https://supabase.com)
2. Vá em SQL Editor e execute `supabase/schema.sql`
3. **Execute correções**: Veja `ADVISORS_SUPABASE.md` e aplique o script de correção
4. Anote a URL e API Key (Settings > API)

### 2. n8n Cloud
1. Crie conta em [n8n.cloud](https://n8n.cloud)
2. Importe os workflows de `n8n/workflows/`
3. Configure as credenciais do Supabase

### 3. Hugging Face Spaces
1. Crie um Space em [huggingface.co/spaces](https://huggingface.co/spaces)
2. Faça upload dos arquivos de `huggingface/`
3. Configure as variáveis de ambiente

## 📱 Uso

**Via WhatsApp:**
- Envie áudio: "Gastei 50 reais no almoço"
- Envie texto: "R$ 30 uber"

**Via Web:**
- Acesse o Hugging Face Space
- Cadastre custos manualmente ou use o chatbot
