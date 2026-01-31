# 🔄 Rotação de Credenciais - URGENTE

**Motivo**: Repositório PÚBLICO com credenciais expostas no histórico
**Data**: 2026-01-31
**Status**: ⚠️ AÇÃO IMEDIATA NECESSÁRIA

## Credenciais que DEVEM ser rotacionadas:

### 1. Service Role Key (CRÍTICA)
- **Exposta em**: docs/.env (histórico público do Git)
- **Risco**: Acesso administrativo total ao banco Supabase
- **Ação**: https://supabase.com/dashboard/project/qlifljzlqummsakarpbf/settings/api
  1. Vá em "Project API keys"
  2. Encontre "service_role" key
  3. Clique em "Reveal" para ver a atual
  4. Clique em "Reset" ou "Generate new key"
  5. Copie a NOVA chave

### 2. Anon/Public Key (MÉDIA-ALTA)
- **Exposta em**: docs/.env (histórico público)
- **Risco**: Acesso aos dados com RLS aplicado
- **Ação**: Verificar se Supabase permite regenerar a anon key
  - Se SIM: regenere
  - Se NÃO: considere criar novo projeto Supabase

## Após rotacionar:

### A. Atualizar .env local
```bash
# Editar .env com novas credenciais
nano .env

# Verificar que .env está no .gitignore (já está)
grep "^\.env$" .gitignore
```

### B. Atualizar n8n
1. Acesse n8n
2. Vá em Settings > Environment Variables
3. Atualize:
   - `SUPABASE_SERVICE_ROLE_KEY` = [nova chave]
   - Salve

### C. Atualizar Hugging Face Spaces
1. Acesse: https://huggingface.co/spaces/[seu-usuario]/[seu-space]/settings
2. Vá em "Repository secrets"
3. Atualize:
   - `SUPABASE_SERVICE_ROLE_KEY` = [nova chave]
   - `SUPABASE_PUBLISHABLE_KEY` = [nova chave, se foi rotacionada]

### D. Force Push do Git Limpo
```bash
# ATENÇÃO: Isso sobrescreverá o histórico público!
git push origin --force --all
git push origin --force --tags

# Verificar no GitHub que o histórico está limpo
```

### E. Testar autenticação
```bash
# Testar app Hugging Face
# Testar workflow n8n
# Verificar logs Supabase para confirmar novas chaves funcionando
```

## Monitoramento pós-rotação:

- [ ] Verificar logs Supabase por atividade com chaves antigas
- [ ] Confirmar que chaves antigas retornam 401 Unauthorized
- [ ] Monitorar por 24-48h por acessos suspeitos

## Tempo estimado:
- Rotação: 10-15 minutos
- Atualização ambientes: 10-15 minutos
- Testes: 5-10 minutos
- **Total**: ~30-40 minutos

---

**COMEÇAR AGORA**: https://supabase.com/dashboard/project/qlifljzlqummsakarpbf/settings/api
