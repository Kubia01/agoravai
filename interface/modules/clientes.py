import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from database import DB_NAME
from .base_module import BaseModule
from utils.formatters import format_cnpj, format_phone

class ClientesModule(BaseModule):
    def setup_ui(self):
        # Container principal
        container = tk.Frame(self.frame, bg='#f8fafc')
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        self.create_header(container)
        
        # Área principal
        self.create_main_area(container)
        
        # Carregar dados
        self.load_clientes()
        
    def create_header(self, parent):
        header_frame = tk.Frame(parent, bg='#f8fafc')
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Título
        title_label = tk.Label(header_frame, text="Gestão de Clientes", 
                               font=('Arial', 18, 'bold'),
                               bg='#f8fafc',
                               fg='#1e293b')
        title_label.pack(side="left")
        
        # Botões
        buttons_frame = tk.Frame(header_frame, bg='#f8fafc')
        buttons_frame.pack(side="right")
        
        new_btn = tk.Button(buttons_frame, text="➕ Novo Cliente", 
                            font=('Arial', 10, 'bold'),
                            bg='#3b82f6',
                            fg='white',
                            relief='flat',
                            cursor='hand2',
                            padx=15,
                            pady=8,
                            command=self.new_cliente)
        new_btn.pack(side="right", padx=(10, 0))
        
        refresh_btn = tk.Button(buttons_frame, text="🔄 Atualizar", 
                               font=('Arial', 10),
                               bg='#e2e8f0',
                               fg='#475569',
                               relief='flat',
                               cursor='hand2',
                               padx=15,
                               pady=8,
                               command=self.load_clientes)
        refresh_btn.pack(side="right")
        
    def create_main_area(self, parent):
        # Frame principal
        main_frame = tk.Frame(parent, bg='white', relief='solid', bd=1)
        main_frame.pack(fill="both", expand=True)
        
        content_frame = tk.Frame(main_frame, bg='white', padx=20, pady=20)
        content_frame.pack(fill="both", expand=True)
        
        # Barra de busca
        search_frame = tk.Frame(content_frame, bg='white')
        search_frame.pack(fill="x", pady=(0, 20))
        
        search_label = tk.Label(search_frame, text="🔍 Buscar:", 
                                font=('Arial', 12),
                                bg='white',
                                fg='#374151')
        search_label.pack(side="left", padx=(0, 10))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, 
                               font=('Arial', 11),
                               width=50,
                               relief='solid',
                               bd=1)
        search_entry.pack(side="left", fill="x", expand=True, ipady=5)
        
        # Grid de clientes
        self.create_clientes_grid(content_frame)
        
    def create_clientes_grid(self, parent):
        # Frame com scroll
        canvas = tk.Canvas(parent, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg='white')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
    def load_clientes(self, search_term=""):
        # Limpar grid
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            query = "SELECT * FROM clientes"
            params = []
            
            if search_term:
                query += " WHERE LOWER(nome) LIKE ? OR LOWER(cnpj) LIKE ? OR LOWER(email) LIKE ?"
                search_param = f"%{search_term}%"
                params = [search_param, search_param, search_param]
                
            query += " ORDER BY nome"
            
            c.execute(query, params)
            clientes = c.fetchall()
            
            # Criar cards
            row = 0
            col = 0
            max_cols = 3
            
            for cliente in clientes:
                card = self.create_cliente_card(self.scrollable_frame, cliente)
                card.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
                
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
                    
            # Configurar colunas para expandir
            for i in range(max_cols):
                self.scrollable_frame.grid_columnconfigure(i, weight=1)
                
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao carregar clientes: {e}")
        finally:
            conn.close()
            
    def create_cliente_card(self, parent, cliente):
        # Card frame
        card = tk.Frame(parent, bg='white', relief='solid', bd=1, padx=15, pady=15)
        
        # Header do card
        header_frame = tk.Frame(card, bg='white')
        header_frame.pack(fill="x")
        
        # Nome do cliente
        nome_label = tk.Label(header_frame, text=cliente[1], 
                              font=('Arial', 14, 'bold'),
                              bg='white',
                              fg='#1e293b')
        nome_label.pack(side="left")
        
        # Botões de ação
        actions_frame = tk.Frame(header_frame, bg='white')
        actions_frame.pack(side="right")
        
        edit_btn = tk.Button(actions_frame, text="✏️", 
                             font=('Arial', 10),
                             bg='#e2e8f0',
                             fg='#475569',
                             relief='flat',
                             cursor='hand2',
                             width=3,
                             command=lambda: self.edit_cliente(cliente[0]))
        edit_btn.pack(side="right", padx=(5, 0))
        
        delete_btn = tk.Button(actions_frame, text="🗑️", 
                               font=('Arial', 10),
                               bg='#dc2626',
                               fg='white',
                               relief='flat',
                               cursor='hand2',
                               width=3,
                               command=lambda: self.delete_cliente(cliente[0]))
        delete_btn.pack(side="right")
        
        # Informações do cliente
        info_frame = tk.Frame(card, bg='white')
        info_frame.pack(fill="x", pady=(10, 0))
        
        # CNPJ
        if cliente[4]:  # cnpj
            cnpj_label = tk.Label(info_frame, text=f"CNPJ: {format_cnpj(cliente[4])}", 
                                  font=('Arial', 10),
                                  bg='white',
                                  fg='#374151')
            cnpj_label.pack(anchor="w")
            
        # Telefone
        if cliente[10]:  # telefone
            tel_label = tk.Label(info_frame, text=f"📞 {format_phone(cliente[10])}", 
                                 font=('Arial', 10),
                                 bg='white',
                                 fg='#374151')
            tel_label.pack(anchor="w")
            
        # Email
        if cliente[11]:  # email
            email_label = tk.Label(info_frame, text=f"✉️ {cliente[11]}", 
                                   font=('Arial', 10),
                                   bg='white',
                                   fg='#374151')
            email_label.pack(anchor="w")
            
        # Cidade/Estado
        if cliente[6] and cliente[7]:  # cidade, estado
            loc_label = tk.Label(info_frame, text=f"📍 {cliente[6]}/{cliente[7]}", 
                                 font=('Arial', 10),
                                 bg='white',
                                 fg='#374151')
            loc_label.pack(anchor="w")
            
        return card
        
    def on_search_change(self, *args):
        search_term = self.search_var.get().lower()
        self.load_clientes(search_term)
        
    def new_cliente(self):
        self.open_cliente_form()
        
    def edit_cliente(self, cliente_id):
        self.open_cliente_form(cliente_id)
        
    def delete_cliente(self, cliente_id):
        if messagebox.askyesno("Confirmar", "Deseja realmente excluir este cliente?"):
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            
            try:
                c.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
                conn.commit()
                
                messagebox.showinfo("Sucesso", "Cliente excluído com sucesso!")
                self.load_clientes()
                
            except sqlite3.Error as e:
                messagebox.showerror("Erro", f"Erro ao excluir cliente: {e}")
            finally:
                conn.close()
                
    def open_cliente_form(self, cliente_id=None):
        from interface.forms.cliente_form import ClienteForm
        
        form = ClienteForm(self.frame, cliente_id)
        # Adicionar callback para atualizar combobox de clientes em outros módulos
        form.on_save = lambda: self.load_clientes()
        
        # Try to notify listeners if the parent has this functionality
        try:
            if hasattr(self.master, 'notify_listeners'):
                form.on_save = lambda: [
                    self.load_clientes(),
                    self.master.notify_listeners('clientes_updated')
                ]
            elif hasattr(self.master, 'master') and hasattr(self.master.master, 'notify_listeners'):
                form.on_save = lambda: [
                    self.load_clientes(),
                    self.master.master.notify_listeners('clientes_updated')
                ]
        except:
            pass