# Upload Rápido - Hugging Face Space

## ✅ Você já criou o Space! Agora:

### 1️⃣ Fazer Upload dos Arquivos

Você tem duas opções:

#### Opção A: Via Interface Web (RECOMENDADO - Mais Fácil)

1. Na página do seu Space, clique em **"Files and versions"** (aba no topo)
2. Clique em **"Add file"** → **"Upload files"**
3. Arraste ou selecione estes 2 arquivos:
   - `E:\Yugo\huggingface\app.py`
   - `E:\Yugo\huggingface\requirements.txt`
4. Escreva uma mensagem de commit (ex: "Initial upload")
5. Clique em **"Commit changes to main"**

#### Opção B: Via Git (se preferir)

Copie e cole estes comandos no terminal:

```bash
# Clone o repositório
git clone https://huggingface.co/spaces/cydgxbriel/controle-financeiro
cd controle-financeiro

# Copie os arquivos
copy E:\Yugo\huggingface\app.py .
copy E:\Yugo\huggingface\requirements.txt .

# Commit e push
git add .
git commit -m "Add Gradio app"
git push
```

---

### 2️⃣ Configurar Secrets (CRÍTICO!)

Após o upload, **IMEDIATAMENTE**:

1. Clique em **"Settings"** (aba no topo)
2. Role até **"Repository secrets"**
3. Adicione os 2 secrets:

**Secret 1:**
- Name: `SUPABASE_URL`
- Value: `https://qlifljzlqummsakarpbf.supabase.co`

**Secret 2:**
- Name: `SUPABASE_KEY`
- Value: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFsaWZsanpscXVtbXNha2FycGJmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzg0NjI5NzAsImV4cCI6MjA1NDAzODk3MH0.sb_publishable_4bbnJ3nT1dOsqgPsl6D82g_QAOJ9jls`

---

### 3️⃣ Aguardar Build

- O Space vai buildar automaticamente (2-5 min)
- Você verá logs na tela
- Quando aparecer "Running on...", está pronto!

---

### 4️⃣ Testar

1. Abra a URL do Space
2. Verifique se aparece: **🟢 Conectado**
3. Teste registrar: `25 mercado pix`

---

## 🆘 Precisa de Ajuda?

Se tiver qualquer erro, me envie um print e te ajudo!
