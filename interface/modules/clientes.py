import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from .base_module import BaseModule
from database import DB_NAME
from utils.formatters import format_cnpj, format_phone, validate_cnpj, validate_email

class ClientesModule(BaseModule):
    def setup_ui(self):
        # Container principal
        container = tk.Frame(self.frame, bg='#f8fafc')
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        self.create_header(container)
        
        # Notebook para organizar seções
        self.notebook = ttk.Notebook(container)
        self.notebook.pack(fill="both", expand=True, pady=(20, 0))
        
        # Aba: Novo Cliente
        self.create_novo_cliente_tab()
        
        # Aba: Lista de Clientes
        self.create_lista_clientes_tab()
        
        # Inicializar variáveis
        self.current_cliente_id = None
        
        # Carregar dados
        self.carregar_clientes()
        
    def create_header(self, parent):
        header_frame = tk.Frame(parent, bg='#f8fafc')
        header_frame.pack(fill="x", pady=(0, 20))
        
        title_label = tk.Label(header_frame, text="Gestão de Clientes", 
                               font=('Arial', 18, 'bold'),
                               bg='#f8fafc',
                               fg='#1e293b')
        title_label.pack(side="left")
        
    def create_novo_cliente_tab(self):
        # Frame da aba
        cliente_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(cliente_frame, text="Novo Cliente")
        
        # Scroll frame
        canvas = tk.Canvas(cliente_frame, bg='white')
        scrollbar = ttk.Scrollbar(cliente_frame, orient="vertical", command=canvas.yview)
        self.scrollable_cliente = tk.Frame(canvas, bg='white')
        
        self.scrollable_cliente.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_cliente, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Conteúdo do cliente
        self.create_cliente_content(self.scrollable_cliente)
        
    def create_cliente_content(self, parent):
        content_frame = tk.Frame(parent, bg='white', padx=20, pady=20)
        content_frame.pack(fill="both", expand=True)
        
        # Seção: Dados Básicos
        self.create_dados_basicos_section(content_frame)
        
        # Seção: Endereço
        self.create_endereco_section(content_frame)
        
        # Seção: Contato
        self.create_contato_section(content_frame)
        
        # Botões de ação
        self.create_cliente_buttons(content_frame)
        
    def create_dados_basicos_section(self, parent):
        section_frame = self.create_section_frame(parent, "Dados Básicos")
        section_frame.pack(fill="x", pady=(0, 15))
        
        # Grid de campos
        fields_frame = tk.Frame(section_frame, bg='white')
        fields_frame.pack(fill="x")
        
        # Variáveis
        self.nome_var = tk.StringVar()
        self.nome_fantasia_var = tk.StringVar()
        self.cnpj_var = tk.StringVar()
        self.contato_var = tk.StringVar()
        
        row = 0
        
        # Nome
        tk.Label(fields_frame, text="Nome/Razão Social *:", 
                 font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.nome_var, 
                 font=('Arial', 10), width=40).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Nome Fantasia
        tk.Label(fields_frame, text="Nome Fantasia:", 
                 font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.nome_fantasia_var, 
                 font=('Arial', 10), width=40).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # CNPJ
        tk.Label(fields_frame, text="CNPJ:", 
                 font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        cnpj_entry = tk.Entry(fields_frame, textvariable=self.cnpj_var, 
                              font=('Arial', 10), width=40)
        cnpj_entry.grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        cnpj_entry.bind('<FocusOut>', self.format_cnpj)
        row += 1
        
        # Contato Principal
        tk.Label(fields_frame, text="Contato Principal:", 
                 font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.contato_var, 
                 font=('Arial', 10), width=40).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Configurar colunas
        fields_frame.grid_columnconfigure(1, weight=1)
        
    def create_endereco_section(self, parent):
        section_frame = self.create_section_frame(parent, "Endereço")
        section_frame.pack(fill="x", pady=(0, 15))
        
        # Grid de campos
        fields_frame = tk.Frame(section_frame, bg='white')
        fields_frame.pack(fill="x")
        
        # Variáveis
        self.endereco_var = tk.StringVar()
        self.cidade_var = tk.StringVar()
        self.estado_var = tk.StringVar()
        self.cep_var = tk.StringVar()
        self.pais_var = tk.StringVar(value="Brasil")
        
        row = 0
        
        # Endereço
        tk.Label(fields_frame, text="Endereço:", 
                 font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.endereco_var, 
                 font=('Arial', 10), width=40).grid(row=row, column=1, columnspan=3, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Cidade
        tk.Label(fields_frame, text="Cidade:", 
                 font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.cidade_var, 
                 font=('Arial', 10), width=20).grid(row=row, column=1, sticky="ew", padx=(10, 5), pady=5)
        
        # Estado
        tk.Label(fields_frame, text="Estado:", 
                 font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=2, sticky="w", pady=5, padx=(10, 0))
        estado_combo = ttk.Combobox(fields_frame, textvariable=self.estado_var, 
                                   values=["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", 
                                          "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", 
                                          "RS", "RO", "RR", "SC", "SP", "SE", "TO"], 
                                   width=5, state="readonly")
        estado_combo.grid(row=row, column=3, sticky="w", padx=(10, 0), pady=5)
        row += 1
        
        # CEP
        tk.Label(fields_frame, text="CEP:", 
                 font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        cep_entry = tk.Entry(fields_frame, textvariable=self.cep_var, 
                             font=('Arial', 10), width=15)
        cep_entry.grid(row=row, column=1, sticky="w", padx=(10, 0), pady=5)
        cep_entry.bind('<FocusOut>', self.format_cep)
        
        # País
        tk.Label(fields_frame, text="País:", 
                 font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=2, sticky="w", pady=5, padx=(10, 0))
        tk.Entry(fields_frame, textvariable=self.pais_var, 
                 font=('Arial', 10), width=15).grid(row=row, column=3, sticky="w", padx=(10, 0), pady=5)
        
        # Configurar colunas
        fields_frame.grid_columnconfigure(1, weight=1)
        
    def create_contato_section(self, parent):
        section_frame = self.create_section_frame(parent, "Informações de Contato")
        section_frame.pack(fill="x", pady=(0, 15))
        
        # Grid de campos
        fields_frame = tk.Frame(section_frame, bg='white')
        fields_frame.pack(fill="x")
        
        # Variáveis
        self.telefone_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.site_var = tk.StringVar()
        self.prazo_pagamento_var = tk.StringVar()
        
        row = 0
        
        # Telefone
        tk.Label(fields_frame, text="Telefone:", 
                 font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        telefone_entry = tk.Entry(fields_frame, textvariable=self.telefone_var, 
                                  font=('Arial', 10), width=20)
        telefone_entry.grid(row=row, column=1, sticky="w", padx=(10, 0), pady=5)
        telefone_entry.bind('<FocusOut>', self.format_telefone)
        
        # Email
        tk.Label(fields_frame, text="Email:", 
                 font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=2, sticky="w", pady=5, padx=(20, 0))
        tk.Entry(fields_frame, textvariable=self.email_var, 
                 font=('Arial', 10), width=25).grid(row=row, column=3, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Site
        tk.Label(fields_frame, text="Site:", 
                 font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.site_var, 
                 font=('Arial', 10), width=30).grid(row=row, column=1, columnspan=2, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Prazo de Pagamento
        tk.Label(fields_frame, text="Prazo de Pagamento:", 
                 font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        prazo_combo = ttk.Combobox(fields_frame, textvariable=self.prazo_pagamento_var,
                                  values=["À vista", "15 dias", "30 dias", "45 dias", "60 dias", "90 dias"],
                                  width=15)
        prazo_combo.grid(row=row, column=1, sticky="w", padx=(10, 0), pady=5)
        
        # Configurar colunas
        fields_frame.grid_columnconfigure(3, weight=1)
        
    def create_cliente_buttons(self, parent):
        buttons_frame = tk.Frame(parent, bg='white')
        buttons_frame.pack(fill="x", pady=(20, 0))
        
        # Botões
        novo_btn = self.create_button(buttons_frame, "Novo Cliente", self.novo_cliente, bg='#e2e8f0', fg='#475569')
        novo_btn.pack(side="left", padx=(0, 10))
        
        salvar_btn = self.create_button(buttons_frame, "Salvar Cliente", self.salvar_cliente)
        salvar_btn.pack(side="left")
        
    def create_lista_clientes_tab(self):
        # Frame da aba
        lista_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(lista_frame, text="Lista de Clientes")
        
        # Container
        container = tk.Frame(lista_frame, bg='white', padx=20, pady=20)
        container.pack(fill="both", expand=True)
        
        # Frame de busca
        search_frame, self.search_var = self.create_search_frame(container, command=self.buscar_clientes)
        search_frame.pack(fill="x", pady=(0, 15))
        
        # Treeview para lista
        columns = ("nome", "cnpj", "cidade", "telefone", "email")
        self.clientes_tree = ttk.Treeview(container, columns=columns, show="headings", height=15)
        
        # Cabeçalhos
        self.clientes_tree.heading("nome", text="Nome/Razão Social")
        self.clientes_tree.heading("cnpj", text="CNPJ")
        self.clientes_tree.heading("cidade", text="Cidade")
        self.clientes_tree.heading("telefone", text="Telefone")
        self.clientes_tree.heading("email", text="Email")
        
        # Larguras
        self.clientes_tree.column("nome", width=250)
        self.clientes_tree.column("cnpj", width=150)
        self.clientes_tree.column("cidade", width=120)
        self.clientes_tree.column("telefone", width=120)
        self.clientes_tree.column("email", width=200)
        
        # Scrollbar
        lista_scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.clientes_tree.yview)
        self.clientes_tree.configure(yscrollcommand=lista_scrollbar.set)
        
        # Pack
        self.clientes_tree.pack(side="left", fill="both", expand=True)
        lista_scrollbar.pack(side="right", fill="y")
        
        # Botões da lista
        lista_buttons = tk.Frame(container, bg='white')
        lista_buttons.pack(fill="x", pady=(15, 0))
        
        editar_btn = self.create_button(lista_buttons, "Editar", self.editar_cliente)
        editar_btn.pack(side="left", padx=(0, 10))
        
        excluir_btn = self.create_button(lista_buttons, "Excluir", self.excluir_cliente, bg='#dc2626')
        excluir_btn.pack(side="left")
        
    def format_cnpj(self, event=None):
        """Formatar CNPJ automaticamente"""
        cnpj = self.cnpj_var.get()
        if cnpj:
            self.cnpj_var.set(format_cnpj(cnpj))
            
    def format_telefone(self, event=None):
        """Formatar telefone automaticamente"""
        telefone = self.telefone_var.get()
        if telefone:
            self.telefone_var.set(format_phone(telefone))
            
    def format_cep(self, event=None):
        """Formatar CEP automaticamente"""
        from utils.formatters import format_cep
        cep = self.cep_var.get()
        if cep:
            self.cep_var.set(format_cep(cep))
            
    def novo_cliente(self):
        """Limpar formulário para novo cliente"""
        self.current_cliente_id = None
        
        # Limpar todos os campos
        self.nome_var.set("")
        self.nome_fantasia_var.set("")
        self.cnpj_var.set("")
        self.contato_var.set("")
        self.endereco_var.set("")
        self.cidade_var.set("")
        self.estado_var.set("")
        self.cep_var.set("")
        self.pais_var.set("Brasil")
        self.telefone_var.set("")
        self.email_var.set("")
        self.site_var.set("")
        self.prazo_pagamento_var.set("")
        
    def salvar_cliente(self):
        """Salvar cliente no banco de dados"""
        # Validações
        nome = self.nome_var.get().strip()
        if not nome:
            self.show_warning("O nome/razão social é obrigatório.")
            return
            
        cnpj = self.cnpj_var.get().strip()
        if cnpj and not validate_cnpj(cnpj):
            self.show_warning("CNPJ inválido.")
            return
            
        email = self.email_var.get().strip()
        if email and not validate_email(email):
            self.show_warning("Email inválido.")
            return
            
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            # Preparar dados
            dados = (
                nome,
                self.contato_var.get().strip(),
                self.nome_fantasia_var.get().strip(),
                cnpj if cnpj else None,
                self.endereco_var.get().strip(),
                self.cidade_var.get().strip(),
                self.estado_var.get().strip(),
                self.cep_var.get().strip(),
                self.pais_var.get().strip(),
                self.telefone_var.get().strip(),
                email if email else None,
                self.site_var.get().strip(),
                self.prazo_pagamento_var.get().strip()
            )
            
            if self.current_cliente_id:
                # Atualizar cliente existente
                c.execute("""
                    UPDATE clientes SET
                        nome = ?, contato = ?, nome_fantasia = ?, cnpj = ?,
                        endereco = ?, cidade = ?, estado = ?, cep = ?, pais = ?,
                        telefone = ?, email = ?, site = ?, prazo_pagamento = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, dados + (self.current_cliente_id,))
            else:
                # Inserir novo cliente
                c.execute("""
                    INSERT INTO clientes (nome, contato, nome_fantasia, cnpj,
                                        endereco, cidade, estado, cep, pais,
                                        telefone, email, site, prazo_pagamento)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, dados)
                
                self.current_cliente_id = c.lastrowid
            
            conn.commit()
            self.show_success("Cliente salvo com sucesso!")
            
            # Emitir evento para atualizar outros módulos
            self.emit_event('cliente_created')
            
            # Recarregar lista
            self.carregar_clientes()
            
        except sqlite3.IntegrityError as e:
            if "cnpj" in str(e).lower():
                self.show_error("CNPJ já cadastrado no sistema.")
            else:
                self.show_error(f"Erro de integridade: {e}")
        except sqlite3.Error as e:
            self.show_error(f"Erro ao salvar cliente: {e}")
        finally:
            conn.close()
            
    def carregar_clientes(self):
        """Carregar lista de clientes"""
        # Limpar lista atual
        for item in self.clientes_tree.get_children():
            self.clientes_tree.delete(item)
            
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            c.execute("""
                SELECT id, nome, cnpj, cidade, telefone, email
                FROM clientes
                ORDER BY nome
            """)
            
            for row in c.fetchall():
                cliente_id, nome, cnpj, cidade, telefone, email = row
                self.clientes_tree.insert("", "end", values=(
                    nome,
                    format_cnpj(cnpj) if cnpj else "",
                    cidade or "",
                    format_phone(telefone) if telefone else "",
                    email or ""
                ), tags=(cliente_id,))
                
        except sqlite3.Error as e:
            self.show_error(f"Erro ao carregar clientes: {e}")
        finally:
            conn.close()
            
    def buscar_clientes(self):
        """Buscar clientes com filtro"""
        termo = self.search_var.get().strip()
        
        # Limpar lista atual
        for item in self.clientes_tree.get_children():
            self.clientes_tree.delete(item)
            
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            if termo:
                c.execute("""
                    SELECT id, nome, cnpj, cidade, telefone, email
                    FROM clientes
                    WHERE nome LIKE ? OR cnpj LIKE ? OR cidade LIKE ?
                    ORDER BY nome
                """, (f"%{termo}%", f"%{termo}%", f"%{termo}%"))
            else:
                c.execute("""
                    SELECT id, nome, cnpj, cidade, telefone, email
                    FROM clientes
                    ORDER BY nome
                """)
            
            for row in c.fetchall():
                cliente_id, nome, cnpj, cidade, telefone, email = row
                self.clientes_tree.insert("", "end", values=(
                    nome,
                    format_cnpj(cnpj) if cnpj else "",
                    cidade or "",
                    format_phone(telefone) if telefone else "",
                    email or ""
                ), tags=(cliente_id,))
                
        except sqlite3.Error as e:
            self.show_error(f"Erro ao buscar clientes: {e}")
        finally:
            conn.close()
            
    def editar_cliente(self):
        """Editar cliente selecionado"""
        selected = self.clientes_tree.selection()
        if not selected:
            self.show_warning("Selecione um cliente para editar.")
            return
            
        # Obter ID do cliente
        tags = self.clientes_tree.item(selected[0])['tags']
        if not tags:
            return
            
        cliente_id = tags[0]
        self.carregar_cliente_para_edicao(cliente_id)
        
        # Mudar para aba de novo cliente
        self.notebook.select(0)
        
    def carregar_cliente_para_edicao(self, cliente_id):
        """Carregar dados do cliente para edição"""
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            c.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,))
            cliente = c.fetchone()
            
            if not cliente:
                self.show_error("Cliente não encontrado.")
                return
                
            # Preencher campos
            self.current_cliente_id = cliente_id
            self.nome_var.set(cliente[1] or "")  # nome
            self.contato_var.set(cliente[2] or "")  # contato
            self.nome_fantasia_var.set(cliente[3] or "")  # nome_fantasia
            self.cnpj_var.set(format_cnpj(cliente[4]) if cliente[4] else "")  # cnpj
            self.endereco_var.set(cliente[5] or "")  # endereco
            self.cidade_var.set(cliente[6] or "")  # cidade
            self.estado_var.set(cliente[7] or "")  # estado
            self.cep_var.set(cliente[8] or "")  # cep
            self.pais_var.set(cliente[9] or "Brasil")  # pais
            self.telefone_var.set(format_phone(cliente[10]) if cliente[10] else "")  # telefone
            self.email_var.set(cliente[11] or "")  # email
            self.site_var.set(cliente[12] or "")  # site
            self.prazo_pagamento_var.set(cliente[13] or "")  # prazo_pagamento
            
        except sqlite3.Error as e:
            self.show_error(f"Erro ao carregar cliente: {e}")
        finally:
            conn.close()
            
    def excluir_cliente(self):
        """Excluir cliente selecionado"""
        selected = self.clientes_tree.selection()
        if not selected:
            self.show_warning("Selecione um cliente para excluir.")
            return
            
        # Confirmar exclusão
        if not messagebox.askyesno("Confirmar Exclusão", 
                                   "Tem certeza que deseja excluir este cliente?\n"
                                   "Esta ação não pode ser desfeita."):
            return
            
        # Obter ID do cliente
        tags = self.clientes_tree.item(selected[0])['tags']
        if not tags:
            return
            
        cliente_id = tags[0]
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            # Verificar se cliente tem cotações ou relatórios
            c.execute("SELECT COUNT(*) FROM cotacoes WHERE cliente_id = ?", (cliente_id,))
            cotacoes_count = c.fetchone()[0]
            
            c.execute("SELECT COUNT(*) FROM relatorios_tecnicos WHERE cliente_id = ?", (cliente_id,))
            relatorios_count = c.fetchone()[0]
            
            if cotacoes_count > 0 or relatorios_count > 0:
                self.show_warning(f"Este cliente possui {cotacoes_count} cotações e {relatorios_count} relatórios.\n"
                                 "Não é possível excluir.")
                return
            
            # Excluir cliente
            c.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
            conn.commit()
            
            self.show_success("Cliente excluído com sucesso!")
            
            # Emitir evento para atualizar outros módulos
            self.emit_event('cliente_deleted')
            
            # Recarregar lista
            self.carregar_clientes()
            
        except sqlite3.Error as e:
            self.show_error(f"Erro ao excluir cliente: {e}")
        finally:
            conn.close()