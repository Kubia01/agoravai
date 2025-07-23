# Guia de Instalação - Sistema de Propostas Comerciais

## 🚀 Instalação Rápida

### 1. Requisitos do Sistema
- **Python 3.6+** instalado
- **Interface gráfica** (X11 no Linux, nativo no Windows/macOS)
- **Conexão com internet** para instalar dependências

### 2. Instalar Dependências
```bash
pip install -r requirements.txt
```

**Ou instalar manualmente:**
```bash
pip install fpdf2 requests Pillow pyinstaller
```

### 3. Testar o Sistema
```bash
python test_sistema.py
```

### 4. Executar o Sistema
```bash
python main.py
```

## 🔧 Correção de Problemas Comuns

### Erro: "No module named 'tkinter'"

**No Ubuntu/Debian:**
```bash
sudo apt-get install python3-tk
```

**No CentOS/RHEL:**
```bash
sudo yum install tkinter
# ou
sudo dnf install python3-tkinter
```

**No macOS:**
```bash
brew install python-tk
```

**No Windows:**
- Tkinter já vem instalado com Python

### Erro: "No module named 'PIL'"

```bash
pip install Pillow
```

### Erro: "No module named 'fpdf'"

```bash
pip install fpdf2
```

### Erro: "DISPLAY not set" (Linux)

**Para SSH:**
```bash
ssh -X usuario@servidor
# ou
ssh -Y usuario@servidor
```

**Para servidor sem interface:**
```bash
# Instalar Xvfb
sudo apt-get install xvfb

# Executar com display virtual
xvfb-run -a python main.py
```

### Erro: Database/Permission Issues

```bash
# Recriar banco de dados
python database.py

# Verificar permissões
chmod 755 .
chmod 644 *.db
```

## 🎯 Login no Sistema

### Usuários Disponíveis:

**Administrador:**
- **Usuário:** admin
- **Senha:** admin123
- **Acesso:** Todas as funcionalidades

**Usuários Normais:**
- **jaqueline/jaqueline123**
- **valdir/valdir123**
- **raquel/raquel123**
- **rogerio/rogerio123**
- **vagner/vagner123**
- **adam/adam123**
- **cicero/cicero123**

## 📁 Estrutura de Arquivos

```
projeto/
├── main.py                 # Arquivo principal
├── database.py            # Configuração do banco
├── requirements.txt       # Dependências
├── interface/             # Interface gráfica
│   ├── login.py
│   ├── main_window.py
│   └── modules/           # Módulos do sistema
│       ├── correcoes.py   # ⚙️ Correções (Admin)
│       ├── editor_pdf.py  # 🎨 Editor PDF
│       └── ...
├── pdf_generators/        # Geradores de PDF
├── assets/               # Templates e recursos
│   ├── templates/capas/  # Templates por usuário
│   └── filiais/         # Configurações
└── data/                # Dados e configurações
```

## 🎨 Funcionalidades Implementadas

### Para Administradores:
1. **⚙️ Correções** - Editar textos e templates
2. **🎨 Editor PDF** - Design visual
3. **👤 Usuários** - Gerenciar usuários
4. **🔐 Permissões** - Controle de acesso

### Para Usuários:
1. **💰 Cotações** - Criar propostas
2. **🎨 Editor PDF** - Design visual
3. **📋 Relatórios** - Visualizar dados
4. **👥 Clientes** - Gerenciar clientes

## 🔍 Teste das Funcionalidades

### 1. Login como Admin
```
Usuário: admin
Senha: admin123
```

### 2. Testar Módulo de Correções
- Clicar na aba "⚙️ Correções"
- Testar as 3 abas: Textos PDF, Templates, Upload

### 3. Testar Editor PDF
- Clicar na aba "🎨 Editor PDF"
- Testar ferramentas de design visual

### 4. Criar uma Cotação
- Clicar na aba "💰 Cotações"
- Criar nova proposta para testar PDF

## 📞 Suporte

### Logs do Sistema
```bash
# Executar com debug
python main.py --debug

# Verificar logs
tail -f sistema.log
```

### Informações do Sistema
```bash
python --version
pip list | grep -E "(fpdf|Pillow|tkinter)"
```

### Reset Completo
```bash
# Backup dos dados
cp -r data/ data_backup/

# Reset do banco
rm -f *.db
python database.py

# Reset das configurações
rm -rf data/
mkdir data/
```

## ✅ Checklist de Instalação

- [ ] Python 3.6+ instalado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Teste passou (`python test_sistema.py`)
- [ ] Sistema executa (`python main.py`)
- [ ] Login funciona (admin/admin123)
- [ ] Módulos carregam sem erro
- [ ] PDF é gerado corretamente

Se todos os itens estão marcados, o sistema está pronto para uso! 🎉