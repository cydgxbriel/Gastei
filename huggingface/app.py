"""
Controle Financeiro - Interface Web + Chatbot
Hugging Face Spaces com Gradio

Para configurar no HF Spaces, adicione os Secrets:
- SUPABASE_URL
- SUPABASE_SERVICE_ROLE_KEY (recomendado) ou SUPABASE_KEY (service_role para ignorar RLS)
- DEFAULT_USER_ID (UUID do usuario no Supabase Auth)
"""

import gradio as gr
import os
import re
import logging
import requests
from datetime import datetime, date
from typing import Optional, Dict, Any, List, Tuple

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tentar carregar .env local
try:
    from dotenv import load_dotenv
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env_paths = [
        os.path.join(current_dir, '.env'),
        os.path.join(os.path.dirname(current_dir), 'docs', '.env')
    ]
    for env_path in env_paths:
        if os.path.exists(env_path):
            load_dotenv(env_path)
            break
except ImportError:
    pass


# =============================================================================
# CONFIGURACAO
# =============================================================================

class Config:
    SUPABASE_URL: str = os.environ.get("SUPABASE_URL", "").strip()
    SUPABASE_KEY: str = (
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or os.environ.get("SUPABASE_KEY")
        or os.environ.get("SUPABASE_PUBLISHABLE_KEY", "")
    ).strip().replace("\n", "").replace(" ", "")
    # User ID fixo para app single-user (pegar do Supabase Dashboard > Authentication > Users)
    DEFAULT_USER_ID: str = os.environ.get("DEFAULT_USER_ID", "").strip()

    @classmethod
    def is_configured(cls) -> bool:
        return bool(cls.SUPABASE_URL and cls.SUPABASE_KEY)


# =============================================================================
# SUPABASE REST CLIENT (HTTP/1.1)
# =============================================================================

class SupabaseRest:
    """Cliente REST simples para Supabase usando requests (HTTP/1.1)"""

    @classmethod
    def _headers(cls) -> Dict[str, str]:
        return {
            "apikey": Config.SUPABASE_KEY,
            "Authorization": f"Bearer {Config.SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }

    @classmethod
    def _base_url(cls) -> str:
        return f"{Config.SUPABASE_URL}/rest/v1"

    @classmethod
    def insert(cls, table: str, data: Dict) -> Tuple[bool, str]:
        """Insere registro na tabela"""
        try:
            url = f"{cls._base_url()}/{table}"
            response = requests.post(url, json=data, headers=cls._headers(), timeout=10)
            if response.status_code in [200, 201]:
                return True, "OK"
            else:
                return False, f"HTTP {response.status_code}: {response.text[:100]}"
        except Exception as e:
            return False, str(e)

    @classmethod
    def select(cls, table: str, params: Dict = None) -> List[Dict]:
        """Busca registros da tabela"""
        try:
            url = f"{cls._base_url()}/{table}"
            response = requests.get(url, params=params, headers=cls._headers(), timeout=10)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            logger.error(f"Select error: {e}")
            return []

    @classmethod
    def rpc(cls, function: str, params: Dict = None) -> List[Dict]:
        """Chama funcao RPC do Supabase"""
        try:
            url = f"{cls._base_url()}/rpc/{function}"
            response = requests.post(url, json=params or {}, headers=cls._headers(), timeout=10)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            logger.error(f"RPC error: {e}")
            return []


# =============================================================================
# PARSING INTELIGENTE
# =============================================================================

# Mapeamento de categoria -> ID (do Supabase)
CATEGORY_IDS = {
    # Expense
    ('Alimentação', 'expense'): '7bc7916f-578f-4892-8252-5fb009a811ab',
    ('Mercado', 'expense'): 'bd7e80b6-4dc1-489e-9cf8-bf81dd23107e',
    ('Casa', 'expense'): 'dcbb830d-d3fa-435a-89a8-8a7962e407cf',
    ('Contas', 'expense'): '302ffea7-6c72-44e6-a142-565d6a8b3faa',
    ('Transporte', 'expense'): 'd08f46e8-7cc8-47f9-b3cd-342b607b685f',
    ('Saúde', 'expense'): '64408fbe-3225-462f-b4d2-d3b805a24c3b',
    ('Roupas & Acessórios', 'expense'): 'a8560155-dbf2-46e6-bb3d-30d77ebefb29',
    ('Entretenimento', 'expense'): '57f5b107-729d-42ab-bc1e-ecf3b95d6987',
    ('Assinaturas', 'expense'): 'fba057db-bec3-4aa9-bd88-6dadbb4d2d4d',
    ('Educação', 'expense'): 'bab28650-1bb2-493a-856d-11266e591800',
    ('Presentes', 'expense'): '2cb4cf5a-cac3-4196-aab8-ca1f16ac5206',
    ('Cuidados pessoais', 'expense'): '839ba5f6-2460-43df-aa52-a14b90b18faa',
    ('Impostos/Taxas', 'expense'): '277e1bc4-5061-4eca-913d-70d1076bce43',
    ('Outros', 'expense'): 'bf891223-e65b-4a1d-83eb-5b541dc7e255',
    # Investment
    ('Renda fixa', 'investment'): 'b3d1dcc2-7ad5-4143-a7f4-f8da47447ff9',
    ('FII', 'investment'): '0ba3e9a3-9521-4d46-a3e4-2eb96c149c2c',
    ('Ações', 'investment'): '043e25b2-63a1-49ea-9b3c-dfec2defa8e0',
    ('ETFs', 'investment'): '4de14bc4-d07b-446c-bb90-644c8f718e64',
    ('Crypto', 'investment'): 'b343fe3d-9d4b-403a-84b5-4c0bdd05f8b5',
    ('Outros', 'investment'): 'b4179034-4596-47e8-8b83-a25fe28dc22f',
    # Income
    ('Salário', 'income'): 'a7ba8c9d-bf97-4f1f-af2b-456965abadb0',
    ('Freelance', 'income'): 'e858b4a9-309d-4fe1-b8d7-d16f17fe5da9',
    ('Rendimentos', 'income'): '170f82e2-e40b-42a7-95c6-2c522f9f488f',
    ('Outros', 'income'): 'ee160689-998b-4034-9635-fcade99cfbb7',
}

CATEGORY_KEYWORDS = {
    'expense': {
        'padaria': 'Alimentação', 'lanche': 'Alimentação', 'almoco': 'Alimentação',
        'almoço': 'Alimentação', 'jantar': 'Alimentação', 'cafe': 'Alimentação',
        'café': 'Alimentação', 'restaurante': 'Alimentação', 'ifood': 'Alimentação',
        'rappi': 'Alimentação', 'pizza': 'Alimentação', 'hamburguer': 'Alimentação',
        'mercado': 'Mercado', 'supermercado': 'Mercado', 'feira': 'Mercado',
        'hortifruti': 'Mercado', 'acougue': 'Mercado',
        'uber': 'Transporte', '99': 'Transporte', 'gasolina': 'Transporte',
        'combustivel': 'Transporte', 'combustível': 'Transporte',
        'onibus': 'Transporte', 'metro': 'Transporte', 'estacionamento': 'Transporte',
        'netflix': 'Assinaturas', 'spotify': 'Assinaturas', 'disney': 'Assinaturas',
        'amazon': 'Assinaturas', 'hbo': 'Assinaturas', 'youtube': 'Assinaturas',
        'prime': 'Assinaturas', 'globoplay': 'Assinaturas',
        'farmacia': 'Saúde', 'farmácia': 'Saúde', 'remedio': 'Saúde',
        'remédio': 'Saúde', 'medico': 'Saúde', 'médico': 'Saúde',
        'hospital': 'Saúde', 'dentista': 'Saúde', 'exame': 'Saúde',
        'luz': 'Contas', 'agua': 'Contas', 'água': 'Contas',
        'internet': 'Contas', 'telefone': 'Contas', 'celular': 'Contas',
        'energia': 'Contas', 'gas': 'Contas', 'gás': 'Contas',
        'aluguel': 'Casa', 'condominio': 'Casa', 'condomínio': 'Casa',
        'iptu': 'Casa', 'seguro': 'Casa',
        'cinema': 'Entretenimento', 'show': 'Entretenimento', 'teatro': 'Entretenimento',
        'bar': 'Entretenimento', 'balada': 'Entretenimento', 'festa': 'Entretenimento',
        'curso': 'Educação', 'livro': 'Educação', 'escola': 'Educação',
        'faculdade': 'Educação', 'mensalidade': 'Educação',
        'roupa': 'Roupas & Acessórios', 'tenis': 'Roupas & Acessórios', 'sapato': 'Roupas & Acessórios',
        'camisa': 'Roupas & Acessórios', 'calca': 'Roupas & Acessórios',
    },
    'income': {
        'salario': 'Salário', 'salário': 'Salário',
        'freelance': 'Freelance', 'freela': 'Freelance',
        'rendimento': 'Rendimentos', 'dividendo': 'Rendimentos',
        'bonus': 'Salário', 'bônus': 'Salário',
        '13': 'Salário', 'decimo': 'Salário',
        'ferias': 'Salário', 'férias': 'Salário',
    },
    'investment': {
        'fii': 'FII', 'fundo imobiliario': 'FII', 'fundo imobiliário': 'FII',
        'acao': 'Ações', 'ação': 'Ações', 'acoes': 'Ações', 'ações': 'Ações',
        'crypto': 'Crypto', 'bitcoin': 'Crypto', 'ethereum': 'Crypto', 'btc': 'Crypto',
        'etf': 'ETFs', 'tesouro': 'Renda fixa', 'cdb': 'Renda fixa',
        'lci': 'Renda fixa', 'lca': 'Renda fixa', 'poupanca': 'Renda fixa',
    }
}

INCOME_WORDS = ['salario', 'salário', 'recebi', 'entrada', 'pagamento',
                'rendimento', 'ganhei', 'bonus', 'bônus', 'ferias', 'férias']
INVESTMENT_WORDS = ['investi', 'investimento', 'aporte', 'apliquei', 'aplicacao',
                    'fii', 'acao', 'ação', 'acoes', 'ações', 'crypto', 'bitcoin',
                    'etf', 'tesouro', 'cdb', 'lci', 'lca']


def parse_transaction(text: str) -> Dict[str, Any]:
    """Parse inteligente de texto para transacao"""
    text_lower = text.lower().strip()

    # Extrair valor
    patterns = [
        r'r\$\s*(\d+(?:[.,]\d{1,2})?)',
        r'(\d+(?:[.,]\d{1,2})?)\s*(?:reais|real)',
        r'(\d+(?:[.,]\d{1,2})?)',
    ]

    amount = None
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            amount = float(match.group(1).replace(',', '.'))
            break

    # Identificar tipo
    trans_type = 'expense'
    if any(w in text_lower for w in INCOME_WORDS):
        trans_type = 'income'
    elif any(w in text_lower for w in INVESTMENT_WORDS):
        trans_type = 'investment'

    # Identificar payment_method
    payment_method = 'pix'
    if 'credito' in text_lower or 'crédito' in text_lower:
        payment_method = 'credit'
    elif 'debito' in text_lower or 'débito' in text_lower:
        payment_method = 'debit'
    elif 'dinheiro' in text_lower or 'cash' in text_lower or 'especie' in text_lower:
        payment_method = 'cash'

    # Encontrar categoria
    category = 'Outros'
    type_keywords = CATEGORY_KEYWORDS.get(trans_type, CATEGORY_KEYWORDS['expense'])
    for keyword, cat in type_keywords.items():
        if keyword in text_lower:
            category = cat
            break

    return {
        'amount_brl': amount,
        'type': trans_type,
        'category': category,
        'payment_method': payment_method,
        'description': text[:200],
        'raw_text': text,
        'source': 'manual'
    }


# =============================================================================
# FUNCOES DO BANCO
# =============================================================================

def add_transaction(data: Dict[str, Any]) -> Tuple[bool, str]:
    """Adiciona transacao ao banco"""
    if not Config.is_configured():
        return False, "Banco nao configurado"

    if not Config.DEFAULT_USER_ID:
        return False, "DEFAULT_USER_ID nao configurado"

    # Buscar category_id pelo nome e tipo
    category_name = data['category']
    trans_type = data['type']
    category_id = CATEGORY_IDS.get((category_name, trans_type))

    # Fallback para "Outros" do tipo correspondente
    if not category_id:
        category_id = CATEGORY_IDS.get(('Outros', trans_type))

    success, msg = SupabaseRest.insert("transactions", {
        "user_id": Config.DEFAULT_USER_ID,
        "type": trans_type,
        "amount_brl": float(data['amount_brl']),
        "category_id": category_id,
        "payment_method": data['payment_method'],
        "description": data.get('description', ''),
        "source": data.get('source', 'manual'),
        "raw_text": data.get('raw_text', '')
    })

    if success:
        emoji = {'income': '📥', 'expense': '📤', 'investment': '📈'}.get(trans_type, '📦')
        return True, f"{emoji} R$ {data['amount_brl']:.2f} - {category_name}"
    return False, f"Erro: {msg}"


def get_transactions_today() -> List[Dict]:
    """Busca transacoes de hoje"""
    if not Config.is_configured():
        return []

    today = date.today().isoformat()
    params = {
        "select": "*",
        "date": f"gte.{today}T00:00:00",
        "order": "created_at.desc",
        "limit": "15"
    }
    return SupabaseRest.select("transactions", params)


def get_monthly_summary() -> Dict[str, float]:
    """Busca resumo do mes"""
    summary = {'income': 0.0, 'expense': 0.0, 'investment': 0.0}

    if not Config.is_configured():
        return summary

    data = SupabaseRest.rpc("get_monthly_summary")
    if data:
        for row in data:
            if row.get('type') in summary:
                summary[row['type']] = float(row.get('total') or 0)

    return summary


def get_weekly_summary() -> List[Dict]:
    """Busca resumo da semana"""
    if not Config.is_configured():
        return []
    return SupabaseRest.rpc("get_weekly_summary")


# =============================================================================
# CHATBOT
# =============================================================================

def chatbot_response(message: str, history: List = None) -> str:
    """Processa mensagem do chatbot"""
    if history is None:
        history = []
    msg_lower = message.lower().strip()

    if not msg_lower:
        return "Digite algo para comecar!"

    # Consultas
    if any(w in msg_lower for w in ['quanto', 'total', 'gastei', 'gasto', 'saldo', 'resumo']):
        if 'saldo' in msg_lower:
            summary = get_monthly_summary()
            balance = summary['income'] - summary['expense'] - summary['investment']
            emoji = '🟢' if balance >= 0 else '🔴'
            return f"{emoji} **Saldo do mes:** R$ {balance:.2f}"

        if 'semana' in msg_lower:
            data = get_weekly_summary()
            if data:
                lines = ["📊 **Esta semana:**"]
                for row in data:
                    emoji = {'income': '📥', 'expense': '📤', 'investment': '📈'}.get(row['type'], '📦')
                    lines.append(f"- {emoji} {row['type']}: R$ {float(row['total']):.2f}")
                return "\n".join(lines)
            return "Sem dados da semana"

        summary = get_monthly_summary()
        balance = summary['income'] - summary['expense'] - summary['investment']
        emoji = '🟢' if balance >= 0 else '🔴'
        return f"""📊 **Este mes:**
- 📥 Entradas: R$ {summary['income']:.2f}
- 📤 Saidas: R$ {summary['expense']:.2f}
- 📈 Investimentos: R$ {summary['investment']:.2f}
- {emoji} **Saldo: R$ {balance:.2f}**"""

    # Registrar transacao
    parsed = parse_transaction(message)
    if parsed['amount_brl'] and parsed['amount_brl'] > 0:
        success, msg = add_transaction(parsed)
        if success:
            return f"{msg}\n\n💡 Use a aba 'Inicio' para ajustar tipo/pagamento"
        return f"❌ {msg}"

    # Ajuda
    if 'ajuda' in msg_lower or 'help' in msg_lower or msg_lower == '?':
        return """🤖 **Como usar:**

📊 **Consultas:**
- "Quanto gastei esse mes?"
- "Qual meu saldo?"
- "Resumo da semana"

💰 **Registrar:**
- "25 mercado"
- "39,90 netflix credito"
- "1000 fii"
- "5000 salario"

O tipo e detectado automaticamente!"""

    return "🤔 Nao entendi. Digite **ajuda** ou tente: '50 almoco pix'"


# =============================================================================
# INTERFACE GRADIO
# =============================================================================

CUSTOM_CSS = """
.gradio-container { max-width: 600px !important; margin: auto; }
.main-input input { font-size: 18px !important; padding: 16px !important; border-radius: 12px !important; }
.chip-btn { min-width: 90px !important; border-radius: 20px !important; }
.status-connected { color: #22c55e; font-weight: bold; }
.status-disconnected { color: #ef4444; font-weight: bold; }
footer { display: none !important; }
"""


def create_interface() -> gr.Blocks:
    """Cria interface Gradio"""
    connected = Config.is_configured()
    has_user = bool(Config.DEFAULT_USER_ID)

    if connected and has_user:
        status_text = "🟢 Conectado ao Supabase"
        status_class = "status-connected"
    elif connected and not has_user:
        status_text = "🟡 Falta DEFAULT_USER_ID nos Secrets"
        status_class = "status-disconnected"
    else:
        status_text = "🔴 Configure SUPABASE_URL e SUPABASE_KEY nos Secrets"
        status_class = "status-disconnected"

    with gr.Blocks(
        title="💰 Controle Financeiro",
        theme=gr.themes.Soft(primary_hue="indigo", secondary_hue="purple"),
        css=CUSTOM_CSS
    ) as app:

        gr.Markdown(f"# 💰 Controle Financeiro")
        gr.Markdown(f"<p class='{status_class}'>{status_text}</p>")

        with gr.Tabs():
            # TAB 1: INICIO
            with gr.Tab("🏠 Inicio"):
                gr.Markdown("### Registro Rapido")

                quick_input = gr.Textbox(
                    label="",
                    placeholder="Ex: 25 mercado, 39.90 netflix, 100 uber",
                    elem_classes=["main-input"],
                    autofocus=True
                )

                gr.Markdown("**Tipo:**")
                with gr.Row():
                    btn_expense = gr.Button("📤 Saida", variant="primary", size="sm", elem_classes=["chip-btn"])
                    btn_income = gr.Button("📥 Entrada", size="sm", elem_classes=["chip-btn"])
                    btn_invest = gr.Button("📈 Invest", size="sm", elem_classes=["chip-btn"])

                selected_type = gr.State("expense")
                type_display = gr.Markdown("**Selecionado:** 📤 Saida")

                gr.Markdown("**Pagamento:**")
                with gr.Row():
                    btn_pix = gr.Button("Pix", variant="primary", size="sm")
                    btn_credit = gr.Button("Credito", size="sm")
                    btn_debit = gr.Button("Debito", size="sm")
                    btn_cash = gr.Button("Dinheiro", size="sm")

                selected_payment = gr.State("pix")
                payment_display = gr.Markdown("**Pagamento:** Pix")

                save_btn = gr.Button("💾 Salvar", variant="primary", size="lg")
                result_msg = gr.Markdown("")

                gr.Markdown("---")
                gr.Markdown("### 📅 Hoje")

                def format_today_list() -> str:
                    txs = get_transactions_today()
                    if not txs:
                        return "_Nenhum registro hoje_"
                    lines = []
                    for t in txs[:10]:
                        emoji = {'income': '📥', 'expense': '📤', 'investment': '📈'}.get(t.get('type'), '📦')
                        amt = t.get('amount_brl', 0)
                        cat = t.get('category', '-')
                        pay = t.get('payment_method', '-')
                        lines.append(f"{emoji} **R$ {amt:.2f}** - {cat} ({pay})")
                    return "\n".join(lines)

                today_list = gr.Markdown(format_today_list())
                refresh_btn = gr.Button("🔄 Atualizar")

                # Handlers - Tipo
                def select_expense():
                    return "expense", "**Selecionado:** 📤 Saida"
                def select_income():
                    return "income", "**Selecionado:** 📥 Entrada"
                def select_invest():
                    return "investment", "**Selecionado:** 📈 Investimento"

                btn_expense.click(select_expense, outputs=[selected_type, type_display])
                btn_income.click(select_income, outputs=[selected_type, type_display])
                btn_invest.click(select_invest, outputs=[selected_type, type_display])

                # Handlers - Pagamento
                def select_pix():
                    return "pix", "**Pagamento:** Pix"
                def select_credit():
                    return "credit", "**Pagamento:** Credito"
                def select_debit():
                    return "debit", "**Pagamento:** Debito"
                def select_cash():
                    return "cash", "**Pagamento:** Dinheiro"

                btn_pix.click(select_pix, outputs=[selected_payment, payment_display])
                btn_credit.click(select_credit, outputs=[selected_payment, payment_display])
                btn_debit.click(select_debit, outputs=[selected_payment, payment_display])
                btn_cash.click(select_cash, outputs=[selected_payment, payment_display])

                # Salvar
                def quick_save(text: str, trans_type: str, payment: str):
                    if not text.strip():
                        return "⚠️ Digite algo", format_today_list()

                    parsed = parse_transaction(text)
                    parsed['type'] = trans_type
                    parsed['payment_method'] = payment

                    if not parsed['amount_brl'] or parsed['amount_brl'] <= 0:
                        return "⚠️ Nao encontrei o valor. Ex: '50 mercado'", format_today_list()

                    success, msg = add_transaction(parsed)
                    status = f"✅ {msg}" if success else f"❌ {msg}"
                    return status, format_today_list()

                save_btn.click(quick_save, [quick_input, selected_type, selected_payment], [result_msg, today_list])
                quick_input.submit(quick_save, [quick_input, selected_type, selected_payment], [result_msg, today_list])
                refresh_btn.click(format_today_list, outputs=today_list)

            # TAB 2: CHATBOT
            with gr.Tab("💬 Chat"):
                gr.ChatInterface(
                    chatbot_response,
                    type="messages",
                    examples=["Qual meu saldo?", "Quanto gastei?", "25 uber pix", "ajuda"],
                )

            # TAB 3: MES
            with gr.Tab("📊 Mes"):
                gr.Markdown("### Resumo Mensal")

                def get_month_display() -> str:
                    summary = get_monthly_summary()
                    balance = summary['income'] - summary['expense'] - summary['investment']
                    emoji = '🟢' if balance >= 0 else '🔴'
                    return f"""
| Tipo | Valor |
|------|-------|
| 📥 Entradas | R$ {summary['income']:.2f} |
| 📤 Saidas | R$ {summary['expense']:.2f} |
| 📈 Investimentos | R$ {summary['investment']:.2f} |
| {emoji} **Saldo** | **R$ {balance:.2f}** |
"""

                month_display = gr.Markdown(get_month_display())
                month_refresh = gr.Button("🔄 Atualizar")
                month_refresh.click(get_month_display, outputs=month_display)

        gr.Markdown("---")
        gr.Markdown("_💡 Registre pelo WhatsApp enviando audio ou texto!_")

    return app


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    app = create_interface()
    app.launch()
