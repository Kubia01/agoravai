# 🖼️ Imagens de Fundo para Capas de Cotação

## 📍 Localização
Este diretório armazena a **imagem de fundo** utilizada nas capas personalizadas das cotações.

## 📁 Estrutura de Arquivos

```
/workspace/assets/backgrounds/
├── capa_fundo.jpg          ← IMAGEM DE FUNDO (adicionar aqui)
└── README_BACKGROUNDS.md   ← Este arquivo
```

## 🎨 Especificações da Imagem

### **Arquivo Principal**: `capa_fundo.jpg`

#### **Especificações Técnicas**:
- **Formato**: JPEG (.jpg)
- **Dimensões**: A4 (210 x 297 mm em 300 DPI)
- **Resolução**: 300 DPI (2480 x 3508 pixels)
- **Orientação**: Retrato (vertical)
- **Tamanho**: Máximo 5MB

#### **Características Visuais**:
- Imagem base conforme modelo fornecido
- Espaço reservado na parte inferior para texto dinâmico
- Layout compatível com as capas personalizadas sobrepostas

## 🔧 Funcionamento do Sistema

### **Composição da Capa Final**:
1. **Fundo**: `capa_fundo.jpg` (imagem base)
2. **Sobreposição**: Capa personalizada do usuário (reduzida)
3. **Texto Dinâmico**: Informações na parte inferior

### **Campos Dinâmicos** (parte inferior):
```
EMPRESA: [NOME_DO_CLIENTE]
A/C SR. [NOME_DO_CONTATO]
[DATA_DA_COTACAO]
```

#### **Exemplo**:
```
EMPRESA: COCA COLA
A/C SR. GUILHERME DE MOURA
01/01/2025
```

## 📋 Como Adicionar a Imagem

### **1. Salvar Arquivo**
- Salve a imagem de fundo como `capa_fundo.jpg`
- Coloque no diretório: `/workspace/assets/backgrounds/`

### **2. Verificar Arquivo**
```bash
ls -la /workspace/assets/backgrounds/capa_fundo.jpg
```

### **3. Testar no Sistema**
- Criar nova cotação
- Gerar PDF para usuário com template personalizado
- Verificar se fundo aparece corretamente

## 🎯 Resultado Final

### **Layout da Nova Capa**:
```
┌─────────────────────────────┐
│        FUNDO FIXO           │ ← capa_fundo.jpg
│   ┌─────────────────────┐   │
│   │   CAPA PERSONAL.    │   │ ← capa_[usuario].jpg (reduzida)
│   │   (Valdir/Vagner/   │   │
│   │    Rogério/Raquel)  │   │
│   └─────────────────────┘   │
│                             │
│     EMPRESA: [Cliente]      │ ← Texto dinâmico
│   A/C SR. [Contato]         │
│     [Data]                  │
└─────────────────────────────┘
```

## ⚠️ Importante

- **A imagem de fundo é compartilhada** por todos os usuários
- **As capas personalizadas** continuam específicas para cada usuário
- **O texto dinâmico** é gerado automaticamente pelo sistema
- **Manter qualidade alta** para impressão profissional

---

**Adicione a imagem `capa_fundo.jpg` neste diretório para ativar o novo layout!** 🎨