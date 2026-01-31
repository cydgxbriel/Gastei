# 🔧 Correções Necessárias - Projeto Gastei

**Data**: 2026-01-31
**Status**: CRÍTICO - Credenciais expostas + Erros de configuração

---

## 📊 Resumo Executivo

### Problemas Encontrados: 7
- 🔴 **Críticos**: 3 (segurança e autenticação)
- 🟡 **Altos**: 4 (configuração e compatibilidade)

### Impacto:
- ❌ Credenciais do Supabase expostas publicamente no Git
- ❌ App não consegue autenticar corretamente (variáveis erradas)
- ❌ N8n workflow com JWT inválido
- ❌ Incompatibilidade de schema entre n8n e banco de dados

---

## 🔴 CRÍTICO 1: Credenciais Expostas no Git

### Problema:
O arquivo `.env` foi commitado com credenciais sensíveis visíveis no histórico do Git.

### Arquivos Afetados:
- `.env` (linhas 1-7)
- `n8n/workflows/whatsapp_simple.json` (linhas 55, 62, 66, 83)

### Dados Expostos:
```
SUPABASE_URL = "https://qlifljzlqummsakarpbf.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGci...XpHkXb4" (JWT completo)
USER_ID = "7d305729-4641-4418-87e6-d8b222fb7e46"
```

### ⚠️ Risco:
Qualquer pessoa com acesso ao repositório pode:
- Acessar seu banco de dados Supabase
- Ler/modificar/deletar todos os dados
- Ignorar Row Level Security (RLS)

### 🛠️ Solução Imediata:

#### Passo 1: Rotacionar credenciais no Supabase
1. Acesse: https://supabase.com/dashboard/project/qlifljzlqummsakarpbf/settings/api
2. Vá em **Settings > API**
3. Em **Service Role Key**, clique em "Reset" ou "Generate New Key"
4. Copie a nova chave

#### Passo 2: Atualizar Project API Keys (se necessário)
1. No mesmo painel, verifique se há opção de regenerar API keys
2. Anote a nova `anon/public` key

#### Passo 3: Remover .env do histórico do Git
```bash
# Remover .env do tracking (mantém arquivo local)
git rm --cached .env

# Adicionar .env ao .gitignore (já existe, mas garantir)
echo ".env" >> .gitignore

# Commit da remoção
git add .gitignore
git commit -m "security: remove exposed credentials from git"

# IMPORTANTE: Reescrever histórico (CUIDADO - isso reescreve commits!)
# Só fazer se o repo não for compartilhado ou se todos concordarem
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (ATENÇÃO: coordenar com equipe!)
# git push origin --force --all
```

**⚠️ ALTERNATIVA SEGURA**: Se o repo for público/compartilhado, melhor:
1. Criar novo projeto Supabase
2. Migrar dados
3. Atualizar credenciais

---

## 🔴 CRÍTICO 2: JWT Inválido no N8n Workflow

### Problema:
O workflow `whatsapp_simple.json` usa uma chave **incorreta** que não é um JWT válido.

### Localização:
- Arquivo: `n8n/workflows/whatsapp_simple.json`
- Linhas: 62, 66

### Código Atual (ERRADO):
```json
{
  "name": "apikey",
  "value": "sb_secret_ARVhcFaATmIwFxcS97v4-w_4PP_FrzU"
},
{
  "name": "Authorization",
  "value": "Bearer sb_secret_ARVhcFaATmIwFxcS97v4-w_4PP_FrzU"
}
```

### Por que está errado:
- `sb_secret_...` NÃO é um JWT válido
- JWT tem formato: `eyJ...` (3 partes separadas por `.`)
- Isso pode ser um "project reference" ou ID incorreto

### 🛠️ Correção:

**Substituir linhas 62 e 66** por:
```json
{
  "name": "apikey",
  "value": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFsaWZsanpscXVtbXNha2FycGJmIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2OTgyNjE3MSwiZXhwIjoyMDg1NDAyMTcxfQ.QHI08RieoU4Wxy8YBb8zwPZb5Rfl7qollzOVFpHkXb4"
},
{
  "name": "Authorization",
  "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFsaWZsanpscXVtbXNha2FycGJmIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2OTgyNjE3MSwiZXhwIjoyMDg1NDAyMTcxfQ.QHI08RieoU4Wxy8YBb8zwPZb5Rfl7qollzOVFpHkXb4"
}
```

**⚠️ MELHOR PRÁTICA**: Usar variáveis de ambiente no n8n:
```json
{
  "name": "apikey",
  "value": "={{ $env.SUPABASE_SERVICE_ROLE_KEY }}"
},
{
  "name": "Authorization",
  "value": "Bearer {{ $env.SUPABASE_SERVICE_ROLE_KEY }}"
}
```

---

## 🔴 CRÍTICO 3: Incompatibilidade de Schema (category vs category_id)

### Problema:
O workflow n8n envia `category` como **texto**, mas o banco espera `category_id` como **UUID**.

### Localização:
- Arquivo: `n8n/workflows/whatsapp_simple.json`
- Linha: 94

### Código Atual (ERRADO):
```json
{
  "name": "category",
  "value": "={{ $json.category }}"
}
```

### Schema do Banco (correto):
```sql
CREATE TABLE transactions (
  ...
  category_id UUID REFERENCES categories(id),  -- Espera UUID!
  ...
);
```

### 🛠️ Solução:

**Opção A - Mapear categorias no n8n** (Recomendado):

Adicionar mapeamento no código JavaScript do nó "Parse Transaction" (linha 21):

```javascript
// ADICIONAR APÓS A LINHA 77 (depois de definir category)

// Mapeamento categoria -> UUID (igual ao app.py)
const CATEGORY_IDS = {
  // Expense
  'Alimentação': '7bc7916f-578f-4892-8252-5fb009a811ab',
  'Mercado': 'bd7e80b6-4dc1-489e-9cf8-bf81dd23107e',
  'Casa': 'dcbb830d-d3fa-435a-89a8-8a7962e407cf',
  'Contas': '302ffea7-6c72-44e6-a142-565d6a8b3faa',
  'Transporte': 'd08f46e8-7cc8-47f9-b3cd-342b607b685f',
  'Saúde': '64408fbe-3225-462f-b4d2-d3b805a24c3b',
  'Roupas & Acessórios': 'a8560155-dbf2-46e6-bb3d-30d77ebefb29',
  'Entretenimento': '57f5b107-729d-42ab-bc1e-ecf3b95d6987',
  'Assinaturas': 'fba057db-bec3-4aa9-bd88-6dadbb4d2d4d',
  'Educação': 'bab28650-1bb2-493a-856d-11266e591800',
  'Presentes': '2cb4cf5a-cac3-4196-aab8-ca1f16ac5206',
  'Cuidados pessoais': '839ba5f6-2460-43df-aa52-a14b90b18faa',
  'Impostos/Taxas': '277e1bc4-5061-4eca-913d-70d1076bce43',
  'Outros': 'bf891223-e65b-4a1d-83eb-5b541dc7e255',
  // Investment
  'Renda fixa': 'b3d1dcc2-7ad5-4143-a7f4-f8da47447ff9',
  'FII': '0ba3e9a3-9521-4d46-a3e4-2eb96c149c2c',
  'Ações': '043e25b2-63a1-49ea-9b3c-dfec2defa8e0',
  'ETFs': '4de14bc4-d07b-446c-bb90-644c8f718e64',
  'Crypto': 'b343fe3d-9d4b-403a-84b5-4c0bdd05f8b5',
  // Income
  'Salário': 'a7ba8c9d-bf97-4f1f-af2b-456965abadb0',
  'Freelance': 'e858b4a9-309d-4fe1-b8d7-d16f17fe5da9',
  'Rendimentos': '170f82e2-e40b-42a7-95c6-2c522f9f488f',
};

// Obter category_id
let category_id = CATEGORY_IDS[category];

// Fallback para "Outros" do tipo correto
if (!category_id) {
  const othersMap = {
    'expense': 'bf891223-e65b-4a1d-83eb-5b541dc7e255',
    'investment': 'b4179034-4596-47e8-8b83-a25fe28dc22f',
    'income': 'ee160689-998b-4034-9635-fcade99cfbb7'
  };
  category_id = othersMap[type];
}

// MODIFICAR O RETURN PARA INCLUIR category_id:
return {
  type,
  amount_brl: amount,
  category,
  category_id,  // ADICIONAR ESTA LINHA
  payment_method: paymentMethod,
  description: text.substring(0, 200).replace(/["\\]/g, ''),
  source: 'whatsapp',
  raw_text: text,
  is_valid: amount !== null && amount > 0 && !isNaN(amount)
};
```

Depois, **SUBSTITUIR linha 94** em `whatsapp_simple.json`:
```json
{
  "name": "category_id",
  "value": "={{ $json.category_id }}"
}
```

**Opção B - Alterar schema do banco** (NÃO recomendado):
- Aceitar `category` como TEXT no banco
- Criar trigger para converter texto → UUID
- **Problema**: Quebra a normalização e RLS

---

## 🟡 ALTO 1: Variável SUPABASE_KEY Errada no app.py

### Problema:
O `app.py` tenta carregar variável que não existe no `.env`.

### Localização:
- Arquivo: `huggingface/app.py`
- Linha: 45

### Código Atual (ERRADO):
```python
SUPABASE_KEY: str = (os.environ.get("SUPABASE_KEY") or
                     os.environ.get("SUPABASE_PUBLISHABLE_KEY", "")).strip()...
```

### Por que está errado:
1. `SUPABASE_KEY` não existe no `.env`
2. `SUPABASE_PUBLISHABLE_KEY` está truncada como `"qu"`
3. Deveria usar `SUPABASE_SERVICE_ROLE_KEY`

### 🛠️ Correção:

**SUBSTITUIR linha 45** por:
```python
SUPABASE_KEY: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip().replace("\n", "").replace(" ", "")
```

**OU**, se quiser flexibilidade:
```python
SUPABASE_KEY: str = (
    os.environ.get("SUPABASE_KEY") or
    os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or
    os.environ.get("SUPABASE_PUBLISHABLE_KEY", "")
).strip().replace("\n", "").replace(" ", "")
```

---

## 🟡 ALTO 2: Chave Publishable Truncada no .env

### Problema:
A chave publishable está incompleta.

### Localização:
- Arquivo: `.env`
- Linha: 3

### Código Atual (ERRADO):
```env
SUPABASE_PUBLISHABLE_KEY = "qu"
```

### 🛠️ Correção:

**Obter a chave correta**:
1. Acesse: https://supabase.com/dashboard/project/qlifljzlqummsakarpbf/settings/api
2. Copie a **anon/public key** (é um JWT que começa com `eyJ...`)

**SUBSTITUIR linha 3**:
```env
SUPABASE_PUBLISHABLE_KEY="eyJhbGci...ABC123"  # (JWT completo)
```

**Nota**: A publishable key é segura para usar no frontend (não ignora RLS).

---

## 🟡 ALTO 3: Nome de Variável Incorreto no .env

### Problema:
`SUPABASE_PROJECT_ID` não é um project ID, é uma chave.

### Localização:
- Arquivo: `.env`
- Linha: 4

### Código Atual (CONFUSO):
```env
SUPABASE_PROJECT_ID = "sb_secret_ARVhcFaATmIwFxcS97v4-w_4PP_FrzU"
```

### 🛠️ Correção:

**Identificar o que é**:
- `sb_secret_...` parece ser um "secret key", mas não é JWT
- Project ID geralmente é: `qlifljzlqummsakarpbf` (do URL)

**SUBSTITUIR linha 4** por:
```env
SUPABASE_PROJECT_ID="qlifljzlqummsakarpbf"
```

**OU**, se for uma chave adicional, renomear:
```env
SUPABASE_SECRET_KEY="sb_secret_ARVhcFaATmIwFxcS97v4-w_4PP_FrzU"
```

---

## 🟡 ALTO 4: Credenciais Hardcoded no Workflow N8n

### Problema:
URL e User ID estão hardcoded no workflow JSON.

### Localização:
- Arquivo: `n8n/workflows/whatsapp_simple.json`
- Linhas: 55, 83

### Código Atual (HARDCODED):
```json
"url": "https://qlifljzlqummsakarpbf.supabase.co/rest/v1/transactions",
...
"value": "7d305729-4641-4418-87e6-d8b222fb7e46"
```

### 🛠️ Correção:

**SUBSTITUIR por variáveis de ambiente**:

```json
"url": "={{ $env.SUPABASE_URL }}/rest/v1/transactions",
...
"value": "={{ $env.USER_ID }}"
```

**Configurar no n8n**:
1. Vá em **Settings > Environments**
2. Adicione:
   - `SUPABASE_URL` = `https://qlifljzlqummsakarpbf.supabase.co`
   - `USER_ID` = `7d305729-4641-4418-87e6-d8b222fb7e46`
   - `SUPABASE_SERVICE_ROLE_KEY` = `eyJ...` (JWT completo)

---

## 📝 Arquivo .env Corrigido (Template)

Criar arquivo `.env.example` (sem credenciais reais):

```env
# Supabase Configuration
SUPABASE_URL="https://[SEU-PROJETO].supabase.co"
SUPABASE_PUBLISHABLE_KEY="eyJhbGci..." # Anon/Public key (JWT)
SUPABASE_SERVICE_ROLE_KEY="eyJhbGci..." # Service Role key (JWT)
SUPABASE_PROJECT_ID="[project-ref]" # Ex: qlifljzlqummsakarpbf

# User Configuration
USER_ID="[UUID-do-usuario]" # Obter em: Dashboard > Authentication > Users
```

**Arquivo `.env` real** (após rotacionar credenciais):

```env
# Supabase Configuration
SUPABASE_URL="https://qlifljzlqummsakarpbf.supabase.co"
SUPABASE_PUBLISHABLE_KEY="[NOVA-PUBLISHABLE-KEY-AQUI]"
SUPABASE_SERVICE_ROLE_KEY="[NOVA-SERVICE-ROLE-KEY-AQUI]"
SUPABASE_PROJECT_ID="qlifljzlqummsakarpbf"

# User Configuration
USER_ID="7d305729-4641-4418-87e6-d8b222fb7e46"
```

---

## ✅ Checklist de Implementação

### Fase 1: Segurança Imediata (URGENTE)
- [ ] Rotacionar Service Role Key no Supabase
- [ ] Rotacionar Publishable Key no Supabase
- [ ] Atualizar `.env` local com novas credenciais
- [ ] Remover `.env` do Git tracking (`git rm --cached .env`)
- [ ] Criar `.env.example` (sem credenciais)
- [ ] Commit: "security: remove exposed credentials"

### Fase 2: Correções de Código
- [ ] Corrigir `app.py` linha 45 (usar `SUPABASE_SERVICE_ROLE_KEY`)
- [ ] Atualizar `whatsapp_simple.json` linhas 62, 66 (JWT correto)
- [ ] Adicionar mapeamento de `category_id` no código JavaScript do n8n
- [ ] Substituir `category` por `category_id` na linha 94 do workflow
- [ ] Substituir hardcoded URL/User ID por variáveis de ambiente (linhas 55, 83)

### Fase 3: Testes
- [ ] Testar autenticação do app.py com Supabase
- [ ] Testar workflow n8n com mensagem de teste
- [ ] Verificar inserção no banco (campos corretos)
- [ ] Confirmar que RLS está funcionando

### Fase 4: Documentação
- [ ] Atualizar `docs/setup.md` com variáveis corretas
- [ ] Documentar processo de rotação de credenciais
- [ ] Adicionar este arquivo ao `.gitignore` (se tiver credenciais)

---

## 🚨 Ações Imediatas (FAZER AGORA)

1. **Rotacionar credenciais no Supabase** (15 minutos)
2. **Atualizar `.env` local** (2 minutos)
3. **Remover `.env` do Git** (5 minutos)

**Depois disso**, você pode trabalhar nas correções de código com calma.

---

## 📞 Suporte

Se precisar de ajuda:
- Documentação Supabase: https://supabase.com/docs/guides/api/api-keys
- Reset API Keys: https://supabase.com/dashboard/project/_/settings/api

---

**Gerado em**: 2026-01-31
**Versão**: 1.0
