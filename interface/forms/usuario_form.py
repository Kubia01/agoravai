import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib
from database import DB_NAME

class UsuarioForm:
    def __init__(self, parent, usuario_id=None):
        self.parent = parent
        self.usuario_id = usuario_id
        self.on_save = None
        
        self.create_window()
        self.setup_ui()
        
        if usuario_id:
            self.load_usuario()
            
    def create_window(self):
        self.window = tk.Toplevel(self.parent)
        self.window.title("Usuário")
        self.window.geometry("500x450")
        self.window.transient(self.parent)
        self.window.grab_set()
        self.window.configure(bg='white')
        
        # Centralizar
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (250)
        y = (self.window.winfo_screenheight() // 2) - (225)
        self.window.geometry(f"500x450+{x}+{y}")
        
    def setup_ui(self):
        # Frame principal
        main_frame = tk.Frame(self.window, bg='white', padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Título
        title_label = tk.Label(main_frame, 
                               text="Novo Usuário" if not self.usuario_id else "Editar Usuário",
                               font=('Arial', 16, 'bold'),
                               bg='white',
                               fg='#1e293b')
        title_label.pack(pady=(0, 20))
        
        # Campos
        self.create_fields(main_frame)
        
        # Botões
        self.create_buttons(main_frame)
        
    def create_fields(self, parent):
        # Frame dos campos
        fields_frame = tk.Frame(parent, bg='white')
        fields_frame.pack(fill="both", expand=True)
        
        # Variáveis
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.nome_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.telefone_var = tk.StringVar()
        self.role_var = tk.StringVar()
        
        # Campos
        row = 0
        
        # Nome Completo
        tk.Label(fields_frame, text="Nome Completo *:", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.nome_var, font=('Arial', 10), width=40).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Username
        tk.Label(fields_frame, text="Usuário *:", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.username_var, font=('Arial', 10), width=40).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Password
        password_label = "Nova Senha:" if self.usuario_id else "Senha *:"
        tk.Label(fields_frame, text=password_label, font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.password_var, show="*", font=('Arial', 10), width=40).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Role
        tk.Label(fields_frame, text="Perfil *:", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        role_combo = ttk.Combobox(fields_frame, textvariable=self.role_var, 
                                 values=["operador", "admin"], 
                                 width=37, state="readonly")
        role_combo.grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        self.role_var.set("operador")
        row += 1
        
        # Email
        tk.Label(fields_frame, text="Email:", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.email_var, font=('Arial', 10), width=40).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Telefone
        tk.Label(fields_frame, text="Telefone:", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.telefone_var, font=('Arial', 10), width=40).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Configurar colunas
        fields_frame.grid_columnconfigure(1, weight=1)
        
    def create_buttons(self, parent):
        # Frame dos botões
        buttons_frame = tk.Frame(parent, bg='white')
        buttons_frame.pack(fill="x", pady=(20, 0))
        
        # Botões
        cancel_btn = tk.Button(buttons_frame, text="Cancelar", 
                               font=('Arial', 10),
                               bg='#e2e8f0',
                               fg='#475569',
                               relief='flat',
                               cursor='hand2',
                               padx=15,
                               pady=8,
                               command=self.window.destroy)
        cancel_btn.pack(side="right", padx=(10, 0))
        
        save_btn = tk.Button(buttons_frame, text="Salvar", 
                             font=('Arial', 10, 'bold'),
                             bg='#3b82f6',
                             fg='white',
                             relief='flat',
                             cursor='hand2',
                             padx=15,
                             pady=8,
                             command=self.save_usuario)
        save_btn.pack(side="right")
        
    def load_usuario(self):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            c.execute("SELECT * FROM usuarios WHERE id = ?", (self.usuario_id,))
            usuario = c.fetchone()
            
            if usuario:
                self.username_var.set(usuario[1] or "")
                self.nome_var.set(usuario[4] or "")
                self.email_var.set(usuario[5] or "")
                self.telefone_var.set(usuario[6] or "")
                self.role_var.set(usuario[3] or "operador")
                
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao carregar usuário: {e}")
        finally:
            conn.close()
            
    def save_usuario(self):
        # Validar campos obrigatórios
        if not self.nome_var.get() or not self.username_var.get():
            messagebox.showwarning("Aviso", "Nome completo e usuário são obrigatórios.")
            return
            
        if not self.usuario_id and not self.password_var.get():
            messagebox.showwarning("Aviso", "Senha é obrigatória para novos usuários.")
            return
            
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            if self.usuario_id:
                # Atualizar
                if self.password_var.get():
                    # Atualizar com nova senha
                    hashed_password = hashlib.sha256(self.password_var.get().encode()).hexdigest()
                    c.execute("""
                        UPDATE usuarios SET
                            username=?, password=?, nome_completo=?, email=?, telefone=?, role=?
                        WHERE id=?
                    """, (
                        self.username_var.get(), hashed_password, self.nome_var.get(),
                        self.email_var.get(), self.telefone_var.get(), self.role_var.get(),
                        self.usuario_id
                    ))
                else:
                    # Atualizar sem alterar senha
                    c.execute("""
                        UPDATE usuarios SET
                            username=?, nome_completo=?, email=?, telefone=?, role=?
                        WHERE id=?
                    """, (
                        self.username_var.get(), self.nome_var.get(),
                        self.email_var.get(), self.telefone_var.get(), self.role_var.get(),
                        self.usuario_id
                    ))
            else:
                # Inserir
                hashed_password = hashlib.sha256(self.password_var.get().encode()).hexdigest()
                c.execute("""
                    INSERT INTO usuarios (username, password, nome_completo, email, telefone, role)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    self.username_var.get(), hashed_password, self.nome_var.get(),
                    self.email_var.get(), self.telefone_var.get(), self.role_var.get()
                ))
            
            conn.commit()
            messagebox.showinfo("Sucesso", "Usuário salvo com sucesso!")
            
            if self.on_save:
                self.on_save()
                
            self.window.destroy()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Nome de usuário já existe.")
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao salvar usuário: {e}")
        finally:
            conn.close()