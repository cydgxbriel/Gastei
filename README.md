# Controle de Custos Pessoais

Aplicativo para controle de custos fixos e variáveis via WhatsApp e interface web.

## 🛠️ Tecnologias

- **Backend**: n8n Cloud (automações)
- **Banco de Dados**: Supabase (PostgreSQL)
- **WhatsApp API**: Evolution API
- **IA**: Hugging Face (Whisper + LLM)
- **Frontend**: Gradio (Hugging Face Spaces)

## 📁 Estrutura do Projeto

```
Yugo/
├── supabase/
│   └── schema.sql         # Schema do banco de dados
├── n8n/
│   └── workflows/         # Workflows exportados
├── huggingface/
│   ├── app.py             # Interface Gradio
│   └── requirements.txt   # Dependências Python
└── docs/
    └── setup.md           # Guia de configuração
```

## 🚀 Setup Rápido

### 1. Supabase
1. Crie um projeto em [supabase.com](https://supabase.com)
2. Vá em SQL Editor e execute `supabase/schema.sql`
3. Anote a URL e API Key (Settings > API)

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
