import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from database import DB_NAME
from .base_module import BaseModule

class UsuariosModule(BaseModule):
    def setup_ui(self):
        # Container principal
        container = tk.Frame(self.frame, bg='#f8fafc')
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        self.create_header(container)
        
        # Área principal
        self.create_main_area(container)
        
        # Carregar dados
        self.load_usuarios()
        
    def create_header(self, parent):
        header_frame = tk.Frame(parent, bg='#f8fafc')
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Título
        title_label = tk.Label(header_frame, text="Gestão de Usuários", 
                               font=('Arial', 18, 'bold'),
                               bg='#f8fafc',
                               fg='#1e293b')
        title_label.pack(side="left")
        
        # Botões
        buttons_frame = tk.Frame(header_frame, bg='#f8fafc')
        buttons_frame.pack(side="right")
        
        new_btn = tk.Button(buttons_frame, text="➕ Novo Usuário", 
                            font=('Arial', 10, 'bold'),
                            bg='#3b82f6',
                            fg='white',
                            relief='flat',
                            cursor='hand2',
                            padx=15,
                            pady=8,
                            command=self.new_usuario)
        new_btn.pack(side="right", padx=(10, 0))
        
        refresh_btn = tk.Button(buttons_frame, text="🔄 Atualizar", 
                               font=('Arial', 10),
                               bg='#e2e8f0',
                               fg='#475569',
                               relief='flat',
                               cursor='hand2',
                               padx=15,
                               pady=8,
                               command=self.load_usuarios)
        refresh_btn.pack(side="right")
        
    def create_main_area(self, parent):
        # Frame principal
        main_frame = tk.Frame(parent, bg='white', relief='solid', bd=1)
        main_frame.pack(fill="both", expand=True)
        
        content_frame = tk.Frame(main_frame, bg='white', padx=20, pady=20)
        content_frame.pack(fill="both", expand=True)
        
        # Tabela de usuários
        self.create_usuarios_table(content_frame)
        
    def create_usuarios_table(self, parent):
        # Treeview
        columns = ("id", "username", "nome_completo", "role", "email", "telefone")
        self.usuarios_tree = ttk.Treeview(parent, 
                                        columns=columns,
                                        show="headings")
        
        # Configurar cabeçalhos
        headers = {
            "id": "ID",
            "username": "Usuário",
            "nome_completo": "Nome Completo",
            "role": "Perfil",
            "email": "Email",
            "telefone": "Telefone"
        }
        
        widths = {
            "id": 60,
            "username": 120,
            "nome_completo": 200,
            "role": 100,
            "email": 200,
            "telefone": 150
        }
        
        for col in columns:
            self.usuarios_tree.heading(col, text=headers[col])
            self.usuarios_tree.column(col, width=widths[col])
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(parent, orient="vertical", 
                                 command=self.usuarios_tree.yview)
        self.usuarios_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        self.usuarios_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind para duplo clique
        self.usuarios_tree.bind("<Double-1>", self.on_double_click)
        
    def load_usuarios(self):
        # Limpar tabela
        for item in self.usuarios_tree.get_children():
            self.usuarios_tree.delete(item)
            
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            c.execute("SELECT id, username, nome_completo, role, email, telefone FROM usuarios ORDER BY nome_completo")
            
            for row in c.fetchall():
                self.usuarios_tree.insert("", "end", values=row)
                
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao carregar usuários: {e}")
        finally:
            conn.close()
            
    def on_double_click(self, event):
        self.edit_usuario()
        
    def new_usuario(self):
        self.open_usuario_form()
        
    def edit_usuario(self):
        selected = self.usuarios_tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um usuário para editar.")
            return
            
        usuario_id = self.usuarios_tree.item(selected[0])['values'][0]
        self.open_usuario_form(usuario_id)
        
    def open_usuario_form(self, usuario_id=None):
        from interface.forms.usuario_form import UsuarioForm
        
        form = UsuarioForm(self.frame, usuario_id)
        form.on_save = self.load_usuarios  # Callback para recarregar