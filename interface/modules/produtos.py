import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from database import DB_NAME
from .base_module import BaseModule

class ProdutosModule(BaseModule):
    def setup_ui(self):
        # Container principal
        container = tk.Frame(self.frame, bg='#f8fafc')
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        self.create_header(container)
        
        # Área principal
        self.create_main_area(container)
        
        # Carregar dados
        self.load_produtos()
        
    def create_header(self, parent):
        header_frame = tk.Frame(parent, bg='#f8fafc')
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Título
        title_label = tk.Label(header_frame, text="Gestão de Produtos/Serviços/Kits", 
                               font=('Arial', 18, 'bold'),
                               bg='#f8fafc',
                               fg='#1e293b')
        title_label.pack(side="left")
        
        # Botões
        buttons_frame = tk.Frame(header_frame, bg='#f8fafc')
        buttons_frame.pack(side="right")
        
        new_btn = tk.Button(buttons_frame, text="➕ Novo Item", 
                            font=('Arial', 10, 'bold'),
                            bg='#3b82f6',
                            fg='white',
                            relief='flat',
                            cursor='hand2',
                            padx=15,
                            pady=8,
                            command=self.new_produto)
        new_btn.pack(side="right", padx=(10, 0))
        
        refresh_btn = tk.Button(buttons_frame, text="🔄 Atualizar", 
                               font=('Arial', 10),
                               bg='#e2e8f0',
                               fg='#475569',
                               relief='flat',
                               cursor='hand2',
                               padx=15,
                               pady=8,
                               command=self.load_produtos)
        refresh_btn.pack(side="right")
        
    def create_main_area(self, parent):
        # Frame principal
        main_frame = tk.Frame(parent, bg='white', relief='solid', bd=1)
        main_frame.pack(fill="both", expand=True)
        
        content_frame = tk.Frame(main_frame, bg='white', padx=20, pady=20)
        content_frame.pack(fill="both", expand=True)
        
        # Filtros
        filter_frame = tk.Frame(content_frame, bg='white')
        filter_frame.pack(fill="x", pady=(0, 20))
        
        # Filtro por tipo
        tk.Label(filter_frame, text="Filtrar por tipo:", 
                 font=('Arial', 10, 'bold'), bg='white').pack(side="left", padx=(0, 10))
        
        self.filter_tipo_var = tk.StringVar()
        self.filter_tipo_var.set("Todos")
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_tipo_var,
                                   values=["Todos", "Serviço", "Produto", "Kit"], 
                                   width=15, state="readonly")
        filter_combo.pack(side="left", padx=(0, 20))
        filter_combo.bind("<<ComboboxSelected>>", lambda e: self.load_produtos())
        
        # Busca
        tk.Label(filter_frame, text="🔍 Buscar:", 
                 font=('Arial', 10, 'bold'), bg='white').pack(side="left", padx=(0, 10))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        search_entry = tk.Entry(filter_frame, textvariable=self.search_var, 
                               font=('Arial', 11), width=30)
        search_entry.pack(side="left", fill="x", expand=True, ipady=5)
        
        # Tabela de produtos
        self.create_produtos_table(content_frame)
        
    def create_produtos_table(self, parent):
        # Treeview
        columns = ("id", "nome", "tipo", "ncm", "valor", "ativo")
        self.produtos_tree = ttk.Treeview(parent, 
                                        columns=columns,
                                        show="headings")
        
        # Configurar cabeçalhos
        headers = {
            "id": "ID",
            "nome": "Nome",
            "tipo": "Tipo",
            "ncm": "NCM",
            "valor": "Valor Unitário",
            "ativo": "Status"
        }
        
        widths = {
            "id": 60,
            "nome": 300,
            "tipo": 100,
            "ncm": 120,
            "valor": 120,
            "ativo": 80
        }
        
        for col in columns:
            self.produtos_tree.heading(col, text=headers[col])
            self.produtos_tree.column(col, width=widths[col])
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(parent, orient="vertical", 
                                 command=self.produtos_tree.yview)
        self.produtos_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        self.produtos_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind para duplo clique
        self.produtos_tree.bind("<Double-1>", self.on_double_click)
        
        # Menu de contexto
        self.context_menu = tk.Menu(self.produtos_tree, tearoff=0)
        self.context_menu.add_command(label="Editar", command=self.edit_produto)
        self.context_menu.add_command(label="Ativar/Desativar", command=self.toggle_ativo)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Excluir", command=self.delete_produto)
        
        self.produtos_tree.bind("<Button-3>", self.show_context_menu)
        
    def show_context_menu(self, event):
        # Selecionar o item clicado
        item = self.produtos_tree.identify_row(event.y)
        if item:
            self.produtos_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
            
    def load_produtos(self):
        # Limpar tabela
        for item in self.produtos_tree.get_children():
            self.produtos_tree.delete(item)
            
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            query = "SELECT id, nome, tipo, ncm, valor_unitario, ativo FROM produtos"
            params = []
            
            # Aplicar filtros
            conditions = []
            
            # Filtro por tipo
            if self.filter_tipo_var.get() != "Todos":
                conditions.append("tipo = ?")
                params.append(self.filter_tipo_var.get())
            
            # Filtro por busca
            search_term = self.search_var.get().lower()
            if search_term:
                conditions.append("(LOWER(nome) LIKE ? OR LOWER(ncm) LIKE ?)")
                params.extend([f"%{search_term}%", f"%{search_term}%"])
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY tipo, nome"
            
            c.execute(query, params)
            
            for row in c.fetchall():
                produto_id, nome, tipo, ncm, valor, ativo = row
                status = "Ativo" if ativo else "Inativo"
                valor_formatado = f"R$ {valor:.2f}" if valor else "R$ 0,00"
                
                self.produtos_tree.insert("", "end", values=(
                    produto_id, nome, tipo, ncm or "", valor_formatado, status
                ))
                
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao carregar produtos: {e}")
        finally:
            conn.close()
            
    def on_search_change(self, *args):
        self.load_produtos()
        
    def on_double_click(self, event):
        self.edit_produto()
        
    def new_produto(self):
        self.open_produto_form()
        
    def edit_produto(self):
        selected = self.produtos_tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um produto para editar.")
            return
            
        produto_id = self.produtos_tree.item(selected[0])['values'][0]
        self.open_produto_form(produto_id)
        
    def toggle_ativo(self):
        selected = self.produtos_tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um produto.")
            return
            
        produto_id = self.produtos_tree.item(selected[0])['values'][0]
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            # Alternar status ativo
            c.execute("UPDATE produtos SET ativo = NOT ativo WHERE id = ?", (produto_id,))
            conn.commit()
            
            messagebox.showinfo("Sucesso", "Status alterado com sucesso!")
            self.load_produtos()
            
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao alterar status: {e}")
        finally:
            conn.close()
            
    def delete_produto(self):
        selected = self.produtos_tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um produto para excluir.")
            return
            
        produto_id = self.produtos_tree.item(selected[0])['values'][0]
        nome = self.produtos_tree.item(selected[0])['values'][1]
        
        if messagebox.askyesno("Confirmar", f"Deseja realmente excluir '{nome}'?"):
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            
            try:
                # Verificar se está sendo usado em cotações
                c.execute("SELECT COUNT(*) FROM itens_cotacao WHERE produto_id = ?", (produto_id,))
                if c.fetchone()[0] > 0:
                    messagebox.showwarning("Aviso", "Este produto está sendo usado em cotações e não pode ser excluído.")
                    return
                
                # Excluir composição do kit se for kit
                c.execute("DELETE FROM kit_composicao WHERE kit_id = ?", (produto_id,))
                
                # Excluir produto
                c.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
                conn.commit()
                
                messagebox.showinfo("Sucesso", "Produto excluído com sucesso!")
                self.load_produtos()
                
            except sqlite3.Error as e:
                messagebox.showerror("Erro", f"Erro ao excluir produto: {e}")
            finally:
                conn.close()
                
    def open_produto_form(self, produto_id=None):
        from interface.forms.produto_form import ProdutoForm
        
        form = ProdutoForm(self.frame, produto_id)
        form.on_save = self.load_produtos
        
        # Try to notify listeners if the parent has this functionality
        try:
            if hasattr(self.master, 'notify_listeners'):
                form.on_save = lambda: [
                    self.load_produtos(),
                    self.master.notify_listeners('produtos_updated')
                ]
            elif hasattr(self.master, 'master') and hasattr(self.master.master, 'notify_listeners'):
                form.on_save = lambda: [
                    self.load_produtos(),
                    self.master.master.notify_listeners('produtos_updated')
                ]
        except:
            pass  # Callback para recarregar