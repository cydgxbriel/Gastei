# Guia Passo-a-Passo: Configurar n8n Cloud

## 📋 Pré-requisitos
- Credenciais do Supabase (em `docs/keys.md`)
- Workflow JSON (em `n8n/workflows/whatsapp_audio_processor.json`)

---

## 1️⃣ Criar Conta no n8n Cloud

1. Acesse [https://n8n.cloud](https://n8n.cloud)
2. Clique em **"Start for free"** ou **"Sign up"**
3. Escolha uma opção:
   - Email/senha
   - GitHub
   - Google
4. Confirme seu email (se necessário)
5. Você será redirecionado para o dashboard

---

## 2️⃣ Criar Novo Workflow

1. No dashboard, clique em **"New workflow"** (botão azul)
2. Você verá um canvas vazio

---

## 3️⃣ Importar o Workflow

### Opção A: Importar JSON (Recomendado)

1. No canto superior direito, clique nos **3 pontinhos** (⋮)
2. Clique em **"Import from file"**
3. Selecione o arquivo: `E:\Yugo\n8n\workflows\whatsapp_audio_processor.json`
4. O workflow será carregado com todos os nós

### Opção B: Criar Manualmente (Não Recomendado)

Se a importação não funcionar, me avise que te ajudo a criar manualmente.

---

## 4️⃣ Configurar Credenciais

Você precisa configurar 2 credenciais:

### A) Supabase

1. No workflow, clique no nó **"Save to Supabase"**
2. Clique em **"Create New Credential"** (ou no ícone de chave)
3. Preencha:
   - **Credential name**: `Supabase - Controle Financeiro`
   - **Host**: `qlifljzlqummsakarpbf.supabase.co` (sem https://)
   - **Service Role Secret**: Cole a **Service Role Key** de `docs/keys.md`:
     ```
     eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFsaWZsanpscXVtbXNha2FycGJmIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczODQ2Mjk3MCwiZXhwIjoyMDU0MDM4OTcwfQ.sb_secret_ARVhcFaATmIwFxcS97v4-w_4PP_FrzU
     ```
4. Clique em **"Save"**

### B) Hugging Face API (para Whisper)

1. Primeiro, crie uma API Key no Hugging Face:
   - Acesse [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
   - Clique em **"New token"**
   - Name: `n8n-whisper`
   - Type: **Read**
   - Clique em **"Generate"**
   - **Copie o token** (começa com `hf_...`)

2. No workflow n8n, clique no nó **"Whisper Transcription"**
3. Clique em **"Create New Credential"**
4. Preencha:
   - **Credential name**: `Hugging Face API`
   - **API Key**: Cole o token que você acabou de criar
5. Clique em **"Save"**

---

## 5️⃣ Ativar o Workflow

1. No canto superior direito, mude o toggle de **"Inactive"** para **"Active"**
2. O workflow agora está rodando! 🎉

---

## 6️⃣ Obter URL do Webhook

1. Clique no nó **"Webhook WhatsApp"** (primeiro nó)
2. Você verá a **Production URL**:
   ```
   https://SEU_WORKSPACE.app.n8n.cloud/webhook/whatsapp-webhook
   ```
3. **Copie essa URL** - vamos usar na configuração do WhatsApp

---

## 7️⃣ Testar o Webhook (Opcional)

Teste se o webhook está funcionando:

```bash
curl -X POST https://SEU_WORKSPACE.app.n8n.cloud/webhook/whatsapp-webhook \
  -H "Content-Type: application/json" \
  -d '{
    "messageType": "text",
    "message": "Gastei 50 reais no almoço pix"
  }'
```

**Resultado esperado**: Você deve ver a execução aparecer em **"Executions"** no n8n.

---

## 📝 Checklist

- [ ] Conta criada no n8n Cloud
- [ ] Workflow importado
- [ ] Credencial Supabase configurada
- [ ] Credencial Hugging Face configurada
- [ ] Workflow ativado
- [ ] URL do webhook copiada
- [ ] (Opcional) Teste do webhook funcionou

**Próximo passo: Configurar WhatsApp API!**
