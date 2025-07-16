import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib
from python_app.database import criar_banco, DB_NAME
from interface.login import LoginWindow

def main():
    # Criar banco de dados
    criar_banco()
    
    # Criar janela principal
    root = tk.Tk()
    root.withdraw()  # Esconder janela principal inicialmente
    
    # Configurar estilo
    style = ttk.Style()
    style.theme_use('clam')
    
    # Configurar cores personalizadas
    style.configure('Modern.TFrame', background='#f8fafc')
    style.configure('Card.TFrame', background='white', relief='solid', borderwidth=1)
    style.configure('Card.TLabel', background='white', foreground='#374151', font=('Arial', 10))
    style.configure('Modern.TEntry', fieldbackground='white', borderwidth=1, relief='solid')
    style.configure('Modern.TButton', background='#3b82f6', foreground='white', font=('Arial', 10, 'bold'))
    style.configure('Secondary.TButton', background='#e2e8f0', foreground='#475569', font=('Arial', 10))
    style.configure('Danger.TButton', background='#dc2626', foreground='white', font=('Arial', 10))
    style.configure('Modern.Treeview', background='white', foreground='#374151', font=('Arial', 10))
    style.configure('Modern.Treeview.Heading', background='#f1f5f9', foreground='#1e293b', font=('Arial', 10, 'bold'))
    
    # Mostrar tela de login
    login_window = LoginWindow(root)
    
    root.mainloop()

if __name__ == "__main__":
    main()