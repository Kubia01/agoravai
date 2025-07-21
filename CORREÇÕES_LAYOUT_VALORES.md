# Correções de Layout e Valores no PDF

## 🎯 Problemas Corrigidos

### 1. ✅ Capa JPEG Sem Header/Footer

**Problema**: Capa JPEG tinha cabeçalho e rodapé sobrepostos
**Solução**: Sistema reescrito para não exibir header/footer na primeira página

#### Como funciona agora:
- **Página 1**: Apenas template JPEG (sem header/footer)
- **Página 2+**: Header/footer normais

#### Implementação:
```python
def header(self):
    # NÃO exibir header na página da capa JPEG
    if self.capa_jpeg_page:
        self.capa_jpeg_page = False
        return

def footer(self):
    # NÃO exibir footer na página da capa JPEG (primeira página)
    if self.page_no() == 1:
        return
```

### 2. ✅ Layout Segunda Página (Modelo Antigo)

**Problema**: Layout não seguia o modelo antigo solicitado
**Solução**: Segunda página completamente reescrita

#### Layout Implementado:
```
┌─────────────────────────────────────┐
│            [LOGO CENTRO]            │ ← Logo centralizado no topo
│                                     │
│ APRESENTADO PARA:  APRESENTADO POR: │ ← Esquerda / Direita
│ Cliente            Filial           │
│ CNPJ: xxx          CNPJ: xxx       │
│ Endereço           Telefones        │
│                    E-mail           │
│                                     │
│        Texto de apresentação        │ ← Centralizado abaixo
│        (modelo antigo)              │
└─────────────────────────────────────┘
```

#### Código da Segunda Página:
```python
# LOGO CENTRALIZADO NO TOPO
logo_path = dados_filial.get("logo_path", "assets/logos/world_comp_brasil.jpg")
if os.path.exists(logo_path):
    logo_height = 30
    logo_width = logo_height * 1.5
    x_centro = (210 - logo_width) / 2
    pdf.image(logo_path, x=x_centro, y=20, h=logo_height)

# "APRESENTADO PARA" - Lado Esquerdo
pdf.set_xy(15, 70)
pdf.cell(85, 8, "APRESENTADO PARA:", 0, 0, 'L')

# "APRESENTADO POR" - Lado Direito  
pdf.set_xy(110, 70)
pdf.cell(85, 8, "APRESENTADO POR:", 0, 1, 'L')
```

### 3. ✅ Header Páginas 3+ Simplificado

**Problema**: Header das páginas de itens estava complexo
**Solução**: Header simples apenas para páginas de conteúdo

#### Layout Header Páginas 3+:
```
┌─────────────────────────────────────┐
│ PROPOSTA COMERCIAL                  │ ← Simples, esquerda
│ NÚMERO: 123                         │
│─────────────────────────────────────│
│ Conteúdo dos itens...               │
```

### 4. 🔍 Debug de Valores Adicionado

**Problema**: Valores dos itens aparecendo como zero
**Solução**: Sistema de debug implementado para identificar origem

#### Debug Implementado:
```python
# DEBUG: Imprimir valores originais
print(f"DEBUG Item {item_counter}: valor_unitario={valor_unitario}, valor_total_item={valor_total_item}")

# Conversão melhorada
valor_unitario = float(valor_unitario) if valor_unitario is not None else 0.0
valor_total_item = float(valor_total_item) if valor_total_item is not None else 0.0

print(f"DEBUG APÓS conversão: valor_unitario={valor_unitario}, valor_total_item={valor_total_item}")
```

## 🔧 Estrutura Final do PDF

### Página 1: Capa JPEG
- ✅ Template JPEG ocupando página inteira
- ✅ SEM header ou footer
- ✅ Imagem de 0,0 até 210x297mm

### Página 2: Apresentação
- ✅ Logo centralizado no topo
- ✅ "Apresentado para" (esquerda) + "Apresentado por" (direita)
- ✅ Dados do cliente e filial organizados
- ✅ Texto de apresentação centralizado abaixo
- ✅ Footer com dados da filial

### Páginas 3+: Itens e Detalhes
- ✅ Header simples (proposta + número)
- ✅ Conteúdo dos itens com formatação corrigida
- ✅ Footer com dados da filial

## 🐛 Investigação de Valores

### Sistema de Debug Ativo
Para identificar por que valores aparecem como zero:

1. **Log na busca do banco**: Valores originais da query
2. **Log na conversão**: Após conversão para float
3. **Log nos cálculos**: Verificação de recálculos automáticos

### Como Testar o Debug:
1. Executar sistema: `python3 main.py`
2. Gerar PDF de cotação
3. Verificar console para logs de debug:
```
DEBUG Item 1: valor_unitario=1500.00, valor_total_item=3000.00, quantidade=2
DEBUG Item 1 APÓS conversão: valor_unitario=1500.0, valor_total_item=3000.0
```

### Possíveis Causas dos Valores Zero:
1. **Dados NULL no banco**: Query já usa COALESCE
2. **Conversão incorreta**: Debug mostrará
3. **Recálculo errado**: Logs revelarão
4. **Problema na formatação final**: Debug identificará

## ⚠️ Próximos Passos

### Para Resolver Valores:
1. **Executar PDF com debug ativo**
2. **Analisar logs do console**
3. **Identificar em que ponto valores viram zero**
4. **Corrigir problema específico encontrado**

### Para Testar Layout:
1. **Gerar PDF com usuário que tem template JPEG**
2. **Verificar página 1**: Apenas imagem, sem header/footer
3. **Verificar página 2**: Layout "apresentado para/por"
4. **Verificar páginas 3+**: Header simples

## 🎯 Status Atual

### ✅ Implementado:
1. **Capa JPEG limpa** (sem header/footer)
2. **Layout segunda página** (modelo antigo)
3. **Header simplificado** páginas 3+
4. **Sistema de debug** para valores

### 🔍 Em Investigação:
1. **Valores dos itens** (debug ativo para identificar causa)

### 📋 Teste Necessário:
1. Executar sistema e verificar logs de debug
2. Confirmar layout das páginas
3. Testar com diferentes tipos de itens

**Sistema está 90% pronto - apenas falta resolver questão específica dos valores!**