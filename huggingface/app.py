"""
Controle Financeiro - Interface Web + Chatbot
Alinhado com Lovable Dashboard (yugodinheiros)
Hugging Face Spaces com Gradio
"""

import gradio as gr
import os
import re
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime, date

# Load .env locally if present
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(os.path.dirname(current_dir), 'docs', '.env')
    load_dotenv(env_path)
except Exception:
    pass

# Configuração do Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_PUBLISHABLE_KEY", "")

supabase: Client = None

def init_supabase():
    global supabase
    if SUPABASE_URL and SUPABASE_KEY:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        return True
    return False

# =============================================
# PARSING INTELIGENTE (mesmo do n8n)
# =============================================

CATEGORY_KEYWORDS = {
    'expense': {
        'padaria': 'Alimentação', 'lanche': 'Alimentação', 'almoço': 'Alimentação',
        'almoco': 'Alimentação', 'jantar': 'Alimentação', 'café': 'Alimentação',
        'restaurante': 'Alimentação', 'ifood': 'Alimentação',
        'mercado': 'Mercado', 'supermercado': 'Mercado', 'feira': 'Mercado',
        'uber': 'Transporte', '99': 'Transporte', 'gasolina': 'Transporte',
        'combustível': 'Transporte', 'onibus': 'Transporte', 'metro': 'Transporte',
        'netflix': 'Assinaturas', 'spotify': 'Assinaturas', 'disney': 'Assinaturas',
        'amazon': 'Assinaturas', 'hbo': 'Assinaturas', 'youtube': 'Assinaturas',
        'farmacia': 'Saúde', 'farmácia': 'Saúde', 'remedio': 'Saúde',
        'remédio': 'Saúde', 'medico': 'Saúde', 'médico': 'Saúde',
        'luz': 'Contas', 'água': 'Contas', 'agua': 'Contas',
        'internet': 'Contas', 'telefone': 'Contas',
        'aluguel': 'Casa', 'condomínio': 'Casa', 'condominio': 'Casa'
    },
    'income': {
        'salário': 'Salário', 'salario': 'Salário',
        'freelance': 'Freelance', 'freela': 'Freelance',
        'rendimento': 'Rendimentos', 'dividendo': 'Rendimentos'
    },
    'investment': {
        'fii': 'FII', 'fundo imobiliário': 'FII',
        'ação': 'Ações', 'acao': 'Ações', 'ações': 'Ações', 'acoes': 'Ações',
        'crypto': 'Crypto', 'bitcoin': 'Crypto', 'ethereum': 'Crypto',
        'etf': 'ETFs', 'tesouro': 'Renda fixa', 'cdb': 'Renda fixa'
    }
}

INCOME_WORDS = ['salário', 'salario', 'recebi', 'entrada', 'pagamento', 'rendimento', 'ganhei']
INVESTMENT_WORDS = ['investi', 'investimento', 'fii', 'ação', 'acao', 'ações', 'acoes', 
                    'crypto', 'bitcoin', 'etf', 'tesouro', 'cdb', 'renda fixa']

def parse_transaction(text):
    """Parse inteligente de texto para transação"""
    text_lower = text.lower()
    
    # Extrair valor
    valor_match = re.search(r'r?\$?\s*(\d+(?:[.,]\d{1,2})?)', text_lower)
    amount = float(valor_match.group(1).replace(',', '.')) if valor_match else None
    
    # Identificar tipo
    trans_type = 'expense'  # Default
    if any(w in text_lower for w in INCOME_WORDS):
        trans_type = 'income'
    elif any(w in text_lower for w in INVESTMENT_WORDS):
        trans_type = 'investment'
    
    # Identificar payment_method
    payment_method = 'pix'  # Default
    if 'crédito' in text_lower or 'credito' in text_lower:
        payment_method = 'credit'
    elif 'débito' in text_lower or 'debito' in text_lower:
        payment_method = 'debit'
    elif 'dinheiro' in text_lower or 'cash' in text_lower:
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

# =============================================
# FUNÇÕES DO BANCO DE DADOS
# =============================================

def get_categories(trans_type=None):
    """Busca categorias do banco"""
    if not supabase:
        return []
    
    query = supabase.table("categories").select("*").eq("is_default", True)
    if trans_type:
        query = query.eq("type", trans_type)
    
    result = query.execute()
    return result.data if result.data else []

def add_transaction(data):
    """Adiciona transação"""
    if not supabase:
        return False, "Supabase não configurado"
    
    try:
        supabase.table("transactions").insert({
            "type": data['type'],
            "amount_brl": float(data['amount_brl']),
            "category": data['category'],
            "payment_method": data['payment_method'],
            "description": data.get('description', ''),
            "source": data.get('source', 'manual'),
            "raw_text": data.get('raw_text', '')
        }).execute()
        return True, f"✅ {type_emoji(data['type'])} R$ {data['amount_brl']:.2f} • {data['category']}"
    except Exception as e:
        return False, f"❌ Erro: {str(e)}"

def type_emoji(t):
    return {'income': '📥 Entrada', 'expense': '📤 Saída', 'investment': '📈 Investimento'}.get(t, t)

def get_transactions_today():
    """Busca transações de hoje"""
    if not supabase:
        return []
    
    today = date.today().isoformat()
    result = supabase.table("transactions")\
        .select("*")\
        .gte("date", f"{today}T00:00:00")\
        .order("created_at", desc=True)\
        .execute()
    
    return result.data if result.data else []

def get_monthly_summary():
    """Busca resumo do mês"""
    if not supabase:
        return {'income': 0, 'expense': 0, 'investment': 0}
    
    result = supabase.rpc("get_monthly_summary").execute()
    summary = {'income': 0, 'expense': 0, 'investment': 0}
    
    if result.data:
        for row in result.data:
            summary[row['type']] = float(row['total'] or 0)
    
    return summary

def get_balance():
    """Calcula saldo do mês"""
    summary = get_monthly_summary()
    return summary['income'] - summary['expense'] - summary['investment']

# =============================================
# CHATBOT
# =============================================

def chatbot_response(message, history):
    """Processa mensagem do chatbot"""
    msg_lower = message.lower()
    
    # Consultas
    if any(w in msg_lower for w in ['quanto', 'total', 'gastei', 'gasto', 'saldo']):
        if 'saldo' in msg_lower:
            balance = get_balance()
            emoji = '🟢' if balance >= 0 else '🔴'
            return f"{emoji} **Saldo do mês:** R$ {balance:.2f}"
        
        if 'semana' in msg_lower:
            if supabase:
                result = supabase.rpc("get_weekly_summary").execute()
                if result.data:
                    lines = ["📊 **Esta semana:**"]
                    for row in result.data:
                        lines.append(f"- {type_emoji(row['type'])}: R$ {float(row['total']):.2f}")
                    return "\n".join(lines)
            return "⚠️ Banco não configurado"
        
        # Mês (default)
        summary = get_monthly_summary()
        balance = summary['income'] - summary['expense'] - summary['investment']
        return f"""📊 **Este mês:**
- 📥 Entradas: R$ {summary['income']:.2f}
- 📤 Saídas: R$ {summary['expense']:.2f}
- 📈 Investimentos: R$ {summary['investment']:.2f}
- {'🟢' if balance >= 0 else '🔴'} **Saldo: R$ {balance:.2f}**"""
    
    # Registrar transação
    parsed = parse_transaction(message)
    if parsed['amount_brl'] and parsed['amount_brl'] > 0:
        success, msg = add_transaction(parsed)
        if success:
            return f"{msg}\n\n💡 Edite na aba 'Registrar' se precisar ajustar."
        return msg
    
    # Ajuda
    if 'ajuda' in msg_lower or 'help' in msg_lower:
        return """🤖 **Modo Ultra-Rápido**

📊 **Consultas:**
- "Quanto gastei esse mês?"
- "Qual meu saldo?"
- "Quanto gastei essa semana?"

💰 **Registrar (só digitar):**
- "25 mercado pix"
- "39,90 netflix crédito"
- "1000 fii"
- "5000 salário"

O tipo é detectado automaticamente!"""
    
    return "🤔 Não entendi. Digite **ajuda** ou tente: '50 almoço pix'"

# =============================================
# INTERFACE GRADIO (Mobile-First)
# =============================================

def create_interface():
    db_status = "🟢 Conectado" if init_supabase() else "🔴 Não configurado"
    
    with gr.Blocks(title="💰 Controle Financeiro"
    ) as app:
        
        gr.Markdown(f"# 💰 Controle Financeiro\n**{db_status}**")
        
        with gr.Tabs():
            # =============================================
            # TAB 1: HOME (Registro Rápido)
            # =============================================
            with gr.Tab("🏠 Inicio"):
                gr.Markdown("### Modo Ultra-Rápido")
                
                # Input principal
                quick_input = gr.Textbox(
                    label="",
                    placeholder="Digite: '25 mercado' ou '39,90 netflix crédito'",
                    elem_classes=["main-input"],
                    autofocus=True
                )
                
                # Chips de tipo
                gr.Markdown("**Tipo:**")
                with gr.Row():
                    btn_expense = gr.Button("📤 Saída", variant="primary", size="sm", elem_classes=["chip-btn"])
                    btn_income = gr.Button("📥 Entrada", size="sm", elem_classes=["chip-btn"])
                    btn_invest = gr.Button("📈 Invest", size="sm", elem_classes=["chip-btn"])
                
                selected_type = gr.State("expense")
                
                # Chips de pagamento
                gr.Markdown("**Pagamento:**")
                with gr.Row():
                    btn_pix = gr.Button("Pix", variant="primary", size="sm")
                    btn_credit = gr.Button("Crédito", size="sm")
                    btn_debit = gr.Button("Débito", size="sm")
                    btn_cash = gr.Button("Dinheiro", size="sm")
                
                selected_payment = gr.State("pix")
                
                # Botão salvar
                save_btn = gr.Button("💾 Salvar", variant="primary", size="lg")
                result_msg = gr.Markdown("")
                
                # Transações de hoje
                gr.Markdown("### 📅 Hoje")
                
                def format_today():
                    txs = get_transactions_today()
                    if not txs:
                        return "Nenhum registro hoje"
                    lines = []
                    for t in txs[:10]:
                        emoji = {'income': '📥', 'expense': '📤', 'investment': '📈'}.get(t['type'], '📦')
                        lines.append(f"{emoji} **R$ {t['amount_brl']:.2f}** • {t['category']} • {t['payment_method']}")
                    return "\n".join(lines)
                
                today_list = gr.Markdown(format_today())
                refresh_btn = gr.Button("🔄 Atualizar")
                
                # Handlers
                def on_type_select(t):
                    return t
                
                btn_expense.click(lambda: "expense", outputs=selected_type)
                btn_income.click(lambda: "income", outputs=selected_type)
                btn_invest.click(lambda: "investment", outputs=selected_type)
                
                btn_pix.click(lambda: "pix", outputs=selected_payment)
                btn_credit.click(lambda: "credit", outputs=selected_payment)
                btn_debit.click(lambda: "debit", outputs=selected_payment)
                btn_cash.click(lambda: "cash", outputs=selected_payment)
                
                def quick_save(text, trans_type, payment):
                    if not text.strip():
                        return "⚠️ Digite algo", format_today()
                    
                    parsed = parse_transaction(text)
                    parsed['type'] = trans_type
                    parsed['payment_method'] = payment
                    
                    if not parsed['amount_brl'] or parsed['amount_brl'] <= 0:
                        return "⚠️ Não encontrei o valor. Tente: '50 mercado'", format_today()
                    
                    success, msg = add_transaction(parsed)
                    return msg, format_today()
                
                save_btn.click(quick_save, [quick_input, selected_type, selected_payment], [result_msg, today_list])
                refresh_btn.click(format_today, outputs=today_list)
            
            # =============================================
            # TAB 2: CHATBOT
            # =============================================
            with gr.Tab("💬 Chat"):
                gr.ChatInterface(
                    chatbot_response,
                    chatbot=gr.Chatbot(height=350),
                    textbox=gr.Textbox(placeholder="Ex: 50 almoço pix", container=False),
                    examples=["Qual meu saldo?", "25 uber pix", "1000 fii", "ajuda"]
                )
            
            # =============================================
            # TAB 3: MÊS
            # =============================================
            with gr.Tab("📊 Mês"):
                gr.Markdown("### Resumo do Mês")
                
                def get_month_display():
                    summary = get_monthly_summary()
                    balance = summary['income'] - summary['expense'] - summary['investment']
                    emoji = '🟢' if balance >= 0 else '🔴'
                    
                    return f"""
| Tipo | Valor |
|------|-------|
| 📥 Entradas | R$ {summary['income']:.2f} |
| 📤 Saídas | R$ {summary['expense']:.2f} |
| 📈 Investimentos | R$ {summary['investment']:.2f} |
| {emoji} **Saldo** | **R$ {balance:.2f}** |
"""
                
                month_display = gr.Markdown(get_month_display())
                month_refresh = gr.Button("🔄 Atualizar")
                month_refresh.click(get_month_display, outputs=month_display)
        
        gr.Markdown("---\n💡 Use WhatsApp para registrar por áudio!")
    
    return app

if __name__ == "__main__":
    app = create_interface()
    app.launch(
        theme=gr.themes.Soft(primary_hue="indigo", secondary_hue="purple"),
        css="""
        .gradio-container { max-width: 500px !important; margin: auto; }
        .main-input input { font-size: 18px !important; padding: 15px !important; }
        .chip-btn { min-width: 80px !important; }
        """
    )
