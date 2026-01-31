# Inconsistências n8n × Supabase (verificação via MCPs)

**Data**: 2026-01-31  
**Fonte**: MCP Supabase + MCP n8n + arquivo `CORREÇÕES_NECESSARIAS.md`

---

## 1. Resumo do que os MCPs mostraram

### Supabase (MCP)

| Item | Valor |
|------|--------|
| **Project URL** | `https://qlifljzlqummsakarpbf.supabase.co` |
| **Tabela `transactions`** | Tem **ambos**: `category` (TEXT, NOT NULL) e `category_id` (UUID, nullable, FK → `categories.id`) |
| **Tabela `categories`** | 25 categorias com UUIDs (expense, income, investment) |
| **Chaves disponíveis (get_publishable_keys)** | `anon` (JWT legacy), `sb_publishable_...` (publishable). **Service Role JWT não é retornado** por essa API (segurança). |

Ou seja: o banco **aceita** envio só de `category` (texto); `category_id` pode ficar NULL. Para integridade e relatórios, o ideal é enviar `category_id` (UUID).

### n8n – Workflow “WhatsApp Transaction Processor - FINAL 4.0 (SB Keys)”

| Item | Valor atual | Observação |
|------|-------------|------------|
| **ID** | `VBxlrdWb4M1ot5p_PLFXZ` | Workflow ativo no n8n |
| **URL Supabase** | `https://qlifljzlqummsakarpbf.supabase.co/rest/v1/transactions` | Hardcoded |
| **Headers** | `apikey` e `Authorization: Bearer` = `sb_secret_ARVhcFaATmIwFxcS97v4-w_4PP_FrzU` | Chave `sb_secret_...` |
| **Body** | `user_id`, `type`, `amount_brl`, **`category`** (texto), `payment_method`, `description`, `source`, `raw_text` | **Não envia `category_id`** |
| **user_id** | `7d305729-4641-4418-87e6-d8b222fb7e46` | Hardcoded |

### Validação do workflow (MCP n8n)

- **valid**: `false`
- **Erros**: nó “Is Valid?” – “Filter must have a combinator field” e “Filter must have a conditions field”
- **Avisos**: typeVersions desatualizados (Webhook, If, HTTP Request, Respond to Webhook), uso de `$` no Code, falta de error handling em vários nós

---

## 2. Confronto com o CORREÇÕES_NECESSARIAS.md

### 2.1 JWT inválido / chave incorreta (CRÍTICO 2)

- **Doc**: diz que `sb_secret_...` não é JWT e que a REST API espera JWT (`eyJ...`).
- **Supabase docs (API keys)**:
  - Chaves **secret** (`sb_secret_...`) têm privilégio elevado (tipo service_role) e **podem** ser usadas em backend.
  - Porém: *“You cannot send a publishable or secret key in the `Authorization: Bearer ...` header, **except if the value exactly equals the apikey header**. In this case, your request will be forwarded down to your project's database, **but will be rejected as the value is not a JWT**.”*
- **Conclusão**: Para **PostgREST (REST API)** o gateway pode rejeitar quando o valor em `Authorization: Bearer` não é um JWT. Ou seja, usar **service_role JWT** em `apikey` e `Authorization: Bearer` é o caminho seguro para o n8n; o uso de `sb_secret_...` no header Bearer pode causar 401/rejeição.

**Recomendação**: usar no n8n a **Service Role Key (JWT)** em variável de ambiente e colocar esse JWT em `apikey` e `Authorization: Bearer`, em vez de `sb_secret_...` hardcoded.

---

### 2.2 Schema: category vs category_id (CRÍTICO 3)

- **Doc**: “workflow envia `category` (texto), banco espera `category_id` (UUID)”.
- **MCP Supabase**: a tabela `transactions` tem **os dois**:
  - `category` TEXT NOT NULL
  - `category_id` UUID nullable, FK para `categories(id)`
- **Conclusão**: enviar só `category` (texto) **não quebra** o insert; o banco aceita. Porém `category_id` fica NULL, o que:
  - enfraquece a integridade referencial e
  - pode atrapalhar relatórios/views que dependem de `category_id`.

**Recomendação**: manter envio de `category` (texto) e **adicionar** envio de `category_id` (UUID), mapeando no n8n o nome da categoria → UUID (lista de categorias obtida via MCP Supabase abaixo).

---

### 2.3 Categorias no banco (UUIDs para mapeamento no n8n)

Consulta usada: `SELECT id, name, type FROM categories ORDER BY type, name`.

| name | type | id (UUID) |
|------|------|-----------|
| Alimentação | expense | 7bc7916f-578f-4892-8252-5fb009a811ab |
| Assinaturas | expense | fba057db-bec3-4aa9-bd88-6dadbb4d2d4d |
| Casa | expense | dcbb830d-d3fa-435a-89a8-8a7962e407cf |
| Contas | expense | 302ffea7-6c72-44e6-a142-565d6a8b3faa |
| Cuidados pessoais | expense | 839ba5f6-2460-43df-aa52-a14b90b18faa |
| Educação | expense | bab28650-1bb2-493a-856d-11266e591800 |
| Entretenimento | expense | 57f5b107-729d-42ab-bc1e-ecf3b95d6987 |
| Impostos/Taxas | expense | 277e1bc4-5061-4eca-913d-70d1076bce43 |
| Mercado | expense | bd7e80b6-4dc1-489e-9cf8-bf81dd23107e |
| Outros | expense | bf891223-e65b-4a1d-83eb-5b541dc7e255 |
| Presentes | expense | 2cb4cf5a-cac3-4196-aab8-ca1f16ac5206 |
| Roupas & Acessórios | expense | a8560155-dbf2-46e6-bb3d-30d77ebefb29 |
| Saúde | expense | 64408fbe-3225-462f-b4d2-d3b805a24c3b |
| Transporte | expense | d08f46e8-7cc8-47f9-b3cd-342b607b685f |
| Freelance | income | e858b4a9-309d-4fe1-b8d7-d16f17fe5da9 |
| Outros | income | ee160689-998b-4034-9635-fcade99cfbb7 |
| Rendimentos | income | 170f82e2-e40b-42a7-95c6-2c522f9f488f |
| Salário | income | a7ba8c9d-bf97-4f1f-af2b-456965abadb0 |
| Ações | investment | 043e25b2-63a1-49ea-9b3c-dfec2defa8e0 |
| Crypto | investment | b343fe3d-9d4b-403a-84b5-4c0bdd05f8b5 |
| ETFs | investment | 4de14bc4-d07b-446c-bb90-644c8f718e64 |
| FII | investment | 0ba3e9a3-9521-4d46-a3e4-2eb96c149c2c |
| Outros | investment | b4179034-4596-47e8-8b83-a25fe28dc22f |
| Renda fixa | investment | b3d1dcc2-7ad5-4143-a7f4-f8da47447ff9 |

Use essa tabela no nó “Parse Transaction” (ou em um nó seguinte) para preencher `category_id` a partir de `category` (nome) e `type`.

---

### 2.4 Credenciais e hardcode (CRÍTICO 1, ALTO 4)

- **Doc**: credenciais no Git; URL e user_id hardcoded no workflow.
- **MCP n8n**: confirma URL e user_id fixos no JSON do workflow; chave `sb_secret_...` está no nó HTTP Request.
- **Recomendação**: mover URL, user_id e chave (de preferência JWT service_role) para variáveis de ambiente do n8n e usar expressões tipo `={{ $env.SUPABASE_URL }}`, `={{ $env.USER_ID }}`, `={{ $env.SUPABASE_SERVICE_ROLE_KEY }}`.

---

## 3. Checklist objetivo (alinhado aos MCPs)

- [ ] **Autenticação REST**: trocar `sb_secret_...` por **Service Role JWT** em `apikey` e `Authorization: Bearer` (variável de ambiente no n8n).
- [ ] **Schema**: no body do POST para `transactions`, **adicionar** campo `category_id` (UUID) mapeado a partir de `category` + `type` usando a tabela de categorias acima.
- [ ] **Hardcode**: substituir URL, user_id e chave por variáveis de ambiente no n8n.
- [ ] **Validação n8n**: corrigir nó “Is Valid?” (combinator + conditions) e, se desejado, atualizar typeVersions e error handling conforme avisos do MCP.
- [ ] **Segurança**: seguir CORREÇÕES_NECESSARIAS.md (rotacionar chaves, remover .env do Git, usar .env.example).

---

## 4. Referências

- Supabase – Understanding API keys: anon/service_role (JWT) vs publishable/secret (`sb_...`), e limite de usar secret no `Authorization: Bearer`.
- Supabase – Creating API routes: URL da API e uso de `apikey` (e JWT no Bearer para PostgREST).
- n8n MCP – `n8n_get_workflow`, `n8n_validate_workflow`, estrutura do nó HTTP Request e do Code “Parse Transaction”.

Se quiser, o próximo passo pode ser: (1) aplicar as alterações no workflow via MCP n8n (parcial ou completo) ou (2) gerar o trecho de código do nó “Parse Transaction” com o mapeamento `category` → `category_id` usando a tabela acima.
