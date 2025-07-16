#!/usr/bin/env python3

import sys
import os
import platform

print("=== DIAGNÓSTICO DO SISTEMA CRM ===")
print(f"Data/Hora: {__import__('datetime').datetime.now()}")
print()

# 1. Informações do Sistema
print("📋 INFORMAÇÕES DO SISTEMA:")
print(f"   Sistema Operacional: {platform.system()} {platform.release()}")
print(f"   Arquitetura: {platform.architecture()}")
print(f"   Python: {sys.version}")
print(f"   Executável Python: {sys.executable}")
print()

# 2. Variáveis de Ambiente
print("🌍 VARIÁVEIS DE AMBIENTE:")
print(f"   DISPLAY: {os.environ.get('DISPLAY', 'NÃO DEFINIDO')}")
print(f"   XDG_SESSION_TYPE: {os.environ.get('XDG_SESSION_TYPE', 'NÃO DEFINIDO')}")
print(f"   DESKTOP_SESSION: {os.environ.get('DESKTOP_SESSION', 'NÃO DEFINIDO')}")
print(f"   SSH_CONNECTION: {os.environ.get('SSH_CONNECTION', 'NÃO DEFINIDO')}")
print()

# 3. Teste de Importações
print("📦 TESTE DE IMPORTAÇÕES:")
try:
    import tkinter as tk
    print(f"   ✅ tkinter: versão {tk.TkVersion}")
except Exception as e:
    print(f"   ❌ tkinter: {e}")

try:
    from tkinter import ttk
    print("   ✅ tkinter.ttk: OK")
except Exception as e:
    print(f"   ❌ tkinter.ttk: {e}")

try:
    import sqlite3
    print(f"   ✅ sqlite3: versão {sqlite3.sqlite_version}")
except Exception as e:
    print(f"   ❌ sqlite3: {e}")

print()

# 4. Teste Básico do Tkinter
print("🖥️  TESTE BÁSICO DO TKINTER:")
try:
    import tkinter as tk
    
    # Teste 1: Criar root
    print("   Criando janela raiz...")
    root = tk.Tk()
    print("   ✅ Janela raiz criada")
    
    # Teste 2: Configurar janela
    print("   Configurando janela...")
    root.title("Teste")
    root.geometry("300x200")
    print("   ✅ Janela configurada")
    
    # Teste 3: Informações da tela
    print(f"   Largura da tela: {root.winfo_screenwidth()}")
    print(f"   Altura da tela: {root.winfo_screenheight()}")
    
    # Teste 4: Criar widgets
    print("   Criando widgets...")
    label = tk.Label(root, text="Teste de funcionalidade")
    label.pack()
    button = tk.Button(root, text="Fechar", command=root.quit)
    button.pack()
    print("   ✅ Widgets criados")
    
    # Teste 5: Mostrar janela temporariamente
    print("   Mostrando janela por 2 segundos...")
    root.after(2000, root.quit)  # Fechar após 2 segundos
    
    # Centralizar
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (150)
    y = (root.winfo_screenheight() // 2) - (100)
    root.geometry(f"300x200+{x}+{y}")
    
    root.mainloop()
    print("   ✅ Janela mostrada e fechada com sucesso")
    
except Exception as e:
    print(f"   ❌ Erro no teste do tkinter: {e}")
    import traceback
    traceback.print_exc()

print()

# 5. Teste dos Arquivos do Projeto
print("📁 VERIFICAÇÃO DOS ARQUIVOS:")
arquivos_necessarios = [
    "main.py",
    "database.py",
    "interface/login.py",
    "interface/main_window.py",
    "interface/__init__.py",
    "interface/modules/__init__.py",
    "interface/modules/base_module.py"
]

for arquivo in arquivos_necessarios:
    if os.path.exists(arquivo):
        tamanho = os.path.getsize(arquivo)
        print(f"   ✅ {arquivo} ({tamanho} bytes)")
    else:
        print(f"   ❌ {arquivo} - ARQUIVO NÃO ENCONTRADO")

print()

# 6. Teste de Importação dos Módulos do Projeto
print("🔧 TESTE DOS MÓDULOS DO PROJETO:")
try:
    from database import criar_banco, DB_NAME
    print("   ✅ database.py importado com sucesso")
except Exception as e:
    print(f"   ❌ database.py: {e}")

try:
    from interface.login import LoginWindow
    print("   ✅ interface.login importado com sucesso")
except Exception as e:
    print(f"   ❌ interface.login: {e}")

print()

# 7. Recomendações
print("💡 RECOMENDAÇÕES:")

if os.environ.get('DISPLAY') is None:
    print("   ⚠️  DISPLAY não está definido")
    print("   📌 Se você está usando SSH, conecte com: ssh -X usuario@servidor")
    print("   📌 Se você está no WSL, instale um servidor X como VcXsrv")
    print("   📌 Se você está no Windows, use o sistema diretamente ou WSL com X11")

if os.environ.get('SSH_CONNECTION'):
    print("   🔗 Conexão SSH detectada")
    print("   📌 Certifique-se de usar 'ssh -X' ou 'ssh -Y' para X11 forwarding")

print()
print("=== FIM DO DIAGNÓSTICO ===")
print()
print("Para testar apenas o tkinter: python test_tkinter.py")
print("Para testar login simples: python test_login.py")
print("Para executar o sistema: python main.py")