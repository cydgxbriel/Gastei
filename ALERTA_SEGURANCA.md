# 🚨 ALERTA DE SEGURANÇA CRÍTICO

**Data**: 2026-01-31
**Severidade**: CRÍTICA

## ⚠️ Credenciais Expostas no Histórico do Git

O arquivo `docs/.env` foi commitado com credenciais sensíveis e permanece no histórico:

### Commit com credenciais:
- **Commit**: `caa1efd` (feat: configuração de segurança com .env)
- **Arquivo**: `docs/.env`
- **Status**: Removido em `ab98820`, mas AINDA NO HISTÓRICO

### Dados Expostos:
```
SUPABASE_URL = "https://qlifljzlqummsakarpbf.supabase.co"
SUPABASE_PUBLISHABLE_KEY = "eyJhbGci..." (JWT anon completo)
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGci..." (JWT service_role completo - CRÍTICO!)
USER_ID = "7d305729-4641-4418-87e6-d8b222fb7e46"
```

## 🔥 Risco Imediato

A **SERVICE_ROLE_KEY** permite:
- ✗ Bypass completo de Row Level Security (RLS)
- ✗ Acesso total a TODOS os dados do banco
- ✗ Modificar/deletar qualquer registro
- ✗ Criar/alterar schema do banco
- ✗ Executar qualquer operação administrativa

## ✅ AÇÕES URGENTES (FAZER AGORA)

### 1. Rotacionar Credenciais (15 minutos)

Acesse: https://supabase.com/dashboard/project/qlifljzlqummsakarpbf/settings/api

**A. Regenerar Service Role Key:**
1. Vá em "Service Role Key"
2. Clique em "Reset" ou "Regenerate"
3. Copie a NOVA chave
4. Atualize seu `.env` local
5. Atualize variáveis de ambiente no n8n
6. Atualize secrets no Hugging Face Spaces

**B. Verificar se é possível regenerar Anon/Publishable Key:**
1. Veja se há opção de regenerar a "anon/public" key
2. Se sim, regenere e atualize `.env` local

### 2. Limpar Histórico do Git (ESCOLHA UMA OPÇÃO)

#### Opção A: Reescrever Histórico (SE REPO FOR PRIVADO/PESSOAL)

```bash
# ATENÇÃO: Isso reescreve o histórico! Coordenar com equipe se compartilhado

# 1. Remover docs/.env do histórico
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch docs/.env" \
  --prune-empty --tag-name-filter cat -- --all

# 2. Forçar garbage collection
rm -rf .git/refs/original/
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 3. Force push (CUIDADO!)
# git push origin --force --all
# git push origin --force --tags
```

#### Opção B: Criar Novo Repositório (SE REPO FOR PÚBLICO)

Se o repositório foi publicado no GitHub/GitLab público:

1. Rotacione TODAS as credenciais do Supabase
2. Crie novo repositório Git do zero
3. Faça commit limpo do código atual
4. Arquive o repositório antigo (NÃO delete para manter histórico)

### 3. Verificar onde o repositório foi publicado

```bash
git remote -v
```

Se houver remote `origin` apontando para GitHub/GitLab/etc:
- Verifique se o repositório é PÚBLICO ou PRIVADO
- Se PÚBLICO: Credenciais estão expostas publicamente! Rotacione IMEDIATAMENTE
- Se PRIVADO: Rotacione e considere reescrever histórico

### 4. Atualizar todos os ambientes

Após rotacionar credenciais:

- [ ] `.env` local
- [ ] Variáveis de ambiente n8n
- [ ] Secrets Hugging Face Spaces
- [ ] Qualquer outro ambiente/deploy

## 📋 Checklist de Segurança

- [ ] Rotacionar Service Role Key no Supabase
- [ ] Rotacionar Anon/Publishable Key (se possível)
- [ ] Atualizar `.env` local com novas credenciais
- [ ] Verificar se repo tem remote público
- [ ] Limpar histórico do Git (opção A ou B acima)
- [ ] Atualizar credenciais em n8n
- [ ] Atualizar secrets em Hugging Face
- [ ] Testar autenticação em todos os ambientes
- [ ] Monitorar logs do Supabase por atividade suspeita

## 🔍 Monitoramento Pós-Incidente

1. Acesse: https://supabase.com/dashboard/project/qlifljzlqummsakarpbf/logs
2. Verifique logs de autenticação e acesso ao banco
3. Procure por:
   - Acessos de IPs desconhecidos
   - Operações em horários incomuns
   - Queries suspeitas (DELETE em massa, etc)

## 📞 Recursos

- Reset API Keys: https://supabase.com/dashboard/project/_/settings/api
- Docs Supabase Security: https://supabase.com/docs/guides/api/api-keys

---

**Status**: PENDENTE - Aguardando rotação de credenciais
**Próxima verificação**: Após rotação, validar que credenciais antigas não funcionam mais
