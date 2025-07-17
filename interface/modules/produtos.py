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
        self.create_kit_tab()
        self.create_lista_produtos_tab()
        
        self.current_produto_id = None
        self.kit_items = []  # Lista de itens do kit
        self.carregar_produtos()
        
    def create_header(self, parent):
        header_frame = tk.Frame(parent, bg='#f8fafc')
        header_frame.pack(fill="x", pady=(0, 20))
        
        title_label = tk.Label(header_frame, text="Gestão de Produtos/Serviços/Kits", 
                               font=('Arial', 18, 'bold'), bg='#f8fafc', fg='#1e293b')
        title_label.pack(side="left")
        
    def create_novo_produto_tab(self):
        produto_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(produto_frame, text="Produto/Serviço")
        
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
                                 values=["Produto", "Serviço"], width=37, state="readonly")
        tipo_combo.grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        tipo_combo.bind('<<ComboboxSelected>>', self.on_tipo_changed)
        row += 1
        
        # NCM (só para produtos)
        tk.Label(fields_frame, text="NCM:", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        self.ncm_entry = tk.Entry(fields_frame, textvariable=self.ncm_var, font=('Arial', 10), width=40)
        self.ncm_entry.grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Valor Unitário
        tk.Label(fields_frame, text="Valor Unitário:", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        valor_entry = tk.Entry(fields_frame, textvariable=self.valor_var, font=('Arial', 10), width=40)
        valor_entry.grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        valor_entry.bind('<FocusOut>', self.format_valor)
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
        
    def create_kit_tab(self):
        kit_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(kit_frame, text="Kit")
        
        content_frame = tk.Frame(kit_frame, bg='white', padx=20, pady=20)
        content_frame.pack(fill="both", expand=True)
        
        # Seção: Dados do Kit
        section_frame = self.create_section_frame(content_frame, "Dados do Kit")
        section_frame.pack(fill="x", pady=(0, 15))
        
        fields_frame = tk.Frame(section_frame, bg='white')
        fields_frame.pack(fill="x")
        
        # Variáveis do kit
        self.kit_nome_var = tk.StringVar()
        self.kit_descricao_var = tk.StringVar()
        self.kit_ativo_var = tk.BooleanVar(value=True)
        
        row = 0
        
        # Nome do Kit
        tk.Label(fields_frame, text="Nome do Kit *:", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.kit_nome_var, font=('Arial', 10), width=40).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Descrição do Kit
        tk.Label(fields_frame, text="Descrição:", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.kit_descricao_var, font=('Arial', 10), width=40).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Ativo
        tk.Label(fields_frame, text="Ativo:", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Checkbutton(fields_frame, variable=self.kit_ativo_var, bg='white').grid(row=row, column=1, sticky="w", padx=(10, 0), pady=5)
        
        fields_frame.grid_columnconfigure(1, weight=1)
        
        # Seção: Adicionar Itens ao Kit
        add_section = self.create_section_frame(content_frame, "Adicionar Itens ao Kit")
        add_section.pack(fill="x", pady=(15, 0))
        
        add_frame = tk.Frame(add_section, bg='white')
        add_frame.pack(fill="x")
        
        # Variáveis para adicionar itens
        self.item_tipo_var = tk.StringVar(value="Produto")
        self.item_produto_var = tk.StringVar()
        self.item_quantidade_var = tk.StringVar(value="1")
        
        row = 0
        
        # Tipo de Item
        tk.Label(add_frame, text="Tipo:", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        item_tipo_combo = ttk.Combobox(add_frame, textvariable=self.item_tipo_var, 
                                      values=["Produto", "Serviço"], width=15, state="readonly")
        item_tipo_combo.grid(row=row, column=1, sticky="w", padx=(10, 0), pady=5)
        item_tipo_combo.bind('<<ComboboxSelected>>', self.on_item_tipo_changed)
        
        # Produto/Serviço
        tk.Label(add_frame, text="Item:", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=2, sticky="w", pady=5, padx=(20, 0))
        self.item_combo = ttk.Combobox(add_frame, textvariable=self.item_produto_var, width=30, state="readonly")
        self.item_combo.grid(row=row, column=3, sticky="ew", padx=(10, 0), pady=5)
        
        # Quantidade
        tk.Label(add_frame, text="Qtd:", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=4, sticky="w", pady=5, padx=(20, 0))
        tk.Entry(add_frame, textvariable=self.item_quantidade_var, font=('Arial', 10), width=8).grid(row=row, column=5, sticky="w", padx=(10, 0), pady=5)
        
        add_frame.grid_columnconfigure(3, weight=1)
        
        # Botão adicionar item
        add_item_btn = self.create_button(add_frame, "Adicionar Item", self.adicionar_item_kit)
        add_item_btn.grid(row=row, column=6, padx=(20, 0), pady=5)
        
        # Lista de itens do kit
        lista_section = self.create_section_frame(content_frame, "Itens do Kit")
        lista_section.pack(fill="both", expand=True, pady=(15, 0))
        
        # Treeview para itens do kit
        kit_container = tk.Frame(lista_section, bg='white')
        kit_container.pack(fill="both", expand=True)
        
        columns = ("tipo", "nome", "quantidade", "valor_unitario", "valor_total")
        self.kit_tree = ttk.Treeview(kit_container, columns=columns, show="headings", height=8)
        
        # Cabeçalhos
        self.kit_tree.heading("tipo", text="Tipo")
        self.kit_tree.heading("nome", text="Nome")
        self.kit_tree.heading("quantidade", text="Qtd")
        self.kit_tree.heading("valor_unitario", text="Valor Unit.")
        self.kit_tree.heading("valor_total", text="Valor Total")
        
        # Larguras
        self.kit_tree.column("tipo", width=80)
        self.kit_tree.column("nome", width=250)
        self.kit_tree.column("quantidade", width=60)
        self.kit_tree.column("valor_unitario", width=100)
        self.kit_tree.column("valor_total", width=100)
        
        # Scrollbar para kit
        kit_scrollbar = ttk.Scrollbar(kit_container, orient="vertical", command=self.kit_tree.yview)
        self.kit_tree.configure(yscrollcommand=kit_scrollbar.set)
        
        # Pack
        self.kit_tree.pack(side="left", fill="both", expand=True)
        kit_scrollbar.pack(side="right", fill="y")
        
        # Label para valor total do kit
        self.kit_total_label = tk.Label(lista_section, text="Valor Total do Kit: R$ 0,00", 
                                       font=('Arial', 12, 'bold'), bg='white', fg='#1e293b')
        self.kit_total_label.pack(pady=(10, 0))
        
        # Botões do kit
        kit_buttons = tk.Frame(lista_section, bg='white')
        kit_buttons.pack(fill="x", pady=(10, 0))
        
        remover_item_btn = self.create_button(kit_buttons, "Remover Item", self.remover_item_kit, bg='#dc2626')
        remover_item_btn.pack(side="left", padx=(0, 10))
        
        novo_kit_btn = self.create_button(kit_buttons, "Novo Kit", self.novo_kit, bg='#e2e8f0', fg='#475569')
        novo_kit_btn.pack(side="left", padx=(0, 10))
        
        salvar_kit_btn = self.create_button(kit_buttons, "Salvar Kit", self.salvar_kit)
        salvar_kit_btn.pack(side="left")
        
        # Carregar produtos e serviços para os combos
        self.atualizar_combo_items()
        
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

    def on_tipo_changed(self, event):
        """Controla visibilidade do campo NCM baseado no tipo"""
        current_tipo = self.tipo_var.get()
        if current_tipo == "Serviço":
            self.ncm_entry.config(state='disabled')
            self.ncm_var.set("")
        else:
            self.ncm_entry.config(state='normal')
            
    def format_valor(self, event):
        """Formatar valor monetário"""
        valor_str = self.valor_var.get()
        try:
            valor_float = clean_number(valor_str)
            self.valor_var.set(f"{valor_float:.2f}")
        except ValueError:
            self.valor_var.set("0.00")
            
    def novo_produto(self):
        self.current_produto_id = None
        self.nome_var.set("")
        self.tipo_var.set("Produto")
        self.ncm_var.set("")
        self.valor_var.set("0.00")
        self.descricao_var.set("")
        self.ativo_var.set(True)
        self.ncm_entry.config(state='normal') # Habilita o campo NCM para produtos
        
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
        """Carregar lista de produtos"""
        # Limpar lista atual
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
        """Buscar produtos com filtro"""
        termo = self.search_var.get().strip()
        
        # Limpar lista atual
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
        """Editar produto selecionado"""
        selected = self.produtos_tree.selection()
        if not selected:
            self.show_warning("Selecione um produto para editar.")
            return
            
        # Obter ID do produto
        tags = self.produtos_tree.item(selected[0])['tags']
        if not tags:
            return
            
        produto_id = tags[0]
        self.carregar_produto_para_edicao(produto_id)
        
    def carregar_produto_para_edicao(self, produto_id):
        """Carregar dados do produto para edição"""
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            c.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
            produto = c.fetchone()
            
            if not produto:
                self.show_error("Produto não encontrado.")
                return
                
            self.current_produto_id = produto_id
            
            if produto[2] == "Kit":
                # Carregar kit
                self.kit_nome_var.set(produto[1] or "")  # nome
                self.kit_descricao_var.set(produto[5] or "")  # descricao
                self.kit_ativo_var.set(bool(produto[6]))  # ativo
                
                # Carregar itens do kit
                self.kit_items = []
                c.execute("""
                    SELECT p.id, p.nome, p.tipo, p.valor_unitario, ki.quantidade
                    FROM kit_items ki
                    JOIN produtos p ON ki.produto_id = p.id
                    WHERE ki.kit_id = ?
                """, (produto_id,))
                
                for item_row in c.fetchall():
                    item_id, nome, tipo, valor_unitario, quantidade = item_row
                    self.kit_items.append({
                        'id': item_id,
                        'tipo': tipo,
                        'nome': nome,
                        'quantidade': quantidade,
                        'valor_unitario': valor_unitario,
                        'valor_total': quantidade * valor_unitario
                    })
                
                self.atualizar_kit_tree()
                self.notebook.select(1)  # Ir para aba do kit
            else:
                # Carregar produto/serviço
                self.nome_var.set(produto[1] or "")  # nome
                self.tipo_var.set(produto[2] or "Produto")  # tipo
                self.ncm_var.set(produto[3] or "")  # ncm
                self.valor_var.set(f"{produto[4]:.2f}" if produto[4] else "0.00")  # valor_unitario
                self.descricao_var.set(produto[5] or "")  # descricao
                self.ativo_var.set(bool(produto[6]))  # ativo
                
                if produto[2] == "Produto":
                    self.ncm_entry.config(state='normal')
                else:
                    self.ncm_entry.config(state='disabled')
                
                self.notebook.select(0)  # Ir para aba de produto/serviço
                
        except sqlite3.Error as e:
            self.show_error(f"Erro ao carregar produto: {e}")
        finally:
            conn.close()
            
    def toggle_ativo(self):
        """Ativar/desativar produto selecionado"""
        selected = self.produtos_tree.selection()
        if not selected:
            self.show_warning("Selecione um produto para ativar/desativar.")
            return
            
        # Obter ID do produto
        tags = self.produtos_tree.item(selected[0])['tags']
        if not tags:
            return
            
        produto_id = tags[0]
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            # Inverter status ativo
            c.execute("UPDATE produtos SET ativo = NOT ativo WHERE id = ?", (produto_id,))
            conn.commit()
            
            self.show_success("Status do produto alterado com sucesso!")
            self.carregar_produtos()
            
        except sqlite3.Error as e:
            self.show_error(f"Erro ao alterar status: {e}")
        finally:
            conn.close()

    def atualizar_combo_items(self):
        """Atualizar combo com produtos e serviços disponíveis"""
        self.on_item_tipo_changed()
        
    def on_item_tipo_changed(self, event=None):
        """Atualizar combo de itens baseado no tipo selecionado"""
        tipo = self.item_tipo_var.get()
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            c.execute("SELECT id, nome, valor_unitario FROM produtos WHERE tipo = ? AND ativo = 1 ORDER BY nome", (tipo,))
            items = c.fetchall()
            
            values = [f"{item[1]} - R$ {item[2]:.2f}" for item in items]
            self.item_combo['values'] = values
            self.item_combo.set("")
            
            # Armazenar dados para uso posterior
            self.items_data = {f"{item[1]} - R$ {item[2]:.2f}": item for item in items}
            
        except sqlite3.Error as e:
            self.show_error(f"Erro ao carregar itens: {e}")
        finally:
            conn.close()
            
    def adicionar_item_kit(self):
        """Adicionar item ao kit"""
        item_str = self.item_produto_var.get()
        if not item_str:
            self.show_warning("Selecione um item.")
            return
            
        try:
            quantidade = int(self.item_quantidade_var.get())
            if quantidade <= 0:
                raise ValueError
        except ValueError:
            self.show_warning("Quantidade deve ser um número inteiro positivo.")
            return
            
        if item_str not in self.items_data:
            self.show_warning("Item inválido.")
            return
            
        item_data = self.items_data[item_str]
        item_id, nome, valor_unitario = item_data
        
        # Verificar se item já está no kit
        for item in self.kit_items:
            if item['id'] == item_id and item['tipo'] == self.item_tipo_var.get():
                self.show_warning("Este item já está no kit.")
                return
                
        # Adicionar item
        valor_total = quantidade * valor_unitario
        kit_item = {
            'id': item_id,
            'tipo': self.item_tipo_var.get(),
            'nome': nome,
            'quantidade': quantidade,
            'valor_unitario': valor_unitario,
            'valor_total': valor_total
        }
        
        self.kit_items.append(kit_item)
        self.atualizar_kit_tree()
        
        # Limpar campos
        self.item_produto_var.set("")
        self.item_quantidade_var.set("1")
        
    def atualizar_kit_tree(self):
        """Atualizar lista de itens do kit"""
        # Limpar tree
        for item in self.kit_tree.get_children():
            self.kit_tree.delete(item)
            
        total_kit = 0
        
        # Adicionar itens
        for item in self.kit_items:
            self.kit_tree.insert("", "end", values=(
                item['tipo'],
                item['nome'],
                item['quantidade'],
                f"R$ {item['valor_unitario']:.2f}",
                f"R$ {item['valor_total']:.2f}"
            ), tags=(item['id'], item['tipo']))
            
            total_kit += item['valor_total']
            
        # Atualizar label do total
        self.kit_total_label.config(text=f"Valor Total do Kit: R$ {total_kit:.2f}")
        
    def remover_item_kit(self):
        """Remover item selecionado do kit"""
        selected = self.kit_tree.selection()
        if not selected:
            self.show_warning("Selecione um item para remover.")
            return
            
        tags = self.kit_tree.item(selected[0])['tags']
        if not tags:
            return
            
        item_id, item_tipo = tags
        
        # Remover da lista
        self.kit_items = [item for item in self.kit_items 
                         if not (item['id'] == int(item_id) and item['tipo'] == item_tipo)]
        
        self.atualizar_kit_tree()
        
    def novo_kit(self):
        """Limpar formulário para novo kit"""
        self.current_produto_id = None
        self.kit_nome_var.set("")
        self.kit_descricao_var.set("")
        self.kit_ativo_var.set(True)
        self.kit_items = []
        self.atualizar_kit_tree()
        
    def salvar_kit(self):
        """Salvar kit no banco de dados"""
        nome = self.kit_nome_var.get().strip()
        if not nome:
            self.show_warning("O nome do kit é obrigatório.")
            return
            
        if not self.kit_items:
            self.show_warning("O kit deve ter pelo menos um item.")
            return
            
        # Calcular valor total do kit
        valor_total = sum(item['valor_total'] for item in self.kit_items)
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            # Inserir kit como produto
            dados_kit = (
                nome, "Kit", "", valor_total,
                self.kit_descricao_var.get().strip(),
                1 if self.kit_ativo_var.get() else 0
            )
            
            if self.current_produto_id:
                # Atualizar kit existente
                c.execute("""
                    UPDATE produtos SET nome = ?, tipo = ?, ncm = ?, valor_unitario = ?,
                                      descricao = ?, ativo = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, dados_kit + (self.current_produto_id,))
                
                # Remover itens antigos do kit
                c.execute("DELETE FROM kit_items WHERE kit_id = ?", (self.current_produto_id,))
                kit_id = self.current_produto_id
            else:
                # Inserir novo kit
                c.execute("""
                    INSERT INTO produtos (nome, tipo, ncm, valor_unitario, descricao, ativo)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, dados_kit)
                kit_id = c.lastrowid
                self.current_produto_id = kit_id
            
            # Inserir itens do kit
            for item in self.kit_items:
                c.execute("""
                    INSERT INTO kit_items (kit_id, produto_id, quantidade)
                    VALUES (?, ?, ?)
                """, (kit_id, item['id'], item['quantidade']))
            
            conn.commit()
            self.show_success("Kit salvo com sucesso!")
            
            # Emitir evento
            self.emit_event('produto_created')
            
            self.carregar_produtos()
            
        except sqlite3.IntegrityError as e:
            self.show_error("Nome do kit já existe.")
        except sqlite3.Error as e:
            self.show_error(f"Erro ao salvar kit: {e}")
        finally:
            conn.close()