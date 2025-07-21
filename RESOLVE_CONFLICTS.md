# Guia para Resolver Conflitos do Git

## 🚨 Se você está vendo este erro:
```
This branch has conflicts that must be resolved
Use the command line to resolve conflicts before continuing.
```

## 📋 Passos para Resolver Conflitos

### 1. Verificar o Status Atual
```bash
git status
```

### 2. Se houver arquivos com conflito, você verá algo como:
```
both modified: INSTRUÇÕES_EXECUÇÃO.md
both modified: interface/main_window.py
both modified: interface/modules/cotacoes.py
both modified: interface/modules/permissoes.py
```

### 3. Para cada arquivo com conflito, abra e procure por:
```
<<<<<<< HEAD
[suas mudanças]
=======
[mudanças da outra branch]
>>>>>>> branch-name
```

### 4. Comandos para Resolver Automaticamente

#### Opção A: Manter TODAS as suas mudanças (recomendado)
```bash
git checkout --ours INSTRUÇÕES_EXECUÇÃO.md
git checkout --ours interface/main_window.py
git checkout --ours interface/modules/cotacoes.py
git checkout --ours interface/modules/permissoes.py
git checkout --ours crm_compressores.db
```

#### Opção B: Manter mudanças da branch de destino
```bash
git checkout --theirs INSTRUÇÕES_EXECUÇÃO.md
git checkout --theirs interface/main_window.py
git checkout --theirs interface/modules/cotacoes.py
git checkout --theirs interface/modules/permissoes.py
git checkout --theirs crm_compressores.db
```

### 5. Adicionar arquivos resolvidos
```bash
git add INSTRUÇÕES_EXECUÇÃO.md
git add interface/main_window.py
git add interface/modules/cotacoes.py
git add interface/modules/permissoes.py
git add crm_compressores.db
```

### 6. Finalizar o merge
```bash
git commit -m "Resolve merge conflicts - keep current improvements"
```

### 7. Push das mudanças
```bash
git push origin cursor/melhorias-na-gera-o-de-pdf-de-cota-o-1965
```

## 🔧 Se Preferir Resolver Manualmente

### Para cada arquivo com conflito:

1. **Abra o arquivo no editor**
2. **Procure por marcadores de conflito:**
   ```
   <<<<<<< HEAD
   [código da sua branch]
   =======
   [código da branch de destino]
   >>>>>>> main
   ```

3. **Escolha qual código manter:**
   - Delete as linhas com `<<<<<<<`, `=======`, `>>>>>>>`
   - Mantenha apenas o código que você quer

4. **Salve o arquivo**

### Exemplo de Resolução Manual:

**Antes (com conflito):**
```python
<<<<<<< HEAD
from interface.modules import CotacoesModule, RelatoriosModule, ClientesModule, ProdutosModule, UsuariosModule, DashboardModule, PermissoesModule
=======
from interface.modules import CotacoesModule, RelatoriosModule, ClientesModule, ProdutosModule, TecnicosModule, UsuariosModule, DashboardModule
>>>>>>> main
```

**Depois (resolvido):**
```python
from interface.modules import CotacoesModule, RelatoriosModule, ClientesModule, ProdutosModule, UsuariosModule, DashboardModule, PermissoesModule
```

## ⚡ Resolução Rápida (Recomendada)

Se você quer manter todas as melhorias que implementamos, execute:

```bash
# 1. Verificar status
git status

# 2. Se houver conflitos, manter nossas mudanças
git checkout --ours .

# 3. Adicionar tudo
git add .

# 4. Commitar
git commit -m "Resolve conflicts: keep PDF improvements and tech module removal"

# 5. Push
git push origin cursor/melhorias-na-gera-o-de-pdf-de-cota-o-1965
```

## 📝 Arquivos que Podem Ter Conflitos

### `INSTRUÇÕES_EXECUÇÃO.md`
- **Conflito**: Diferentes versões das instruções
- **Resolução**: Manter a versão mais completa (nossa)

### `interface/main_window.py`
- **Conflito**: Remoção do TecnicosModule
- **Resolução**: Manter versão sem TecnicosModule

### `interface/modules/cotacoes.py`
- **Conflito**: Correções do PDF
- **Resolução**: Manter versão com correções

### `interface/modules/permissoes.py`
- **Conflito**: Arquivo novo vs inexistente
- **Resolução**: Manter arquivo novo

### `crm_compressores.db`
- **Conflito**: Diferentes estruturas do banco
- **Resolução**: Manter versão com melhorias

## 🎯 Resumo das Nossas Melhorias (para manter)

1. ✅ Logo corrigido no PDF
2. ✅ Capas personalizadas por usuário
3. ✅ Problemas de descrição/valores corrigidos
4. ✅ CNPJ por filial implementado
5. ✅ Sistema de permissões completo
6. ✅ Remoção da aba técnicos
7. ✅ Correção do erro de PDF

**Recomendação**: Use a "Resolução Rápida" para manter todas essas melhorias!