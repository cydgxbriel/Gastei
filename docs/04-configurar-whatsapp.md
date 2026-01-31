# Guia: Configurar WhatsApp API

## 🎯 Escolha da API

Você tem 2 opções principais:

| Opção | Custo | Complexidade | Recomendação |
|-------|-------|--------------|--------------|
| **Evolution API** | Gratuito + VPS (~R$30-50/mês) | Média | ⭐ Melhor custo-benefício |
| **Z-API** | ~R$90/mês | Baixa | Mais simples |

---

## Opção 1: Evolution API (Recomendado)

### A) Hospedar a Evolution API

Você precisa de um servidor. Opções:

#### 1. VPS (Recomendado)
- **Contabo**: ~R$30/mês (4GB RAM)
- **DigitalOcean**: ~$6/mês (1GB RAM)
- **Vultr**: ~$6/mês (1GB RAM)

#### 2. Railway/Render (Mais Fácil)
- Railway: ~$5/mês
- Render: Plano gratuito disponível

### B) Instalar Evolution API

**Via Docker (VPS):**

```bash
# Conecte no seu VPS via SSH
ssh root@SEU_IP

# Clone o repositório
git clone https://github.com/EvolutionAPI/evolution-api.git
cd evolution-api

# Configure
cp .env.example .env
nano .env

# Edite estas linhas:
# AUTHENTICATION_API_KEY=SUA_SENHA_SECRETA_AQUI
# DATABASE_ENABLED=true
# DATABASE_CONNECTION_URI=postgresql://...

# Inicie
docker-compose up -d

# Verifique
docker-compose logs -f
```

**Via Railway (Mais Fácil):**

1. Acesse [railway.app](https://railway.app)
2. Clique em **"New Project"** → **"Deploy from GitHub repo"**
3. Conecte ao repositório: `https://github.com/EvolutionAPI/evolution-api`
4. Configure as variáveis de ambiente
5. Deploy automático!

### C) Conectar WhatsApp

1. Acesse a Evolution API: `http://SEU_IP:8080` ou `https://seu-app.railway.app`
2. Crie uma instância:
   ```bash
   curl -X POST http://SEU_IP:8080/instance/create \
     -H "apikey: SUA_SENHA_SECRETA" \
     -H "Content-Type: application/json" \
     -d '{
       "instanceName": "controle-financeiro",
       "qrcode": true
     }'
   ```
3. Escaneie o QR Code com seu WhatsApp
4. Pronto! WhatsApp conectado

### D) Configurar Webhook

```bash
curl -X POST http://SEU_IP:8080/webhook/set/controle-financeiro \
  -H "apikey: SUA_SENHA_SECRETA" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://SEU_WORKSPACE.app.n8n.cloud/webhook/whatsapp-webhook",
    "webhook_by_events": false,
    "webhook_base64": false,
    "events": [
      "MESSAGES_UPSERT"
    ]
  }'
```

---

## Opção 2: Z-API (Mais Simples)

### A) Criar Conta

1. Acesse [https://z-api.io](https://z-api.io)
2. Clique em **"Criar conta"**
3. Escolha o plano (~R$90/mês)
4. Preencha os dados e pague

### B) Conectar WhatsApp

1. No dashboard da Z-API, clique em **"Conectar número"**
2. Escaneie o QR Code com seu WhatsApp
3. Aguarde a conexão (alguns segundos)

### C) Configurar Webhook

1. No dashboard, vá em **"Webhooks"**
2. Cole a URL do n8n:
   ```
   https://SEU_WORKSPACE.app.n8n.cloud/webhook/whatsapp-webhook
   ```
3. Selecione os eventos:
   - ✅ **Mensagens recebidas**
   - ✅ **Áudios recebidos**
4. Clique em **"Salvar"**

---

## 🧪 Testar o Fluxo Completo

1. Envie uma mensagem para o WhatsApp conectado:
   ```
   Gastei 50 reais no almoço pix
   ```

2. Verifique:
   - ✅ n8n recebeu a mensagem (veja em "Executions")
   - ✅ Transação foi salva no Supabase (veja no Table Editor)
   - ✅ WhatsApp respondeu com confirmação

3. Teste com áudio:
   - Grave um áudio: "Gastei 30 reais no Uber"
   - Envie para o WhatsApp
   - Verifique se foi transcrito e salvo

---

## 🆘 Problemas Comuns

| Problema | Solução |
|----------|---------|
| QR Code não aparece | Verifique se a Evolution API está rodando (`docker-compose logs`) |
| Webhook não recebe | Verifique se a URL está correta e o workflow está ativo |
| Erro de autenticação | Verifique a `apikey` da Evolution API |
| WhatsApp desconecta | Mantenha o WhatsApp Web fechado no navegador |

---

## 📝 Checklist

- [ ] Escolheu Evolution API ou Z-API
- [ ] API WhatsApp configurada
- [ ] WhatsApp conectado (QR Code escaneado)
- [ ] Webhook configurado com URL do n8n
- [ ] Teste com mensagem de texto funcionou
- [ ] Teste com áudio funcionou
- [ ] Confirmação chegou no WhatsApp

**Parabéns! Sistema completo funcionando! 🎉**
