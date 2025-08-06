import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sqlite3
from datetime import datetime
from .base_module import BaseModule
from database import DB_NAME
from utils.formatters import format_currency, format_date, clean_number
from pdf_generators.cotacao_nova import gerar_pdf_cotacao_nova
from collections import Counter

class CotacoesModule(BaseModule):
    def setup_ui(self):
        self.ensure_responsavel_id_column()
        # Container principal
        container = tk.Frame(self.frame, bg='#f8fafc')
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        self.create_header(container)
        
        # Notebook para organizar seções
        self.notebook = ttk.Notebook(container)
        self.notebook.pack(fill="both", expand=True, pady=(20, 0))
        
        # Aba: Nova Cotação
        self.create_nova_cotacao_tab()
        
        # Aba: Lista de Cotações
        self.create_lista_cotacoes_tab()
        
        # Inicializar variáveis
        self.current_cotacao_id = None
        self.current_cotacao_itens = []
        
        # Carregar dados iniciais
        self.refresh_all_data()
        
        # Verificar cotações vencidas automaticamente
        self.verificar_cotacoes_vencidas()
        
    def ensure_responsavel_id_column(self):
        import sqlite3
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("PRAGMA table_info(cotacoes)")
        columns = [row[1] for row in c.fetchall()]
        if 'responsavel_id' not in columns:
            try:
                c.execute("ALTER TABLE cotacoes ADD COLUMN responsavel_id INTEGER")
                conn.commit()
            except Exception as e:
                print(f"Erro ao adicionar coluna responsavel_id em cotacoes: {e}")
        conn.close()
        
    def create_header(self, parent):
        header_frame = tk.Frame(parent, bg='#f8fafc')
        header_frame.pack(fill="x", pady=(0, 20))
        
        title_label = tk.Label(header_frame, text="Gestão de Cotações", 
                               font=('Arial', 18, 'bold'),
                               bg='#f8fafc',
                               fg='#1e293b')
        title_label.pack(side="left")
        
    def create_nova_cotacao_tab(self):
        # Frame da aba
        cotacao_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(cotacao_frame, text="Nova Cotação")
        
        # Scroll frame
        canvas = tk.Canvas(cotacao_frame, bg='white')
        scrollbar = ttk.Scrollbar(cotacao_frame, orient="vertical", command=canvas.yview)
        self.scrollable_cotacao = tk.Frame(canvas, bg='white')
        
        self.scrollable_cotacao.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_cotacao, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Conteúdo da cotação
        self.create_cotacao_content(self.scrollable_cotacao)
        
    def create_cotacao_content(self, parent):
        # Frame principal dividido em duas colunas: conteúdo e indicadores
        main_content_frame = tk.Frame(parent, bg='white')
        main_content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Coluna esquerda (conteúdo principal)
        left_frame = tk.Frame(main_content_frame, bg='white')
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Coluna direita (indicadores)
        right_frame = tk.Frame(main_content_frame, bg='#f8fafc', width=320)
        right_frame.pack(side="right", fill="y", padx=(10, 0))
        right_frame.pack_propagate(False)  # Manter largura fixa
        self.create_cotacoes_indicadores(right_frame)
        
        # Conteúdo principal
        self.create_dados_cotacao_section(left_frame)
        self.create_itens_cotacao_section(left_frame)
        self.create_cotacao_buttons(left_frame)
        
    def create_dados_cotacao_section(self, parent):
        section_frame = self.create_section_frame(parent, "Dados da Cotação")
        section_frame.pack(fill="x", pady=(0, 15))
        
        # Grid de campos
        fields_frame = tk.Frame(section_frame, bg='white')
        fields_frame.pack(fill="x")
        
        # Variáveis
        self.numero_var = tk.StringVar()
        self.cliente_var = tk.StringVar()
        self.filial_var = tk.StringVar(value="2")  # Default para World Comp do Brasil
        self.modelo_var = tk.StringVar()
        self.serie_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Em Aberto")
        self.data_validade_var = tk.StringVar()
        self.condicao_pagamento_var = tk.StringVar()
        self.prazo_entrega_var = tk.StringVar()
        self.observacoes_var = tk.StringVar()
        
        row = 0
        
        # Número da Proposta
        tk.Label(fields_frame, text="Número da Proposta *:", 
                 font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.numero_var, 
                 font=('Arial', 10), width=30).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Filial
        tk.Label(fields_frame, text="Filial *:", 
                 font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        filial_combo = ttk.Combobox(fields_frame, textvariable=self.filial_var, 
                                   values=["1 - WORLD COMP COMPRESSORES LTDA", 
                                          "2 - WORLD COMP DO BRASIL COMPRESSORES LTDA"], 
                                   width=45, state="readonly")
        filial_combo.grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Cliente com busca reativa
        tk.Label(fields_frame, text="Cliente *:", 
                 font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        
        cliente_frame = tk.Frame(fields_frame, bg='white')
        cliente_frame.grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        self.cliente_combo = ttk.Combobox(cliente_frame, textvariable=self.cliente_var, width=25)
        self.cliente_combo.pack(side="left", fill="x", expand=True)
        self.cliente_combo.bind('<<ComboboxSelected>>', self.on_cliente_selected)
        
        # Botão para buscar/atualizar clientes
        refresh_clientes_btn = self.create_button(cliente_frame, "🔄", self.refresh_clientes, bg='#10b981')
        refresh_clientes_btn.pack(side="right", padx=(5, 0))
        
        row += 1
        
        # Modelo e Série
        tk.Label(fields_frame, text="Modelo do Compressor:", 
                 font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.modelo_var, 
                 font=('Arial', 10), width=30).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        tk.Label(fields_frame, text="Número de Série:", 
                 font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.serie_var, 
                 font=('Arial', 10), width=30).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Status
        tk.Label(fields_frame, text="Status:", 
                 font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        status_combo = ttk.Combobox(fields_frame, textvariable=self.status_var, 
                                   values=["Em Aberto", "Aprovada", "Rejeitada"], 
                                   width=27, state="readonly")
        status_combo.grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Data de Validade
        tk.Label(fields_frame, text="Data de Validade:", 
                 font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.data_validade_var, 
                 font=('Arial', 10), width=30).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Condição de Pagamento
        tk.Label(fields_frame, text="Condição de Pagamento:", 
                 font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.condicao_pagamento_var, 
                 font=('Arial', 10), width=30).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Prazo de Entrega
        tk.Label(fields_frame, text="Prazo de Entrega:", 
                 font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.prazo_entrega_var, 
                 font=('Arial', 10), width=30).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Observações
        tk.Label(fields_frame, text="Observações:", 
                 font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="nw", pady=5)
        self.observacoes_text = scrolledtext.ScrolledText(fields_frame, height=3, width=30)
        self.observacoes_text.grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Esboço do Serviço (para PDF)
        tk.Label(fields_frame, text="Esboço do Serviço:", 
                 font=('Arial', 10, 'bold'), bg='white', fg='#3b82f6').grid(row=row, column=0, sticky="nw", pady=5)
        self.esboco_servico_text = scrolledtext.ScrolledText(fields_frame, height=4, width=30)
        self.esboco_servico_text.grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Relação de Peças a Serem Substituídas (para PDF)
        tk.Label(fields_frame, text="Peças a Substituir:", 
                 font=('Arial', 10, 'bold'), bg='white', fg='#3b82f6').grid(row=row, column=0, sticky="nw", pady=5)
        self.relacao_pecas_text = scrolledtext.ScrolledText(fields_frame, height=4, width=30)
        self.relacao_pecas_text.grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Configurar colunas
        fields_frame.grid_columnconfigure(1, weight=1)
        
    def create_itens_cotacao_section(self, parent):
        section_frame = self.create_section_frame(parent, "Itens da Cotação")
        section_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # Frame para adicionar item
        add_item_frame = tk.Frame(section_frame, bg='white')
        add_item_frame.pack(fill="x", pady=(0, 10))
        
        # Campos para novo item
        self.create_item_fields(add_item_frame)
        
        # Lista de itens
        self.create_itens_list(section_frame)
        
    def create_item_fields(self, parent):
        # Variáveis
        self.item_tipo_var = tk.StringVar()
        self.item_nome_var = tk.StringVar()
        self.item_qtd_var = tk.StringVar(value="1")
        self.item_valor_var = tk.StringVar(value="0.00")
        self.item_desc_var = tk.StringVar()
        self.item_mao_obra_var = tk.StringVar(value="0.00")
        self.item_deslocamento_var = tk.StringVar(value="0.00")
        self.item_estadia_var = tk.StringVar(value="0.00")
        self.item_tipo_transacao_var = tk.StringVar(value="Compra")
        
        # Grid de campos
        fields_grid = tk.Frame(parent, bg="white")
        fields_grid.pack(padx=10, pady=(0, 10), fill="x")
        
        # Primeira linha
        tk.Label(fields_grid, text="Tipo:", font=("Arial", 10, "bold"), bg="white").grid(row=0, column=0, padx=5, sticky="w")
        self.tipo_combo = ttk.Combobox(fields_grid, textvariable=self.item_tipo_var, 
                                      values=["Produto", "Serviço", "Kit"], 
                                      width=10, state="readonly")
        self.tipo_combo.grid(row=0, column=1, padx=5)
        self.tipo_combo.bind("<<ComboboxSelected>>", self.on_tipo_changed)
        
        tk.Label(fields_grid, text="Nome:", font=("Arial", 10, "bold"), bg="white").grid(row=0, column=2, padx=5, sticky="w")
        
        # Frame para nome do item com botão de refresh
        nome_frame = tk.Frame(fields_grid, bg='white')
        nome_frame.grid(row=0, column=3, padx=5, sticky="ew")
        
        self.item_nome_combo = ttk.Combobox(nome_frame, textvariable=self.item_nome_var, width=20)
        self.item_nome_combo.pack(side="left", fill="x", expand=True)
        self.item_nome_combo.bind("<<ComboboxSelected>>", self.on_item_selected)
        
        refresh_produtos_btn = self.create_button(nome_frame, "🔄", self.refresh_produtos, bg='#10b981')
        refresh_produtos_btn.pack(side="right", padx=(2, 0))
        
        tk.Label(fields_grid, text="Qtd:", font=("Arial", 10, "bold"), bg="white").grid(row=0, column=4, padx=5, sticky="w")
        tk.Entry(fields_grid, textvariable=self.item_qtd_var, width=5).grid(row=0, column=5, padx=5)
        
        tk.Label(fields_grid, text="Tipo:", font=("Arial", 10, "bold"), bg="white").grid(row=0, column=6, padx=5, sticky="w")
        tipo_transacao_combo = ttk.Combobox(fields_grid, textvariable=self.item_tipo_transacao_var, 
                                           values=["Compra", "Locação"], width=8, state="readonly")
        tipo_transacao_combo.grid(row=0, column=7, padx=5)
        
        tk.Label(fields_grid, text="Valor Unit.:", font=("Arial", 10, "bold"), bg="white").grid(row=0, column=8, padx=5, sticky="w")
        tk.Entry(fields_grid, textvariable=self.item_valor_var, width=10).grid(row=0, column=9, padx=5)
        
        # Segunda linha - Descrição
        tk.Label(fields_grid, text="Descrição:", font=("Arial", 10, "bold"), bg="white").grid(row=1, column=0, padx=5, sticky="w")
        tk.Entry(fields_grid, textvariable=self.item_desc_var, width=50).grid(row=1, column=1, columnspan=6, padx=5, sticky="ew")
        
        # Terceira linha - Campos de serviço (inicialmente ocultos)
        self.servico_frame = tk.Frame(fields_grid, bg="white")
        self.servico_frame.grid(row=2, column=0, columnspan=10, sticky="ew", pady=5)
        
        tk.Label(self.servico_frame, text="Mão de Obra:", font=("Arial", 10, "bold"), bg="white").grid(row=0, column=0, padx=5, sticky="w")
        tk.Entry(self.servico_frame, textvariable=self.item_mao_obra_var, width=10).grid(row=0, column=1, padx=5)
        
        tk.Label(self.servico_frame, text="Deslocamento:", font=("Arial", 10, "bold"), bg="white").grid(row=0, column=2, padx=5, sticky="w")
        tk.Entry(self.servico_frame, textvariable=self.item_deslocamento_var, width=10).grid(row=0, column=3, padx=5)
        
        tk.Label(self.servico_frame, text="Estadia:", font=("Arial", 10, "bold"), bg="white").grid(row=0, column=4, padx=5, sticky="w")
        tk.Entry(self.servico_frame, textvariable=self.item_estadia_var, width=10).grid(row=0, column=5, padx=5)
        
        # Inicialmente ocultar campos de serviço
        self.servico_frame.grid_remove()
        
        # Botão adicionar
        adicionar_button = self.create_button(fields_grid, "Adicionar Item", self.adicionar_item)
        adicionar_button.grid(row=3, column=0, columnspan=8, pady=10)
        
        # Configurar grid
        fields_grid.grid_columnconfigure(3, weight=1)
        
    def on_tipo_changed(self, event=None):
        """Callback quando o tipo do item muda"""
        tipo = self.item_tipo_var.get()
        
        # Mostrar/ocultar campos de serviço
        if tipo == "Serviço":
            self.servico_frame.grid()
        else:
            self.servico_frame.grid_remove()
            # Resetar valores de serviço
            self.item_mao_obra_var.set("0.00")
            self.item_deslocamento_var.set("0.00")
            self.item_estadia_var.set("0.00")
        
        # Atualizar lista de produtos
        self.update_produtos_combo()
        
    def update_produtos_combo(self):
        """Atualizar combo de produtos baseado no tipo selecionado"""
        tipo = self.item_tipo_var.get()
        if not tipo:
            self.item_nome_combo['values'] = []
            return
            
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            c.execute("SELECT nome FROM produtos WHERE tipo = ? AND ativo = 1 ORDER BY nome", (tipo,))
            produtos = [row[0] for row in c.fetchall()]
            self.item_nome_combo['values'] = produtos
            self.item_nome_var.set("")  # Limpar seleção
        except sqlite3.Error as e:
            self.show_error(f"Erro ao carregar produtos: {e}")
        finally:
            conn.close()
            
    def on_cliente_selected(self, event=None):
        """Quando um cliente é selecionado, preencher automaticamente o prazo de pagamento"""
        selected = self.cliente_var.get()
        if selected:
            # Buscar o prazo de pagamento do cliente no banco
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT prazo_pagamento FROM clientes WHERE nome = ?", (selected,))
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0]:
                self.condicao_pagamento_var.set(result[0])
    
    def on_item_selected(self, event=None):
        """Callback quando um produto é selecionado"""
        nome = self.item_nome_var.get()
        tipo = self.item_tipo_var.get()
        
        if not nome or not tipo:
            return
            
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            c.execute("SELECT valor_unitario, descricao FROM produtos WHERE nome = ? AND tipo = ?", (nome, tipo))
            result = c.fetchone()
            if result:
                valor, descricao = result
                self.item_valor_var.set(f"{valor:.2f}")
                if descricao:
                    self.item_desc_var.set(descricao)
        except sqlite3.Error as e:
            self.show_error(f"Erro ao buscar dados do produto: {e}")
        finally:
            conn.close()
            
    def create_itens_list(self, parent):
        # Frame para lista
        list_frame = tk.Frame(parent, bg='white')
        list_frame.pack(fill="both", expand=True)
        
        # Treeview
        columns = ("tipo", "nome", "qtd", "tipo_transacao", "valor_unit", "mao_obra", "deslocamento", "estadia", "valor_total", "descricao")
        self.itens_tree = ttk.Treeview(list_frame, 
                                      columns=columns,
                                      show="headings",
                                      height=8)
        
        # Cabeçalhos
        self.itens_tree.heading("tipo", text="Tipo")
        self.itens_tree.heading("nome", text="Nome")
        self.itens_tree.heading("qtd", text="Qtd")
        self.itens_tree.heading("tipo_transacao", text="Transação")
        self.itens_tree.heading("valor_unit", text="Valor Unit.")
        self.itens_tree.heading("mao_obra", text="Mão Obra")
        self.itens_tree.heading("deslocamento", text="Desloc.")
        self.itens_tree.heading("estadia", text="Estadia")
        self.itens_tree.heading("valor_total", text="Total")
        self.itens_tree.heading("descricao", text="Descrição")
        
        # Larguras
        self.itens_tree.column("tipo", width=80)
        self.itens_tree.column("nome", width=150)
        self.itens_tree.column("qtd", width=50)
        self.itens_tree.column("tipo_transacao", width=80)
        self.itens_tree.column("valor_unit", width=80)
        self.itens_tree.column("mao_obra", width=80)
        self.itens_tree.column("deslocamento", width=80)
        self.itens_tree.column("estadia", width=80)
        self.itens_tree.column("valor_total", width=80)
        self.itens_tree.column("descricao", width=200)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", 
                                 command=self.itens_tree.yview)
        self.itens_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        self.itens_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Botões para itens
        item_buttons = tk.Frame(parent, bg='white')
        item_buttons.pack(fill="x", pady=(10, 0))
        
        remove_btn = self.create_button(item_buttons, "Remover Item", self.remover_item, bg='#dc2626')
        remove_btn.pack(side="left", padx=5)
        
        # Label do total
        self.total_label = tk.Label(item_buttons, text="Total: R$ 0,00",
                                   font=('Arial', 12, 'bold'),
                                   bg='white',
                                   fg='#1e293b')
        self.total_label.pack(side="right")
        
    def create_cotacao_buttons(self, parent):
        buttons_frame = tk.Frame(parent, bg='white')
        buttons_frame.pack(fill="x", pady=(20, 0))
        
        # Botões
        nova_btn = self.create_button(buttons_frame, "Nova Cotação", self.nova_cotacao, bg='#e2e8f0', fg='#475569')
        nova_btn.pack(side="left", padx=(0, 10))
        
        salvar_btn = self.create_button(buttons_frame, "Salvar Cotação", self.salvar_cotacao)
        salvar_btn.pack(side="left", padx=(0, 10))
        
        gerar_pdf_btn = self.create_button(buttons_frame, "Gerar PDF", self.gerar_pdf, bg='#10b981')
        gerar_pdf_btn.pack(side="right")
        

        
    def refresh_all_data(self):
        """Atualizar todos os dados do módulo"""
        self.refresh_clientes()
        self.refresh_produtos()
        self.carregar_cotacoes()
        
    def refresh_clientes(self):
        """Atualizar lista de clientes"""
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            c.execute("SELECT id, nome FROM clientes ORDER BY nome")
            clientes = c.fetchall()
            
            self.clientes_dict = {f"{nome} (ID: {id})": id for id, nome in clientes}
            cliente_values = list(self.clientes_dict.keys())
            
            self.cliente_combo['values'] = cliente_values
            
            print(f"Clientes carregados: {len(cliente_values)}")  # Debug
            
        except sqlite3.Error as e:
            self.show_error(f"Erro ao carregar clientes: {e}")
        finally:
            conn.close()
            
    def refresh_produtos(self):
        """Atualizar lista de produtos"""
        # Atualizar combo baseado no tipo selecionado
        self.update_produtos_combo()
        print("Produtos atualizados")  # Debug
        
    def adicionar_item(self):
        tipo = self.item_tipo_var.get()
        nome = self.item_nome_var.get()
        qtd_str = self.item_qtd_var.get()
        valor_str = self.item_valor_var.get()
        descricao = self.item_desc_var.get()
        mao_obra_str = self.item_mao_obra_var.get()
        deslocamento_str = self.item_deslocamento_var.get()
        estadia_str = self.item_estadia_var.get()
        tipo_transacao = self.item_tipo_transacao_var.get()
        
        # Validações
        if not tipo or not nome:
            self.show_warning("Selecione o tipo e nome do item.")
            return
            
        try:
            quantidade = float(qtd_str) if qtd_str else 1
            valor_unitario = clean_number(valor_str)
            mao_obra = clean_number(mao_obra_str)
            deslocamento = clean_number(deslocamento_str)
            estadia = clean_number(estadia_str)
            
            valor_total = quantidade * (valor_unitario + mao_obra + deslocamento + estadia)
        except ValueError:
            self.show_error("Verifique os valores numéricos informados.")
            return
            
        # Adicionar à lista
        self.itens_tree.insert("", "end", values=(
            tipo,
            nome,
            f"{quantidade:.2f}",
            tipo_transacao,
            format_currency(valor_unitario),
            format_currency(mao_obra),
            format_currency(deslocamento),
            format_currency(estadia),
            format_currency(valor_total),
            descricao
        ))
        
        # Limpar campos
        self.item_nome_var.set("")
        self.item_desc_var.set("")
        self.item_qtd_var.set("1")
        self.item_valor_var.set("0.00")
        self.item_mao_obra_var.set("0.00")
        self.item_deslocamento_var.set("0.00")
        self.item_estadia_var.set("0.00")
        self.item_tipo_transacao_var.set("Compra")
        
        # Atualizar total
        self.atualizar_total()
        
    def remover_item(self):
        selected = self.itens_tree.selection()
        if not selected:
            self.show_warning("Selecione um item para remover.")
            return
            
        for item in selected:
            self.itens_tree.delete(item)
            
        self.atualizar_total()
        
    def atualizar_total(self):
        """Atualizar valor total da cotação"""
        total = 0
        for item in self.itens_tree.get_children():
            values = self.itens_tree.item(item)['values']
            if len(values) >= 8:
                # Remover formatação e converter para float
                valor_total_str = values[7].replace('R$ ', '').replace('.', '').replace(',', '.')
                try:
                    total += float(valor_total_str)
                except ValueError:
                    pass
                    
        self.total_label.config(text=f"Total: {format_currency(total)}")
        
    def nova_cotacao(self):
        """Limpar formulário para nova cotação"""
        self.current_cotacao_id = None
        
        # Limpar campos
        self.numero_var.set("")
        self.cliente_var.set("")
        self.modelo_var.set("")
        self.serie_var.set("")
        self.status_var.set("Em Aberto")
        self.data_validade_var.set("")
        self.condicao_pagamento_var.set("")
        self.prazo_entrega_var.set("")
        self.observacoes_text.delete("1.0", tk.END)
        self.esboco_servico_text.delete("1.0", tk.END)
        self.relacao_pecas_text.delete("1.0", tk.END)
        
        # Limpar itens
        for item in self.itens_tree.get_children():
            self.itens_tree.delete(item)
            
        self.atualizar_total()
        
        # Gerar número sequencial automático
        numero = self.gerar_numero_sequencial()
        self.numero_var.set(numero)
    
    def gerar_numero_sequencial(self):
        """Gerar número sequencial para cotação"""
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            # Buscar o maior número sequencial existente
            c.execute("""
                SELECT numero_proposta 
                FROM cotacoes 
                WHERE numero_proposta LIKE 'PROP-%' 
                ORDER BY CAST(SUBSTR(numero_proposta, 6) AS INTEGER) DESC 
                LIMIT 1
            """)
            
            resultado = c.fetchone()
            
            if resultado:
                # Extrair o número da última cotação
                ultimo_numero = resultado[0]
                if ultimo_numero.startswith('PROP-'):
                    try:
                        numero_atual = int(ultimo_numero[5:])  # Remove 'PROP-' e converte para int
                        proximo_numero = numero_atual + 1
                    except ValueError:
                        # Se não conseguir converter, usar timestamp
                        proximo_numero = int(datetime.now().strftime('%Y%m%d%H%M%S'))
                else:
                    proximo_numero = 1
            else:
                # Primeira cotação
                proximo_numero = 1
            
            # Formatar o número com zeros à esquerda (6 dígitos)
            numero_formatado = f"PROP-{proximo_numero:06d}"
            
            return numero_formatado
            
        except Exception as e:
            print(f"Erro ao gerar número sequencial: {e}")
            # Fallback para timestamp
            return f"PROP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        finally:
            conn.close()
        
    def salvar_cotacao(self):
        """Salvar cotação no banco de dados"""
        # Validações
        numero = self.numero_var.get().strip()
        cliente_str = self.cliente_var.get().strip()
        
        if not numero:
            self.show_warning("Informe o número da proposta.")
            return
            
        if not cliente_str:
            self.show_warning("Selecione um cliente.")
            return
            
        # Obter ID do cliente
        cliente_id = self.clientes_dict.get(cliente_str)
        if not cliente_id:
            self.show_warning("Cliente selecionado inválido.")
            return
            
        # Verificar se há itens
        if not self.itens_tree.get_children():
            self.show_warning("Adicione pelo menos um item à cotação.")
            return
            
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            # Calcular valor total
            valor_total = 0
            for item in self.itens_tree.get_children():
                values = self.itens_tree.item(item)['values']
                if len(values) >= 9:  # Ajustado para nova estrutura
                    valor_total_str = values[8].replace('R$ ', '').replace('.', '').replace(',', '.')  # Valor total agora é índice 8
                    try:
                        valor_total += float(valor_total_str)
                    except ValueError:
                        pass
            
            # Obter ID da filial
            filial_str = self.filial_var.get()
            filial_id = int(filial_str.split(' - ')[0]) if ' - ' in filial_str else int(filial_str)
            
            # Dados da cotação
            if self.current_cotacao_id:
                # Atualizar cotação existente
                c.execute("""
                    UPDATE cotacoes SET
                        numero_proposta = ?, modelo_compressor = ?, numero_serie_compressor = ?,
                        observacoes = ?, valor_total = ?, status = ?, data_validade = ?,
                        condicao_pagamento = ?, prazo_entrega = ?, filial_id = ?,
                        esboco_servico = ?, relacao_pecas_substituir = ?, responsavel_id = ?
                    WHERE id = ?
                """, (numero, self.modelo_var.get(), self.serie_var.get(),
                     self.observacoes_text.get("1.0", tk.END).strip(), valor_total,
                     self.status_var.get(), self.data_validade_var.get(),
                     self.condicao_pagamento_var.get(), self.prazo_entrega_var.get(),
                     filial_id, self.esboco_servico_text.get("1.0", tk.END).strip(),
                     self.relacao_pecas_text.get("1.0", tk.END).strip(), self.user_id, self.current_cotacao_id))
                
                # Remover itens antigos
                c.execute("DELETE FROM itens_cotacao WHERE cotacao_id = ?", (self.current_cotacao_id,))
                cotacao_id = self.current_cotacao_id
            else:
                # Inserir nova cotação
                c.execute("""
                    INSERT INTO cotacoes (numero_proposta, cliente_id, responsavel_id, data_criacao,
                                        modelo_compressor, numero_serie_compressor, observacoes,
                                        valor_total, status, data_validade, condicao_pagamento,
                                        prazo_entrega, filial_id, esboco_servico, relacao_pecas_substituir)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (numero, cliente_id, self.user_id, datetime.now().strftime('%Y-%m-%d'),
                     self.modelo_var.get(), self.serie_var.get(),
                     self.observacoes_text.get("1.0", tk.END).strip(), valor_total,
                     self.status_var.get(), self.data_validade_var.get(),
                     self.condicao_pagamento_var.get(), self.prazo_entrega_var.get(),
                     filial_id, self.esboco_servico_text.get("1.0", tk.END).strip(),
                     self.relacao_pecas_text.get("1.0", tk.END).strip()))
                     
                cotacao_id = c.lastrowid
                self.current_cotacao_id = cotacao_id
            
            # Inserir itens
            for item in self.itens_tree.get_children():
                values = self.itens_tree.item(item)['values']
                tipo, nome, qtd, tipo_transacao, valor_unit, mao_obra, desloc, estadia, total, desc = values
                
                # Converter valores
                quantidade = float(qtd)
                valor_unitario = clean_number(valor_unit)
                valor_mao_obra = clean_number(mao_obra)
                valor_desloc = clean_number(desloc)
                valor_estadia = clean_number(estadia)
                valor_total_item = clean_number(total)
                
                c.execute("""
                    INSERT INTO itens_cotacao (cotacao_id, tipo, item_nome, quantidade,
                                             valor_unitario, valor_total_item, descricao,
                                             mao_obra, deslocamento, estadia, tipo_transacao)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (cotacao_id, tipo, nome, quantidade, valor_unitario,
                     valor_total_item, desc, valor_mao_obra, valor_desloc, valor_estadia, tipo_transacao))
            
            conn.commit()
            self.show_success("Cotação salva com sucesso!")
            
            # Emitir evento para atualizar outros módulos
            self.emit_event('cotacao_created')
            
            # Recarregar lista
            self.carregar_cotacoes()
            
        except sqlite3.Error as e:
            self.show_error(f"Erro ao salvar cotação: {e}")
        finally:
            conn.close()
            
    def gerar_pdf(self):
        """Gerar PDF da cotação atual"""
        if not self.current_cotacao_id:
            self.show_warning("Salve a cotação antes de gerar o PDF.")
            return
            
        # Obter username do usuário atual para template personalizado
        current_username = self._get_current_username()
        
        sucesso, resultado = gerar_pdf_cotacao_nova(self.current_cotacao_id, DB_NAME, current_username)
        
        if sucesso:
            self.show_success(f"PDF gerado com sucesso!\nLocal: {resultado}")
        else:
            self.show_error(f"Erro ao gerar PDF: {resultado}")
            
    def _get_current_username(self):
        """Obter o username do usuário atual"""
        try:
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("SELECT username FROM usuarios WHERE id = ?", (self.user_id,))
            result = c.fetchone()
            return result[0] if result else None
        except:
            return None
        finally:
            if 'conn' in locals():
                conn.close()
            
    def carregar_cotacoes(self):
        """Carregar lista de cotações com filtro por status"""
        # Limpar lista atual
        for item in self.cotacoes_tree.get_children():
            self.cotacoes_tree.delete(item)
            
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            # Aplicar filtro por status se definido
            status_filter = getattr(self, 'status_filter_var', None)
            if status_filter and status_filter.get() != "Todos":
                c.execute("""
                    SELECT c.id, c.numero_proposta, cl.nome, c.data_criacao, c.valor_total, c.status
                    FROM cotacoes c
                    JOIN clientes cl ON c.cliente_id = cl.id
                    WHERE c.status = ?
                    ORDER BY c.created_at DESC
                """, (status_filter.get(),))
            else:
                c.execute("""
                    SELECT c.id, c.numero_proposta, cl.nome, c.data_criacao, c.valor_total, c.status
                    FROM cotacoes c
                    JOIN clientes cl ON c.cliente_id = cl.id
                    ORDER BY c.created_at DESC
                """)
            
            for row in c.fetchall():
                cotacao_id, numero, cliente, data, valor, status = row
                self.cotacoes_tree.insert("", "end", values=(
                    numero,
                    cliente,
                    format_date(data),
                    format_currency(valor) if valor else "R$ 0,00",
                    status
                ), tags=(cotacao_id,))
                
        except sqlite3.Error as e:
            self.show_error(f"Erro ao carregar cotações: {e}")
        finally:
            conn.close()
            
    def buscar_cotacoes(self):
        """Buscar cotações com filtro"""
        termo = self.search_var.get().strip()
        
        # Limpar lista atual
        for item in self.cotacoes_tree.get_children():
            self.cotacoes_tree.delete(item)
            
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            if termo:
                c.execute("""
                    SELECT c.id, c.numero_proposta, cl.nome, c.data_criacao, c.valor_total, c.status
                    FROM cotacoes c
                    JOIN clientes cl ON c.cliente_id = cl.id
                    WHERE c.numero_proposta LIKE ? OR cl.nome LIKE ?
                    ORDER BY c.created_at DESC
                """, (f"%{termo}%", f"%{termo}%"))
            else:
                c.execute("""
                    SELECT c.id, c.numero_proposta, cl.nome, c.data_criacao, c.valor_total, c.status
                    FROM cotacoes c
                    JOIN clientes cl ON c.cliente_id = cl.id
                    ORDER BY c.created_at DESC
                """)
            
            for row in c.fetchall():
                cotacao_id, numero, cliente, data, valor, status = row
                self.cotacoes_tree.insert("", "end", values=(
                    numero,
                    cliente,
                    format_date(data),
                    format_currency(valor) if valor else "R$ 0,00",
                    status
                ), tags=(cotacao_id,))
                
        except sqlite3.Error as e:
            self.show_error(f"Erro ao buscar cotações: {e}")
        finally:
            conn.close()
            
    def editar_cotacao_selecionada(self):
        """Editar cotação selecionada"""
        selected = self.cotacoes_tree.selection()
        if not selected:
            self.show_warning("Selecione uma cotação para editar.")
            return
            
        # Obter ID da cotação
        tags = self.cotacoes_tree.item(selected[0])['tags']
        if not tags:
            return
            
        cotacao_id = tags[0]
        self.carregar_cotacao_para_edicao(cotacao_id)
        
        # Mudar para aba de nova cotação
        self.notebook.select(0)
        
    def carregar_cotacao_para_edicao(self, cotacao_id):
        """Carregar dados da cotação para edição"""
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            # Carregar dados da cotação
            c.execute("""
                SELECT c.*, cl.nome
                FROM cotacoes c
                JOIN clientes cl ON c.cliente_id = cl.id
                WHERE c.id = ?
            """, (cotacao_id,))
            
            cotacao = c.fetchone()
            if not cotacao:
                self.show_error("Cotação não encontrada.")
                return
                
            # Preencher campos
            self.current_cotacao_id = cotacao_id
            self.numero_var.set(cotacao[1])  # numero_proposta
            
            # Encontrar cliente no combo
            cliente_nome = cotacao[17]  # nome do cliente
            for key, value in self.clientes_dict.items():
                if value == cotacao[2]:  # cliente_id
                    self.cliente_var.set(key)
                    break
                    
            self.modelo_var.set(cotacao[6] or "")
            self.serie_var.set(cotacao[7] or "")
            self.status_var.set(cotacao[15] or "Em Aberto")
            self.data_validade_var.set(cotacao[5] or "")
            self.condicao_pagamento_var.set(cotacao[12] or "")
            self.prazo_entrega_var.set(cotacao[13] or "")
            
            # Observações
            self.observacoes_text.delete("1.0", tk.END)
            if cotacao[9]:  # observacoes
                self.observacoes_text.insert("1.0", cotacao[9])
            
            # Esboço do Serviço
            self.esboco_servico_text.delete("1.0", tk.END)
            if len(cotacao) > 18 and cotacao[18]:  # esboco_servico
                self.esboco_servico_text.insert("1.0", cotacao[18])
            
            # Relação de Peças a Substituir
            self.relacao_pecas_text.delete("1.0", tk.END)
            if len(cotacao) > 19 and cotacao[19]:  # relacao_pecas_substituir
                self.relacao_pecas_text.insert("1.0", cotacao[19])
            
            # Carregar itens
            self.carregar_itens_cotacao(cotacao_id)
            
        except sqlite3.Error as e:
            self.show_error(f"Erro ao carregar cotação: {e}")
        finally:
            conn.close()
            
    def carregar_itens_cotacao(self, cotacao_id):
        """Carregar itens da cotação"""
        # Limpar lista atual
        for item in self.itens_tree.get_children():
            self.itens_tree.delete(item)
            
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            c.execute("""
                SELECT tipo, item_nome, quantidade, valor_unitario, valor_total_item,
                       descricao, mao_obra, deslocamento, estadia, COALESCE(tipo_transacao, 'Compra')
                FROM itens_cotacao
                WHERE cotacao_id = ?
                ORDER BY id
            """, (cotacao_id,))
            
            for row in c.fetchall():
                tipo, nome, qtd, valor_unit, total, desc, mao_obra, desloc, estadia, tipo_transacao = row
                self.itens_tree.insert("", "end", values=(
                    tipo,
                    nome,
                    f"{qtd:.2f}",
                    tipo_transacao,
                    format_currency(valor_unit),
                    format_currency(mao_obra or 0),
                    format_currency(desloc or 0),
                    format_currency(estadia or 0),
                    format_currency(total),
                    desc or ""
                ))
                
            self.atualizar_total()
            
        except sqlite3.Error as e:
            self.show_error(f"Erro ao carregar itens: {e}")
        finally:
            conn.close()
            
    def duplicar_cotacao(self):
        """Duplicar cotação selecionada"""
        selected = self.cotacoes_tree.selection()
        if not selected:
            self.show_warning("Selecione uma cotação para duplicar.")
            return
            
        # Obter ID da cotação
        tags = self.cotacoes_tree.item(selected[0])['tags']
        if not tags:
            return
            
        cotacao_id = tags[0]
        self.carregar_cotacao_para_edicao(cotacao_id)
        
        # Limpar ID e gerar novo número
        self.current_cotacao_id = None
        numero = f"PROP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.numero_var.set(numero)
        
        # Mudar para aba de nova cotação
        self.notebook.select(0)
        
    def gerar_pdf_selecionado(self):
        """Gerar PDF da cotação selecionada"""
        selected = self.cotacoes_tree.selection()
        if not selected:
            self.show_warning("Selecione uma cotação para gerar PDF.")
            return
            
        # Obter ID da cotação
        tags = self.cotacoes_tree.item(selected[0])['tags']
        if not tags:
            return
            
        cotacao_id = tags[0]
        # Obter username do usuário atual para template personalizado
        current_username = self._get_current_username()
        sucesso, resultado = gerar_pdf_cotacao_nova(cotacao_id, DB_NAME, current_username)
        
        if sucesso:
            self.show_success(f"PDF gerado com sucesso!\nLocal: {resultado}")
        else:
            self.show_error(f"Erro ao gerar PDF: {resultado}")
            
    def handle_event(self, event_type, data=None):
        """Manipular eventos do sistema"""
        if event_type == 'cliente_created':
            self.refresh_clientes()
            print("Lista de clientes atualizada automaticamente!")
        elif event_type == 'produto_created':
            self.refresh_produtos()
            print("Lista de produtos atualizada automaticamente!")

    def create_cotacao_dashboard_section(self, parent):
        """Criar dashboard específico da cotação"""
        section_frame = self.create_section_frame(parent, "Dashboard da Cotação")
        section_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # Container do dashboard
        dashboard_frame = tk.Frame(section_frame, bg='white')
        dashboard_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Card: Total de Itens
        self.create_dashboard_card(dashboard_frame, "📦 Itens", "0", "#3b82f6", 0)
        
        # Card: Valor Total
        self.create_dashboard_card(dashboard_frame, "💰 Total", "R$ 0,00", "#10b981", 1)
        
        # Card: Status
        self.create_dashboard_card(dashboard_frame, "📋 Status", "Em Aberto", "#f59e0b", 2)
        
        # Card: Validade
        self.create_dashboard_card(dashboard_frame, "⏰ Validade", "Não definida", "#ef4444", 3)
        
        # Resumo rápido
        self.create_quick_summary_section(dashboard_frame)
        
    def create_dashboard_card(self, parent, title, value, color, row):
        """Criar card do dashboard"""
        card_frame = tk.Frame(parent, bg='white', relief='solid', bd=1)
        card_frame.grid(row=row, column=0, sticky="ew", pady=2, padx=2)
        
        # Título
        title_label = tk.Label(card_frame, text=title, 
                              font=('Arial', 8, 'bold'),
                              bg='white', fg=color)
        title_label.pack(pady=(5, 0))
        
        # Valor
        value_label = tk.Label(card_frame, text=value,
                              font=('Arial', 10, 'bold'),
                              bg='white', fg='#1e293b')
        value_label.pack(pady=(0, 5))
        
        # Configurar grid
        parent.grid_columnconfigure(0, weight=1)
        
        return card_frame
        
    def create_quick_summary_section(self, parent):
        """Criar seção de resumo rápido"""
        summary_frame = tk.Frame(parent, bg='white', relief='solid', bd=1)
        summary_frame.grid(row=4, column=0, sticky="ew", pady=(10, 0), padx=2)
        
        # Título
        title_label = tk.Label(summary_frame, text="📊 Resumo Rápido",
                              font=('Arial', 8, 'bold'),
                              bg='white', fg='#1e293b')
        title_label.pack(pady=5)
        
        # Lista de resumo
        self.summary_listbox = tk.Listbox(summary_frame, height=4,
                                        font=('Arial', 8),
                                        bg='#f8fafc',
                                        relief='flat')
        self.summary_listbox.pack(fill="both", expand=True, padx=5, pady=(0, 5))
        
    def update_cotacao_dashboard(self):
        """Atualizar dashboard da cotação"""
        try:
            # Atualizar resumo rápido
            if hasattr(self, 'summary_listbox'):
                self.summary_listbox.delete(0, tk.END)
                
                total_itens = len(self.current_cotacao_itens)
                self.summary_listbox.insert(tk.END, f"Total de itens: {total_itens}")
                
                if self.current_cotacao_itens:
                    produtos = sum(1 for item in self.current_cotacao_itens if item.get('tipo') == 'Produto')
                    servicos = sum(1 for item in self.current_cotacao_itens if item.get('tipo') == 'Serviço')
                    kits = sum(1 for item in self.current_cotacao_itens if item.get('tipo') == 'Kit')
                    
                    if produtos > 0:
                        self.summary_listbox.insert(tk.END, f"Produtos: {produtos}")
                    if servicos > 0:
                        self.summary_listbox.insert(tk.END, f"Serviços: {servicos}")
                    if kits > 0:
                        self.summary_listbox.insert(tk.END, f"Kits: {kits}")
                else:
                    self.summary_listbox.insert(tk.END, "Nenhum item adicionado")
                    
        except Exception as e:
            print(f"Erro ao atualizar dashboard: {e}")

    def verificar_cotacoes_vencidas(self):
        """Verificar e atualizar automaticamente cotações vencidas"""
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            # Buscar cotações em aberto com data de validade vencida
            c.execute("""
                UPDATE cotacoes 
                SET status = 'Rejeitada' 
                WHERE status = 'Em Aberto' 
                AND data_validade IS NOT NULL 
                AND data_validade != ''
                AND date(data_validade) < date('now')
            """)
            
            rows_affected = c.rowcount
            conn.commit()
            
            if rows_affected > 0:
                print(f"✅ {rows_affected} cotação(ões) vencida(s) atualizada(s) automaticamente para 'Rejeitada'")
                
        except sqlite3.Error as e:
            print(f"Erro ao verificar cotações vencidas: {e}")
        finally:
            conn.close()

    def create_lista_cotacoes_tab(self):
        # Frame da aba
        lista_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(lista_frame, text="Lista de Cotações")
        
        container = tk.Frame(lista_frame, bg='white', padx=20, pady=20)
        container.pack(fill="both", expand=True)
        
        # Frame de busca e filtros
        search_frame, self.search_var = self.create_search_frame(container, command=self.buscar_cotacoes)
        search_frame.pack(fill="x", pady=(0, 15))
        
        # Frame de filtros por status
        filter_frame = tk.Frame(container, bg='white')
        filter_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(filter_frame, text="Filtrar por status:", font=('Arial', 10, 'bold'), bg='white').pack(side="left")
        
        self.status_filter_var = tk.StringVar(value="Todos")
        status_filter_combo = ttk.Combobox(filter_frame, textvariable=self.status_filter_var,
                                          values=["Todos", "Em Aberto", "Aprovada", "Rejeitada"],
                                          width=15, state="readonly")
        status_filter_combo.pack(side="left", padx=(10, 0))
        status_filter_combo.bind('<<ComboboxSelected>>', self.filtrar_por_status)
        
        # Botão para verificar cotações vencidas manualmente
        verificar_btn = self.create_button(filter_frame, "🔄 Verificar Vencidas", self.verificar_cotacoes_vencidas_manual, bg='#f59e0b')
        verificar_btn.pack(side="left", padx=(20, 0))
        
        # Lista de cotações
        self.create_lista_cotacoes_treeview(container)
        
        # Botões de ação
        self.create_lista_cotacoes_buttons(container)
        
    def create_lista_cotacoes_treeview(self, parent):
        """Criar treeview para lista de cotações"""
        # Treeview para lista
        columns = ("numero", "cliente", "data", "valor", "status")
        self.cotacoes_tree = ttk.Treeview(parent, columns=columns, show="headings", height=15)
        
        # Cabeçalhos
        self.cotacoes_tree.heading("numero", text="Número")
        self.cotacoes_tree.heading("cliente", text="Cliente")
        self.cotacoes_tree.heading("data", text="Data")
        self.cotacoes_tree.heading("valor", text="Valor")
        self.cotacoes_tree.heading("status", text="Status")
        
        # Larguras
        self.cotacoes_tree.column("numero", width=150)
        self.cotacoes_tree.column("cliente", width=250)
        self.cotacoes_tree.column("data", width=100)
        self.cotacoes_tree.column("valor", width=120)
        self.cotacoes_tree.column("status", width=100)
        
        # Scrollbar
        lista_scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.cotacoes_tree.yview)
        self.cotacoes_tree.configure(yscrollcommand=lista_scrollbar.set)
        
        # Pack
        self.cotacoes_tree.pack(side="left", fill="both", expand=True)
        lista_scrollbar.pack(side="right", fill="y")
        
    def create_lista_cotacoes_buttons(self, parent):
        """Criar botões para lista de cotações"""
        buttons_frame = tk.Frame(parent, bg='white')
        buttons_frame.pack(fill="x", pady=(15, 0))
        
        # Botões
        editar_btn = self.create_button(buttons_frame, "Editar", self.editar_cotacao_selecionada)
        editar_btn.pack(side="left", padx=(0, 10))
        
        duplicar_btn = self.create_button(buttons_frame, "Duplicar", self.duplicar_cotacao, bg='#f59e0b')
        duplicar_btn.pack(side="left", padx=(0, 10))
        
        pdf_btn = self.create_button(buttons_frame, "Gerar PDF", self.gerar_pdf_selecionado, bg='#10b981')
        pdf_btn.pack(side="left")
        
    def filtrar_por_status(self, event=None):
        """Filtrar cotações por status"""
        self.carregar_cotacoes()
        
    def verificar_cotacoes_vencidas_manual(self):
        """Verificar cotações vencidas manualmente e mostrar resultado"""
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            # Primeiro verificar quantas cotações serão afetadas
            c.execute("""
                SELECT COUNT(*) FROM cotacoes 
                WHERE status = 'Em Aberto' 
                AND data_validade IS NOT NULL 
                AND data_validade != ''
                AND date(data_validade) < date('now')
            """)
            
            count_before = c.fetchone()[0]
            
            if count_before == 0:
                self.show_info("Não há cotações vencidas para atualizar.")
                return
            
            # Confirmar ação
            if not messagebox.askyesno("Confirmar Atualização", 
                                     f"Foram encontradas {count_before} cotação(ões) vencida(s).\n"
                                     f"Deseja atualizar o status para 'Rejeitada'?"):
                return
            
            # Atualizar cotações vencidas
            c.execute("""
                UPDATE cotacoes 
                SET status = 'Rejeitada' 
                WHERE status = 'Em Aberto' 
                AND data_validade IS NOT NULL 
                AND data_validade != ''
                AND date(data_validade) < date('now')
            """)
            
            conn.commit()
            
            self.show_success(f"{count_before} cotação(ões) vencida(s) atualizada(s) para 'Rejeitada'!")
            self.carregar_cotacoes()  # Recarregar lista
            
        except sqlite3.Error as e:
            self.show_error(f"Erro ao verificar cotações vencidas: {e}")
        finally:
            conn.close()

    def create_cotacoes_indicadores(self, parent):
        """Criar indicadores para a aba de cotações"""
        # Criar indicadores baseados no nível de acesso
        if self.role == 'Admin':
            self.create_admin_cotacoes_indicadores(parent)
        else:
            self.create_user_cotacoes_indicadores(parent)
    
    def create_admin_cotacoes_indicadores(self, parent):
        """Indicadores para administradores - dados gerais"""
        # Faturamento total
        faturamento_frame = tk.LabelFrame(parent, text="Faturamento Total", bg='#f8fafc', font=('Arial', 12, 'bold'))
        faturamento_frame.pack(fill="x", padx=10, pady=5)
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT COALESCE(SUM(valor_total), 0) FROM cotacoes WHERE status = 'Aprovada'")
        faturamento = c.fetchone()[0]
        conn.close()
        
        tk.Label(faturamento_frame, text=f"R$ {format_currency(faturamento)}", font=('Arial', 20, 'bold'), 
                bg='#f8fafc', fg='#059669').pack(pady=10)
        
        # Total de itens vendidos
        itens_frame = tk.LabelFrame(parent, text="Total de Itens Vendidos", bg='#f8fafc', font=('Arial', 12, 'bold'))
        itens_frame.pack(fill="x", padx=10, pady=5)
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""
            SELECT COALESCE(SUM(ci.quantidade), 0)
            FROM cotacoes c
            JOIN cotacao_itens ci ON c.id = ci.cotacao_id
            WHERE c.status = 'Aprovada'
        """)
        itens_vendidos = c.fetchone()[0]
        conn.close()
        
        tk.Label(itens_frame, text=f"{itens_vendidos}", font=('Arial', 20, 'bold'), 
                bg='#f8fafc', fg='#1e40af').pack(pady=10)
        
        # Estados que mais compram
        estados_frame = tk.LabelFrame(parent, text="Estados que Mais Compram", bg='#f8fafc', font=('Arial', 12, 'bold'))
        estados_frame.pack(fill="x", padx=10, pady=5)
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""
            SELECT cl.estado, COUNT(c.id) as total_cotacoes
            FROM cotacoes c
            JOIN clientes cl ON c.cliente_id = cl.id
            WHERE c.status = 'Aprovada' AND cl.estado IS NOT NULL
            GROUP BY cl.estado
            ORDER BY total_cotacoes DESC
            LIMIT 5
        """)
        estados = c.fetchall()
        conn.close()
        
        for estado, total in estados:
            tk.Label(estados_frame, text=f"{estado}: {total}", font=('Arial', 10), 
                    bg='#f8fafc').pack(anchor="w", padx=10, pady=2)
        
        # Cotações declinadas
        declinadas_frame = tk.LabelFrame(parent, text="Cotações Declinadas", bg='#f8fafc', font=('Arial', 12, 'bold'))
        declinadas_frame.pack(fill="x", padx=10, pady=5)
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM cotacoes WHERE status = 'Rejeitada'")
        declinadas = c.fetchone()[0]
        conn.close()
        
        tk.Label(declinadas_frame, text=f"{declinadas}", font=('Arial', 20, 'bold'), 
                bg='#f8fafc', fg='#dc2626').pack(pady=10)
        
        # Status das cotações
        status_frame = tk.LabelFrame(parent, text="Status das Cotações", bg='#f8fafc', font=('Arial', 12, 'bold'))
        status_frame.pack(fill="x", padx=10, pady=5)
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""
            SELECT status, COUNT(*) as total
            FROM cotacoes
            GROUP BY status
            ORDER BY total DESC
        """)
        status_list = c.fetchall()
        conn.close()
        
        for status, total in status_list:
            color = '#059669' if status == 'Aprovada' else '#dc2626' if status == 'Rejeitada' else '#f59e0b'
            tk.Label(status_frame, text=f"{status}: {total}", font=('Arial', 10), 
                    bg='#f8fafc', fg=color).pack(anchor="w", padx=10, pady=2)
    
    def create_user_cotacoes_indicadores(self, parent):
        """Indicadores para usuários comuns - dados individuais"""
        # Minhas cotações
        minhas_frame = tk.LabelFrame(parent, text="Minhas Cotações", bg='#f8fafc', font=('Arial', 12, 'bold'))
        minhas_frame.pack(fill="x", padx=10, pady=5)
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM cotacoes WHERE responsavel_id = ?", (self.user_id,))
        total = c.fetchone()[0]
        conn.close()
        
        tk.Label(minhas_frame, text=f"{total}", font=('Arial', 24, 'bold'), 
                bg='#f8fafc', fg='#059669').pack(pady=10)
        
        # Meu faturamento
        faturamento_frame = tk.LabelFrame(parent, text="Meu Faturamento", bg='#f8fafc', font=('Arial', 12, 'bold'))
        faturamento_frame.pack(fill="x", padx=10, pady=5)
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT COALESCE(SUM(valor_total), 0) FROM cotacoes WHERE responsavel_id = ? AND status = 'Aprovada'", (self.user_id,))
        faturamento = c.fetchone()[0]
        conn.close()
        
        tk.Label(faturamento_frame, text=f"R$ {format_currency(faturamento)}", font=('Arial', 16, 'bold'), 
                bg='#f8fafc', fg='#059669').pack(pady=10)
        
        # Meus status
        status_frame = tk.LabelFrame(parent, text="Status das Minhas Cotações", bg='#f8fafc', font=('Arial', 12, 'bold'))
        status_frame.pack(fill="x", padx=10, pady=5)
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""
            SELECT status, COUNT(*) as total
            FROM cotacoes
            WHERE responsavel_id = ?
            GROUP BY status
            ORDER BY total DESC
        """, (self.user_id,))
        status_list = c.fetchall()
        conn.close()
        
        for status, total in status_list:
            color = '#059669' if status == 'Aprovada' else '#dc2626' if status == 'Rejeitada' else '#f59e0b'
            tk.Label(status_frame, text=f"{status}: {total}", font=('Arial', 10), 
                    bg='#f8fafc', fg=color).pack(anchor="w", padx=10, pady=2)
        
        # Meus clientes mais frequentes
        clientes_frame = tk.LabelFrame(parent, text="Meus Clientes Mais Frequentes", bg='#f8fafc', font=('Arial', 12, 'bold'))
        clientes_frame.pack(fill="x", padx=10, pady=5)
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""
            SELECT cl.nome, COUNT(c.id) as total_cotacoes
            FROM cotacoes c
            JOIN clientes cl ON c.cliente_id = cl.id
            WHERE c.responsavel_id = ?
            GROUP BY c.cliente_id
            ORDER BY total_cotacoes DESC
            LIMIT 5
        """, (self.user_id,))
        clientes = c.fetchall()
        conn.close()
        
        for nome, total in clientes:
            tk.Label(clientes_frame, text=f"{nome}: {total}", font=('Arial', 10), 
                    bg='#f8fafc').pack(anchor="w", padx=10, pady=2)