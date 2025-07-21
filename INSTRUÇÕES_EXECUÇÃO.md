# Instruções para Executar o Sistema de Compressores

## Pré-requisitos

### 1. Python 3.7 ou superior
```bash
python3 --version
```

### 2. Instalar Dependências

#### Opção A: Usando pip (recomendado)
```bash
pip install fpdf2 requests Pillow
```

#### Opção B: Usando apt (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3-tk python3-pip
pip3 install fpdf2 requests Pillow
```

#### Opção C: Ambiente Virtual (mais seguro)
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## Como Executar

### 1. Preparar o Banco de Dados
```bash
cd /caminho/para/o/projeto
python3 database.py
```

### 2. Executar o Sistema
```bash
python3 main.py
```

## Credenciais de Acesso

### Administradores
- **Username**: `admin` | **Senha**: `admin123`
- **Username**: `master` | **Senha**: `master123`

### Funcionários com Templates de Cotação Personalizados
- **Username**: `valdir` | **Senha**: `valdir123`
- **Username**: `vagner` | **Senha**: `vagner123`
- **Username**: `rogerio` | **Senha**: `rogerio123`
- **Username**: `raquel` | **Senha**: `raquel123`

### Outros Funcionários
- **Username**: `jaqueline` | **Senha**: `jaqueline123`
- **Username**: `cicero` | **Senha**: `cicero123`
- **Username**: `adham` | **Senha**: `adham123`

## Funcionalidades Implementadas

### ✅ 1. Geração de PDF com Logo Corrigido
- Faça login com qualquer usuário autorizado
- Acesse "Cotações" → "Nova Cotação"
- Preencha os dados e adicione itens
- Clique em "Gerar PDF"
- O logo aparecerá corretamente no cabeçalho

### ✅ 2. Capa Personalizada por Usuário
- Faça login com: `valdir`, `vagner`, `rogerio` ou `raquel`
- Crie uma cotação e gere o PDF
- A primeira página será uma capa personalizada para o usuário

### ✅ 3. Seleção de Filial
- Na criação da cotação, selecione a filial desejada
- O rodapé do PDF mostrará os dados da filial selecionada
- CNPJ, endereço e telefones específicos da filial

### ✅ 4. Sistema de Permissões
- Faça login como administrador (`admin` ou `master`)
- Acesse o módulo "Permissões"
- Configure permissões por usuário e módulo
- Use templates para configuração rápida

## Estrutura do Projeto

```
sistema-compressores/
├── main.py                     # Arquivo principal
├── database.py                 # Configuração do banco
├── requirements.txt            # Dependências
├── crm_compressores.db        # Banco de dados SQLite
├── logo.jpg                   # Logo original
├── assets/                    # Recursos organizados
│   ├── logos/
│   │   └── world_comp_brasil.jpg
│   ├── filiais/
│   │   └── filiais_config.py
│   └── templates/
│       └── capas/
│           ├── base_capa.py
│           ├── capa_valdir.py
│           ├── capa_vagner.py
│           ├── capa_rogerio.py
│           └── capa_raquel.py
├── interface/                 # Interface gráfica
│   ├── login.py
│   ├── main_window.py
│   └── modules/
│       ├── cotacoes.py        # ← MODIFICADO (campo filial)
│       ├── permissoes.py      # ← NOVO MÓDULO
│       └── ...
├── pdf_generators/            # Geradores de PDF
│   ├── cotacao.py            # Versão original
│   └── cotacao_nova.py       # ← NOVA VERSÃO MELHORADA
└── utils/                    # Utilitários
    └── formatters.py
```

## Testes Recomendados

### 1. Teste de Login
```
✓ Faça login com cada usuário para verificar acesso
✓ Teste credenciais inválidas
✓ Verifique se admins têm acesso ao módulo de permissões
```

### 2. Teste de Cotações
```
✓ Crie cotação como 'rogerio' - verifique capa personalizada
✓ Selecione filial 1 - verifique CNPJ no rodapé
✓ Selecione filial 2 - verifique CNPJ diferente
✓ Adicione itens com valores - verifique se não aparecem zeros
✓ Teste descrições vazias - verifique fallback
```

### 3. Teste de Permissões
```
✓ Configure usuário com apenas consulta
✓ Configure usuário com controle total
✓ Teste acesso negado aos módulos sem permissão
✓ Use templates de permissão para configuração rápida
```

## Solução de Problemas

### Erro: "No module named 'tkinter'"
```bash
# Ubuntu/Debian
sudo apt install python3-tk

# Fedora/CentOS
sudo dnf install tkinter
```

### Erro: "No module named 'fpdf'"
```bash
pip3 install fpdf2
```

### Erro: "Database locked"
```bash
# Feche todas as instâncias do sistema
# Execute novamente database.py
python3 database.py
```

### PDFs não são gerados
```bash
# Verifique se o diretório existe
mkdir -p data/cotacoes/arquivos

# Verifique permissões de escrita
chmod 755 data/cotacoes/arquivos
```

## Arquivos de Dados

### Banco de Dados
- **Arquivo**: `crm_compressores.db`
- **Tipo**: SQLite
- **Backup**: Recomendado antes de atualizações

### PDFs Gerados
- **Localização**: `data/cotacoes/arquivos/`
- **Formato**: `Proposta_NUMERO.pdf`
- **Conteúdo**: Capa + Apresentação + Detalhes

### Logs do Sistema
- **Console**: Mensagens de erro e debug
- **Interface**: Notificações de sucesso/erro

## Contato e Suporte

### Melhorias Implementadas
✅ Logo da empresa no PDF corrigido
✅ Capa personalizada por usuário  
✅ Problemas de descrição e valores corrigidos
✅ CNPJ da filial no rodapé
✅ Sistema de armazenamento organizado
✅ 7 funcionários cadastrados
✅ Tela de permissões completa

### Próximos Passos
- Sistema está pronto para produção
- Todos os requisitos foram atendidos
- Documentação completa fornecida