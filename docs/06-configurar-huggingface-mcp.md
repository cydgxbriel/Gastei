# Configurar MCP do Hugging Face no Cursor

O agente MCP do Hugging Face foi adicionado ao Cursor. Para ativar e usar, siga os passos abaixo.

## 1. Obter URL e token do MCP

1. Acesse **[Hugging Face → Settings → MCP](https://huggingface.co/settings/mcp)**.
2. Faça login na sua conta (ou crie uma).
3. Na página de MCP, **ative o acesso** e copie:
   - **URL do endpoint MCP** (se fornecida)
   - **Token de acesso** (tipo `hf_...`).

Se a página só mostrar o token, use:

- **URL:** `https://huggingface.co/mcp` (padrão oficial).
- **Token:** o valor que aparecer na tela (ex.: `hf_xxxxxxxxxxxx`).

## 2. Configurar no Cursor

O arquivo de configuração do MCP no Cursor é:

- **Linux/WSL:** `~/.cursor/mcp.json`

Edite o bloco do servidor `huggingface` e substitua o placeholder pelo seu token:

```json
"huggingface": {
  "type": "http",
  "url": "https://huggingface.co/mcp",
  "headers": {
    "Authorization": "Bearer hf_SEU_TOKEN_REAL_AQUI"
  }
}
```

Se o Hugging Face mostrar uma URL diferente na página de MCP, use essa URL no campo `"url"` em vez de `https://huggingface.co/mcp`.

## 3. Reiniciar o Cursor

Depois de salvar o `mcp.json`:

1. Feche e abra de novo o Cursor, ou
2. Recarregue a janela: **Ctrl+Shift+P** → “Developer: Reload Window”.

## 4. O que o MCP do Hugging Face oferece

Com o MCP configurado, o assistente no Cursor pode usar o Hugging Face para:

- Busca semântica em **Spaces** e **Papers**
- Explorar **datasets** e **modelos**
- Acessar **Spaces com ferramentas MCP compatíveis** (incluindo Gradio)

## Referência

- [Hugging Face – MCP (lista oficial de servidores MCP)](https://github.com/modelcontextprotocol/servers#-official-integrations)
- [Configuração MCP no Hugging Face](https://huggingface.co/settings/mcp)
