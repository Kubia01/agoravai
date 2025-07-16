import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib
from database import DB_NAME

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.login_window = tk.Toplevel(root)
        self.login_window.title("Login - CRM Compressores")
        self.login_window.geometry("400x350")
        self.login_window.resizable(False, False)
        self.login_window.configure(bg='#f0f0f0')
        
        # Centralizar janela
        self.center_window()
        
        # Configurar protocolo de fechamento
        self.login_window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.create_widgets()
        
        # Focar na janela de login
        self.login_window.grab_set()
        self.login_window.focus_force()
        
    def center_window(self):
        self.login_window.update_idletasks()
        width = 400
        height = 350
        x = (self.login_window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.login_window.winfo_screenheight() // 2) - (height // 2)
        self.login_window.geometry(f'{width}x{height}+{x}+{y}')
        
    def create_widgets(self):
        # Frame principal
        main_frame = tk.Frame(self.login_window, bg='#f0f0f0', padx=40, pady=40)
        main_frame.pack(expand=True, fill="both")
        
        # Logo/Título
        title_label = tk.Label(main_frame, text="CRM Compressores", 
                              font=('Arial', 20, 'bold'),
                              bg='#f0f0f0',
                              fg='#2c3e50')
        title_label.pack(pady=(0, 10))
        
        subtitle_label = tk.Label(main_frame, text="Sistema de Gestão", 
                                 font=('Arial', 12),
                                 bg='#f0f0f0',
                                 fg='#7f8c8d')
        subtitle_label.pack(pady=(0, 30))
        
        # Campo usuário
        user_label = tk.Label(main_frame, text="Usuário:", 
                             font=('Arial', 10, 'bold'),
                             bg='#f0f0f0',
                             fg='#2c3e50')
        user_label.pack(anchor='w', pady=(0, 5))
        
        self.username_entry = tk.Entry(main_frame, 
                                      font=('Arial', 11),
                                      width=25,
                                      relief='solid',
                                      bd=1)
        self.username_entry.pack(fill='x', pady=(0, 15), ipady=5)
        self.username_entry.focus_set()
        
        # Campo senha
        pass_label = tk.Label(main_frame, text="Senha:", 
                             font=('Arial', 10, 'bold'),
                             bg='#f0f0f0',
                             fg='#2c3e50')
        pass_label.pack(anchor='w', pady=(0, 5))
        
        self.password_entry = tk.Entry(main_frame, 
                                      show="*", 
                                      font=('Arial', 11),
                                      width=25,
                                      relief='solid',
                                      bd=1)
        self.password_entry.pack(fill='x', pady=(0, 25), ipady=5)
        self.password_entry.bind("<Return>", lambda event: self.login())
        
        # Botão login
        login_btn = tk.Button(main_frame, 
                             text="Entrar", 
                             font=('Arial', 11, 'bold'),
                             bg='#3498db',
                             fg='white',
                             relief='flat',
                             cursor='hand2',
                             command=self.login,
                             width=20,
                             pady=8)
        login_btn.pack(fill='x', pady=(0, 20))
        
        # Informações de login
        info_frame = tk.Frame(main_frame, bg='#f0f0f0')
        info_frame.pack(fill='x')
        
        info_label = tk.Label(info_frame, text="Usuários padrão:", 
                             font=('Arial', 9, 'bold'),
                             bg='#f0f0f0',
                             fg='#7f8c8d')
        info_label.pack()
        
        admin_label = tk.Label(info_frame, text="admin / admin123", 
                              font=('Arial', 8),
                              bg='#f0f0f0',
                              fg='#95a5a6')
        admin_label.pack()
        
        master_label = tk.Label(info_frame, text="master / master123", 
                               font=('Arial', 8),
                               bg='#f0f0f0',
                               fg='#95a5a6')
        master_label.pack()
        
    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showwarning("Campos Obrigatórios", "Por favor, preencha usuário e senha.")
            return
            
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        try:
            c.execute("SELECT id, username, role, nome_completo FROM usuarios WHERE username=? AND password=?", 
                     (username, hashed_password))
            user = c.fetchone()
            
            if user:
                user_id, username, role, nome_completo = user
                messagebox.showinfo("Login", f"Bem-vindo, {nome_completo}!")
                
                # Fechar janela de login
                self.login_window.destroy()
                
                # Abrir janela principal
                from interface.main_window import MainWindow
                self.root.deiconify()
                MainWindow(self.root, user_id, username, role, nome_completo)
            else:
                messagebox.showerror("Login", "Usuário ou senha incorretos.")
                self.password_entry.delete(0, tk.END)
                self.username_entry.focus_set()
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro no banco de dados: {e}")
        finally:
            conn.close()
            
    def on_closing(self):
        self.root.quit()