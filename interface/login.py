import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib
from database import DB_NAME

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.login_window = tk.Toplevel(root)
        self.login_window.title("Login - Sistema CRM Compressores")
        self.login_window.geometry("400x300")
        self.login_window.resizable(False, False)
        
        # Centralizar janela
        self.center_window()
        
        # Configurar janela
        self.login_window.configure(bg='#f8fafc')
        self.login_window.transient(root)
        self.login_window.grab_set()
        
        # Fechar aplicação se janela de login for fechada
        self.login_window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.create_login_ui()
        
        # Focar no campo de usuário
        self.username_entry.focus()
        
    def center_window(self):
        """Centralizar a janela na tela"""
        self.login_window.update_idletasks()
        width = self.login_window.winfo_width()
        height = self.login_window.winfo_height()
        x = (self.login_window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.login_window.winfo_screenheight() // 2) - (height // 2)
        self.login_window.geometry(f'{width}x{height}+{x}+{y}')
        
    def create_login_ui(self):
        # Container principal
        main_frame = tk.Frame(self.login_window, bg='#f8fafc')
        main_frame.pack(fill="both", expand=True, padx=40, pady=40)
        
        # Título
        title_label = tk.Label(main_frame, 
                              text="Sistema CRM\nCompressores", 
                              font=('Arial', 18, 'bold'),
                              bg='#f8fafc',
                              fg='#1e293b',
                              justify='center')
        title_label.pack(pady=(0, 30))
        
        # Frame dos campos
        fields_frame = tk.Frame(main_frame, bg='#f8fafc')
        fields_frame.pack(fill="x", pady=(0, 20))
        
        # Campo usuário
        tk.Label(fields_frame, text="Usuário:", 
                font=('Arial', 10, 'bold'),
                bg='#f8fafc',
                fg='#374151').pack(anchor="w", pady=(0, 5))
        
        self.username_var = tk.StringVar()
        self.username_entry = tk.Entry(fields_frame, 
                                      textvariable=self.username_var,
                                      font=('Arial', 11),
                                      relief='solid',
                                      bd=1)
        self.username_entry.pack(fill="x", ipady=8, pady=(0, 15))
        
        # Campo senha
        tk.Label(fields_frame, text="Senha:", 
                font=('Arial', 10, 'bold'),
                bg='#f8fafc',
                fg='#374151').pack(anchor="w", pady=(0, 5))
        
        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(fields_frame, 
                                      textvariable=self.password_var,
                                      font=('Arial', 11),
                                      relief='solid',
                                      bd=1,
                                      show="*")
        self.password_entry.pack(fill="x", ipady=8)
        
        # Botão login
        login_btn = tk.Button(main_frame, 
                             text="Entrar",
                             font=('Arial', 11, 'bold'),
                             bg='#3b82f6',
                             fg='white',
                             relief='flat',
                             cursor='hand2',
                             command=self.login)
        login_btn.pack(fill="x", ipady=10, pady=(20, 0))
        
        # Bind Enter key
        self.login_window.bind('<Return>', lambda e: self.login())
        
        # Info de login padrão
        info_frame = tk.Frame(main_frame, bg='#f8fafc')
        info_frame.pack(fill="x", pady=(20, 0))
        
        info_label = tk.Label(info_frame, 
                             text="Usuários padrão:\nadmin / admin123\nmaster / master123",
                             font=('Arial', 8),
                             bg='#f8fafc',
                             fg='#6b7280',
                             justify='center')
        info_label.pack()
        
    def login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        if not username or not password:
            messagebox.showerror("Erro", "Preencha todos os campos!")
            return
            
        # Verificar credenciais
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            c.execute("SELECT id, role, nome_completo FROM usuarios WHERE username=? AND password=?", 
                     (username, password_hash))
            user = c.fetchone()
            
            if user:
                user_id, role, nome_completo = user
                self.login_window.destroy()
                
                # Importar e abrir janela principal
                from interface.main_window import MainWindow
                main_window = MainWindow(self.root, user_id, role, nome_completo)
                
            else:
                messagebox.showerror("Erro", "Usuário ou senha incorretos!")
                self.password_var.set("")
                self.password_entry.focus()
                
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro no banco de dados: {e}")
        finally:
            conn.close()
            
    def on_closing(self):
        """Fechar aplicação quando a janela de login é fechada"""
        self.root.quit()