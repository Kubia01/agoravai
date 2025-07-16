#!/usr/bin/env python3

import sys
import os

print("=== Sistema CRM - Debug ===")
print(f"Python version: {sys.version}")
print(f"Diretório atual: {os.getcwd()}")
print(f"DISPLAY: {os.environ.get('DISPLAY', 'Não definido')}")

try:
    print("\n1. Testando imports...")
    import tkinter as tk
    from tkinter import ttk, messagebox
    print("✅ Tkinter importado com sucesso!")
    
    import sqlite3
    print("✅ SQLite3 importado com sucesso!")
    
    import hashlib
    print("✅ Hashlib importado com sucesso!")
    
    print("\n2. Testando imports do projeto...")
    from database import criar_banco, DB_NAME
    print("✅ Database importado com sucesso!")
    
    from interface.login import LoginWindow
    print("✅ LoginWindow importado com sucesso!")
    
    print("\n3. Criando banco de dados...")
    criar_banco()
    print("✅ Banco de dados criado/verificado!")
    
    print("\n4. Testando criação da janela raiz...")
    root = tk.Tk()
    root.title("CRM - Sistema de Compressores")
    print("✅ Janela raiz criada!")
    
    # Não esconder a janela principal para debug
    root.geometry("1x1+0+0")  # Janela mínima
    
    print("\n5. Testando criação da tela de login...")
    login_window = LoginWindow(root)
    print("✅ Tela de login criada!")
    
    print("\n6. Iniciando loop principal...")
    print("Se a tela não aparecer, pode ser problema de ambiente gráfico.")
    print("Pressione Ctrl+C para interromper se necessário.")
    
    root.mainloop()
    print("✅ Aplicação encerrada normalmente.")
    
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    print("Verifique se todos os arquivos estão presentes.")
    
except Exception as e:
    print(f"❌ Erro geral: {e}")
    import traceback
    traceback.print_exc()
    
    # Tentar mostrar uma janela simples de erro
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Erro", f"Erro ao iniciar o sistema:\n{e}")
    except:
        print("Não foi possível mostrar janela de erro.")

print("\nFim do debug.")