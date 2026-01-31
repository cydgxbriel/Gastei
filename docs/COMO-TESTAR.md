# Como testar o workflow n8n (WhatsApp → Supabase)

## Situação atual (credencial corrigida)

O fluxo **não usa Service Role** no n8n. Uma função RPC no Supabase (`insert_transaction_from_webhook`) insere a transação com `SECURITY DEFINER`, permitindo usar a **chave anon** no n8n.

- **Webhook** recebe o POST.
- **Parse Transaction** extrai valor, tipo, categoria e **category_id** (UUID). Termos mais específicos primeiro (ex.: "alimentação" antes de "ação").
- **Is Valid?** encaminha só transações válidas (valor numérico > 0).
- **Save to Supabase** chama `POST /rest/v1/rpc/insert_transaction_from_webhook` com a chave **anon** → insert OK.

---

## Testes executados (checklist)

| Caso | Payload | Resposta esperada | Supabase |
|------|--------|-------------------|----------|
| **Sucesso** | `{"body":{"message":"50 mercado"}}` | HTTP 200; webhook retorna `{"success": true, "message": "Transação salva com sucesso!"}` | Nova linha: `type=expense`, `category=Mercado`, `category_id` preenchido |
| **Sucesso** | `{"body":{"message":"25 alimentação"}}` | HTTP 200 | Nova linha: `category=Alimentação` (não Ações) |
| **Sucesso** | `{"body":{"message":"100 uber"}}` | HTTP 200 | Nova linha: `category=Transporte` |
| **Rejeitado** | `{"body":{"message":"texto sem valor"}}` | HTTP 200; webhook retorna `{"success": false, "error": "Não entendi o valor. Tente ex: 50 mercado"}` | Nenhuma linha nova |

**Nota:** Ao chamar o webhook via curl, a resposta que você vê é a do nó **Respond Success** ou **Respond Error** (não a do Supabase).

---

## Teste rápido (curl)

Substitua `SEU_N8N_URL` pela URL base do seu n8n (ex.: `https://meu-n8n.example.com`).

```bash
# Sucesso
curl -X POST "https://SEU_N8N_URL/webhook/whatsapp-webhook" \
  -H "Content-Type: application/json" \
  -d '{"body":{"message":"50 mercado"}}'
```

**Resposta esperada:** `{"success": true, "message": "Transação salva com sucesso!"}`

**Mensagem inválida (sem valor):**

```bash
curl -X POST "https://SEU_N8N_URL/webhook/whatsapp-webhook" \
  -H "Content-Type: application/json" \
  -d '{"body":{"message":"texto sem valor"}}'
```

**Resposta esperada:** `{"success": false, "error": "Não entendi o valor. Tente ex: 50 mercado"}`

---

## Conferir no Supabase

1. Acesse o [Supabase Dashboard](https://supabase.com/dashboard/project/qlifljzlqummsakarpbf) → **Table Editor** → **transactions**.
2. Filtre ou ordene por `source = whatsapp` e `created_at` descendente.
3. Confira: `amount_brl`, `category`, `category_id` (UUID) preenchido, `source: whatsapp`.

---

## Alternativa: usar Service Role Key no n8n

Se preferir inserir direto na tabela (sem RPC), use a **Service Role Key** no nó "Save to Supabase":

1. Supabase Dashboard → **Settings** → **API** → copie a chave **service_role** (JWT).
2. No n8n, no nó "Save to Supabase": **URL** = `https://qlifljzlqummsakarpbf.supabase.co/rest/v1/transactions`, **apikey** e **Authorization: Bearer** = essa chave, **body** com `user_id`, `type`, `amount_brl`, `category`, `category_id`, etc.

Com a RPC + anon, **não é necessário** colar a Service Role no n8n.
