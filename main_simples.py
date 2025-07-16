#!/usr/bin/env python3

import tkinter as tk
from tkinter import messagebox
import traceback

print("=== TESTE MAIN SIMPLIFICADO ===")

try:
    print("1. Criando janela principal...")
    root = tk.Tk()
    root.title("CRM - Teste")
    print("✅ Janela principal criada")
    
    print("2. Escondendo janela principal...")
    root.withdraw()
    print("✅ Janela principal escondida")
    
    print("3. Criando janela de login...")
    login_window = tk.Toplevel(root)
    login_window.title("Login - CRM Test")
    login_window.geometry("400x300")
    login_window.configure(bg='white')
    print("✅ Janela de login criada")
    
    print("4. Configurando janela de login...")
    # Centralizar
    login_window.update_idletasks()
    x = (login_window.winfo_screenwidth() // 2) - 200
    y = (login_window.winfo_screenheight() // 2) - 150
    login_window.geometry(f"400x300+{x}+{y}")
    
    # Forçar para frente
    login_window.lift()
    login_window.focus_force()
    login_window.grab_set()
    print("✅ Janela configurada e centralizada")
    
    print("5. Adicionando conteúdo...")
    tk.Label(login_window, text="TESTE DE LOGIN", font=('Arial', 16, 'bold'), bg='white').pack(pady=50)
    
    def fechar():
        print("Fechando aplicação...")
        root.quit()
    
    tk.Button(login_window, text="Fechar Teste", command=fechar, font=('Arial', 12)).pack(pady=20)
    print("✅ Conteúdo adicionado")
    
    print("6. Iniciando loop...")
    print("A janela deveria aparecer AGORA!")
    print("Se não aparecer, pressione Ctrl+C")
    
    root.mainloop()
    print("✅ Aplicação encerrada normalmente")
    
except Exception as e:
    print(f"❌ ERRO: {e}")
    traceback.print_exc()
    
    # Tentar mostrar erro em messagebox
    try:
        messagebox.showerror("Erro", f"Erro no teste: {e}")
    except:
        pass

print("=== FIM DO TESTE ===")