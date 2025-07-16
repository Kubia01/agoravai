import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from database import DB_NAME
from .base_module import BaseModule

class TecnicosModule(BaseModule):
    def setup_ui(self):
        # Container principal
        container = tk.Frame(self.frame, bg='#f8fafc')
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        self.create_header(container)
        
        # Área principal
        self.create_main_area(container)
        
        # Carregar dados
        self.load_tecnicos()
        
    def create_header(self, parent):
        header_frame = tk.Frame(parent, bg='#f8fafc')
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Título
        title_label = tk.Label(header_frame, text="Gestão de Técnicos", 
                               font=('Arial', 18, 'bold'),
                               bg='#f8fafc',
                               fg='#1e293b')
        title_label.pack(side="left")
        
        # Botões
        buttons_frame = tk.Frame(header_frame, bg='#f8fafc')
        buttons_frame.pack(side="right")
        
        new_btn = tk.Button(buttons_frame, text="➕ Novo Técnico", 
                            font=('Arial', 10, 'bold'),
                            bg='#3b82f6',
                            fg='white',
                            relief='flat',
                            cursor='hand2',
                            padx=15,
                            pady=8,
                            command=self.new_tecnico)
        new_btn.pack(side="right", padx=(10, 0))
        
        refresh_btn = tk.Button(buttons_frame, text="🔄 Atualizar", 
                               font=('Arial', 10),
                               bg='#e2e8f0',
                               fg='#475569',
                               relief='flat',
                               cursor='hand2',
                               padx=15,
                               pady=8,
                               command=self.load_tecnicos)
        refresh_btn.pack(side="right")
        
    def create_main_area(self, parent):
        # Frame principal
        main_frame = tk.Frame(parent, bg='white', relief='solid', bd=1)
        main_frame.pack(fill="both", expand=True)
        
        content_frame = tk.Frame(main_frame, bg='white', padx=20, pady=20)
        content_frame.pack(fill="both", expand=True)
        
        # Tabela de técnicos
        self.create_tecnicos_table(content_frame)
        
    def create_tecnicos_table(self, parent):
        # Treeview
        columns = ("id", "nome", "especialidade", "telefone", "email")
        self.tecnicos_tree = ttk.Treeview(parent, 
                                        columns=columns,
                                        show="headings")
        
        # Configurar cabeçalhos
        headers = {
            "id": "ID",
            "nome": "Nome",
            "especialidade": "Especialidade",
            "telefone": "Telefone",
            "email": "Email"
        }
        
        widths = {
            "id": 60,
            "nome": 200,
            "especialidade": 250,
            "telefone": 150,
            "email": 200
        }
        
        for col in columns:
            self.tecnicos_tree.heading(col, text=headers[col])
            self.tecnicos_tree.column(col, width=widths[col])
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(parent, orient="vertical", 
                                 command=self.tecnicos_tree.yview)
        self.tecnicos_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        self.tecnicos_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind para duplo clique
        self.tecnicos_tree.bind("<Double-1>", self.on_double_click)
        
    def load_tecnicos(self):
        # Limpar tabela
        for item in self.tecnicos_tree.get_children():
            self.tecnicos_tree.delete(item)
            
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            c.execute("SELECT * FROM tecnicos ORDER BY nome")
            
            for row in c.fetchall():
                self.tecnicos_tree.insert("", "end", values=row)
                
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao carregar técnicos: {e}")
        finally:
            conn.close()
            
    def on_double_click(self, event):
        self.edit_tecnico()
        
    def new_tecnico(self):
        self.open_tecnico_form()
        
    def edit_tecnico(self):
        selected = self.tecnicos_tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um técnico para editar.")
            return
            
        tecnico_id = self.tecnicos_tree.item(selected[0])['values'][0]
        self.open_tecnico_form(tecnico_id)
        
    def open_tecnico_form(self, tecnico_id=None):
        from interface.forms.tecnico_form import TecnicoForm
        
        form = TecnicoForm(self.frame, tecnico_id)
        form.on_save = self.load_tecnicos  # Callback para recarregar