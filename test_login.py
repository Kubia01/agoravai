#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

print("=== Teste de Login Simples ===")

try:
    # Criar janela principal
    root = tk.Tk()
    root.title("CRM - Login")
    root.withdraw()  # Esconder janela principal
    
    # Criar janela de login
    login_window = tk.Toplevel(root)
    login_window.title("Login - Sistema CRM")
    login_window.geometry("400x300")
    login_window.resizable(False, False)
    
    # Configurar janela
    login_window.configure(bg='white')
    login_window.transient(root)
    login_window.grab_set()
    
    # Centralizar janela
    login_window.update_idletasks()
    width = 400
    height = 300
    x = (login_window.winfo_screenwidth() // 2) - (width // 2)
    y = (login_window.winfo_screenheight() // 2) - (height // 2)
    login_window.geometry(f'{width}x{height}+{x}+{y}')
    
    # Conteúdo da janela
    title_label = tk.Label(login_window, 
                          text="Sistema CRM\nCompressores", 
                          font=('Arial', 18, 'bold'),
                          bg='white')
    title_label.pack(pady=30)
    
    # Campo usuário
    tk.Label(login_window, text="Usuário:", bg='white').pack()
    username_entry = tk.Entry(login_window, width=20)
    username_entry.pack(pady=5)
    
    # Campo senha
    tk.Label(login_window, text="Senha:", bg='white').pack()
    password_entry = tk.Entry(login_window, show="*", width=20)
    password_entry.pack(pady=5)
    
    def fazer_login():
        usuario = username_entry.get()
        senha = password_entry.get()
        
        if usuario == "admin" and senha == "admin":
            messagebox.showinfo("Sucesso", "Login realizado com sucesso!")
            login_window.destroy()
            root.quit()
        else:
            messagebox.showerror("Erro", "Usuário ou senha incorretos!")
    
    # Botão login
    login_btn = tk.Button(login_window, text="Entrar", command=fazer_login)
    login_btn.pack(pady=20)
    
    # Botão fechar
    def on_closing():
        root.quit()
    
    login_window.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Focar no campo usuário
    username_entry.focus()
    
    print("✅ Janela de login criada! Mostrando...")
    
    # Forçar janela para frente
    login_window.lift()
    login_window.attributes('-topmost', True)
    login_window.after_idle(lambda: login_window.attributes('-topmost', False))
    
    root.mainloop()
    
    print("Aplicação encerrada.")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()