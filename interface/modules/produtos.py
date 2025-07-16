import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from .base_module import BaseModule
from database import DB_NAME
from utils.formatters import format_currency, clean_number

class ProdutosModule(BaseModule):
    def setup_ui(self):
        container = tk.Frame(self.frame, bg='#f8fafc')
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        self.create_header(container)
        
        # Notebook
        self.notebook = ttk.Notebook(container)
        self.notebook.pack(fill="both", expand=True, pady=(20, 0))
        
        # Abas
        self.create_novo_produto_tab()
        self.create_lista_produtos_tab()
        
        self.current_produto_id = None
        self.carregar_produtos()
        
    def create_header(self, parent):
        header_frame = tk.Frame(parent, bg='#f8fafc')
        header_frame.pack(fill="x", pady=(0, 20))
        
        title_label = tk.Label(header_frame, text="Gestão de Produtos/Serviços", 
                               font=('Arial', 18, 'bold'), bg='#f8fafc', fg='#1e293b')
        title_label.pack(side="left")
        
    def create_novo_produto_tab(self):
        produto_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(produto_frame, text="Novo Produto/Serviço")
        
        content_frame = tk.Frame(produto_frame, bg='white', padx=20, pady=20)
        content_frame.pack(fill="both", expand=True)
        
        # Seção principal
        section_frame = self.create_section_frame(content_frame, "Dados do Produto/Serviço")
        section_frame.pack(fill="x", pady=(0, 15))
        
        fields_frame = tk.Frame(section_frame, bg='white')
        fields_frame.pack(fill="x")
        
        # Variáveis
        self.nome_var = tk.StringVar()
        self.tipo_var = tk.StringVar(value="Produto")
        self.ncm_var = tk.StringVar()
        self.valor_var = tk.StringVar(value="0.00")
        self.descricao_var = tk.StringVar()
        self.ativo_var = tk.BooleanVar(value=True)
        
        row = 0
        
        # Nome
        tk.Label(fields_frame, text="Nome *:", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.nome_var, font=('Arial', 10), width=40).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Tipo
        tk.Label(fields_frame, text="Tipo *:", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tipo_combo = ttk.Combobox(fields_frame, textvariable=self.tipo_var, 
                                 values=["Produto", "Serviço", "Kit"], width=37, state="readonly")
        tipo_combo.grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # NCM
        tk.Label(fields_frame, text="NCM:", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.ncm_var, font=('Arial', 10), width=40).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Valor Unitário
        tk.Label(fields_frame, text="Valor Unitário:", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.valor_var, font=('Arial', 10), width=40).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Descrição
        tk.Label(fields_frame, text="Descrição:", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.descricao_var, font=('Arial', 10), width=40).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Ativo
        tk.Label(fields_frame, text="Ativo:", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Checkbutton(fields_frame, variable=self.ativo_var, bg='white').grid(row=row, column=1, sticky="w", padx=(10, 0), pady=5)
        
        fields_frame.grid_columnconfigure(1, weight=1)
        
        # Botões
        buttons_frame = tk.Frame(content_frame, bg='white')
        buttons_frame.pack(fill="x", pady=(20, 0))
        
        novo_btn = self.create_button(buttons_frame, "Novo Produto", self.novo_produto, bg='#e2e8f0', fg='#475569')
        novo_btn.pack(side="left", padx=(0, 10))
        
        salvar_btn = self.create_button(buttons_frame, "Salvar Produto", self.salvar_produto)
        salvar_btn.pack(side="left")
        
    def create_lista_produtos_tab(self):
        lista_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(lista_frame, text="Lista de Produtos")
        
        container = tk.Frame(lista_frame, bg='white', padx=20, pady=20)
        container.pack(fill="both", expand=True)
        
        # Frame de busca
        search_frame, self.search_var = self.create_search_frame(container, command=self.buscar_produtos)
        search_frame.pack(fill="x", pady=(0, 15))
        
        # Treeview
        columns = ("nome", "tipo", "valor", "ativo")
        self.produtos_tree = ttk.Treeview(container, columns=columns, show="headings", height=15)
        
        self.produtos_tree.heading("nome", text="Nome")
        self.produtos_tree.heading("tipo", text="Tipo")
        self.produtos_tree.heading("valor", text="Valor")
        self.produtos_tree.heading("ativo", text="Ativo")
        
        self.produtos_tree.column("nome", width=300)
        self.produtos_tree.column("tipo", width=100)
        self.produtos_tree.column("valor", width=120)
        self.produtos_tree.column("ativo", width=80)
        
        # Scrollbar
        lista_scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.produtos_tree.yview)
        self.produtos_tree.configure(yscrollcommand=lista_scrollbar.set)
        
        self.produtos_tree.pack(side="left", fill="both", expand=True)
        lista_scrollbar.pack(side="right", fill="y")
        
        # Botões
        lista_buttons = tk.Frame(container, bg='white')
        lista_buttons.pack(fill="x", pady=(15, 0))
        
        editar_btn = self.create_button(lista_buttons, "Editar", self.editar_produto)
        editar_btn.pack(side="left", padx=(0, 10))
        
        ativar_btn = self.create_button(lista_buttons, "Ativar/Desativar", self.toggle_ativo, bg='#f59e0b')
        ativar_btn.pack(side="left")
        
    def novo_produto(self):
        self.current_produto_id = None
        self.nome_var.set("")
        self.tipo_var.set("Produto")
        self.ncm_var.set("")
        self.valor_var.set("0.00")
        self.descricao_var.set("")
        self.ativo_var.set(True)
        
    def salvar_produto(self):
        nome = self.nome_var.get().strip()
        tipo = self.tipo_var.get()
        
        if not nome:
            self.show_warning("O nome é obrigatório.")
            return
            
        if not tipo:
            self.show_warning("Selecione o tipo.")
            return
            
        try:
            valor = clean_number(self.valor_var.get())
        except ValueError:
            self.show_warning("Valor inválido.")
            return
            
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            dados = (
                nome, tipo, self.ncm_var.get().strip(),
                valor, self.descricao_var.get().strip(),
                1 if self.ativo_var.get() else 0
            )
            
            if self.current_produto_id:
                c.execute("""
                    UPDATE produtos SET nome = ?, tipo = ?, ncm = ?, valor_unitario = ?,
                                      descricao = ?, ativo = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, dados + (self.current_produto_id,))
            else:
                c.execute("""
                    INSERT INTO produtos (nome, tipo, ncm, valor_unitario, descricao, ativo)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, dados)
                self.current_produto_id = c.lastrowid
            
            conn.commit()
            self.show_success("Produto salvo com sucesso!")
            
            # Emitir evento
            self.emit_event('produto_created')
            
            self.carregar_produtos()
            
        except sqlite3.Error as e:
            self.show_error(f"Erro ao salvar produto: {e}")
        finally:
            conn.close()
            
    def carregar_produtos(self):
        for item in self.produtos_tree.get_children():
            self.produtos_tree.delete(item)
            
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            c.execute("""
                SELECT id, nome, tipo, valor_unitario, ativo
                FROM produtos
                ORDER BY nome
            """)
            
            for row in c.fetchall():
                produto_id, nome, tipo, valor, ativo = row
                self.produtos_tree.insert("", "end", values=(
                    nome,
                    tipo,
                    format_currency(valor),
                    "Sim" if ativo else "Não"
                ), tags=(produto_id,))
                
        except sqlite3.Error as e:
            self.show_error(f"Erro ao carregar produtos: {e}")
        finally:
            conn.close()
            
    def buscar_produtos(self):
        termo = self.search_var.get().strip()
        
        for item in self.produtos_tree.get_children():
            self.produtos_tree.delete(item)
            
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            if termo:
                c.execute("""
                    SELECT id, nome, tipo, valor_unitario, ativo
                    FROM produtos
                    WHERE nome LIKE ? OR tipo LIKE ? OR descricao LIKE ?
                    ORDER BY nome
                """, (f"%{termo}%", f"%{termo}%", f"%{termo}%"))
            else:
                c.execute("""
                    SELECT id, nome, tipo, valor_unitario, ativo
                    FROM produtos
                    ORDER BY nome
                """)
            
            for row in c.fetchall():
                produto_id, nome, tipo, valor, ativo = row
                self.produtos_tree.insert("", "end", values=(
                    nome,
                    tipo,
                    format_currency(valor),
                    "Sim" if ativo else "Não"
                ), tags=(produto_id,))
                
        except sqlite3.Error as e:
            self.show_error(f"Erro ao buscar produtos: {e}")
        finally:
            conn.close()
            
    def editar_produto(self):
        selected = self.produtos_tree.selection()
        if not selected:
            self.show_warning("Selecione um produto para editar.")
            return
            
        tags = self.produtos_tree.item(selected[0])['tags']
        if not tags:
            return
            
        produto_id = tags[0]
        self.carregar_produto_para_edicao(produto_id)
        self.notebook.select(0)
        
    def carregar_produto_para_edicao(self, produto_id):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            c.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
            produto = c.fetchone()
            
            if not produto:
                self.show_error("Produto não encontrado.")
                return
                
            self.current_produto_id = produto_id
            self.nome_var.set(produto[1] or "")  # nome
            self.tipo_var.set(produto[2] or "Produto")  # tipo
            self.ncm_var.set(produto[3] or "")  # ncm
            self.valor_var.set(f"{produto[4]:.2f}" if produto[4] else "0.00")  # valor_unitario
            self.descricao_var.set(produto[5] or "")  # descricao
            self.ativo_var.set(bool(produto[6]))  # ativo
            
        except sqlite3.Error as e:
            self.show_error(f"Erro ao carregar produto: {e}")
        finally:
            conn.close()
            
    def toggle_ativo(self):
        selected = self.produtos_tree.selection()
        if not selected:
            self.show_warning("Selecione um produto.")
            return
            
        tags = self.produtos_tree.item(selected[0])['tags']
        if not tags:
            return
            
        produto_id = tags[0]
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            c.execute("SELECT ativo FROM produtos WHERE id = ?", (produto_id,))
            ativo_atual = c.fetchone()[0]
            novo_ativo = 0 if ativo_atual else 1
            
            c.execute("UPDATE produtos SET ativo = ? WHERE id = ?", (novo_ativo, produto_id))
            conn.commit()
            
            self.show_success(f"Produto {'ativado' if novo_ativo else 'desativado'} com sucesso!")
            
            # Emitir evento
            self.emit_event('produto_updated')
            
            self.carregar_produtos()
            
        except sqlite3.Error as e:
            self.show_error(f"Erro ao atualizar produto: {e}")
        finally:
            conn.close()