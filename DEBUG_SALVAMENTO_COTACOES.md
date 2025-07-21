# Debug do Salvamento de Cotações

## 🚨 Problema Identificado

**Issue**: Valores dos itens aparecem zerados após salvar e recarregar cotação
**Local**: Interface de cotações (salvamento/carregamento de itens)

## 🔍 Debug Implementado

### 1. **Debug no Salvamento**
- Mostra valores originais da interface (TreeView)
- Mostra valores após conversão com clean_number
- Confirma o que foi inserido no banco

### 2. **Debug no Carregamento**  
- Mostra valores vindos diretamente do banco
- Mostra valores após formatação para interface
- Confirma o que é exibido na TreeView

## 🧪 Como Testar

### 1. **Executar Sistema**
```bash
python3 main.py
```

### 2. **Cenário de Teste**
1. Fazer login
2. Ir para "Cotações" → "Nova Cotação"
3. Preencher dados básicos (número, cliente)
4. **Adicionar item com valor**:
   - Tipo: Produto
   - Nome: Teste Debug
   - Quantidade: 2
   - Valor Unitário: 150.50
5. **Salvar cotação**
6. **Verificar console** para logs de salvamento
7. **Recarregar cotação** (editar a mesma)
8. **Verificar console** para logs de carregamento
9. **Verificar interface** se valores aparecem corretos

### 3. **Logs Esperados**

#### Salvamento:
```
DEBUG SALVAMENTO - Item: Teste Debug
  - Valores originais: ('Produto', 'Teste Debug', '2.00', 'R$ 150,50', 'R$ 0,00', 'R$ 0,00', 'R$ 0,00', 'R$ 301,00', '')
  - Valor unit string: 'R$ 150,50'
  - Total string: 'R$ 301,00'
  - Valor unit convertido: 150.5
  - Total convertido: 301.0
  - Quantidade: 2.0
  - Inserido no banco: cotacao_id=123, tipo=Produto, nome=Teste Debug
  - Valores inseridos: unit=150.5, total=301.0
  ---
```

#### Carregamento:
```
DEBUG CARREGAMENTO - Item: Teste Debug
  - Row do banco: ('Produto', 'Teste Debug', 2.0, 150.5, 301.0, '', 0.0, 0.0, 0.0)
  - Valor unit do banco: 150.5
  - Total do banco: 301.0
  - Valor unit formatado: R$ 150,50
  - Total formatado: R$ 301,00
  ---
```

## 🔧 Possíveis Problemas e Soluções

### **Caso 1: Valores Zerados no Salvamento**
```
  - Valor unit convertido: 0.0
  - Total convertido: 0.0
```
**Problema**: clean_number não está funcionando ou valores da interface estão incorretos
**Solução**: Verificar função clean_number e format_currency

### **Caso 2: Valores Corretos no Salvamento, Zerados no Carregamento**
```
Salvamento: Valores inseridos: unit=150.5, total=301.0
Carregamento: Valor unit do banco: 0.0
```
**Problema**: Banco de dados não está salvando ou query está incorreta
**Solução**: Verificar schema do banco e commits

### **Caso 3: Valores Corretos no Carregamento, Zerados na Interface**
```
Carregamento: Total do banco: 301.0
Interface: Mostra R$ 0,00
```
**Problema**: format_currency não está funcionando corretamente
**Solução**: Verificar função format_currency

### **Caso 4: Problema na Conversão de Moeda**
```
  - Valor unit string: 'R$ 150,50'
  - Valor unit convertido: 0.0
```
**Problema**: clean_number não remove "R$ " ou não converte vírgula
**Solução**: Melhorar função clean_number

## 🛠️ Correções Baseadas no Debug

### **Se clean_number estiver falhando**:
```python
def clean_number(value):
    if not value:
        return 0.0
    try:
        # Remove R$, espaços e converte vírgula para ponto
        cleaned = str(value).replace('R$', '').replace(' ', '').replace(',', '.')
        return float(cleaned)
    except (ValueError, TypeError):
        return 0.0
```

### **Se format_currency estiver falhando**:
```python
def format_currency(value):
    if value is None:
        return "R$ 0,00"
    try:
        return f"R$ {float(value):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except (ValueError, TypeError):
        return "R$ 0,00"
```

### **Se o problema for no TreeView**:
Verificar se as colunas estão na ordem correta e se os índices correspondem.

## 📋 Checklist de Verificação

### Durante o Teste:
- [ ] Valores aparecem corretos na interface antes de salvar
- [ ] Logs de salvamento mostram valores corretos
- [ ] Logs de carregamento mostram valores corretos
- [ ] Interface mostra valores corretos após carregamento

### Análise dos Logs:
- [ ] clean_number funciona corretamente
- [ ] Valores são salvos no banco corretamente
- [ ] Valores são carregados do banco corretamente
- [ ] format_currency formata corretamente

## 🎯 Próximo Passo

1. **Execute o teste** com o cenário descrito
2. **Analise os logs** no console
3. **Identifique onde o problema ocorre**:
   - Salvamento (valores viram 0 na conversão)
   - Banco (valores não são salvos)
   - Carregamento (valores não são recuperados)
   - Interface (valores não são exibidos)
4. **Aplique a correção** específica conforme o problema identificado

**Com esses logs detalhados, vamos identificar exatamente onde os valores estão sendo perdidos!** 🔍