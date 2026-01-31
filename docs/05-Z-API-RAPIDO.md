# Guia Rápido: Configurar Z-API

## 🎯 O que você vai fazer:
1. Criar conta na Z-API (~R$90/mês)
2. Conectar seu WhatsApp
3. Configurar webhook para o n8n
4. Testar!

---

## 1️⃣ Criar Conta na Z-API

1. Acesse: [https://z-api.io](https://z-api.io)
2. Clique em **"Criar conta"** ou **"Começar agora"**
3. Preencha seus dados:
   - Nome
   - Email
   - Telefone
4. Escolha o plano:
   - **Recomendado**: Plano Básico (~R$90/mês)
   - Mensagens ilimitadas
   - 1 número conectado
5. Complete o pagamento

---

## 2️⃣ Conectar WhatsApp

Após criar a conta:

1. No dashboard da Z-API, você verá **"Conectar número"**
2. Clique em **"Conectar"**
3. Um **QR Code** aparecerá na tela
4. No seu WhatsApp:
   - Abra o WhatsApp
   - Vá em **Configurações** → **Aparelhos conectados**
   - Clique em **"Conectar um aparelho"**
   - Escaneie o QR Code da Z-API
5. Aguarde a conexão (alguns segundos)
6. ✅ WhatsApp conectado!

---

## 3️⃣ Configurar Webhook

### A) Copiar URL do n8n

Primeiro, pegue a URL do webhook do n8n:
1. No n8n, clique no nó **"Webhook WhatsApp1"**
2. Copie a **Production URL** (algo como):
   ```
   https://seu-workspace.app.n8n.cloud/webhook/whatsapp-webhook
   ```

### B) Configurar na Z-API

1. No dashboard da Z-API, vá em **"Webhooks"** ou **"Configurações"**
2. Cole a URL do n8n no campo **"URL do Webhook"**
3. Selecione os eventos:
   - ✅ **Mensagens recebidas** (ou "message-received")
   - ✅ **Mensagens de áudio** (se disponível)
4. Clique em **"Salvar"** ou **"Ativar"**

---

## 4️⃣ Testar o Fluxo Completo

### Teste 1: Mensagem de Texto

1. Envie uma mensagem para o WhatsApp conectado:
   ```
   Gastei 50 reais no mercado pix
   ```

2. Verifique:
   - ✅ No n8n: Vá em **"Executions"** - deve aparecer uma nova execução
   - ✅ No Supabase: Vá em **Table Editor** → **transactions** - deve ter um novo registro
   - ✅ No WhatsApp: Deve receber uma confirmação (se configurado)

### Teste 2: Outros Formatos

Teste diferentes formatos:
```
25 uber pix
1000 fii
5000 salário
39,90 netflix crédito
```

Cada um deve ser registrado com tipo e categoria corretos!

---

## 🆘 Problemas Comuns

| Problema | Solução |
|----------|---------|
| QR Code não aparece | Recarregue a página da Z-API |
| WhatsApp desconecta | Feche o WhatsApp Web no navegador |
| Webhook não recebe | Verifique se a URL está correta e o workflow está ativo |
| Mensagem não é salva | Verifique os logs no n8n (Executions) |

---

## 📝 Checklist

- [ ] Conta criada na Z-API
- [ ] Pagamento confirmado
- [ ] WhatsApp conectado (QR Code escaneado)
- [ ] URL do webhook configurada
- [ ] Teste com mensagem funcionou
- [ ] Registro apareceu no Supabase

---

## 💰 Custo Total do Sistema

| Serviço | Custo |
|---------|-------|
| Supabase | Gratuito (plano free) |
| Hugging Face | Gratuito |
| n8n Cloud | Gratuito (até 5k execuções/mês) |
| **Z-API** | **~R$90/mês** |
| **TOTAL** | **~R$90/mês** |

---

## 🎉 Pronto!

Quando tudo estiver funcionando, você terá:
- ✅ WhatsApp registrando gastos automaticamente
- ✅ Interface web para consultas
- ✅ Chatbot inteligente
- ✅ Tudo salvo no Supabase

**Parabéns! Sistema completo funcionando!** 🚀
