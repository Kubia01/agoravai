import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib
from database import criar_banco, DB_NAME
from interface.login import LoginWindow

def main():
    # Criar banco de dados
    criar_banco()
    
    # Criar janela principal
    root = tk.Tk()
    root.withdraw()  # Esconder janela principal inicialmente
    
    # Mostrar tela de login
    login_window = LoginWindow(root)
    
    root.mainloop()

if __name__ == "__main__":
    main()