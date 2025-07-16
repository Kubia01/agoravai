import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from database import DB_NAME

class CotacaoForm:
    def __init__(self, parent, cotacao_id=None, user_id=None):
        self.parent = parent
        self.cotacao_id = cotacao_id
        self.user_id = user_id
        self.on_save = None
        self.itens = []
        self.clientes_dict = {}
        self.produtos_data = []
        
        self.create_window()
        self.setup_ui()
        
        if cotacao_id:
            self.load_cotacao()

        if hasattr(self.master.master, "register_listener"):
            self.master.master.register_listener(self.on_notify)

    def on_notify(self, event):
        if event == "produtos_updated":
            self.carregar_produtos()
            
    def create_window(self):
        self.window = tk.Toplevel(self.parent)
        self.window.title("Cotação")
        self.window.geometry("1200x900")
        self.window.transient(self.parent)
        self.window.grab_set()
        
    def setup_ui(self):
        # Frame principal com scroll
        main_frame = tk.Frame(self.window, bg='white')
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Canvas e scrollbar
        canvas = tk.Canvas(main_frame, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg='white')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Título
        title_label = tk.Label(self.scrollable_frame, 
                               text="Nova Cotação" if not self.cotacao_id else "Editar Cotação",
                               font=('Arial', 16, 'bold'),
                               bg='white',
                               fg='#1e293b')
        title_label.pack(pady=(0, 20))
        
        # Seção: Dados da Cotação
        self.create_dados_cotacao_section()
        
        # Seção: Descrições
        self.create_descricoes_section()
        
        # Seção: Itens da Cotação
        self.create_itens_section()
        
        # Seção: Condições Comerciais
        self.create_condicoes_section()
        
        # Botões
        self.create_buttons()
        
    def create_dados_cotacao_section(self):
        # Frame da seção
        section_frame = tk.LabelFrame(self.scrollable_frame, text="Dados da Cotação", 
                                      font=('Arial', 12, 'bold'),
                                      bg='white',
                                      padx=15, pady=15)
        section_frame.pack(fill="x", pady=(0, 15))
        
        # Variáveis
        self.numero_var = tk.StringVar()
        self.cliente_var = tk.StringVar()
        self.cliente_search_var = tk.StringVar()
        self.data_validade_var = tk.StringVar()
        self.modelo_var = tk.StringVar()
        self.serie_var = tk.StringVar()
        self.status_var = tk.StringVar()
        self.status_var.set("Em Aberto")
        
        # Grid de campos
        fields_frame = tk.Frame(section_frame, bg='white')
        fields_frame.pack(fill="x")
        
        # Campos
        row = 0
        
        # Número da Proposta
        tk.Label(fields_frame, text="Número da Proposta *:", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.numero_var, font=('Arial', 10), width=30).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Data de Validade
        tk.Label(fields_frame, text="Data de Validade:", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=2, sticky="w", padx=(20, 0), pady=5)
        tk.Entry(fields_frame, textvariable=self.data_validade_var, font=('Arial', 10), width=15).grid(row=row, column=3, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Busca de Cliente
        tk.Label(fields_frame, text="Buscar Cliente *:", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        
        # Frame para busca de cliente
        cliente_frame = tk.Frame(fields_frame, bg='white')
        cliente_frame.grid(row=row, column=1, columnspan=3, sticky="ew", padx=(10, 0), pady=5)
        
        # Entry para busca
        self.cliente_search_entry = tk.Entry(cliente_frame, textvariable=self.cliente_search_var, 
                                           font=('Arial', 10), width=40)
        self.cliente_search_entry.pack(side="left", fill="x", expand=True)
        self.cliente_search_entry.bind('<KeyRelease>', self.on_cliente_search)
        
        # Botão de busca
        search_btn = tk.Button(cliente_frame, text="Buscar",
                              font=('Arial', 10),
                              bg='#3b82f6',
                              fg='white',
                              relief='flat',
                              cursor='hand2',
                              padx=10,
                              command=self.buscar_clientes)
        search_btn.pack(side="left", padx=(5, 0))
        
        row += 1
        
        # Lista de clientes encontrados
        tk.Label(fields_frame, text="Clientes:", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="nw", pady=5)
        
        # Listbox para clientes
        self.clientes_listbox = tk.Listbox(fields_frame, height=4, font=('Arial', 10))
        self.clientes_listbox.grid(row=row, column=1, columnspan=3, sticky="ew", padx=(10, 0), pady=5)
        self.clientes_listbox.bind('<<ListboxSelect>>', self.on_cliente_select)
        
        row += 1
        
        # Cliente selecionado
        tk.Label(fields_frame, text="Cliente Selecionado:", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        self.cliente_selecionado_label = tk.Label(fields_frame, text="Nenhum cliente selecionado", 
                                                 font=('Arial', 10), bg='white', fg='#059669')
        self.cliente_selecionado_label.grid(row=row, column=1, columnspan=3, sticky="w", padx=(10, 0), pady=5)
        
        row += 1
        
        # Modelo do Compressor
        tk.Label(fields_frame, text="Modelo do Compressor:", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.modelo_var, font=('Arial', 10), width=30).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Número de Série
        tk.Label(fields_frame, text="Número de Série:", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=2, sticky="w", padx=(20, 0), pady=5)
        tk.Entry(fields_frame, textvariable=self.serie_var, font=('Arial', 10), width=20).grid(row=row, column=3, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Status
        tk.Label(fields_frame, text="Status:", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        status_combo = ttk.Combobox(fields_frame, textvariable=self.status_var, 
                                   values=["Em Aberto", "Aprovada", "Rejeitada"], 
                                   width=30)
        status_combo.grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Configurar colunas
        fields_frame.grid_columnconfigure(1, weight=1)
        fields_frame.grid_columnconfigure(3, weight=1)
        
        # Carregar clientes inicialmente
        self.load_clientes()
        
    def create_descricoes_section(self):
        # Frame da seção
        section_frame = tk.LabelFrame(self.scrollable_frame, text="Descrições", 
                                      font=('Arial', 12, 'bold'),
                                      bg='white',
                                      padx=15, pady=15)
        section_frame.pack(fill="x", pady=(0, 15))
        
        # Descrição da Atividade
        tk.Label(section_frame, text="Descrição da Atividade:", font=('Arial', 10, 'bold'), bg='white').pack(anchor="w")
        self.descricao_text = tk.Text(section_frame, height=4, wrap=tk.WORD, font=('Arial', 10))
        self.descricao_text.pack(fill="x", pady=(5, 10))
        
        # Relação de Peças
        tk.Label(section_frame, text="Relação de Peças:", font=('Arial', 10, 'bold'), bg='white').pack(anchor="w")
        self.relacao_text = tk.Text(section_frame, height=3, wrap=tk.WORD, font=('Arial', 10))
        self.relacao_text.pack(fill="x", pady=(5, 10))
        
        # Observações
        tk.Label(section_frame, text="Observações:", font=('Arial', 10, 'bold'), bg='white').pack(anchor="w")
        self.observacoes_text = tk.Text(section_frame, height=3, wrap=tk.WORD, font=('Arial', 10))
        self.observacoes_text.pack(fill="x", pady=(5, 0))
        
    def create_itens_section(self):
        # Frame da seção
        section_frame = tk.LabelFrame(self.scrollable_frame, text="Itens da Cotação", 
                                      font=('Arial', 12, 'bold'),
                                      bg='white',
                                      padx=15, pady=15)
        section_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # Frame para adicionar item
        add_frame = tk.Frame(section_frame, bg='#f8fafc', relief='solid', bd=1)
        add_frame.pack(fill="x", pady=(0, 10), padx=5, ipady=10)
        
        # Variáveis para novo item
        self.item_tipo_var = tk.StringVar()
        self.item_tipo_var.set("Serviço")
        self.item_produto_var = tk.StringVar()
        self.item_nome_var = tk.StringVar()
        self.item_qtd_var = tk.StringVar()
        self.item_qtd_var.set("1")
        self.item_valor_var = tk.StringVar()
        self.item_valor_var.set("0.00")
        self.item_desc_var = tk.StringVar()
        # CAMPOS ESPECÍFICOS PARA SERVIÇOS
        self.item_mao_obra_var = tk.StringVar()
        self.item_mao_obra_var.set("0.00")
        self.item_deslocamento_var = tk.StringVar()
        self.item_deslocamento_var.set("0.00")
        self.item_estadia_var = tk.StringVar()
        self.item_estadia_var.set("0.00")
        
        # Primeira linha - Tipo e Item
        linha1 = tk.Frame(add_frame, bg='#f8fafc')
        linha1.pack(fill="x", padx=10, pady=5)
        
        tk.Label(linha1, text="Tipo:", font=('Arial', 10, 'bold'), bg='#f8fafc').pack(side="left")
        tipo_combo = ttk.Combobox(linha1, textvariable=self.item_tipo_var,
                                 values=["Serviço", "Produto", "Kit"], width=10)
        tipo_combo.pack(side="left", padx=(5, 20))
        tipo_combo.bind("<<ComboboxSelected>>", self.on_tipo_change)
        
        tk.Label(linha1, text="Item:", font=('Arial', 10, 'bold'), bg='#f8fafc').pack(side="left")
        self.item_combo = ttk.Combobox(linha1, textvariable=self.item_produto_var, width=40)
        self.item_combo.pack(side="left", padx=(5, 20))
        self.item_combo.bind("<<ComboboxSelected>>", self.on_produto_select)
        
        tk.Label(linha1, text="Qtd:", font=('Arial', 10, 'bold'), bg='#f8fafc').pack(side="left")
        tk.Entry(linha1, textvariable=self.item_qtd_var, width=8).pack(side="left", padx=(5, 0))
        
        # Segunda linha - Valores (varia conforme o tipo)
        self.linha2 = tk.Frame(add_frame, bg='#f8fafc')
        self.linha2.pack(fill="x", padx=10, pady=5)
        
        # Terceira linha - Descrição e botão
        linha3 = tk.Frame(add_frame, bg='#f8fafc')
        linha3.pack(fill="x", padx=10, pady=5)
        
        tk.Label(linha3, text="Descrição:", font=('Arial', 10, 'bold'), bg='#f8fafc').pack(side="left")
        tk.Entry(linha3, textvariable=self.item_desc_var, width=50).pack(side="left", padx=(5, 20))
        
        tk.Button(linha3, text="Adicionar Item",
                  font=('Arial', 10, 'bold'),
                  bg='#10b981',
                  fg='white',
                  relief='flat',
                  cursor='hand2',
                  padx=20,
                  command=self.adicionar_item).pack(side="right")
        
        # Atualizar campos baseado no tipo inicial
        self.on_tipo_change()
        
        # Lista de itens
        self.itens_tree = ttk.Treeview(section_frame, 
                                      columns=("tipo", "nome", "qtd", "valor_unit", "valor_total"),
                                      show="headings",
                                      height=8)
        
        # Cabeçalhos
        self.itens_tree.heading("tipo", text="Tipo")
        self.itens_tree.heading("nome", text="Nome")
        self.itens_tree.heading("qtd", text="Qtd")
        self.itens_tree.heading("valor_unit", text="Valor Unit.")
        self.itens_tree.heading("valor_total", text="Valor Total")
        
        # Larguras
        self.itens_tree.column("tipo", width=80)
        self.itens_tree.column("nome", width=300)
        self.itens_tree.column("qtd", width=60)
        self.itens_tree.column("valor_unit", width=100)
        self.itens_tree.column("valor_total", width=100)
        
        self.itens_tree.pack(fill="both", expand=True, pady=(10, 0))
        
        # Botões para itens
        item_buttons = tk.Frame(section_frame, bg='white')
        item_buttons.pack(fill="x", pady=(10, 0))
        
        tk.Button(item_buttons, text="Remover Item",
                  font=('Arial', 10),
                  bg='#dc2626',
                  fg='white',
                  relief='flat',
                  cursor='hand2',
                  padx=15,
                  command=self.remover_item).pack(side="left", padx=5)
        
        # Label do total
        self.total_label = tk.Label(item_buttons, text="Total: R$ 0,00",
                                   font=('Arial', 12, 'bold'),
                                   bg='white',
                                   fg='#1e293b')
        self.total_label.pack(side="right")
        
    def create_condicoes_section(self):
        # Frame da seção
        section_frame = tk.LabelFrame(self.scrollable_frame, text="Condições Comerciais", 
                                      font=('Arial', 12, 'bold'),
                                      bg='white',
                                      padx=15, pady=15)
        section_frame.pack(fill="x", pady=(0, 15))
        
        # Variáveis
        self.tipo_frete_var = tk.StringVar()
        self.tipo_frete_var.set("FOB")
        self.condicao_pagamento_var = tk.StringVar()
        self.prazo_entrega_var = tk.StringVar()
        self.moeda_var = tk.StringVar()
        self.moeda_var.set("BRL")
        
        # Grid de campos
        fields_frame = tk.Frame(section_frame, bg='white')
        fields_frame.pack(fill="x")
        
        # Tipo de Frete
        tk.Label(fields_frame, text="Tipo de Frete:", font=('Arial', 10, 'bold'), bg='white').grid(row=0, column=0, sticky="w", pady=5)
        frete_combo = ttk.Combobox(fields_frame, textvariable=self.tipo_frete_var,
                                  values=["FOB", "CIF", "Não se aplica"], width=15)
        frete_combo.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Condição de Pagamento
        tk.Label(fields_frame, text="Condição de Pagamento:", font=('Arial', 10, 'bold'), bg='white').grid(row=0, column=2, sticky="w", padx=(20, 0), pady=5)
        tk.Entry(fields_frame, textvariable=self.condicao_pagamento_var, font=('Arial', 10), width=20).grid(row=0, column=3, sticky="ew", padx=(10, 0), pady=5)
        
        # Prazo de Entrega
        tk.Label(fields_frame, text="Prazo de Entrega:", font=('Arial', 10, 'bold'), bg='white').grid(row=1, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.prazo_entrega_var, font=('Arial', 10), width=20).grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Moeda
        tk.Label(fields_frame, text="Moeda:", font=('Arial', 10, 'bold'), bg='white').grid(row=1, column=2, sticky="w", padx=(20, 0), pady=5)
        moeda_combo = ttk.Combobox(fields_frame, textvariable=self.moeda_var,
                                  values=["BRL", "USD", "EUR"], width=10)
        moeda_combo.grid(row=1, column=3, sticky="ew", padx=(10, 0), pady=5)
        
        # Configurar colunas
        fields_frame.grid_columnconfigure(1, weight=1)
        fields_frame.grid_columnconfigure(3, weight=1)
        
    def create_buttons(self):
        # Frame dos botões
        buttons_frame = tk.Frame(self.scrollable_frame, bg='white')
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
                             command=self.save_cotacao)
        save_btn.pack(side="right")
        
        # Botão para gerar PDF
        pdf_btn = tk.Button(buttons_frame, text="Gerar PDF", 
                           font=('Arial', 10, 'bold'),
                           bg='#8b5cf6',
                           fg='white',
                           relief='flat',
                           cursor='hand2',
                           padx=15,
                           pady=8,
                           command=self.gerar_pdf)
        pdf_btn.pack(side="left")
        
    def on_cliente_search(self, event=None):
        # Busca automática enquanto digita
        search_term = self.cliente_search_var.get()
        if len(search_term) >= 2:  # Buscar apenas com 2+ caracteres
            self.buscar_clientes()
    
    def buscar_clientes(self):
        search_term = self.cliente_search_var.get().lower()
        
        # Limpar listbox
        self.clientes_listbox.delete(0, tk.END)
        
        if not search_term:
            return
            
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            c.execute("""
                SELECT id, nome, cnpj FROM clientes 
                WHERE LOWER(nome) LIKE ? OR LOWER(cnpj) LIKE ?
                ORDER BY nome
            """, (f"%{search_term}%", f"%{search_term}%"))
            
            clientes = c.fetchall()
            self.clientes_dict = {}
            
            for cliente in clientes:
                display_text = f"{cliente[1]} - {cliente[2]}"
                self.clientes_listbox.insert(tk.END, display_text)
                self.clientes_dict[display_text] = cliente[0]
                
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao buscar clientes: {e}")
        finally:
            conn.close()
    
    def on_cliente_select(self, event):
        selection = self.clientes_listbox.curselection()
        if selection:
            cliente_text = self.clientes_listbox.get(selection[0])
            self.cliente_var.set(self.clientes_dict[cliente_text])
            self.cliente_selecionado_label.config(text=cliente_text)
    
    def on_tipo_change(self, event=None):
        # Limpar linha2
        for widget in self.linha2.winfo_children():
            widget.destroy()
            
        tipo = self.item_tipo_var.get()
        
        if tipo == "Serviço":
            # Campos para serviço - INCLUINDO TODOS OS CAMPOS SOLICITADOS
            tk.Label(self.linha2, text="Valor Base:", font=('Arial', 10, 'bold'), bg='#f8fafc').pack(side="left")
            tk.Entry(self.linha2, textvariable=self.item_valor_var, width=12).pack(side="left", padx=(5, 20))
            
            tk.Label(self.linha2, text="Mão de Obra:", font=('Arial', 10, 'bold'), bg='#f8fafc').pack(side="left")
            tk.Entry(self.linha2, textvariable=self.item_mao_obra_var, width=12).pack(side="left", padx=(5, 20))
            
            tk.Label(self.linha2, text="Deslocamento:", font=('Arial', 10, 'bold'), bg='#f8fafc').pack(side="left")
            tk.Entry(self.linha2, textvariable=self.item_deslocamento_var, width=12).pack(side="left", padx=(5, 20))
            
            tk.Label(self.linha2, text="Estadia:", font=('Arial', 10, 'bold'), bg='#f8fafc').pack(side="left")
            tk.Entry(self.linha2, textvariable=self.item_estadia_var, width=12).pack(side="left", padx=(5, 0))
        else:
            # Campos para produto/kit
            tk.Label(self.linha2, text="Valor Unitário:", font=('Arial', 10, 'bold'), bg='#f8fafc').pack(side="left")
            tk.Entry(self.linha2, textvariable=self.item_valor_var, width=15).pack(side="left", padx=(5, 0))
            
        # Atualizar combo com produtos do tipo selecionado
        self.load_produtos_por_tipo(tipo)
        
    def load_produtos_por_tipo(self, tipo):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            c.execute("SELECT id, nome, valor_unitario FROM produtos WHERE tipo = ? AND ativo = 1 ORDER BY nome", (tipo,))
            produtos = c.fetchall()
            
            produtos_display = [f"{produto[1]} - R$ {produto[2]:.2f}" for produto in produtos]
            self.item_combo['values'] = produtos_display
            self.produtos_data = produtos  # Guardar dados para uso posterior
            
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao carregar produtos: {e}")
        finally:
            conn.close()
            
    def on_produto_select(self, event=None):
        if not hasattr(self, 'produtos_data'):
            return
            
        selected_index = self.item_combo.current()
        if selected_index >= 0 and selected_index < len(self.produtos_data):
            produto = self.produtos_data[selected_index]
            produto_id, nome, valor_unitario = produto
            
            self.item_nome_var.set(nome)
            self.item_valor_var.set(f"{valor_unitario:.2f}")

    def load_clientes(self):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            c.execute("SELECT id, nome, cnpj FROM clientes ORDER BY nome")
            clientes = c.fetchall()
            
            # Carregar todos os clientes no dicionário
            for cliente in clientes:
                display_text = f"{cliente[1]} - {cliente[2]}"
                self.clientes_dict[display_text] = cliente[0]
            
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao carregar clientes: {e}")
        finally:
            conn.close()
            
    def adicionar_item(self):
        tipo = self.item_tipo_var.get()
        nome = self.item_nome_var.get()
        qtd_str = self.item_qtd_var.get()
        valor_str = self.item_valor_var.get()
        descricao = self.item_desc_var.get()
        
        if not nome:
            messagebox.showwarning("Aviso", "Nome do item é obrigatório.")
            return
            
        try:
            quantidade = float(qtd_str) if qtd_str else 1
            valor_unitario = float(valor_str.replace(',', '.')) if valor_str else 0
            
            if tipo == "Serviço":
                mao_obra = float(self.item_mao_obra_var.get().replace(',', '.')) if self.item_mao_obra_var.get() else 0
                deslocamento = float(self.item_deslocamento_var.get().replace(',', '.')) if self.item_deslocamento_var.get() else 0
                estadia = float(self.item_estadia_var.get().replace(',', '.')) if self.item_estadia_var.get() else 0
                valor_total = quantidade * (valor_unitario + mao_obra + deslocamento + estadia)
                
                item = {
                    "tipo": tipo,
                    "nome": nome,
                    "quantidade": quantidade,
                    "valor_unitario": valor_unitario,
                    "valor_total": valor_total,
                    "descricao": descricao,
                    "mao_obra": mao_obra,
                    "deslocamento": deslocamento,
                    "estadia": estadia
                }
            else:  # Produto ou Kit
                valor_total = quantidade * valor_unitario
                
                item = {
                    "tipo": tipo,
                    "nome": nome,
                    "quantidade": quantidade,
                    "valor_unitario": valor_unitario,
                    "valor_total": valor_total,
                    "descricao": descricao
                }
                
        except ValueError:
            messagebox.showerror("Erro", "Valores devem ser números válidos.")
            return
            
        # Adicionar item à lista
        self.itens.append(item)
        self.atualizar_lista_itens()
        self.calcular_total()
        
        # Limpar campos
        self.item_nome_var.set("")
        self.item_qtd_var.set("1")
        self.item_valor_var.set("0.00")
        self.item_desc_var.set("")
        self.item_mao_obra_var.set("0.00")
        self.item_deslocamento_var.set("0.00")
        self.item_estadia_var.set("0.00")
        self.item_produto_var.set("")
        
    def remover_item(self):
        selected = self.itens_tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um item para remover.")
            return
            
        index = self.itens_tree.index(selected[0])
        del self.itens[index]
        self.atualizar_lista_itens()
        self.calcular_total()
        
    def atualizar_lista_itens(self):
        # Limpar lista
        for item in self.itens_tree.get_children():
            self.itens_tree.delete(item)
            
        # Adicionar itens
        for item in self.itens:
            self.itens_tree.insert("", "end", values=(
                item["tipo"],
                item["nome"],
                item["quantidade"],
                f"R$ {item['valor_unitario']:.2f}",
                f"R$ {item['valor_total']:.2f}"
            ))
            
    def calcular_total(self):
        total = sum(item["valor_total"] for item in self.itens)
        self.total_label.config(text=f"Total: R$ {total:.2f}")
        
    def save_cotacao(self):
        # Validar campos obrigatórios
        if not self.numero_var.get() or not self.cliente_var.get():
            messagebox.showwarning("Aviso", "Número da proposta e cliente são obrigatórios.")
            return
            
        cliente_id = self.cliente_var.get()
        valor_total = sum(item["valor_total"] for item in self.itens)
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            if self.cotacao_id:
                # Atualizar cotação existente
                c.execute("""
                    UPDATE cotacoes SET
                        numero_proposta=?, cliente_id=?, data_validade=?, modelo_compressor=?,
                        numero_serie_compressor=?, descricao_atividade=?, relacao_pecas=?,
                        observacoes=?, valor_total=?, tipo_frete=?, condicao_pagamento=?,
                        prazo_entrega=?, moeda=?, status=?
                    WHERE id=?
                """, (
                    self.numero_var.get(), cliente_id, self.data_validade_var.get(),
                    self.modelo_var.get(), self.serie_var.get(),
                    self.descricao_text.get("1.0", tk.END).strip(),
                    self.relacao_text.get("1.0", tk.END).strip(),
                    self.observacoes_text.get("1.0", tk.END).strip(),
                    valor_total, self.tipo_frete_var.get(), self.condicao_pagamento_var.get(),
                    self.prazo_entrega_var.get(), self.moeda_var.get(), self.status_var.get(),
                    self.cotacao_id
                ))
                
                # Remover itens antigos
                c.execute("DELETE FROM itens_cotacao WHERE cotacao_id=?", (self.cotacao_id,))
            else:
                # Inserir nova cotação
                data_criacao = datetime.now().strftime('%Y-%m-%d')
                
                c.execute("""
                    INSERT INTO cotacoes (
                        numero_proposta, cliente_id, responsavel_id, data_criacao, data_validade,
                        modelo_compressor, numero_serie_compressor, descricao_atividade,
                        relacao_pecas, observacoes, valor_total, tipo_frete, condicao_pagamento,
                        prazo_entrega, moeda, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.numero_var.get(), cliente_id, self.user_id, data_criacao,
                    self.data_validade_var.get(), self.modelo_var.get(), self.serie_var.get(),
                    self.descricao_text.get("1.0", tk.END).strip(),
                    self.relacao_text.get("1.0", tk.END).strip(),
                    self.observacoes_text.get("1.0", tk.END).strip(),
                    valor_total, self.tipo_frete_var.get(), self.condicao_pagamento_var.get(),
                    self.prazo_entrega_var.get(), self.moeda_var.get(), self.status_var.get()
                ))
                
                self.cotacao_id = c.lastrowid
            
            # Inserir itens
            for item in self.itens:
                c.execute("""
                    INSERT INTO itens_cotacao (
                        cotacao_id, tipo, item_nome, quantidade, descricao,
                        valor_unitario, valor_total_item, mao_obra, deslocamento, estadia
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.cotacao_id, item["tipo"], item["nome"], item["quantidade"],
                    item["descricao"], item["valor_unitario"], item["valor_total"],
                    item.get("mao_obra", 0), item.get("deslocamento", 0), item.get("estadia", 0)
                ))
            
            conn.commit()
            messagebox.showinfo("Sucesso", "Cotação salva com sucesso!")
            
            if self.on_save:
                self.on_save()
                
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Número da proposta já existe.")
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao salvar cotação: {e}")
        finally:
            conn.close()
            
    def gerar_pdf(self):
        if not self.cotacao_id:
            messagebox.showwarning("Aviso", "Salve a cotação antes de gerar o PDF.")
            return
            
        try:
            from python_app.pdf_generator_cotacao import gerar_pdf_cotacao
            sucesso, resultado = gerar_pdf_cotacao(self.cotacao_id, DB_NAME)
            
            if sucesso:
                messagebox.showinfo("Sucesso", f"PDF gerado com sucesso!\nArquivo: {resultado}")
                # Abrir o arquivo PDF
                import os
                os.startfile(resultado)
            else:
                messagebox.showerror("Erro", f"Erro ao gerar PDF: {resultado}")
                
        except ImportError:
            messagebox.showerror("Erro", "Módulo de geração de PDF não encontrado. Instale: pip install fpdf2")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {e}")
            
    def load_cotacao(self):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            c.execute("""
                SELECT c.*, cl.nome as cliente_nome, cl.cnpj as cliente_cnpj
                FROM cotacoes c
                JOIN clientes cl ON c.cliente_id = cl.id
                WHERE c.id = ?
            """, (self.cotacao_id,))
            
            cotacao = c.fetchone()
            if cotacao:
                self.numero_var.set(cotacao[1])
                
                # Configurar cliente
                cliente_display = f"{cotacao[-2]} - {cotacao[-1]}"  # nome - cnpj
                self.cliente_var.set(cotacao[2])  # cliente_id
                self.cliente_selecionado_label.config(text=cliente_display)
                
                self.data_validade_var.set(cotacao[5] or "")
                self.modelo_var.set(cotacao[6] or "")
                self.serie_var.set(cotacao[7] or "")
                self.status_var.set(cotacao[15] or "Em Aberto")
                
                if cotacao[8]:  # descricao_atividade
                    self.descricao_text.insert("1.0", cotacao[8])
                if cotacao[17]:  # relacao_pecas
                    self.relacao_text.insert("1.0", cotacao[17])
                if cotacao[9]:  # observacoes
                    self.observacoes_text.insert("1.0", cotacao[9])
                
                self.tipo_frete_var.set(cotacao[11] or "FOB")
                self.condicao_pagamento_var.set(cotacao[12] or "")
                self.prazo_entrega_var.set(cotacao[13] or "")
                self.moeda_var.set(cotacao[14] or "BRL")
                
                # Carregar itens
                c.execute("""
                    SELECT tipo, item_nome, quantidade, descricao, valor_unitario, valor_total_item, mao_obra, deslocamento, estadia
                    FROM itens_cotacao WHERE cotacao_id = ?
                """, (self.cotacao_id,))
                
                self.itens = []
                for item_row in c.fetchall():
                    item = {
                        "tipo": item_row[0],
                        "nome": item_row[1],
                        "quantidade": item_row[2],
                        "descricao": item_row[3],
                        "valor_unitario": item_row[4],
                        "valor_total": item_row[5],
                        "mao_obra": item_row[6] or 0,
                        "deslocamento": item_row[7] or 0,
                        "estadia": item_row[8] or 0
                    }
                    self.itens.append(item)
                
                self.atualizar_lista_itens()
                self.calcular_total()
                
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao carregar cotação: {e}")
        finally:
            conn.close()