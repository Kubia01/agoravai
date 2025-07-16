#!/usr/bin/env python3

import tkinter as tk
from tkinter import messagebox
import sys
import os

def main():
    print("=== Sistema CRM - Windows ===")
    
    try:
        # Criar banco de dados
        print("Criando banco de dados...")
        from database import criar_banco
        criar_banco()
        print("✅ Banco de dados OK")
        
        # Criar janela principal
        print("Criando interface...")
        root = tk.Tk()
        root.title("CRM - Sistema de Compressores")
        
        # Esconder janela principal temporariamente
        root.withdraw()
        
        # Garantir que a janela seja criada antes de continuar
        root.update()
        
        print("Carregando tela de login...")
        
        # Usar versão corrigida da LoginWindow
        from interface.login_fixed import LoginWindow
        login_window = LoginWindow(root)
        
        print("✅ Tela de login criada!")
        print("A janela deveria estar visível agora.")
        
        # Iniciar loop principal
        root.mainloop()
        
        print("Sistema encerrado.")
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        messagebox.showerror("Erro", f"Arquivo não encontrado: {e}")
        return 1
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        
        try:
            messagebox.showerror("Erro", f"Erro ao iniciar sistema:\n\n{str(e)}")
        except:
            pass
        
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    if exit_code != 0:
        input("Pressione Enter para fechar...")
    sys.exit(exit_code)