# Instruções para Correção dos Bugs Identificados

## 🐛 1. Erro no Kit - AttributeError: 'items_data'

**Arquivo:** `interface/modules/produtos.py`
**Linha:** Aproximadamente linha 803 na função `adicionar_item_kit`

**Problema:** A função está referenciando `self.items_data` que não existe.

**Solução:** Substitua a função `adicionar_item_kit` completa por:

```python
def adicionar_item_kit(self):
    """Adicionar item à composição do kit"""
    if not self.item_produto_var.get():
        self.show_warning("Selecione um produto/serviço!")
        return
        
    try:
        quantidade = float(self.item_quantidade_var.get())
        if quantidade <= 0:
            raise ValueError()
    except ValueError:
        self.show_error("Quantidade deve ser um número positivo!")
        return
    
    # Obter dados do produto selecionado
    index = self.produto_kit_combo.current()
    if index < 0:
        self.show_warning("Produto não selecionado corretamente!")
        return
        
    if not hasattr(self, 'produtos_kit_map') or index not in self.produtos_kit_map:
        self.show_warning("Erro ao obter dados do produto!")
        return
        
    produto_id = self.produtos_kit_map[index]
    produto_nome, produto_tipo = self.produtos_kit_data[index][1], self.produtos_kit_data[index][2]
    
    # Verificar se já existe
    for item in self.kit_items:
        if item['produto_id'] == produto_id:
            self.show_warning("Este produto já está no kit!")
            return
    
    # Adicionar à lista
    item = {
        'produto_id': produto_id,
        'nome': produto_nome,
        'tipo': produto_tipo,
        'quantidade': quantidade
    }
    self.kit_items.append(item)
    
    # Atualizar treeview
    self.atualizar_kit_tree()
    
    # Limpar campos
    self.limpar_item_kit()
```

## 🐛 2. Erro no PDF de Cotação - "no such column: cli.pais"

**Arquivo:** `pdf_generators/cotacao.py`
**Linha:** Aproximadamente linha 140 na query SQL

**Problema:** A query está tentando acessar a coluna `cli.pais` que não existe na tabela `clientes`.

**Solução:** 

1. **Encontre esta linha na query SQL:**
```sql
cli.id AS cliente_id, cli.nome AS cliente_nome, cli.nome_fantasia, cli.endereco, cli.email, 
cli.telefone, cli.site, cli.cnpj, cli.cidade, cli.estado, cli.cep, cli.pais,
```

2. **Substitua por (removendo cli.pais):**
```sql
cli.id AS cliente_id, cli.nome AS cliente_nome, cli.nome_fantasia, cli.endereco, cli.email, 
cli.telefone, cli.site, cli.cnpj, cli.cidade, cli.estado, cli.cep,
```

3. **Encontre a tupla de desempacotamento:**
```python
cliente_estado, cliente_cep, cliente_pais,
```

4. **Substitua por:**
```python
cliente_estado, cliente_cep,
```

## 🐛 3. PDF de Relatório Técnico - Atualizar para Formato Corporativo

**Arquivo:** `pdf_generators/relatorio_tecnico.py`

**Problema:** O PDF não está no formato corporativo igual ao de cotação e não mostra anexos.

**Solução:** Substitua a classe `RelatorioPDF` completa por:

```python
def clean_text(text):
    """Substitui tabs por espaços e remove caracteres problemáticos"""
    if text is None:
        return ""
    text = text.replace('\t', '    ')
    return text

class RelatorioPDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_auto_page_break(auto=True, margin=25)
        self.baby_blue = (137, 207, 240)
    
    def header(self):
        # Desenha a borda em todas as páginas
        self.set_line_width(0.5)
        self.rect(5, 5, 200, 287)
        
        # Cabeçalho corporativo
        self.set_font("Arial", 'B', 11)
        self.set_y(10)
        self.cell(0, 5, clean_text("WORLD COMP DO BRASIL COMPRESSORES EIRELI"), 0, 1)
        self.cell(0, 5, clean_text("ORDEM DE SERVIÇO DE CAMPO SIMPLIFICADA"), 0, 1)
        
        # Logo centralizado
        logo_path = "logo.jpg"
        if os.path.exists(logo_path):
            logo_height = 25
            logo_width = logo_height * 1.5
            self.image(logo_path, x=(210 - logo_width) / 2, y=25, w=logo_width)
        
        self.set_y(60)
    
    def footer(self):
        self.set_y(-20)
        self.line(10, self.get_y() - 5, 200, self.get_y() - 5)
        
        self.set_font("Arial", '', 10)
        self.set_text_color(*self.baby_blue)
        self.cell(0, 5, clean_text("Rua Fernando Pessoa, 17 - Batistini - São Bernardo do Campo/SP - CEP 09844-390"), 0, 1, 'C')
        self.cell(0, 5, clean_text("E-mail: rogerio@worldcompressores.com.br | Fone: (11) 4543-6896/4543-6857/4357-8062"), 0, 1, 'C')
        
        self.set_text_color(0, 0, 0)

    def section_title(self, title):
        self.set_text_color(*self.baby_blue)
        self.set_font("Arial", 'B', 12)
        self.cell(0, 8, clean_text(title), 0, 1, 'L')
        self.set_text_color(0, 0, 0)
        self.ln(2)
```

**E adicione a seção de anexos na função principal:**

```python
# Anexos (adicionar antes do final)
if anexos:
    pdf.section_title("ANEXOS")
    for i, anexo in enumerate(anexos, 1):
        if isinstance(anexo, dict):
            nome = anexo.get('nome', f'Anexo {i}')
            descricao = anexo.get('descricao', '')
            pdf.cell(0, 6, f"Anexo {i}: {nome}", 0, 1)
            if descricao:
                pdf.multi_cell(0, 5, f"Descrição: {descricao}")
            pdf.ln(2)
```

## ✅ Teste após as correções

1. **Teste Kit**: Criar um novo kit selecionando produtos existentes
2. **Teste PDF Cotação**: Gerar PDF de uma cotação existente  
3. **Teste PDF Relatório**: Gerar PDF de um relatório com anexos

## 📁 Arquivos a serem modificados

- `interface/modules/produtos.py` (função adicionar_item_kit)
- `pdf_generators/cotacao.py` (query SQL e tupla)
- `pdf_generators/relatorio_tecnico.py` (classe RelatorioPDF e anexos)

Após aplicar essas correções, todos os problemas relatados devem estar resolvidos! 🎯
