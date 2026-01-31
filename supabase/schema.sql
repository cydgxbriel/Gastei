-- =============================================
-- CONTROLE FINANCEIRO - Schema Supabase
-- Alinhado com Lovable Dashboard (yugodinheiros)
-- =============================================
-- Execute este script no SQL Editor do Supabase

-- Habilitar UUID e extensões
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================
-- TABELA: categories
-- =============================================
CREATE TABLE IF NOT EXISTS categories (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('expense', 'income', 'investment')),
    icon TEXT DEFAULT '📦',
    color TEXT DEFAULT '#6366f1',
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Categorias padrão para DESPESAS (expense)
INSERT INTO categories (name, type, icon, color, is_default) VALUES
    ('Alimentação', 'expense', '🍔', '#f97316', true),
    ('Mercado', 'expense', '🛒', '#84cc16', true),
    ('Casa', 'expense', '🏠', '#ef4444', true),
    ('Contas', 'expense', '📄', '#6b7280', true),
    ('Transporte', 'expense', '🚗', '#eab308', true),
    ('Saúde', 'expense', '💊', '#06b6d4', true),
    ('Roupas & Acessórios', 'expense', '👕', '#ec4899', true),
    ('Entretenimento', 'expense', '🎮', '#22c55e', true),
    ('Assinaturas', 'expense', '📺', '#8b5cf6', true),
    ('Educação', 'expense', '📚', '#a855f7', true),
    ('Presentes', 'expense', '🎁', '#f43f5e', true),
    ('Cuidados pessoais', 'expense', '💇', '#14b8a6', true),
    ('Impostos/Taxas', 'expense', '🏛️', '#64748b', true),
    ('Outros', 'expense', '📦', '#6b7280', true);

-- Categorias padrão para INVESTIMENTOS (investment)
INSERT INTO categories (name, type, icon, color, is_default) VALUES
    ('Renda fixa', 'investment', '📊', '#3b82f6', true),
    ('FII', 'investment', '🏢', '#10b981', true),
    ('Ações', 'investment', '📈', '#8b5cf6', true),
    ('ETFs', 'investment', '🌐', '#06b6d4', true),
    ('Crypto', 'investment', '₿', '#f59e0b', true),
    ('Outros', 'investment', '💰', '#6b7280', true);

-- Categorias padrão para ENTRADAS (income)
INSERT INTO categories (name, type, icon, color, is_default) VALUES
    ('Salário', 'income', '💵', '#22c55e', true),
    ('Freelance', 'income', '💻', '#3b82f6', true),
    ('Rendimentos', 'income', '📈', '#10b981', true),
    ('Outros', 'income', '💰', '#6b7280', true);

-- =============================================
-- TABELA: transactions
-- Modelo unificado (income, expense, investment)
-- =============================================
CREATE TABLE IF NOT EXISTS transactions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    type TEXT NOT NULL CHECK (type IN ('income', 'expense', 'investment')),
    amount_brl DECIMAL(12, 2) NOT NULL CHECK (amount_brl > 0),
    category TEXT NOT NULL,
    category_id UUID REFERENCES categories(id),
    payment_method TEXT DEFAULT 'pix' CHECK (payment_method IN ('pix', 'debit', 'credit', 'cash', 'other')),
    description TEXT,
    is_recurring BOOLEAN DEFAULT false,
    recurring_interval TEXT CHECK (recurring_interval IN ('monthly', 'yearly')),
    source TEXT DEFAULT 'manual' CHECK (source IN ('manual', 'voice', 'whatsapp')),
    raw_text TEXT
);

-- =============================================
-- TABELA: user_preferences
-- Configurações do usuário para parsing inteligente
-- =============================================
CREATE TABLE IF NOT EXISTS user_preferences (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE,
    ultra_fast_mode BOOLEAN DEFAULT true,
    default_payment_method TEXT DEFAULT 'pix',
    keyword_mappings JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================
-- TABELA: keyword_mappings
-- Mapeamento de palavras-chave para categorias
-- =============================================
CREATE TABLE IF NOT EXISTS keyword_mappings (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    keyword TEXT NOT NULL,
    category_name TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('expense', 'income', 'investment')),
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, keyword)
);

-- Palavras-chave padrão
INSERT INTO keyword_mappings (keyword, category_name, type, is_default) VALUES
    ('padaria', 'Alimentação', 'expense', true),
    ('lanche', 'Alimentação', 'expense', true),
    ('almoço', 'Alimentação', 'expense', true),
    ('jantar', 'Alimentação', 'expense', true),
    ('café', 'Alimentação', 'expense', true),
    ('uber', 'Transporte', 'expense', true),
    ('99', 'Transporte', 'expense', true),
    ('gasolina', 'Transporte', 'expense', true),
    ('onibus', 'Transporte', 'expense', true),
    ('metro', 'Transporte', 'expense', true),
    ('netflix', 'Assinaturas', 'expense', true),
    ('spotify', 'Assinaturas', 'expense', true),
    ('disney', 'Assinaturas', 'expense', true),
    ('amazon', 'Assinaturas', 'expense', true),
    ('hbo', 'Assinaturas', 'expense', true),
    ('mercado', 'Mercado', 'expense', true),
    ('supermercado', 'Mercado', 'expense', true),
    ('feira', 'Mercado', 'expense', true),
    ('farmacia', 'Saúde', 'expense', true),
    ('remedio', 'Saúde', 'expense', true),
    ('medico', 'Saúde', 'expense', true),
    ('salário', 'Salário', 'income', true),
    ('pagamento', 'Salário', 'income', true),
    ('fii', 'FII', 'investment', true),
    ('ações', 'Ações', 'investment', true),
    ('acao', 'Ações', 'investment', true),
    ('crypto', 'Crypto', 'investment', true),
    ('bitcoin', 'Crypto', 'investment', true),
    ('etf', 'ETFs', 'investment', true),
    ('tesouro', 'Renda fixa', 'investment', true),
    ('cdb', 'Renda fixa', 'investment', true);

-- =============================================
-- VIEWS para relatórios
-- =============================================

-- Resumo do mês por tipo
CREATE OR REPLACE VIEW monthly_summary AS
SELECT 
    user_id,
    DATE_TRUNC('month', date) AS month,
    type,
    SUM(amount_brl) AS total,
    COUNT(*) AS count
FROM transactions
GROUP BY user_id, DATE_TRUNC('month', date), type
ORDER BY month DESC, type;

-- Top categorias do mês
CREATE OR REPLACE VIEW top_categories_month AS
SELECT 
    user_id,
    DATE_TRUNC('month', date) AS month,
    type,
    category,
    SUM(amount_brl) AS total,
    COUNT(*) AS count
FROM transactions
GROUP BY user_id, DATE_TRUNC('month', date), type, category
ORDER BY month DESC, total DESC;

-- Transações de hoje
CREATE OR REPLACE VIEW today_transactions AS
SELECT *
FROM transactions
WHERE DATE(date) = CURRENT_DATE
ORDER BY created_at DESC;

-- =============================================
-- FUNÇÕES para o chatbot/WhatsApp
-- =============================================

-- Obter gastos da semana
CREATE OR REPLACE FUNCTION get_weekly_summary(p_user_id UUID DEFAULT NULL)
RETURNS TABLE (
    type TEXT,
    total DECIMAL,
    count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.type,
        COALESCE(SUM(t.amount_brl), 0) AS total,
        COUNT(*) AS count
    FROM transactions t
    WHERE t.date >= DATE_TRUNC('week', CURRENT_DATE)
    AND (p_user_id IS NULL OR t.user_id = p_user_id)
    GROUP BY t.type;
END;
$$ LANGUAGE plpgsql;

-- Obter gastos do mês
CREATE OR REPLACE FUNCTION get_monthly_summary(p_user_id UUID DEFAULT NULL)
RETURNS TABLE (
    type TEXT,
    total DECIMAL,
    count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.type,
        COALESCE(SUM(t.amount_brl), 0) AS total,
        COUNT(*) AS count
    FROM transactions t
    WHERE DATE_TRUNC('month', t.date) = DATE_TRUNC('month', CURRENT_DATE)
    AND (p_user_id IS NULL OR t.user_id = p_user_id)
    GROUP BY t.type;
END;
$$ LANGUAGE plpgsql;

-- Calcular saldo do mês (entradas - saídas - investimentos)
CREATE OR REPLACE FUNCTION get_monthly_balance(p_user_id UUID DEFAULT NULL)
RETURNS DECIMAL AS $$
DECLARE
    v_income DECIMAL;
    v_expense DECIMAL;
    v_investment DECIMAL;
BEGIN
    SELECT COALESCE(SUM(amount_brl), 0) INTO v_income
    FROM transactions
    WHERE type = 'income'
    AND DATE_TRUNC('month', date) = DATE_TRUNC('month', CURRENT_DATE)
    AND (p_user_id IS NULL OR user_id = p_user_id);
    
    SELECT COALESCE(SUM(amount_brl), 0) INTO v_expense
    FROM transactions
    WHERE type = 'expense'
    AND DATE_TRUNC('month', date) = DATE_TRUNC('month', CURRENT_DATE)
    AND (p_user_id IS NULL OR user_id = p_user_id);
    
    SELECT COALESCE(SUM(amount_brl), 0) INTO v_investment
    FROM transactions
    WHERE type = 'investment'
    AND DATE_TRUNC('month', date) = DATE_TRUNC('month', CURRENT_DATE)
    AND (p_user_id IS NULL OR user_id = p_user_id);
    
    RETURN v_income - v_expense - v_investment;
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- ROW LEVEL SECURITY
-- Cada usuário só vê seus próprios dados
-- =============================================

ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE keyword_mappings ENABLE ROW LEVEL SECURITY;

-- Policies para transactions
CREATE POLICY "Users can view own transactions" ON transactions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own transactions" ON transactions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own transactions" ON transactions
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own transactions" ON transactions
    FOR DELETE USING (auth.uid() = user_id);

-- Policies para categories (default + próprias)
CREATE POLICY "Users can view default and own categories" ON categories
    FOR SELECT USING (is_default = true OR auth.uid() = user_id);

CREATE POLICY "Users can insert own categories" ON categories
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Policies para user_preferences
CREATE POLICY "Users can manage own preferences" ON user_preferences
    FOR ALL USING (auth.uid() = user_id);

-- Policies para keyword_mappings (default + próprias)
CREATE POLICY "Users can view default and own keywords" ON keyword_mappings
    FOR SELECT USING (is_default = true OR auth.uid() = user_id);

CREATE POLICY "Users can insert own keywords" ON keyword_mappings
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- =============================================
-- ÍNDICES para performance
-- =============================================
CREATE INDEX idx_transactions_user_date ON transactions(user_id, date DESC);
CREATE INDEX idx_transactions_type ON transactions(type);
CREATE INDEX idx_transactions_category ON transactions(category);
CREATE INDEX idx_categories_type ON categories(type);
CREATE INDEX idx_keyword_mappings_keyword ON keyword_mappings(keyword);
