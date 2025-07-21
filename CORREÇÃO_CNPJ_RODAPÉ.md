# Correção: CNPJ da Empresa no Rodapé

## Problema
O rodapé do PDF estava sem o CNPJ da empresa, que deveria variar conforme a filial responsável pela cotação.

## Solução Implementada
- **Arquivo modificado**: `pdf_generators/cotacao_nova.py`
- **Método alterado**: `footer()` da classe `PDFCotacao`

### Alterações realizadas:
1. **Aumentou espaço do rodapé**: `self.set_y(-25)` (era -20) para acomodar uma linha adicional
2. **Adicionou linha do CNPJ**: Nova linha centralizada com `CNPJ: {dados_filial.cnpj}`
3. **Ordem das informações no rodapé**:
   - Linha 1: Endereço e CEP
   - Linha 2: **CNPJ** (nova linha)
   - Linha 3: E-mail e telefones

## Estrutura Final do Rodapé
```
Rua Fernando Pessoa, nº 17 – Batistini – São Bernardo do Campo – SP - CEP: 09844-390
CNPJ: 22.790.603/0001-77
E-mail: rogerio@worldcompressores.com.br | Fone: (11) 4543-6896 / 4543-6857 / 4357-8062
```

## Observações Técnicas
- O CNPJ é obtido automaticamente dos dados da filial (`self.dados_filial.get('cnpj', 'N/A')`)
- Cada filial tem seu próprio CNPJ configurado em `assets/filiais/filiais_config.py`
- Mantida a cor azul bebê (`baby_blue`) para consistência visual
- O rodapé não aparece na capa (página 1)

## Teste
Para testar, gere um PDF de cotação e verifique se:
1. O CNPJ aparece centralizado no rodapé
2. O CNPJ corresponde à filial responsável pela cotação
3. O layout permanece bem formatado em todas as páginas