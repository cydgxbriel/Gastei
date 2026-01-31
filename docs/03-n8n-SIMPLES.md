# n8n - Guia Simplificado (SEM Credenciais)

## 🎯 Versão Mais Fácil

Criei um workflow simplificado que **NÃO precisa configurar credenciais**!

---

## 1️⃣ Importar o Workflow Simplificado

1. No n8n, clique nos **3 pontinhos** (⋮) → **"Import from file"**
2. Selecione: `E:\Yugo\n8n\workflows\whatsapp_simple.json`
3. Pronto! O workflow já vem com tudo configurado

---

## 2️⃣ Ativar o Workflow

1. No canto superior direito, mude de **"Inactive"** para **"Active"**
2. Pronto! Já está funcionando

---

## 3️⃣ Copiar URL do Webhook

1. Clique no nó **"Webhook WhatsApp"** (primeiro nó)
2. Copie a **Production URL**:
   ```
   https://SEU_WORKSPACE.app.n8n.cloud/webhook/whatsapp-webhook
   ```
3. Guarde essa URL para configurar o WhatsApp

---

## 4️⃣ Testar

Teste se está funcionando:

```bash
curl -X POST https://SEU_WORKSPACE.app.n8n.cloud/webhook/whatsapp-webhook \
  -H "Content-Type: application/json" \
  -d '{"message": "Gastei 50 reais no mercado pix"}'
```

**Resultado esperado:**
```json
{
  "success": true,
  "message": "Registrado: expense R$ 50 - Mercado"
}
```

---

## ✅ Vantagens desta Versão

- ✅ **Sem configurar credenciais** (tudo já vem no workflow)
- ✅ **Mais rápido** de configurar
- ✅ **Funciona igual** ao workflow original

---

## 🔒 Segurança

> ⚠️ As credenciais estão "hardcoded" no workflow. Isso é OK para testes, mas para produção é recomendado usar variáveis de ambiente.

---

## 📝 Checklist

- [ ] Workflow importado
- [ ] Workflow ativado
- [ ] URL do webhook copiada
- [ ] Teste funcionou

**Próximo: Configurar WhatsApp!**
