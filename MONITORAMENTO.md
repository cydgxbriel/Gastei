# 📊 Monitoramento de Segurança

**Status**: Histórico do Git limpo, mas credenciais não rotacionadas
**Risco**: Médio - credenciais antigas podem ter sido copiadas antes da limpeza

## Ações de Monitoramento:

### 1. Logs do Supabase (DIÁRIO por 1 semana)

Acesse: https://supabase.com/dashboard/project/qlifljzlqummsakarpbf/logs

**Procurar por:**
- ❌ Acessos de IPs desconhecidos
- ❌ Horários incomuns (madrugada, finais de semana)
- ❌ Queries suspeitas: DELETE em massa, DROP table, INSERT anormal
- ❌ Múltiplas tentativas de autenticação

### 2. Logs de API (Auth)

- Verificar tentativas de login suspeitas
- Novos usuários criados sem sua ação
- Tokens gerados em horários estranhos

### 3. Dados do Banco

Execute mensalmente:
```sql
-- Verificar número de registros
SELECT 
  'transactions' as table_name, 
  COUNT(*) as total 
FROM transactions
UNION ALL
SELECT 'categories', COUNT(*) FROM categories;

-- Verificar última modificação
SELECT 
  table_name,
  MAX(created_at) as last_insert
FROM information_schema.tables
WHERE table_schema = 'public';
```

### 4. Alertas a Configurar

Se Supabase permitir, configure alertas para:
- Queries com tempo > 5s
- Mais de 100 requests/minuto
- Erros 401/403 em sequência

## Se Detectar Atividade Suspeita:

1. **IMEDIATO**: Desabilite o projeto no Supabase
2. Crie novo projeto Supabase
3. Migre dados
4. Atualize todas as configurações

## Plano B (Futuro):

Se quiser segurança máxima:
- Criar novo projeto Supabase
- Migrar schema e dados
- Atualizar todas as integrações
- Arquivar projeto atual

---

**Próxima verificação**: 2026-02-01 (amanhã)
