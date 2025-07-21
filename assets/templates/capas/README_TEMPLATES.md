# Templates de Capa em JPEG

## 📍 LOCALIZAÇÃO DOS TEMPLATES

**IMPORTANTE**: Adicione os 4 arquivos JPEG EXATAMENTE neste diretório:
```
/workspace/assets/templates/capas/
```

## 📋 Arquivos Necessários

Adicione os seguintes arquivos JPEG neste diretório:

1. **capa_valdir.jpg** - Template personalizado para Valdir
2. **capa_vagner.jpg** - Template personalizado para Vagner Cerqueira  
3. **capa_rogerio.jpg** - Template personalizado para Rogério Cerqueira
4. **capa_raquel.jpg** - Template personalizado para Raquel

### 📂 Estrutura Final:
```
/workspace/assets/templates/capas/
├── capa_valdir.jpg
├── capa_vagner.jpg  
├── capa_rogerio.jpg
├── capa_raquel.jpg
└── README_TEMPLATES.md (este arquivo)
```

## 📐 Especificações dos Templates

- **Formato**: JPEG (.jpg)
- **Tamanho**: A4 (210 x 297 mm)
- **Resolução**: 300 DPI recomendado
- **Orientação**: Retrato (Portrait)

## 🔧 Como Funciona

1. O sistema verifica o username do responsável pela cotação
2. Se for um dos 4 usuários especiais, usa o template JPEG correspondente
3. O template é inserido como primeira página completa do PDF
4. Depois segue com o conteúdo normal da cotação

## ⚙️ Configuração

Os templates são configurados em `assets/filiais/filiais_config.py`:

```python
USUARIOS_COTACAO = {
    "valdir": {
        "template_capa_jpeg": "assets/templates/capas/capa_valdir.jpg"
    },
    # ... outros usuários
}
```

## 📝 Notas Importantes

- **Posição do Logo**: O logo da empresa NÃO aparece na capa (apenas no template)
- **Primeira Página**: A capa ocupa toda a primeira página
- **Conteúdo**: A partir da segunda página segue o formato normal
- **Fallback**: Se o arquivo JPEG não existir, usa capa padrão