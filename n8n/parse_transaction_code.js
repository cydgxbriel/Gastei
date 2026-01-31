/* 
  PARSING INTELIGENTE DE MENSAGENS E TRANSAÇÕES 
  + mapeamento category -> category_id (UUID Supabase)
*/

const json = $input.first().json;

// 1. Tenta extrair a mensagem de todas as formas conhecidas
let text = json.body?.message ||          // Teste manual PowerShell
           json.text?.message ||          // Z-API (alguns casos)
           json.text?.body ||             // Z-API (padrão)
           json.message?.conversation ||  // WhatsApp Web
           json.message?.extendedTextMessage?.text || // Mensagem longa
           json.message ||                // Teste simples
           json.body ||                   // Teste simples
           '';

// 2. Se for áudio, tenta pegar a transcrição
if (!text && json.audio && json.audio.transcription) {
    text = json.audio.transcription;
}

// 3. Fallback agressivo: converte tudo para string para tentar achar números
if (!text || typeof text !== 'string') {
    const content = json.body || json;
    text = JSON.stringify(content);
}

const textLower = text.toLowerCase();

// 4. Extrair Valor (Regex robusto para R$ e formatos BR)
const valorMatch = textLower.match(/r?\$?\s*([\d.,]+)/);
let amount = null;

if (valorMatch) {
    let cleanValue = valorMatch[1];
    if (cleanValue.includes(',')) {
        cleanValue = cleanValue.replace(/\./g, '').replace(',', '.');
    }
    amount = parseFloat(cleanValue);
}

// 5. Identificar Tipo
let type = 'expense';
const incomeWords = ['salário', 'salario', 'recebi', 'entrada', 'pagamento', 'ganhei', 'pix recebido'];
const investmentWords = ['investi', 'investimento', 'fii', 'ações', 'crypto', 'etf', 'renda fixa', 'tesouro'];

if (incomeWords.some(w => textLower.includes(w))) {
  type = 'income';
} else if (investmentWords.some(w => textLower.includes(w))) {
  type = 'investment';
}

// 6. Categoria (nome) — termos mais específicos primeiro (ex: alimentação antes de ação)
const categoryMap = {
  'alimentação': 'Alimentação', 'alimentacao': 'Alimentação',
  'mercado': 'Mercado', 'supermercado': 'Mercado', 'feira': 'Mercado',
  'padaria': 'Alimentação', 'almoço': 'Alimentação', 'jantar': 'Alimentação', 'ifood': 'Alimentação',
  'uber': 'Transporte', '99': 'Transporte', 'gasolina': 'Transporte', 'posto': 'Transporte',
  'netflix': 'Assinaturas', 'spotify': 'Assinaturas', 'disney': 'Assinaturas',
  'farmacia': 'Saúde', 'remedio': 'Saúde', 'médico': 'Saúde',
  'fii': 'FII', 'ação': 'Ações', 'ações': 'Ações', 'crypto': 'Crypto',
  'salário': 'Salário'
};

let category = 'Outros';
for (const [keyword, cat] of Object.entries(categoryMap)) {
  if (textLower.includes(keyword)) {
    category = cat;
    break;
  }
}

// 7. category_id (UUID) - alinhado ao Supabase categories
const CATEGORY_IDS = {
  'Alimentação': '7bc7916f-578f-4892-8252-5fb009a811ab',
  'Assinaturas': 'fba057db-bec3-4aa9-bd88-6dadbb4d2d4d',
  'Casa': 'dcbb830d-d3fa-435a-89a8-8a7962e407cf',
  'Contas': '302ffea7-6c72-44e6-a142-565d6a8b3faa',
  'Cuidados pessoais': '839ba5f6-2460-43df-aa52-a14b90b18faa',
  'Educação': 'bab28650-1bb2-493a-856d-11266e591800',
  'Entretenimento': '57f5b107-729d-42ab-bc1e-ecf3b95d6987',
  'Impostos/Taxas': '277e1bc4-5061-4eca-913d-70d1076bce43',
  'Mercado': 'bd7e80b6-4dc1-489e-9cf8-bf81dd23107e',
  'Outros': 'bf891223-e65b-4a1d-83eb-5b541dc7e255',
  'Presentes': '2cb4cf5a-cac3-4196-aab8-ca1f16ac5206',
  'Roupas & Acessórios': 'a8560155-dbf2-46e6-bb3d-30d77ebefb29',
  'Saúde': '64408fbe-3225-462f-b4d2-d3b805a24c3b',
  'Transporte': 'd08f46e8-7cc8-47f9-b3cd-342b607b685f',
  'Freelance': 'e858b4a9-309d-4fe1-b8d7-d16f17fe5da9',
  'Rendimentos': '170f82e2-e40b-42a7-95c6-2c522f9f488f',
  'Salário': 'a7ba8c9d-bf97-4f1f-af2b-456965abadb0',
  'Ações': '043e25b2-63a1-49ea-9b3c-dfec2defa8e0',
  'Crypto': 'b343fe3d-9d4b-403a-84b5-4c0bdd05f8b5',
  'ETFs': '4de14bc4-d07b-446c-bb90-644c8f718e64',
  'FII': '0ba3e9a3-9521-4d46-a3e4-2eb96c149c2c',
  'Renda fixa': 'b3d1dcc2-7ad5-4143-a7f4-f8da47447ff9'
};

const OTHERS_BY_TYPE = {
  'expense': 'bf891223-e65b-4a1d-83eb-5b541dc7e255',
  'investment': 'b4179034-4596-47e8-8b83-a25fe28dc22f',
  'income': 'ee160689-998b-4034-9635-fcade99cfbb7'
};

let category_id = CATEGORY_IDS[category] || OTHERS_BY_TYPE[type] || OTHERS_BY_TYPE['expense'];

// 8. Método de Pagamento
let paymentMethod = 'pix';
if (textLower.includes('crédito') || textLower.includes('credito')) paymentMethod = 'credit';
if (textLower.includes('débito') || textLower.includes('debito')) paymentMethod = 'debit';
if (textLower.includes('dinheiro')) paymentMethod = 'cash';

// Retorno (inclui category_id para Supabase)
return {
  type,
  amount_brl: amount,
  category,
  category_id,
  payment_method: paymentMethod,
  description: text.substring(0, 200).replace(/["\\]/g, ''),
  source: 'whatsapp',
  raw_text: text,
  is_valid: amount !== null && amount > 0 && !isNaN(amount)
};
