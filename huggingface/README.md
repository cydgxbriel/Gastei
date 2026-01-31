---
title: Controle Financeiro
emoji: 💰
colorFrom: indigo
colorTo: purple
sdk: gradio
sdk_version: 5.9.1
app_file: app.py
pinned: false
license: mit
short_description: Controle de gastos pessoais via chat
---

# Controle Financeiro

Aplicativo de controle de gastos pessoais com interface intuitiva.

## Funcionalidades

- **Registro Rapido**: Digite "25 mercado" e salve
- **Chat Inteligente**: Pergunte "quanto gastei?" ou registre gastos
- **Resumo Mensal**: Veja entradas, saidas e saldo

## Configuracao

### 1. Secrets (Obrigatorio)

Adicione os seguintes Secrets no seu Space:

| Secret | Descricao |
|--------|-----------|
| `SUPABASE_URL` | URL do seu projeto Supabase |
| `SUPABASE_KEY` | Chave publica (anon key) do Supabase |

### 2. Como adicionar Secrets

1. Acesse seu Space
2. Va em **Settings** > **Repository secrets**
3. Clique em **New secret**
4. Adicione `SUPABASE_URL` e `SUPABASE_KEY`

## Exemplos de Uso

### Registrar Gastos
```
25 mercado
39,90 netflix credito
100 uber pix
1000 fii
5000 salario
```

### Consultas
```
Quanto gastei?
Qual meu saldo?
Resumo da semana
```

## Integracao WhatsApp

Este app funciona junto com workflows n8n para receber gastos via WhatsApp.

## Stack

- **Frontend**: Gradio
- **Backend**: Supabase (PostgreSQL)
- **Automacao**: n8n
