import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib
from database import DB_NAME

class LoginWindow:
    def __init__(self, root):
        self.root = root
        
        # Criar janela de login
        self.login_window = tk.Toplevel(root)
        self.login_window.title("Login - Sistema CRM Compressores")
        self.login_window.geometry("400x350")
        self.login_window.resizable(False, False)
        
        # Configurar janela
        self.login_window.configure(bg='#f8fafc')
        self.login_window.transient(root)
        
        # Fechar aplicação se janela de login for fechada
        self.login_window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Criar interface
        self.create_login_ui()
        
        # Centralizar DEPOIS de criar a UI
        self.center_window()
        
        # Configurações finais para Windows
        self.setup_window_focus()
        
    def center_window(self):
        """Centralizar a janela na tela - versão melhorada para Windows"""
        # Forçar atualização da geometria
        self.login_window.update_idletasks()
        
        # Obter tamanho da janela
        width = 400
        height = 350
        
        # Obter tamanho da tela
        screen_width = self.login_window.winfo_screenwidth()
        screen_height = self.login_window.winfo_screenheight()
        
        # Calcular posição central
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        
        # Aplicar geometria
        self.login_window.geometry(f'{width}x{height}+{x}+{y}')
        
    def setup_window_focus(self):
        """Configurar foco da janela para Windows"""
        # Forçar janela para frente
        self.login_window.lift()
        self.login_window.attributes('-topmost', True)
        
        # Remover topmost após um breve delay
        self.login_window.after(100, lambda: self.login_window.attributes('-topmost', False))
        
        # Focar na janela
        self.login_window.focus_force()
        
        # Capturar todos os eventos
        self.login_window.grab_set()
        
        # Focar no campo de usuário
        self.login_window.after(200, lambda: self.username_entry.focus())
        
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
                             text="Login padrão: admin / admin",
                             font=('Arial', 9),
                             bg='#f8fafc',
                             fg='#6b7280',
                             justify='center')
        info_label.pack()
        
        # Botão de teste
        test_btn = tk.Button(main_frame, 
                            text="Preencher Login Teste",
                            font=('Arial', 9),
                            bg='#e5e7eb',
                            fg='#374151',
                            command=self.fill_test_login)
        test_btn.pack(pady=(10, 0))
        
    def fill_test_login(self):
        """Preencher campos com login de teste"""
        self.username_var.set("admin")
        self.password_var.set("admin")
        
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
                messagebox.showinfo("Sucesso", f"Login realizado com sucesso!\nBem-vindo, {nome_completo}")
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