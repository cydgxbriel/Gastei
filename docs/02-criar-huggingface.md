# Guia Passo-a-Passo: Criar Hugging Face Space

## 📋 Pré-requisitos
- Conta no Hugging Face (crie em [huggingface.co](https://huggingface.co) se não tiver)
- Credenciais do Supabase (já temos em `docs/keys.md`)

---

## 1️⃣ Criar Conta/Login no Hugging Face

1. Acesse [https://huggingface.co](https://huggingface.co)
2. Clique em **"Sign Up"** (ou "Log In" se já tiver conta)
3. Complete o cadastro com email/senha ou GitHub

---

## 2️⃣ Criar Novo Space

1. Acesse [https://huggingface.co/spaces](https://huggingface.co/spaces)
2. Clique em **"Create new Space"** (botão azul no canto superior direito)
3. Preencha os dados:
   - **Owner**: Sua conta (será selecionada automaticamente)
   - **Space name**: `controle-financeiro` (ou o nome que preferir)
   - **License**: MIT (recomendado)
   - **Select the Space SDK**: **Gradio** ⚠️ IMPORTANTE!
   - **Space hardware**: CPU basic - 2 vCPU - 16GB RAM (Free)
   - **Visibility**: Public (ou Private se preferir)
4. Clique em **"Create Space"**

---

## 3️⃣ Fazer Upload dos Arquivos

Você tem duas opções:

### Opção A: Upload via Interface Web (Mais Fácil)

1. Após criar o Space, você verá a página do projeto
2. Clique em **"Files"** (aba no topo)
3. Clique em **"Add file"** → **"Upload files"**
4. Faça upload dos seguintes arquivos de `E:\Yugo\huggingface\`:
   - ✅ `app.py`
   - ✅ `requirements.txt`
5. Clique em **"Commit changes to main"**

### Opção B: Via Git (Para Usuários Avançados)

```bash
# Clone o repositório do Space
git clone https://huggingface.co/spaces/SEU_USERNAME/controle-financeiro
cd controle-financeiro

# Copie os arquivos
copy E:\Yugo\huggingface\app.py .
copy E:\Yugo\huggingface\requirements.txt .

# Commit e push
git add .
git commit -m "Initial commit"
git push
```

---

## 4️⃣ Configurar Variáveis de Ambiente (Secrets)

⚠️ **PASSO CRÍTICO** - Sem isso o app não funcionará!

1. No seu Space, clique em **"Settings"** (aba no topo)
2. Role até a seção **"Repository secrets"**
3. Clique em **"New secret"**

### Secret 1: SUPABASE_URL
- **Name**: `SUPABASE_URL`
- **Value**: `https://qlifljzlqummsakarpbf.supabase.co`
- Clique em **"Add"**

### Secret 2: SUPABASE_KEY
- **Name**: `SUPABASE_KEY`
- **Value**: Cole a **Anon/Public Key** de `docs/keys.md`:
  ```
  eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFsaWZsanpscXVtbXNha2FycGJmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzg0NjI5NzAsImV4cCI6MjA1NDAzODk3MH0.sb_publishable_4bbnJ3nT1dOsqgPsl6D82g_QAOJ9jls
  ```
- Clique em **"Add"**

---

## 5️⃣ Aguardar Build e Deploy

1. Após fazer upload dos arquivos, o Space começará a buildar automaticamente
2. Você verá logs na tela (pode levar 2-5 minutos)
3. Mensagens esperadas:
   ```
   Installing dependencies from requirements.txt
   Running app.py
   Running on local URL: http://0.0.0.0:7860
   ```
4. Quando aparecer **"Running on..."**, o app está pronto! 🎉

---

## 6️⃣ Testar a Interface

### Teste 1: Verificar Conexão com Supabase
1. Abra o Space (a URL será algo como `https://huggingface.co/spaces/SEU_USERNAME/controle-financeiro`)
2. No topo da página, deve aparecer:
   - 🟢 **"Status do Banco: Conectado"** ✅
   - 🔴 **"Status do Banco: Não configurado"** ❌ (volte ao passo 4)

### Teste 2: Registrar uma Transação
1. Vá na aba **"🏠 Inicio"**
2. Digite no campo: `25 mercado pix`
3. Clique em **"💾 Salvar"**
4. Deve aparecer: ✅ **"📤 Saída • R$ 25.00 • Mercado"**

### Teste 3: Usar o Chatbot
1. Vá na aba **"💬 Chat"**
2. Digite: `Quanto gastei esse mês?`
3. Deve responder com o resumo (incluindo os R$ 25 que você acabou de registrar)

### Teste 4: Ver Resumo do Mês
1. Vá na aba **"📊 Mês"**
2. Deve mostrar:
   - 📤 Saídas: R$ 25.00
   - 🔴 Saldo: R$ -25.00

---

## 7️⃣ Compartilhar o App

Após tudo funcionando, você pode:

1. **Compartilhar a URL**: `https://huggingface.co/spaces/SEU_USERNAME/controle-financeiro`
2. **Embedar em site**: Hugging Face fornece código iframe
3. **Tornar público**: Se criou como Private, pode mudar em Settings

---

## 🆘 Problemas Comuns

| Problema | Solução |
|----------|---------|
| "Status do Banco: Não configurado" | Verifique se adicionou as secrets SUPABASE_URL e SUPABASE_KEY corretamente |
| Erro "ModuleNotFoundError" | Verifique se o `requirements.txt` foi enviado corretamente |
| App não carrega | Veja os logs em "Logs" (aba no topo) e me envie o erro |
| "Connection refused" ao Supabase | Verifique se a URL está correta (sem espaços ou caracteres extras) |

---

## 📝 Checklist

- [ ] Conta criada no Hugging Face
- [ ] Space criado com SDK Gradio
- [ ] Arquivos `app.py` e `requirements.txt` enviados
- [ ] Secret `SUPABASE_URL` configurado
- [ ] Secret `SUPABASE_KEY` configurado
- [ ] Build concluído com sucesso
- [ ] Status mostra "🟢 Conectado"
- [ ] Teste de registro funcionou
- [ ] Chatbot respondeu corretamente
- [ ] Resumo do mês apareceu

**Quando terminar, me avise e vamos configurar o n8n + WhatsApp!** 🚀
