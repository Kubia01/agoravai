# 🚀 Como Executar o Sistema CRM

## Pré-requisitos

- Python 3.7+
- Linux/Windows/macOS com interface gráfica

## Instalação

1. **Instalar dependências:**
```bash
pip install -r requirements.txt
```

2. **Executar o sistema:**
```bash
python main.py
```

## Estrutura do Projeto

```
crm_compressores/
├── main.py                    # Arquivo principal
├── database.py                # Configuração do banco de dados
├── crm_compressores.db        # Banco de dados SQLite
├── logo.jpg                   # Logo da empresa
├── requirements.txt           # Dependências Python
├── utils/
│   ├── __init__.py
│   └── formatters.py          # Formatadores de dados
├── interface/
│   ├── __init__.py
│   ├── login.py               # Tela de login
│   ├── main_window.py         # Janela principal
│   └── modules/
│       ├── __init__.py
│       ├── base_module.py     # Módulo base
│       ├── clientes.py        # Gestão de clientes
│       ├── cotacoes.py        # Gestão de cotações
│       ├── dashboard.py       # Dashboard principal
│       ├── produtos.py        # Gestão de produtos
│       ├── relatorios.py      # Relatórios técnicos
│       ├── tecnicos.py        # Gestão de técnicos
│       └── usuarios.py        # Gestão de usuários
└── pdf_generators/
    ├── __init__.py
    ├── cotacao.py             # Gerador de PDF de cotações
    └── relatorio_tecnico.py   # Gerador de PDF de relatórios técnicos
```

## Funcionalidades Principais

- ✅ **Gestão de Clientes**: Cadastro e edição
- ✅ **Gestão de Produtos**: Catálogo de produtos
- ✅ **Cotações**: Geração de orçamentos
- ✅ **Relatórios Técnicos**: Com anexos e imagens
- ✅ **PDFs Profissionais**: Layout corporativo
- ✅ **Gestão de Usuários**: Controle de acesso

## Login Padrão

- **Usuário**: `admin`
- **Senha**: `admin123`

## Notas Importantes

- O banco de dados SQLite é criado automaticamente na primeira execução
- Arquivos de imagem anexados aos relatórios são exibidos nos PDFs
- Sistema funciona offline (não requer internet)
- Interface gráfica em português brasileiro

## Suporte

Para problemas ou dúvidas, verifique:
1. Se todas as dependências estão instaladas
2. Se o Python 3.7+ está sendo usado
3. Se o sistema tem interface gráfica disponível