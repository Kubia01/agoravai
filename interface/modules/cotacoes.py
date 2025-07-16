import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sqlite3
from database import DB_NAME
from .base_module import BaseModule
from utils.formatters import format_currency, format_date
from python_app.pdf_generator_cotacao import gerar_pdf_cotacao

class CotacoesModule(BaseModule):
    def __init__(self, parent, user_id, role):
        super().__init__(parent, user_id, role)
        # Registrar para receber eventos
        if hasattr(self.master, 'register_listener'):
            self.master.register_listener(self.handle_event)
            
    def handle_event(self, event_type):
        if event_type == 'clientes_updated':
            self.load_clientes()
            # Notification without the popup for a smoother experience
            print("Lista de clientes atualizada no módulo de cotações")
        elif event_type == 'produtos_updated':
            self.carregar_itens_do_banco()
            # Update any item dropdown menus
            self.update_item_dropdown()
            print("Lista de produtos atualizada no módulo de cotações")
            
    def update_item_dropdown(self):
        """Update the item dropdown with the latest items"""
        current_tipo = self.item_tipo_var.get()
        current_items = self.itens_cadastrados.get(current_tipo, [])
        self.item_nome_combo['values'] = [item['nome'] for item in current_items]
        # If the current selected item is no longer in the list, clear it
        if self.item_nome_var.get() and self.item_nome_var.get() not in self.item_nome_combo['values']:
            self.item_nome_var.set('')

    def setup_ui(self):
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
        
    def create_header(self, parent):
        header_frame = tk.Frame(parent, bg='#f8fafc')
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Título
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
        content_frame = tk.Frame(parent, bg='white', padx=20, pady=20)
        content_frame.pack(fill="both", expand=True)
        
        # Seção: Dados da Cotação
        self.create_dados_cotacao_section(content_frame)
        
        # Seção: Itens da Cotação
        self.create_itens_cotacao_section(content_frame)
        
        # Botões de ação
        self.create_cotacao_buttons(content_frame)
        
    def create_dados_cotacao_section(self, parent):
        # Frame da seção
        section_frame = tk.LabelFrame(parent, text="Dados da Cotação", 
                                      font=('Arial', 12, 'bold'),
                                      bg='white',
                                      padx=15, pady=15)
        section_frame.pack(fill="x", pady=(0, 15))
        
        # Grid de campos
        fields_frame = tk.Frame(section_frame, bg='white')
        fields_frame.pack(fill="x")
        
        # Variáveis
        self.numero_var = tk.StringVar()
        self.cliente_var = tk.StringVar()
        self.modelo_var = tk.StringVar()
        self.serie_var = tk.StringVar()
        self.valor_var = tk.StringVar()
        self.status_var = tk.StringVar()
        
        # Campos
        row = 0
        
        # Número da Proposta
        tk.Label(fields_frame, text="Número da Proposta *:", 
                 font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.numero_var, 
                 font=('Arial', 10), width=30).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Cliente
        tk.Label(fields_frame, text="Cliente *:", 
                 font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        self.cliente_combo = ttk.Combobox(fields_frame, textvariable=self.cliente_var, 
                                         width=30, state="readonly")
        self.cliente_combo.grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Modelo do Compressor
        tk.Label(fields_frame, text="Modelo do Compressor:", 
                 font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.modelo_var, 
                 font=('Arial', 10), width=30).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Número de Série
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
                                   width=30)
        status_combo.grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        self.status_var.set("Em Aberto")
        
        # Configurar colunas
        fields_frame.grid_columnconfigure(1, weight=1)
        
        # Carregar clientes
        self.load_clientes()
        
    def create_itens_cotacao_section(self, parent):
        # Frame da seção
        section_frame = tk.LabelFrame(parent, text="Itens da Cotação", 
                                      font=('Arial', 12, 'bold'),
                                      bg='white',
                                      padx=15, pady=15)
        section_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # Frame para adicionar item
        add_item_frame = tk.Frame(section_frame, bg='white')
        add_item_frame.pack(fill="x", pady=(0, 10))
        
        # Campos para novo item
        self.create_item_fields(add_item_frame)
        
        # Lista de itens
        self.create_itens_list(section_frame)
        
    def create_item_fields(self, frame):
        self.item_tipo_var = tk.StringVar()
        self.item_nome_var = tk.StringVar()
        self.item_qtd_var = tk.StringVar(value="1")
        self.item_valor_var = tk.StringVar(value="0.00")
        self.item_desc_var = tk.StringVar()
        self.item_mao_obra_var = tk.StringVar(value="0.00")
        self.item_deslocamento_var = tk.StringVar(value="0.00")
        self.item_estadia_var = tk.StringVar(value="0.00")

        # Adicionar evento para atualizar nomes quando o tipo muda
        self.item_tipo_var.trace_add('write', self.atualizar_nomes_combobox)
        
        fields_grid = tk.Frame(frame, bg="white")
        fields_grid.pack(padx=10, pady=(0, 10), fill="x")

        tk.Label(fields_grid, text="Tipo:", font=("Arial", 10, "bold"), bg="white").grid(row=0, column=0, padx=5, sticky="w")
        tipo_combo = ttk.Combobox(fields_grid, textvariable=self.item_tipo_var, 
                                 values=["Produto", "Serviço", "Kit"], 
                                 width=10, state="readonly")
        tipo_combo.grid(row=0, column=1, padx=5)

        tk.Label(fields_grid, text="Nome:", font=("Arial", 10, "bold"), bg="white").grid(row=0, column=2, padx=5, sticky="w")
        # Criar combobox para nomes (será preenchido dinamicamente)
        self.nome_combo = ttk.Combobox(fields_grid, textvariable=self.item_nome_var, 
                                      width=25, state="readonly")
        self.nome_combo.grid(row=0, column=3, padx=5)
        self.nome_combo.bind("<<ComboboxSelected>>", self.preencher_valor_unitario)

        tk.Label(fields_grid, text="Qtd:", font=("Arial", 10, "bold"), bg="white").grid(row=0, column=4, padx=5, sticky="w")
        tk.Entry(fields_grid, textvariable=self.item_qtd_var, width=5).grid(row=0, column=5, padx=5)

        tk.Label(fields_grid, text="Valor Unit.:", font=("Arial", 10, "bold"), bg="white").grid(row=0, column=6, padx=5, sticky="w")
        tk.Entry(fields_grid, textvariable=self.item_valor_var, width=10).grid(row=0, column=7, padx=5)

        tk.Label(fields_grid, text="Descrição:", font=("Arial", 10, "bold"), bg="white").grid(row=1, column=0, padx=5, sticky="w")
        tk.Entry(fields_grid, textvariable=self.item_desc_var, width=42).grid(row=1, column=1, columnspan=3, padx=5, sticky="w")

        # Mão de Obra
        tk.Label(fields_grid, text="Mão de Obra:", font=("Arial", 10, "bold"), bg="white").grid(row=2, column=0, padx=5, sticky="w")
        tk.Entry(fields_grid, textvariable=self.item_mao_obra_var, width=10).grid(row=2, column=1, padx=5)

        # Deslocamento
        tk.Label(fields_grid, text="Deslocamento:", font=("Arial", 10, "bold"), bg="white").grid(row=2, column=2, padx=5, sticky="w")
        tk.Entry(fields_grid, textvariable=self.item_deslocamento_var, width=10).grid(row=2, column=3, padx=5)

        # Estadia
        tk.Label(fields_grid, text="Estadia:", font=("Arial", 10, "bold"), bg="white").grid(row=2, column=4, padx=5, sticky="w")
        tk.Entry(fields_grid, textvariable=self.item_estadia_var, width=10).grid(row=2, column=5, padx=5)

        adicionar_button = tk.Button(fields_grid, text="Adicionar Item", command=self.adicionar_item)
        adicionar_button.grid(row=0, column=10, padx=10)
        
        # Carregar itens do banco
        self.carregar_itens_do_banco()

    def carregar_itens_do_banco(self):
        """Carrega todos os produtos/serviços/kits do banco de dados"""
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        try:
            # Carregar itens ativos
            c.execute("SELECT id, nome, tipo, valor_unitario FROM produtos WHERE ativo = 1")
            # Limpar o dicionário atual e reinicializar
            self.itens_cadastrados = {
                "Produto": [],
                "Serviço": [],
                "Kit": []
            }
            
            for item in c.fetchall():
                item_id, nome, tipo, valor = item
                if tipo in self.itens_cadastrados:
                    self.itens_cadastrados[tipo].append({
                        "id": item_id,
                        "nome": nome,
                        "valor": valor
                    })
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao carregar produtos: {e}")
        finally:
            conn.close()

    def atualizar_nomes_combobox(self, *args):
        """Atualiza o combobox de nomes conforme o tipo selecionado"""
        tipo_selecionado = self.item_tipo_var.get()
        if tipo_selecionado in self.itens_cadastrados:
            # Obter apenas os nomes para o combobox
            nomes = [item["nome"] for item in self.itens_cadastrados[tipo_selecionado]]
            self.nome_combo['values'] = nomes
            self.item_nome_var.set('')  # Limpar seleção atual
            # Também limpar o valor unitário
            self.item_valor_var.set("0.00")
        else:
            self.nome_combo['values'] = []

    def preencher_valor_unitario(self, event=None):
        tipo_selecionado = self.item_tipo_var.get()
        nome_selecionado = self.item_nome_var.get()
        
        if tipo_selecionado and nome_selecionado:
            # Encontrar o item correspondente
            for item in self.itens_cadastrados[tipo_selecionado]:
                if item["nome"] == nome_selecionado:
                    self.item_valor_var.set(f"{item['valor']:.2f}")
                    
                    # Preencher descrição para kits
                    if tipo_selecionado == "Kit":
                        descricao = self.obter_descricao_kit(item["id"])
                        self.item_desc_var.set(descricao)
                    break

    def obter_descricao_kit(self, kit_id):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        descricao = "Composição do Kit:\n"
        
        try:
            c.execute("""
                SELECT p.nome, kc.quantidade 
                FROM kit_composicao kc
                JOIN produtos p ON kc.produto_id = p.id
                WHERE kc.kit_id = ?
            """, (kit_id,))
            
            for row in c.fetchall():
                nome, quantidade = row
                descricao += f"{quantidade} x {nome}\n"
                
        except sqlite3.Error:
            descricao = "Kit"
        finally:
            conn.close()
        
        return descricao.strip()

    def create_itens_list(self, parent):
        # Frame para lista
        list_frame = tk.Frame(parent, bg='white')
        list_frame.pack(fill="both", expand=True)
        
        # Treeview
        columns = ("tipo", "nome", "qtd", "valor_unit", "valor_total", "descricao")
        self.itens_tree = ttk.Treeview(list_frame, 
                                      columns=columns,
                                      show="headings",
                                      height=8)
        
        # Cabeçalhos
        self.itens_tree.heading("tipo", text="Tipo")
        self.itens_tree.heading("nome", text="Nome")
        self.itens_tree.heading("qtd", text="Qtd")
        self.itens_tree.heading("valor_unit", text="Valor Unit.")
        self.itens_tree.heading("valor_total", text="Valor Total")
        self.itens_tree.heading("descricao", text="Descrição")
        
        # Larguras
        self.itens_tree.column("tipo", width=80)
        self.itens_tree.column("nome", width=200)
        self.itens_tree.column("qtd", width=60)
        self.itens_tree.column("valor_unit", width=100)
        self.itens_tree.column("valor_total", width=100)
        self.itens_tree.column("descricao", width=250)
        
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
        
        remove_btn = tk.Button(item_buttons, text="Remover Item",
                              font=('Arial', 10),
                              bg='#dc2626',
                              fg='white',
                              relief='flat',
                              cursor='hand2',
                              padx=15,
                              command=self.remover_item)
        remove_btn.pack(side="left", padx=5)
        
        # Label do total
        self.total_label = tk.Label(item_buttons, text="Total: R$ 0,00",
                                   font=('Arial', 12, 'bold'),
                                   bg='white',
                                   fg='#1e293b')
        self.total_label.pack(side="right")
        
    def create_cotacao_buttons(self, parent):
        # Frame dos botões
        buttons_frame = tk.Frame(parent, bg='white')
        buttons_frame.pack(fill="x", pady=(20, 0))
        
        # Botões
        cancel_btn = tk.Button(buttons_frame, text="Nova Cotação",
                              font=('Arial', 10),
                              bg='#e2e8f0',
                              fg='#475569',
                              relief='flat',
                              cursor='hand2',
                              padx=15,
                              pady=8,
                              command=self.nova_cotacao)
        cancel_btn.pack(side="left", padx=(0, 10))
        
        save_btn = tk.Button(buttons_frame, text="Salvar Cotação",
                            font=('Arial', 10, 'bold'),
                            bg='#3b82f6',
                            fg='white',
                            relief='flat',
                            cursor='hand2',
                            padx=15,
                            pady=8,
                            command=self.salvar_cotacao)
        save_btn.pack(side="left")
        
        # Botão para gerar PDF
        pdf_btn = tk.Button(buttons_frame, text="Gerar PDF",
                           font=('Arial', 10, 'bold'),
                           bg='#8b5cf6',
                           fg='white',
                           relief='flat',
                           cursor='hand2',
                           padx=15,
                           pady=8,
                           command=self.gerar_pdf_cotacao)
        pdf_btn.pack(side="left", padx=(10, 0))
        
    def create_lista_cotacoes_tab(self):
        # Frame da aba
        lista_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(lista_frame, text="Lista de Cotações")
        
        content_frame = tk.Frame(lista_frame, bg='white', padx=20, pady=20)
        content_frame.pack(fill="both", expand=True)
        
        # Busca
        search_frame = tk.Frame(content_frame, bg='white')
        search_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(search_frame, text="🔍 Buscar:", 
                 font=('Arial', 12), bg='white').pack(side="left", padx=(0, 10))
        
        self.search_cotacao_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_cotacao_var,
                               font=('Arial', 11), width=50)
        search_entry.pack(side="left", fill="x", expand=True, ipady=5)
        
        search_btn = tk.Button(search_frame, text="Buscar",
                              font=('Arial', 10),
                              bg='#3b82f6',
                              fg='white',
                              relief='flat',
                              cursor='hand2',
                              padx=15,
                              command=self.buscar_cotacoes)
        search_btn.pack(side="left", padx=(10, 0))
        
        # Lista de cotações
        self.create_cotacoes_list(content_frame)
        
    def create_cotacoes_list(self, parent):
        # Treeview
        columns = ("id", "numero", "cliente", "data", "valor", "status")
        self.cotacoes_tree = ttk.Treeview(parent, 
                                         columns=columns,
                                         show="headings")
        
        # Cabeçalhos
        self.cotacoes_tree.heading("id", text="ID")
        self.cotacoes_tree.heading("numero", text="Número")
        self.cotacoes_tree.heading("cliente", text="Cliente")
        self.cotacoes_tree.heading("data", text="Data")
        self.cotacoes_tree.heading("valor", text="Valor")
        self.cotacoes_tree.heading("status", text="Status")
        
        # Larguras
        self.cotacoes_tree.column("id", width=50)
        self.cotacoes_tree.column("numero", width=150)
        self.cotacoes_tree.column("cliente", width=200)
        self.cotacoes_tree.column("data", width=100)
        self.cotacoes_tree.column("valor", width=120)
        self.cotacoes_tree.column("status", width=100)
        
        # Scrollbar
        scrollbar_cot = ttk.Scrollbar(parent, orient="vertical", 
                                     command=self.cotacoes_tree.yview)
        self.cotacoes_tree.configure(yscrollcommand=scrollbar_cot.set)
        
        # Pack
        self.cotacoes_tree.pack(side="left", fill="both", expand=True)
        scrollbar_cot.pack(side="right", fill="y")
        
        # Bind duplo clique
        self.cotacoes_tree.bind("<Double-1>", self.editar_cotacao)
        
        # Menu de contexto
        self.context_menu = tk.Menu(self.cotacoes_tree, tearoff=0)
        self.context_menu.add_command(label="Editar", command=self.editar_cotacao)
        self.context_menu.add_command(label="Gerar PDF", command=self.gerar_pdf_selecionada)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Excluir", command=self.excluir_cotacao)
        
        self.cotacoes_tree.bind("<Button-3>", self.show_context_menu)
        
        # Carregar cotações
        self.carregar_cotacoes()
        
    def show_context_menu(self, event):
        # Selecionar o item clicado
        item = self.cotacoes_tree.identify_row(event.y)
        if item:
            self.cotacoes_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
            
    def load_clientes(self):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            c.execute("SELECT id, nome FROM clientes ORDER BY nome")
            clientes = c.fetchall()
            
            self.clientes_dict = {f"{nome} (ID: {id})": id for id, nome in clientes}
            self.cliente_combo['values'] = list(self.clientes_dict.keys())
            
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

        mao_obra_str = self.item_mao_obra_var.get()
        deslocamento_str = self.item_deslocamento_var.get()
        estadia_str = self.item_estadia_var.get()

        try:
            quantidade = int(qtd_str) if qtd_str else 1
            valor_unitario = float(valor_str.replace(",", ".") or 0.0)
            mao_obra = float(mao_obra_str.replace(",", ".") or 0.0)
            deslocamento = float(deslocamento_str.replace(",", ".") or 0.0)
            estadia = float(estadia_str.replace(",", ".") or 0.0)
            valor_total = quantidade * (valor_unitario + mao_obra + deslocamento + estadia)
        except ValueError:
            messagebox.showerror("Erro", "Preencha os campos numéricos corretamente.")
            return

        item = {
            "tipo": tipo,
            "nome": nome,
            "quantidade": quantidade,
            "valor_unitario": valor_unitario,
            "mao_obra": mao_obra,
            "deslocamento": deslocamento,
            "estadia": estadia,
            "descricao": descricao,
            "valor_total": valor_total,
        }

        self.current_cotacao_itens.append(item)
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
        
    def remover_item(self):
        selected = self.itens_tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um item para remover.")
            return
            
        index = self.itens_tree.index(selected[0])
        del self.current_cotacao_itens[index]
        self.atualizar_lista_itens()
        self.calcular_total()
        
    def atualizar_lista_itens(self):
        for item in self.itens_tree.get_children():
            self.itens_tree.delete(item)
            
        for item in self.current_cotacao_itens:
            # Tratar itens antigos que não têm os campos adicionais
            mao_obra = item.get('mao_obra', 0.0)
            deslocamento = item.get('deslocamento', 0.0)
            estadia = item.get('estadia', 0.0)
            
            descricao = item["descricao"]
            
            # Adicionar detalhes extras para serviços
            if item["tipo"] == "Serviço":
                extras = []
                if mao_obra > 0:
                    extras.append(f"Mão de Obra: R${mao_obra:.2f}")
                if deslocamento > 0:
                    extras.append(f"Deslocamento: R${deslocamento:.2f}")
                if estadia > 0:
                    extras.append(f"Estadia: R${estadia:.2f}")
                    
                if extras:
                    descricao += "\n" + " | ".join(extras)
            
            self.itens_tree.insert("", "end", values=(
                item["tipo"],
                item["nome"],
                item["quantidade"],
                f"R$ {item['valor_unitario']:.2f}",
                f"R$ {item['valor_total']:.2f}",
                descricao
        ))
            
    def calcular_total(self):
        total = sum(item["valor_total"] for item in self.current_cotacao_itens)
        self.total_label.config(text=f"Total: R$ {total:.2f}")
        
    def nova_cotacao(self):
        self.current_cotacao_id = None
        self.current_cotacao_itens = []
        
        # Limpar campos
        self.numero_var.set("")
        self.cliente_var.set("")
        self.modelo_var.set("")
        self.serie_var.set("")
        self.status_var.set("Em Aberto")
        
        # Limpar itens
        self.atualizar_lista_itens()
        self.calcular_total()
        
        messagebox.showinfo("Nova Cotação", "Campos limpos para nova cotação.")
        
    def salvar_cotacao(self):
        numero = self.numero_var.get()
        cliente_key = self.cliente_var.get()
        modelo = self.modelo_var.get()
        serie = self.serie_var.get()
        status = self.status_var.get()
        
        if not numero or not cliente_key:
            messagebox.showwarning("Aviso", "Número da proposta e cliente são obrigatórios.")
            return
            
        if not self.current_cotacao_itens:
            messagebox.showwarning("Aviso", "Adicione pelo menos um item à cotação.")
            return
            
        cliente_id = self.clientes_dict[cliente_key]
        valor_total = sum(item["valor_total"] for item in self.current_cotacao_itens)
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            if self.current_cotacao_id:
                # Atualizar cotação existente
                c.execute("""
                    UPDATE cotacoes SET
                        numero_proposta=?, cliente_id=?, modelo_compressor=?,
                        numero_serie_compressor=?, valor_total=?, status=?
                    WHERE id=?
                """, (numero, cliente_id, modelo, serie, valor_total, status, self.current_cotacao_id))
                
                # Remover itens antigos
                c.execute("DELETE FROM itens_cotacao WHERE cotacao_id=?", (self.current_cotacao_id,))
            else:
                # Inserir nova cotação
                from datetime import datetime
                data_criacao = datetime.now().strftime('%Y-%m-%d')
                
                c.execute("""
                    INSERT INTO cotacoes (
                        numero_proposta, cliente_id, responsavel_id, data_criacao,
                        modelo_compressor, numero_serie_compressor, valor_total, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (numero, cliente_id, self.user_id, data_criacao, modelo, serie, valor_total, status))
                
                self.current_cotacao_id = c.lastrowid
            
            # Inserir itens
            for item in self.current_cotacao_itens:
                c.execute("""
                    INSERT INTO itens_cotacao (
                        cotacao_id, tipo, item_nome, quantidade, descricao,
                        valor_unitario, valor_total_item
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.current_cotacao_id, item["tipo"], item["nome"],
                    item["quantidade"], item["descricao"],
                    item["valor_unitario"], item["valor_total"]
                ))
            
            conn.commit()
            messagebox.showinfo("Sucesso", "Cotação salva com sucesso!")
            self.carregar_cotacoes()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Número da proposta já existe.")
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao salvar cotação: {e}")
        finally:
            conn.close()
            
    def gerar_pdf_cotacao(self):
        if not self.current_cotacao_id:
            messagebox.showwarning("Aviso", "Salve a cotação antes de gerar o PDF.")
            return
            
        try:
            sucesso, resultado = gerar_pdf_cotacao(self.current_cotacao_id, DB_NAME)
            
            if sucesso:
                messagebox.showinfo("Sucesso", f"PDF gerado com sucesso!\nArquivo: {resultado}")
                # Abrir o arquivo PDF
                import os
                os.startfile(resultado)
            else:
                messagebox.showerror("Erro", f"Erro ao gerar PDF: {resultado}")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {e}")
            
    def gerar_pdf_selecionada(self):
        selected = self.cotacoes_tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma cotação para gerar o PDF.")
            return
            
        cotacao_id = self.cotacoes_tree.item(selected[0])['values'][0]
        
        try:
            sucesso, resultado = gerar_pdf_cotacao(cotacao_id, DB_NAME)
            
            if sucesso:
                messagebox.showinfo("Sucesso", f"PDF gerado com sucesso!\nArquivo: {resultado}")
                # Abrir o arquivo PDF
                import os
                os.startfile(resultado)
            else:
                messagebox.showerror("Erro", f"Erro ao gerar PDF: {resultado}")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {e}")
            
    def carregar_cotacoes(self):
        # Limpar lista
        for item in self.cotacoes_tree.get_children():
            self.cotacoes_tree.delete(item)
            
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            c.execute("""
                SELECT c.id, c.numero_proposta, cl.nome, c.data_criacao, c.valor_total, c.status
                FROM cotacoes c
                JOIN clientes cl ON c.cliente_id = cl.id
                ORDER BY c.data_criacao DESC
            """)
            
            for row in c.fetchall():
                self.cotacoes_tree.insert("", "end", values=(
                    row[0], row[1], row[2], row[3], 
                    f"R$ {row[4]:.2f}" if row[4] else "R$ 0,00", row[5]
                ))
                
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao carregar cotações: {e}")
        finally:
            conn.close()
            
    def buscar_cotacoes(self):
        # Implementar busca
        self.carregar_cotacoes()
        
    def editar_cotacao(self, event=None):
        selected = self.cotacoes_tree.selection()
        if not selected:
            return
            
        cotacao_id = self.cotacoes_tree.item(selected[0])['values'][0]
        self.carregar_cotacao_para_edicao(cotacao_id)
        
    def excluir_cotacao(self):
        selected = self.cotacoes_tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma cotação para excluir.")
            return
            
        if messagebox.askyesno("Confirmar", "Deseja realmente excluir esta cotação?"):
            cotacao_id = self.cotacoes_tree.item(selected[0])['values'][0]
            
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            
            try:
                c.execute("DELETE FROM itens_cotacao WHERE cotacao_id=?", (cotacao_id,))
                c.execute("DELETE FROM cotacoes WHERE id=?", (cotacao_id,))
                conn.commit()
                
                messagebox.showinfo("Sucesso", "Cotação excluída com sucesso!")
                self.carregar_cotacoes()
                
            except sqlite3.Error as e:
                messagebox.showerror("Erro", f"Erro ao excluir cotação: {e}")
            finally:
                conn.close()
        
    def carregar_cotacao_para_edicao(self, cotacao_id):
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
            if cotacao:
                self.current_cotacao_id = cotacao_id
                self.numero_var.set(cotacao[1])
                
                # Encontrar cliente no combo
                cliente_key = f"{cotacao[-1]} (ID: {cotacao[2]})"
                self.cliente_var.set(cliente_key)
                
                self.modelo_var.set(cotacao[6] or "")
                self.serie_var.set(cotacao[7] or "")
                self.status_var.set(cotacao[15] or "Em Aberto")
                
                # Carregar itens
                c.execute("""
                    SELECT tipo, item_nome, quantidade, descricao, valor_unitario, valor_total_item
                    FROM itens_cotacao WHERE cotacao_id = ?
                """, (cotacao_id,))
                
                self.current_cotacao_itens = []
                for item_row in c.fetchall():
                    item = {
                        "tipo": item_row[0],
                        "nome": item_row[1],
                        "quantidade": item_row[2],
                        "descricao": item_row[3],
                        "valor_unitario": item_row[4],
                        "valor_total": item_row[5]
                    }
                    self.current_cotacao_itens.append(item)
                
                self.atualizar_lista_itens()
                self.calcular_total()
                
                # Mudar para aba de nova cotação
                self.notebook.select(0)
                
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao carregar cotação: {e}")
        finally:
            conn.close()