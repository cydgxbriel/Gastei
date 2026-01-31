# ⚠️ Advisors de Segurança - Supabase

**Data**: 2026-01-31
**Fonte**: Supabase Security Linter

---

## 🔴 Erros Críticos (3)

### 1. Security Definer Views

**Problema**: 3 views definidas com `SECURITY DEFINER`

**Views afetadas**:
- `public.top_categories_month`
- `public.monthly_summary`
- `public.today_transactions`

**Risco**: 
Views com SECURITY DEFINER executam com as permissões do criador da view, não do usuário que está consultando. Isso pode:
- Burlar políticas de RLS (Row Level Security)
- Permitir acesso não autorizado a dados
- Criar vulnerabilidades de elevação de privilégios

**Solução**:
```sql
-- Para cada view, recriar sem SECURITY DEFINER:

-- Exemplo para top_categories_month:
DROP VIEW IF EXISTS public.top_categories_month;
CREATE VIEW public.top_categories_month AS
  -- (query original da view)
  -- SEM a cláusula SECURITY DEFINER

-- OU adicionar SECURITY INVOKER explicitamente:
CREATE VIEW public.top_categories_month 
WITH (security_invoker = true) AS
  -- (query original)
```

**Documentação**: https://supabase.com/docs/guides/database/database-linter?lint=0010_security_definer_view

---

## 🟡 Avisos (4)

### 2. Function Search Path Mutable

**Problema**: 3 funções sem `search_path` definido

**Funções afetadas**:
- `public.get_monthly_balance`
- `public.get_weekly_summary`
- `public.get_monthly_summary`

**Risco**:
Funções sem search_path fixo podem ser vulneráveis a:
- Ataques de injeção de schema
- Comportamento inesperado se schemas mudarem
- Problemas de segurança se usuário malicioso criar schemas/tabelas com nomes específicos

**Solução**:
```sql
-- Para cada função, adicionar SET search_path:

ALTER FUNCTION public.get_monthly_balance
  SET search_path = public, pg_catalog;

ALTER FUNCTION public.get_weekly_summary
  SET search_path = public, pg_catalog;

ALTER FUNCTION public.get_monthly_summary
  SET search_path = public, pg_catalog;

-- OU redefinir a função com SET search_path:
CREATE OR REPLACE FUNCTION public.get_monthly_balance(...)
RETURNS ...
LANGUAGE plpgsql
SET search_path = public, pg_catalog
AS $$
  -- código da função
$$;
```

**Documentação**: https://supabase.com/docs/guides/database/database-linter?lint=0011_function_search_path_mutable

---

### 3. Leaked Password Protection Disabled

**Problema**: Proteção contra senhas vazadas está desabilitada

**Risco**:
- Usuários podem usar senhas comprometidas conhecidas
- Contas vulneráveis a ataques de credential stuffing
- Menor segurança geral da autenticação

**Solução**:

1. Acesse: https://supabase.com/dashboard/project/qlifljzlqummsakarpbf/auth/policies
2. Vá em **"Password"** ou **"Security"**
3. Habilite **"Leaked Password Protection"**
4. Salve as configurações

Isso ativa verificação contra a base HaveIBeenPwned.org automaticamente.

**Documentação**: https://supabase.com/docs/guides/auth/password-security#password-strength-and-leaked-password-protection

---

## 📋 Checklist de Correção

### Alta Prioridade:
- [ ] Recriar views sem SECURITY DEFINER
  - [ ] `top_categories_month`
  - [ ] `monthly_summary`
  - [ ] `today_transactions`

### Média Prioridade:
- [ ] Adicionar search_path às funções
  - [ ] `get_monthly_balance`
  - [ ] `get_weekly_summary`
  - [ ] `get_monthly_summary`

### Baixa Prioridade:
- [ ] Habilitar Leaked Password Protection no Auth

---

## 🔧 Script de Correção Rápida

```sql
-- 1. Obter definições atuais das views
SELECT 
  schemaname, 
  viewname, 
  definition 
FROM pg_views 
WHERE schemaname = 'public' 
  AND viewname IN ('top_categories_month', 'monthly_summary', 'today_transactions');

-- 2. Copiar as definições e recriar sem SECURITY DEFINER

-- 3. Corrigir funções
ALTER FUNCTION public.get_monthly_balance SET search_path = public, pg_catalog;
ALTER FUNCTION public.get_weekly_summary SET search_path = public, pg_catalog;
ALTER FUNCTION public.get_monthly_summary SET search_path = public, pg_catalog;

-- 4. Verificar
SELECT 
  routine_name, 
  routine_type,
  security_type
FROM information_schema.routines
WHERE routine_schema = 'public'
  AND routine_name LIKE 'get_%';
```

---

## 📊 Impacto

**Sem correção**:
- Risco de segurança MÉDIO-ALTO
- Possível acesso não autorizado via views
- Vulnerabilidade a ataques de schema injection

**Com correção**:
- RLS aplicado corretamente em todas as queries
- Funções protegidas contra manipulação de schema
- Autenticação mais segura

---

**Tempo estimado de correção**: 30-45 minutos
**Próxima verificação**: Após aplicar correções, rodar advisors novamente

---

# 📊 Advisors de Performance - Supabase

**Data**: 2026-01-31
**Fonte**: Supabase Performance Linter

---

## 🟡 Avisos de Performance (11)

### 1. Auth RLS Initialization Plan (11 políticas)

**Problema**: Políticas RLS chamam `auth.uid()` diretamente, sendo reavaliado para cada linha

**Tabelas/Políticas afetadas**:
- `transactions` (4 políticas): view, insert, update, delete
- `categories` (2 políticas): view, insert
- `user_preferences` (1 política): manage own
- `keyword_mappings` (2 políticas): view, insert

**Impacto**: Performance MUITO RUIM em queries com muitos registros

**Solução**: Envolver chamadas em subquery
```sql
-- ANTES (lento):
CREATE POLICY "Users can view own transactions" ON transactions
  FOR SELECT USING (user_id = auth.uid());

-- DEPOIS (rápido):
CREATE POLICY "Users can view own transactions" ON transactions
  FOR SELECT USING (user_id = (SELECT auth.uid()));
```

**Script de correção**:
```sql
-- Recriar políticas com subquery
DROP POLICY "Users can view own transactions" ON transactions;
CREATE POLICY "Users can view own transactions" ON transactions
  FOR SELECT USING (user_id = (SELECT auth.uid()));

DROP POLICY "Users can insert own transactions" ON transactions;
CREATE POLICY "Users can insert own transactions" ON transactions
  FOR INSERT WITH CHECK (user_id = (SELECT auth.uid()));

DROP POLICY "Users can update own transactions" ON transactions;
CREATE POLICY "Users can update own transactions" ON transactions
  FOR UPDATE USING (user_id = (SELECT auth.uid()));

DROP POLICY "Users can delete own transactions" ON transactions;
CREATE POLICY "Users can delete own transactions" ON transactions
  FOR DELETE USING (user_id = (SELECT auth.uid()));

-- Repetir para categories, user_preferences, keyword_mappings
```

---

## ℹ️ Informações (7)

### 2. Foreign Keys sem Índice (2)

**Problema**: Foreign keys sem índice podem causar lentidão em JOINs

**Afetados**:
- `categories.user_id` → falta índice
- `transactions.category_id` → falta índice

**Solução**:
```sql
-- Criar índices para foreign keys
CREATE INDEX idx_categories_user_id ON categories(user_id);
CREATE INDEX idx_transactions_category_id ON transactions(category_id);
```

---

### 3. Índices Não Utilizados (5)

**Problema**: Índices criados mas nunca usados (desperdiçam espaço e INSERT performance)

**Índices não usados**:
- `idx_transactions_user_date` (transactions)
- `idx_transactions_type` (transactions)
- `idx_transactions_category` (transactions)
- `idx_categories_type` (categories)
- `idx_keyword_mappings_keyword` (keyword_mappings)

**Análise**: Podem não ter sido usados ainda por falta de dados ou queries específicas

**Solução**:
```sql
-- OPÇÃO 1: Aguardar mais tempo de uso (recomendado)
-- O banco está novo, índices podem ser úteis quando houver mais dados

-- OPÇÃO 2: Remover se confirmar que não são necessários (após 1 mês de uso)
DROP INDEX idx_transactions_user_date;
DROP INDEX idx_transactions_type;
DROP INDEX idx_transactions_category;
DROP INDEX idx_categories_type;
DROP INDEX idx_keyword_mappings_keyword;
```

---

## 📋 Checklist Completo (Segurança + Performance)

### 🔴 Alta Prioridade:
- [ ] Corrigir 3 views com SECURITY DEFINER
- [ ] Adicionar search_path a 3 funções
- [ ] **Otimizar 11 políticas RLS** (maior impacto em performance!)

### 🟡 Média Prioridade:
- [ ] Criar 2 índices para foreign keys
- [ ] Habilitar Leaked Password Protection

### ⚪ Baixa Prioridade:
- [ ] Monitorar índices não usados (decidir após 1 mês)

---

## 🔧 Script de Correção Completo

```sql
-- ==========================================
-- SEGURANÇA
-- ==========================================

-- 1. Corrigir funções (search_path)
ALTER FUNCTION public.get_monthly_balance SET search_path = public, pg_catalog;
ALTER FUNCTION public.get_weekly_summary SET search_path = public, pg_catalog;
ALTER FUNCTION public.get_monthly_summary SET search_path = public, pg_catalog;

-- 2. Views: obter definições atuais primeiro
SELECT schemaname, viewname, definition 
FROM pg_views 
WHERE schemaname = 'public' 
  AND viewname IN ('top_categories_month', 'monthly_summary', 'today_transactions');

-- (Copiar definições e recriar sem SECURITY DEFINER manualmente)

-- ==========================================
-- PERFORMANCE
-- ==========================================

-- 3. Criar índices para foreign keys
CREATE INDEX IF NOT EXISTS idx_categories_user_id ON categories(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_category_id ON transactions(category_id);

-- 4. Otimizar políticas RLS (transactions)
DROP POLICY IF EXISTS "Users can view own transactions" ON transactions;
CREATE POLICY "Users can view own transactions" ON transactions
  FOR SELECT USING (user_id = (SELECT auth.uid()));

DROP POLICY IF EXISTS "Users can insert own transactions" ON transactions;
CREATE POLICY "Users can insert own transactions" ON transactions
  FOR INSERT WITH CHECK (user_id = (SELECT auth.uid()));

DROP POLICY IF EXISTS "Users can update own transactions" ON transactions;
CREATE POLICY "Users can update own transactions" ON transactions
  FOR UPDATE USING (user_id = (SELECT auth.uid()));

DROP POLICY IF EXISTS "Users can delete own transactions" ON transactions;
CREATE POLICY "Users can delete own transactions" ON transactions
  FOR DELETE USING (user_id = (SELECT auth.uid()));

-- 5. Otimizar políticas RLS (categories)
DROP POLICY IF EXISTS "Users can view default and own categories" ON categories;
CREATE POLICY "Users can view default and own categories" ON categories
  FOR SELECT USING (user_id IS NULL OR user_id = (SELECT auth.uid()));

DROP POLICY IF EXISTS "Users can insert own categories" ON categories;
CREATE POLICY "Users can insert own categories" ON categories
  FOR INSERT WITH CHECK (user_id = (SELECT auth.uid()));

-- 6. Otimizar políticas RLS (user_preferences)
DROP POLICY IF EXISTS "Users can manage own preferences" ON user_preferences;
CREATE POLICY "Users can manage own preferences" ON user_preferences
  FOR ALL USING (user_id = (SELECT auth.uid()));

-- 7. Otimizar políticas RLS (keyword_mappings)
DROP POLICY IF EXISTS "Users can view default and own keywords" ON keyword_mappings;
CREATE POLICY "Users can view default and own keywords" ON keyword_mappings
  FOR SELECT USING (user_id IS NULL OR user_id = (SELECT auth.uid()));

DROP POLICY IF EXISTS "Users can insert own keywords" ON keyword_mappings;
CREATE POLICY "Users can insert own keywords" ON keyword_mappings
  FOR INSERT WITH CHECK (user_id = (SELECT auth.uid()));

-- ==========================================
-- VERIFICAÇÃO
-- ==========================================

-- Verificar políticas
SELECT schemaname, tablename, policyname 
FROM pg_policies 
WHERE schemaname = 'public'
ORDER BY tablename;

-- Verificar índices
SELECT 
  schemaname, 
  tablename, 
  indexname 
FROM pg_indexes 
WHERE schemaname = 'public'
ORDER BY tablename;
```

---

## 📊 Resumo de Impacto

**Total de problemas**: 23
- 🔴 Erros críticos: 3 (segurança)
- 🟡 Avisos: 15 (4 seg + 11 perf)
- ℹ️ Informações: 7 (performance)

**Tempo estimado de correção**: 1-2 horas

**Ganhos após correção**:
- ✅ Segurança: RLS aplicado corretamente, funções protegidas
- ✅ Performance: Queries 10-100x mais rápidas com RLS otimizado
- ✅ Escalabilidade: Índices corretos para JOINs rápidos

---

**Próxima ação**: Execute o script de correção no SQL Editor do Supabase
