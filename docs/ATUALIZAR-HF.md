# Como Atualizar o Arquivo no Hugging Face

## Você tem 2 opções:

### Opção 1: Upload via Interface (Mais Rápido)

1. Vá para o seu Space: https://huggingface.co/spaces/cydgxbriel/controle-financeiro
2. Clique em **"Files and versions"**
3. Clique no arquivo **`app.py`** (que já existe)
4. Clique em **"Edit"** (ícone de lápis no canto superior direito)
5. **Delete todo o conteúdo** e cole o novo conteúdo de `E:\Yugo\huggingface\app.py`
6. Escreva uma mensagem: "Fix Gradio 6.0 compatibility"
7. Clique em **"Commit changes to main"**

### Opção 2: Re-upload

1. Vá em **"Files and versions"**
2. Clique em **"Add file"** → **"Upload files"**
3. Selecione `E:\Yugo\huggingface\app.py` (vai substituir o existente)
4. Commit

---

## O que foi corrigido?

✅ Removido `retry_btn` e `undo_btn` (não existem mais no Gradio 6.0)
✅ Movido `theme` e `css` para o método `launch()`

Após o commit, o Space vai rebuildar automaticamente (~2 min).
