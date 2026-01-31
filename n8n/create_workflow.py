import os
import json
from dotenv import load_dotenv

# Load .env from ../docs/.env
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(os.path.dirname(current_dir), 'docs', '.env')
load_dotenv(env_path)

# Configurações Reais
USER_ID = os.getenv("USER_ID")
SUPABASE_BASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_URL = f"{SUPABASE_BASE_URL}/rest/v1/transactions" if SUPABASE_BASE_URL else None
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")

# Código JavaScript do Parser (Versão Final Refinada)
JS_CODE = r"""
const json = $input.first().json;

// 1. Tenta extrair a mensagem de todas as formas conhecidas
let text = json.body?.message ||          // Teste manual PowerShell (body: { message: ... })
           json.text?.message ||          // Z-API (alguns eventos)
           json.text?.body ||             // Z-API (padrão)
           json.message?.conversation ||  // WhatsApp Web
           json.message?.extendedTextMessage?.text || // Mensagem longa
           json.message ||                // Teste simples { message: ... }
           json.body ||                   // Teste simples { body: ... }
           '';

// 2. Se for áudio, tenta pegar a transcrição
if (!text && json.audio && json.audio.transcription) {
    text = json.audio.transcription;
}

// 3. Fallback agressivo: converte tudo para string para tentar achar números no meio da bagunça
if (!text || typeof text !== 'string') {
    // Evitamos converter headers gigantes, focamos no payload útil se existir
    const content = json.body || json;
    text = JSON.stringify(content);
}

const textLower = text.toLowerCase();

// 4. Extrair Valor (Regex robusto para R$ e formatos BR)
// Aceita: "50", "R$ 50,00", "1.200,50", "50 reais"
const valorMatch = textLower.match(/r?\$?\s*([\d.,]+)/);
let amount = null;

if (valorMatch) {
    let cleanValue = valorMatch[1];
    // Se tiver vírgula, assume formato BR (troca , por .)
    if (cleanValue.includes(',')) {
        cleanValue = cleanValue.replace(/\./g, '').replace(',', '.');
    }
    amount = parseFloat(cleanValue);
}

// 5. Identificar Tipo
let type = 'expense';
const incomeWords = ['salário', 'salario', 'recebi', 'entrada', 'pagamento', 'ganhei', 'pix recebido'];
const investmentWords = ['investi', 'investimento', 'fii', 'ação', 'crypto', 'etf', 'renda fixa', 'tesouro'];

if (incomeWords.some(w => textLower.includes(w))) {
  type = 'income';
} else if (investmentWords.some(w => textLower.includes(w))) {
  type = 'investment';
}

// 6. Categoria
const categoryMap = {
  'mercado': 'Mercado', 'supermercado': 'Mercado', 'feira': 'Mercado',
  'padaria': 'Alimentação', 'almoço': 'Alimentação', 'jantar': 'Alimentação', 'ifood': 'Alimentação',
  'uber': 'Transporte', '99': 'Transporte', 'gasolina': 'Transporte', 'posto': 'Transporte',
  'netflix': 'Assinaturas', 'spotify': 'Assinaturas', 'disney': 'Assinaturas',
  'farmacia': 'Saúde', 'remedio': 'Saúde', 'médico': 'Saúde',
  'fii': 'FII', 'ação': 'Ações', 'crypto': 'Crypto',
  'salário': 'Salário'
};

let category = 'Outros';
for (const [keyword, cat] of Object.entries(categoryMap)) {
  if (textLower.includes(keyword)) {
    category = cat;
    break;
  }
}

// 7. Método de Pagamento
let paymentMethod = 'pix';
if (textLower.includes('crédito') || textLower.includes('credito')) paymentMethod = 'credit';
if (textLower.includes('débito') || textLower.includes('debito')) paymentMethod = 'debit';
if (textLower.includes('dinheiro')) paymentMethod = 'cash';

// Retorno Limpo
return {
  type,
  amount_brl: amount,
  category,
  payment_method: paymentMethod,
  description: text.substring(0, 200).replace(/["\\]/g, ''), // Limpa aspas para evitar quebrar JSON
  source: 'whatsapp',
  raw_text: text,
  is_valid: amount !== null && amount > 0 && !isNaN(amount)
};
"""

# Definição do Workflow
workflow = {
  "name": "WhatsApp Transaction Processor - FINAL 2.0",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "whatsapp-webhook",
        "responseMode": "lastNode"
      },
      "id": "webhook-1",
      "name": "Webhook WhatsApp",
      "type": "n8n-nodes-base.webhook",
      "position": [250, 300],
      "typeVersion": 1
    },
    {
      "parameters": {
        "jsCode": JS_CODE
      },
      "id": "parse",
      "name": "Parse Transaction",
      "type": "n8n-nodes-base.code",
      "position": [450, 300],
      "typeVersion": 2
    },
    {
      "parameters": {
        "conditions": {
          "boolean": [
            {
              "value1": "={{ $json.is_valid }}",
              "value2": true
            }
          ]
        }
      },
      "id": "if-valid",
      "name": "Is Valid?",
      "type": "n8n-nodes-base.if",
      "position": [650, 300],
      "typeVersion": 1
    },
    {
      "parameters": {
        "url": SUPABASE_URL,
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "sendHeaders": True,
        "headerParameters": {
          "parameters": [
            { "name": "apikey", "value": SUPABASE_KEY },
            { "name": "Authorization", "value": f"Bearer {SUPABASE_KEY}" },
            { "name": "Content-Type", "value": "application/json" },
            { "name": "Prefer", "value": "return=representation" }
          ]
        },
        "sendBody": True,
        "bodyParameters": {
          "parameters": [
            { "name": "user_id", "value": USER_ID },
            { "name": "type", "value": "={{ $json.type }}" },
            { "name": "amount_brl", "value": "={{ $json.amount_brl }}" },
            { "name": "category", "value": "={{ $json.category }}" },
            { "name": "payment_method", "value": "={{ $json.payment_method }}" },
            { "name": "description", "value": "={{ $json.description }}" },
            { "name": "source", "value": "whatsapp" },
            { "name": "raw_text", "value": "={{ $json.raw_text }}" }
          ]
        },
        "options": {}
      },
      "id": "supabase",
      "name": "Save to Supabase",
      "type": "n8n-nodes-base.httpRequest",
      "position": [900, 200],
      "typeVersion": 3
    },
    {
      "parameters": {
        "respondWith": "json",
        "responseBody": "{\n  \"success\": true,\n  \"message\": \"Transação salva com sucesso!\"\n}"
      },
      "id": "respond-success",
      "name": "Respond Success",
      "type": "n8n-nodes-base.respondToWebhook",
      "position": [1150, 200],
      "typeVersion": 1
    },
    {
      "parameters": {
        "respondWith": "json",
        "responseBody": "{\n  \"success\": false,\n  \"error\": \"Não entendi o valor. Tente ex: 50 mercado\"\n}"
      },
      "id": "respond-error",
      "name": "Respond Error",
      "type": "n8n-nodes-base.respondToWebhook",
      "position": [900, 450],
      "typeVersion": 1
    }
  ],
  "connections": {
    "Webhook WhatsApp": { "main": [[{ "node": "Parse Transaction", "type": "main", "index": 0 }]] },
    "Parse Transaction": { "main": [[{ "node": "Is Valid?", "type": "main", "index": 0 }]] },
    "Is Valid?": { 
      "main": [
        [{ "node": "Save to Supabase", "type": "main", "index": 0 }],
        [{ "node": "Respond Error", "type": "main", "index": 0 }]
      ]
    },
    "Save to Supabase": { "main": [[{ "node": "Respond Success", "type": "main", "index": 0 }]] }
  }
}

# Salvar arquivo
output_path = r"E:\Yugo\n8n\workflows\whatsapp_simple.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(workflow, f, indent=2, ensure_ascii=False)

print(f"Workflow gerado com sucesso em: {output_path}")
