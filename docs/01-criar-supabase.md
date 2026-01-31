# Guia Passo-a-Passo: Criar Projeto Supabase

## 📋 Pré-requisitos
- Conta no Supabase (crie em [supabase.com](https://supabase.com) se não tiver)

---

## 1️⃣ Criar Novo Projeto

1. Acesse [https://supabase.com/dashboard](https://supabase.com/dashboard)
2. Faça login com sua conta
3. Clique em **"New Project"** (botão verde)
4. Preencha os dados:
   - **Name**: `controle-financeiro` (ou o nome que preferir)
   - **Database Password**: Crie uma senha forte e **ANOTE EM LOCAL SEGURO**
   - **Region**: `South America (São Paulo)` (para menor latência)
   - **Pricing Plan**: Free (suficiente para começar)
5. Clique em **"Create new project"**
6. Aguarde ~2 minutos (o projeto está sendo criado)

---

## 2️⃣ Executar o Schema SQL

### Passo 1: Abrir SQL Editor
1. No menu lateral esquerdo, clique em **"SQL Editor"**
2. Clique em **"New query"** (botão no canto superior direito)

### Passo 2: Copiar e Colar o Schema
1. Abra o arquivo `E:\Yugo\supabase\schema.sql` no seu editor
2. **Copie TODO o conteúdo** do arquivo
3. **Cole** no editor SQL do Supabase

### Passo 3: Executar
1. Clique no botão **"Run"** (ou pressione `Ctrl+Enter`)
2. Aguarde a execução (pode levar ~10-30 segundos)
3. Você verá mensagens de sucesso no painel inferior

> ✅ **Sucesso esperado**: Mensagens como "CREATE TABLE", "INSERT 0 X", "CREATE FUNCTION"

> ⚠️ **Se houver erro**: Copie a mensagem de erro e me envie para ajudar a resolver

---

## 3️⃣ Obter Credenciais (API Keys)

### Passo 1: Ir para Settings
1. No menu lateral, clique em **⚙️ Settings**
2. Clique em **"API"** (submenu)

### Passo 2: Copiar as Credenciais
Você verá duas informações importantes:

#### A) Project URL
```
https://xxxxxxxxxxxxx.supabase.co
```
📋 **Copie e salve** (vamos usar no Hugging Face e n8n)

#### B) API Keys
Você verá duas chaves:

- **`anon` `public`** (chave pública)
  ```
  eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  ```
  📋 **Copie e salve** (vamos usar no Hugging Face)

- **`service_role` `secret`** (chave privada - NUNCA exponha!)
  ```
  eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  ```
  📋 **Copie e salve** (vamos usar no n8n)

---

## 4️⃣ Verificar se Funcionou

### Opção A: Via Table Editor (Mais Fácil)
1. No menu lateral, clique em **"Table Editor"**
2. Você deve ver as tabelas criadas:
   - `categories` (com ~24 linhas)
   - `transactions` (vazia)
   - `user_preferences` (vazia)
   - `keyword_mappings` (com ~30 linhas)

### Opção B: Via SQL Editor
Execute este comando no SQL Editor:
```sql
SELECT COUNT(*) as total FROM categories;
```
**Resultado esperado**: `total: 24`

---

## 5️⃣ Testar Autenticação (Opcional mas Recomendado)

1. No menu lateral, clique em **"Authentication"**
2. Clique em **"Users"**
3. Clique em **"Add user"** (botão verde)
4. Preencha:
   - **Email**: seu email de teste
   - **Password**: senha de teste
5. Clique em **"Create user"**

> ✅ Se conseguir criar, a autenticação está funcionando!

---

## 6️⃣ Próximos Passos

Após concluir estes passos, você terá:
- ✅ Projeto Supabase criado
- ✅ Banco de dados configurado
- ✅ Credenciais (URL + API Keys)

**Agora podemos:**
1. Configurar o Hugging Face Spaces (interface web)
2. Configurar o n8n Cloud (automação WhatsApp)

---

## 🆘 Problemas Comuns

| Problema | Solução |
|----------|---------|
| Erro "relation already exists" | Você já executou o schema antes. Pode ignorar ou deletar as tabelas primeiro |
| Erro "permission denied" | Verifique se está logado e o projeto foi criado corretamente |
| Não vejo as tabelas | Aguarde alguns segundos e recarregue a página |

---

## 📝 Checklist

- [ ] Projeto criado no Supabase
- [ ] Schema SQL executado com sucesso
- [ ] Project URL copiado
- [ ] API Key `anon public` copiado
- [ ] API Key `service_role` copiado
- [ ] Tabelas visíveis no Table Editor
- [ ] (Opcional) Usuário de teste criado

**Quando terminar, me avise e vamos para o próximo passo!**
