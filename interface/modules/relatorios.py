import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sqlite3
from datetime import datetime
from database import DB_NAME
from .base_module import BaseModule
from python_app.pdf_generator_relatorio import gerar_pdf_relatorio
from tkinter import filedialog
from PIL import Image, ImageTk


class RelatoriosModule(BaseModule):
    def __init__(self, parent, user_id, role):
        # Inicialize todos os atributos ANTES de chamar o super
        self.equipamento_vars = {}  
        self.current_relatorio_id = None
        self.tecnicos_eventos = {}
        self.lista_fotos = []
        self.cliente_selecionado_id = None
        self.cotacao_selecionada_id = None
        
        # Agora chame o construtor da classe base
        super().__init__(parent, user_id, role)

    def setup_ui(self):
        # Container principal
        container = tk.Frame(self.frame, bg='#f8fafc')
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        self.create_header(container)
        
        # Notebook para organizar seções
        self.notebook = ttk.Notebook(container)
        self.notebook.pack(fill="both", expand=True, pady=(20, 0))
        
        # Aba: Novo Relatório
        self.create_novo_relatorio_tab()
        
        # Aba: Lista de Relatórios
        self.create_lista_relatorios_tab()
        
    def create_header(self, parent):
        header_frame = tk.Frame(parent, bg='#f8fafc')
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Título
        title_label = tk.Label(header_frame, text="Relatórios Técnicos", 
                               font=('Arial', 18, 'bold'),
                               bg='#f8fafc',
                               fg='#1e293b')
        title_label.pack(side="left")
        
    def create_novo_relatorio_tab(self):
        # Frame da aba
        relatorio_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(relatorio_frame, text="Novo Relatório")
        
        # Scroll frame
        canvas = tk.Canvas(relatorio_frame, bg='white')
        scrollbar = ttk.Scrollbar(relatorio_frame, orient="vertical", command=canvas.yview)
        self.scrollable_relatorio = tk.Frame(canvas, bg='white')
        
        self.scrollable_relatorio.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_relatorio, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Conteúdo do relatório
        self.create_relatorio_content(self.scrollable_relatorio)
        
    def create_relatorio_content(self, parent):
        content_frame = tk.Frame(parent, bg='white', padx=20, pady=20)
        content_frame.pack(fill="both", expand=True)
        
        # Seção: Identificação do Cliente
        self.create_cliente_section(content_frame)
        
        # Seção: Dados do Serviço
        self.create_servico_section(content_frame)
        
        # Seção: Técnicos e Eventos
        self.create_tecnicos_section(content_frame)
        
        # Seção: Condição do Equipamento
        self.create_equipamento_section(content_frame)
        
        # Seção: Vinculação com Cotação
        self.create_vinculacao_section(content_frame)
        
        # Botões de ação
        self.create_relatorio_buttons(content_frame)
        
    def create_cliente_section(self, parent):
        # Frame da seção
        section_frame = tk.LabelFrame(parent, text="Identificação do Cliente", 
                                      font=('Arial', 12, 'bold'),
                                      bg='white',
                                      padx=15, pady=15)
        section_frame.pack(fill="x", pady=(0, 20))
        
        # Busca de cliente
        search_frame = tk.Frame(section_frame, bg='white')
        search_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(search_frame, text="Buscar Cliente:", 
                 font=('Arial', 10, 'bold'), bg='white').pack(side="left")
        
        self.cliente_search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.cliente_search_var,
                               font=('Arial', 10), width=40)
        search_entry.pack(side="left", padx=(10, 0), fill="x", expand=True)
        search_entry.bind('<KeyRelease>', self.on_cliente_search_change)
        
        search_btn = tk.Button(search_frame, text="Buscar",
                              font=('Arial', 10),
                              bg='#3b82f6',
                              fg='white',
                              relief='flat',
                              cursor='hand2',
                              padx=15,
                              command=self.buscar_clientes)
        search_btn.pack(side="left", padx=(10, 0))
        
        # Lista de clientes
        self.clientes_tree = ttk.Treeview(section_frame, 
                                         columns=("id", "nome", "cnpj"),
                                         show="headings",
                                         height=4)
        
        self.clientes_tree.heading("id", text="ID")
        self.clientes_tree.heading("nome", text="Nome")
        self.clientes_tree.heading("cnpj", text="CNPJ")
        
        self.clientes_tree.column("id", width=50)
        self.clientes_tree.column("nome", width=200)
        self.clientes_tree.column("cnpj", width=150)
        
        self.clientes_tree.pack(fill="x", pady=(10, 0))
        self.clientes_tree.bind("<<TreeviewSelect>>", self.selecionar_cliente)
        
        # Cliente selecionado
        self.cliente_selecionado_var = tk.StringVar()
        selected_frame = tk.Frame(section_frame, bg='white')
        selected_frame.pack(fill="x", pady=(10, 0))
        
        tk.Label(selected_frame, text="Cliente Selecionado:", 
                 font=('Arial', 10, 'bold'), bg='white').pack(side="left")
        tk.Label(selected_frame, textvariable=self.cliente_selecionado_var,
                 font=('Arial', 10), bg='white', fg='#059669').pack(side="left", padx=(10, 0))
        
    def create_servico_section(self, parent):
        # Frame da seção
        section_frame = tk.LabelFrame(parent, text="Dados do Serviço", 
                                      font=('Arial', 12, 'bold'),
                                      bg='white',
                                      padx=15, pady=15)
        section_frame.pack(fill="x", pady=(0, 20))
        
        # Grid de campos
        fields_frame = tk.Frame(section_frame, bg='white')
        fields_frame.pack(fill="x")
        
        # Variáveis
        self.form_servico_var = tk.StringVar()
        self.tipo_servico_var = tk.StringVar()
        self.data_recebimento_var = tk.StringVar()
        
        # Campos
        row = 0
        
        # Formulário de Serviço
        tk.Label(fields_frame, text="Formulário de Serviço:", 
                 font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.form_servico_var, 
                 font=('Arial', 10), width=30).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Tipo de Serviço
        tk.Label(fields_frame, text="Tipo de Serviço:", 
                 font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=2, sticky="w", padx=(20, 0), pady=5)
        tipo_combo = ttk.Combobox(fields_frame, textvariable=self.tipo_servico_var,
                                 values=["Manutenção Preventiva", "Manutenção Corretiva", 
                                        "Instalação", "Vistoria", "Outro"],
                                 width=25)
        tipo_combo.grid(row=row, column=3, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Data de Recebimento
        tk.Label(fields_frame, text="Data de Recebimento:", 
                 font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.data_recebimento_var, 
                 font=('Arial', 10), width=30).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Configurar colunas
        fields_frame.grid_columnconfigure(1, weight=1)
        fields_frame.grid_columnconfigure(3, weight=1)
        
        # Descrição do Serviço
        desc_frame = tk.Frame(section_frame, bg='white')
        desc_frame.pack(fill="x", pady=(10, 0))
        
        tk.Label(desc_frame, text="Descrição da Atividade:", 
                 font=('Arial', 10, 'bold'), bg='white').pack(anchor="w")
        self.descricao_text = scrolledtext.ScrolledText(desc_frame, height=4, wrap=tk.WORD, 
                                                       font=('Arial', 10))
        self.descricao_text.pack(fill="x", pady=(5, 0))
        
    def create_tecnicos_section(self, parent):
        # Frame da seção
        section_frame = tk.LabelFrame(parent, text="Técnicos e Eventos em Campo", 
                                      font=('Arial', 12, 'bold'),
                                      bg='white',
                                      padx=15, pady=15)
        section_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Botão para adicionar técnico
        add_tecnico_btn = tk.Button(section_frame, text="➕ Adicionar Técnico",
                                   font=('Arial', 10, 'bold'),
                                   bg='#10b981',
                                   fg='white',
                                   relief='flat',
                                   cursor='hand2',
                                   padx=15,
                                   pady=8,
                                   command=self.adicionar_tecnico)
        add_tecnico_btn.pack(anchor="w", pady=(0, 10))
        
        # Notebook para técnicos
        self.tecnicos_notebook = ttk.Notebook(section_frame)
        self.tecnicos_notebook.pack(fill="both", expand=True)


        # Adicionar campos de tempo
        tempo_frame = tk.Frame(section_frame, bg='white')
        tempo_frame.pack(fill="x", pady=(10, 0))
        
        # Tempo de trabalho
        tk.Label(tempo_frame, text="Tempo Trabalho:", bg='white').pack(side="left")
        self.tempo_trabalho_var = tk.StringVar()
        tk.Entry(tempo_frame, textvariable=self.tempo_trabalho_var, width=10).pack(side="left", padx=5)
        
        # Tempo de deslocamento
        tk.Label(tempo_frame, text="Tempo Deslocamento:", bg='white').pack(side="left", padx=(10,0))
        self.tempo_deslocamento_var = tk.StringVar()
        tk.Entry(tempo_frame, textvariable=self.tempo_deslocamento_var, width=10).pack(side="left", padx=5)
        
        # Totais
        tk.Label(tempo_frame, text="Total HH Trabalho:", bg='white').pack(side="left", padx=(10,0))
        self.total_trabalho_var = tk.StringVar()
        tk.Entry(tempo_frame, textvariable=self.total_trabalho_var, width=10).pack(side="left", padx=5)
        
        tk.Label(tempo_frame, text="Total HH Deslocamento:", bg='white').pack(side="left", padx=(10,0))
        self.total_deslocamento_var = tk.StringVar()
        tk.Entry(tempo_frame, textvariable=self.total_deslocamento_var, width=10).pack(side="left", padx=5)
        
    def create_equipamento_section(self, parent):
        # Frame da seção
        section_frame = tk.LabelFrame(parent, text="Condição do Equipamento", 
                                    font=('Arial', 12, 'bold'),
                                    bg='white',
                                    padx=15, pady=15)
        section_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        notebook = ttk.Notebook(section_frame)
        notebook.pack(fill="both", expand=True)
        
        # Aba 1: Condição Inicial
        frame1 = tk.Frame(notebook, bg='white')
        notebook.add(frame1, text="1. Condição Inicial")
        
        # Conteúdo Aba 1
        tk.Label(frame1, text="CONDIÇÃO ATUAL DO EQUIPAMENTO", 
                font=('Arial', 10, 'bold'), bg='white').pack(anchor="w", pady=5)
        
        # Campos com rótulos formatados
        campos_aba1 = [
            "Cond. Encontrada:",
            "Placa/N.Série:",
            "Acoplamento:",
            "Aspectos Rotores:",
            "Válvulas Acopladas:",
            "Data Recebimento:"
        ]
        
        self.aba1_vars = {}
        for campo in campos_aba1:
            frame = tk.Frame(frame1, bg='white')
            frame.pack(fill="x", padx=5, pady=2)
            
            tk.Label(frame, text=campo, font=('Arial', 9), 
                    bg='white', anchor="w", width=25).pack(side="left")
            
            var = tk.StringVar()
            entry = tk.Entry(frame, textvariable=var, font=('Arial', 9))
            entry.pack(fill="x", expand=True, padx=5)
            
            self.aba1_vars[campo] = var
            self.equipamento_vars[campo] = var  # Armazena no dicionário principal
        
        tk.Label(frame1, text="ESPAÇO PRA ANEXOS", 
                font=('Arial', 10, 'bold'), bg='white').pack(anchor="w", pady=10)
        
        # Container para fotos da aba 1
        self.fotos_aba1_frame = tk.Frame(frame1, bg='white')
        self.fotos_aba1_frame.pack(fill="both", expand=True)
        
        # Botão para adicionar fotos
        btn_aba1 = tk.Button(frame1, text="Adicionar Foto",
                            command=lambda: self.adicionar_foto_aba(1))
        btn_aba1.pack(pady=5)
        
        # Aba 2: Peritagem do Subconjunto
        frame2 = tk.Frame(notebook, bg='white')
        notebook.add(frame2, text="2. Peritagem do Subconjunto")
        
        # Conteúdo Aba 2
        tk.Label(frame2, text="DESACOPLANDO ELEMENTO COMPRESSOR DA CAIXA DE ACIONAMENTO", 
                font=('Arial', 10, 'bold'), bg='white').pack(anchor="w", pady=5)
        
        campos_aba2 = [
            "Parafusos/Pinos:",
            "Superfície Vedação:",
            "Engrenagens:",
            "Bico Injertor:",
            "Rolamentos:",
            "Aspecto Óleo:",
            "Data:"
        ]
        
        self.aba2_vars = {}
        for campo in campos_aba2:
            frame = tk.Frame(frame2, bg='white')
            frame.pack(fill="x", padx=5, pady=2)
            
            tk.Label(frame, text=campo, font=('Arial', 9), 
                    bg='white', anchor="w", width=25).pack(side="left")
            
            var = tk.StringVar()
            entry = tk.Entry(frame, textvariable=var, font=('Arial', 9))
            entry.pack(fill="x", expand=True, padx=5)
            
            self.aba2_vars[campo] = var
            self.equipamento_vars[campo] = var  # Armazena no dicionário principal
        
        tk.Label(frame2, text="ESPAÇO PRA ANEXOS", 
                font=('Arial', 10, 'bold'), bg='white').pack(anchor="w", pady=10)
        
        # Container para fotos da aba 2
        self.fotos_aba2_frame = tk.Frame(frame2, bg='white')
        self.fotos_aba2_frame.pack(fill="both", expand=True)
        
        # Botão para adicionar fotos
        btn_aba2 = tk.Button(frame2, text="Adicionar Foto",
                            command=lambda: self.adicionar_foto_aba(2))
        btn_aba2.pack(pady=5)
        
        # Aba 3: Desmembrando Unidade Compressora
        frame3 = tk.Frame(notebook, bg='white')
        notebook.add(frame3, text="3. Desmembrando Unidade Compressora")
        
        # Conteúdo Aba 3
        tk.Label(frame3, text="GRAU DE INTERFERÊNCIA NA DESMONTAGEM:", 
                font=('Arial', 10, 'bold'), bg='white').pack(anchor="w", pady=5)
        
        campos_aba3 = [
            "Interf. Desmontagem:",
            "Aspecto Rotores:",
            "Aspecto Carcaça:",
            "Interf. Mancais:",
            "Galeria Hidráulica:"
        ]
        
        self.aba3_vars = {}
        for campo in campos_aba3:
            frame = tk.Frame(frame3, bg='white')
            frame.pack(fill="x", padx=5, pady=2)
            
            tk.Label(frame, text=campo, font=('Arial', 9), 
                    bg='white', anchor="w", width=25).pack(side="left")
            
            var = tk.StringVar()
            entry = tk.Entry(frame, textvariable=var, font=('Arial', 9))
            entry.pack(fill="x", expand=True, padx=5)
            
            self.aba3_vars[campo] = var
            self.equipamento_vars[campo] = var  # Armazena no dicionário principal
        
        tk.Label(frame3, text="ESPAÇO PRA ANEXOS", 
                font=('Arial', 10, 'bold'), bg='white').pack(anchor="w", pady=10)
        
        # Container para fotos da aba 3
        self.fotos_aba3_frame = tk.Frame(frame3, bg='white')
        self.fotos_aba3_frame.pack(fill="both", expand=True)
        
        # Botão para adicionar fotos
        btn_aba3 = tk.Button(frame3, text="Adicionar Foto",
                            command=lambda: self.adicionar_foto_aba(3))
        btn_aba3.pack(pady=5)
        
        # Aba 4: Relação de Peças e Serviços
        frame4 = tk.Frame(notebook, bg='white')
        notebook.add(frame4, text="4. Relação de Peças e Serviços")
        
        # Conteúdo Aba 4
        tk.Label(frame4, text="SERVIÇOS PROPOSTO PARA REFORMA DO SUBCONJUNTO:", 
                font=('Arial', 10, 'bold'), bg='white').pack(anchor="w", pady=5)
        
        self.servicos_text = scrolledtext.ScrolledText(frame4, height=5, wrap=tk.WORD)
        self.servicos_text.pack(fill="x", padx=5, pady=2)
        
        tk.Label(frame4, text="PEÇAS RECOMENDADAS PARA REFORMA:", 
                font=('Arial', 10, 'bold'), bg='white').pack(anchor="w", pady=5)
        
        self.pecas_text = scrolledtext.ScrolledText(frame4, height=5, wrap=tk.WORD)
        self.pecas_text.pack(fill="x", padx=5, pady=2)
        
        tk.Label(frame4, text="DATA:", 
                font=('Arial', 10, 'bold'), bg='white').pack(anchor="w", pady=5)
        
        self.data_pecas_var = tk.StringVar()
        tk.Entry(frame4, textvariable=self.data_pecas_var, 
                font=('Arial', 9)).pack(fill="x", padx=5, pady=2)
        
        tk.Label(frame4, text="ESPAÇO PRA ANEXOS", 
                font=('Arial', 10, 'bold'), bg='white').pack(anchor="w", pady=10)
        
        # Container para fotos da aba 4
        self.fotos_aba4_frame = tk.Frame(frame4, bg='white')
        self.fotos_aba4_frame.pack(fill="both", expand=True)
        
        # Botão para adicionar fotos
        btn_aba4 = tk.Button(frame4, text="Adicionar Foto",
                            command=lambda: self.adicionar_foto_aba(4))
        btn_aba4.pack(pady=5)

    def adicionar_foto_aba(self, aba_numero):
        filepath = filedialog.askopenfilename(
            title=f"Selecionar Foto para Aba {aba_numero}",
            filetypes=[("Imagens", "*.jpg *.jpeg *.png")]
        )
        
        if not filepath:
            return
            
        try:
            img = Image.open(filepath)
            img.thumbnail((150, 150))
            photo = ImageTk.PhotoImage(img)
            
            # Determinar o frame correto baseado no número da aba
            if aba_numero == 1:
                frame_container = self.fotos_aba1_frame
            elif aba_numero == 2:
                frame_container = self.fotos_aba2_frame
            elif aba_numero == 3:
                frame_container = self.fotos_aba3_frame
            elif aba_numero == 4:
                frame_container = self.fotos_aba4_frame
            else:
                return
            
            # Contar fotos existentes para determinar posição
            foto_count = len(frame_container.winfo_children())
            row = foto_count // 4
            col = foto_count % 4
            
            # Criar frame para a miniatura
            frame = tk.Frame(frame_container, bd=2, relief="groove", padx=5, pady=5)
            frame.grid(row=row, column=col, padx=5, pady=5)
            
            # Exibir miniatura
            label = tk.Label(frame, image=photo)
            label.image = photo
            label.pack()
            
            # Botão para remover
            tk.Button(frame, text="Remover", 
                    command=lambda f=frame: f.destroy()).pack(pady=2)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível carregar a imagem: {e}")

    def adicionar_foto_por_caminho(self, filepath, aba_numero=1):
        try:
            img = Image.open(filepath)
            img.thumbnail((150, 150))
            photo = ImageTk.PhotoImage(img)
            
            # Determinar o frame correto baseado no número da aba
            if aba_numero == 1:
                frame_container = self.fotos_aba1_frame
            elif aba_numero == 2:
                frame_container = self.fotos_aba2_frame
            elif aba_numero == 3:
                frame_container = self.fotos_aba3_frame
            elif aba_numero == 4:
                frame_container = self.fotos_aba4_frame
            else:
                return
            
            # Criar frame para a miniatura
            frame = tk.Frame(frame_container, bd=2, relief="groove", padx=5, pady=5)
            frame.pack(side="left", padx=5, pady=5)
            
            # Exibir miniatura
            label = tk.Label(frame, image=photo)
            label.image = photo
            label.pack()
            
            # Botão para remover
            tk.Button(frame, text="Remover", 
                    command=lambda f=frame: f.destroy()).pack(pady=2)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível carregar a imagem: {e}")

    def create_fotos_section(self, parent):
        section_frame = tk.LabelFrame(parent, text="Fotos do Serviço", 
                                    font=('Arial', 12, 'bold'),
                                    bg='white',
                                    padx=15, pady=15)
        section_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Botões de controle
        btn_frame = tk.Frame(section_frame, bg='white')
        btn_frame.pack(fill="x", pady=(0, 10))
        
        add_btn = tk.Button(btn_frame, text="Adicionar Foto",
                        command=self.adicionar_foto)
        add_btn.pack(side="left", padx=5)
        
        clear_btn = tk.Button(btn_frame, text="Limpar Todas as Fotos",
                            command=self.limpar_fotos)
        clear_btn.pack(side="left", padx=5)
        
        # Área para miniaturas
        self.fotos_container = tk.Frame(section_frame, bg='white')
        self.fotos_container.pack(fill="both", expand=True)
        
        # Configurar grid (4 colunas)
        for i in range(4):
            self.fotos_container.grid_columnconfigure(i, weight=1)
        
        self.lista_fotos = []

    def adicionar_foto(self):
        filepath = filedialog.askopenfilename(
            title="Selecionar Foto",
            filetypes=[("Imagens", "*.jpg *.jpeg *.png")]
        )
        
        if not filepath:
            return
            
        try:
            # Carregar e redimensionar imagem
            img = Image.open(filepath)
            img.thumbnail((200, 200))
            photo = ImageTk.PhotoImage(img)
            
            # Adicionar à lista
            foto_id = len(self.lista_fotos)
            self.lista_fotos.append({
                "filepath": filepath,
                "photo": photo,
                "id": foto_id
            })
            
            # Calcular posição
            row = foto_id // 4
            col = foto_id % 4
            
            # Criar frame para miniatura
            frame = tk.Frame(self.fotos_container, bd=2, relief="groove", padx=5, pady=5)
            frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            
            # Exibir miniatura
            label = tk.Label(frame, image=photo)
            label.image = photo  # Manter referência
            label.pack()
            
            # Botão para remover
            btn = tk.Button(frame, text="Remover", 
                        command=lambda id=foto_id: self.remover_foto(id))
            btn.pack(pady=5)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível carregar a imagem: {e}")

    def remover_foto(self, foto_id):
        # Remover foto da lista
        self.lista_fotos = [foto for foto in self.lista_fotos if foto['id'] != foto_id]
        
        # Reconstruir toda a área de fotos
        self.reconstruir_area_fotos()


    def limpar_fotos(self):
        self.lista_fotos = []
        self.reconstruir_area_fotos()

    def reconstruir_area_fotos(self):
        # Destruir todos os widgets na área de fotos
        for widget in self.fotos_container.winfo_children():
            widget.destroy()
        
        # Recriar as miniaturas
        for i, foto in enumerate(self.lista_fotos):
            row = i // 4
            col = i % 4
            
            frame = tk.Frame(self.fotos_container, bd=2, relief="groove", padx=5, pady=5)
            frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            
            label = tk.Label(frame, image=foto['photo'])
            label.image = foto['photo']
            label.pack()
            
            btn = tk.Button(frame, text="Remover", 
                        command=lambda id=foto['id']: self.remover_foto(id))
            btn.pack(pady=5)
        
    def create_vinculacao_section(self, parent):
        # Frame da seção
        section_frame = tk.LabelFrame(parent, text="Vinculação com Cotação", 
                                      font=('Arial', 12, 'bold'),
                                      bg='white',
                                      padx=15, pady=15)
        section_frame.pack(fill="x", pady=(0, 20))
        
        # Busca de cotação
        search_frame = tk.Frame(section_frame, bg='white')
        search_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(search_frame, text="Buscar Cotação:", 
                 font=('Arial', 10, 'bold'), bg='white').pack(side="left")
        
        self.cotacao_search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.cotacao_search_var,
                               font=('Arial', 10), width=30)
        search_entry.pack(side="left", padx=(10, 0), fill="x", expand=True)
        search_entry.bind('<KeyRelease>', self.on_cotacao_search_change)
        
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
        self.cotacoes_tree = ttk.Treeview(section_frame, 
                                         columns=("id", "numero", "valor", "data"),
                                         show="headings",
                                         height=4)
        
        self.cotacoes_tree.heading("id", text="ID")
        self.cotacoes_tree.heading("numero", text="Número")
        self.cotacoes_tree.heading("valor", text="Valor")
        self.cotacoes_tree.heading("data", text="Data")
        
        self.cotacoes_tree.column("id", width=50)
        self.cotacoes_tree.column("numero", width=150)
        self.cotacoes_tree.column("valor", width=120)
        self.cotacoes_tree.column("data", width=100)
        
        self.cotacoes_tree.pack(fill="x", pady=(10, 0))
        self.cotacoes_tree.bind("<<TreeviewSelect>>", self.selecionar_cotacao)
        
        # Cotação vinculada
        vinc_frame = tk.Frame(section_frame, bg='white')
        vinc_frame.pack(fill="x", pady=(10, 0))
        
        tk.Label(vinc_frame, text="Cotação Vinculada:", 
                 font=('Arial', 10, 'bold'), bg='white').pack(side="left")
        
        self.cotacao_vinculada_var = tk.StringVar()
        tk.Label(vinc_frame, textvariable=self.cotacao_vinculada_var,
                 font=('Arial', 10), bg='white', fg='#059669').pack(side="left", padx=(10, 0))
        
    def create_relatorio_buttons(self, parent):
        # Frame dos botões
        buttons_frame = tk.Frame(parent, bg='white')
        buttons_frame.pack(fill="x", pady=(20, 0))
        
        # Botões
        novo_btn = tk.Button(buttons_frame, text="Novo Relatório",
                            font=('Arial', 10),
                            bg='#e2e8f0',
                            fg='#475569',
                            relief='flat',
                            cursor='hand2',
                            padx=15,
                            pady=8,
                            command=self.novo_relatorio)
        novo_btn.pack(side="left", padx=(0, 10))
        
        save_btn = tk.Button(buttons_frame, text="Salvar Relatório",
                            font=('Arial', 10, 'bold'),
                            bg='#3b82f6',
                            fg='white',
                            relief='flat',
                            cursor='hand2',
                            padx=15,
                            pady=8,
                            command=self.salvar_relatorio)
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
                           command=self.gerar_pdf_relatorio)
        pdf_btn.pack(side="left", padx=(10, 0))
        
    def create_lista_relatorios_tab(self):
        # Frame da aba
        lista_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(lista_frame, text="Lista de Relatórios")
        
        content_frame = tk.Frame(lista_frame, bg='white', padx=20, pady=20)
        content_frame.pack(fill="both", expand=True)
        
        # Busca
        search_frame = tk.Frame(content_frame, bg='white')
        search_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(search_frame, text="🔍 Buscar:", 
                 font=('Arial', 12), bg='white').pack(side="left", padx=(0, 10))
        
        self.search_relatorio_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_relatorio_var,
                               font=('Arial', 11), width=50)
        search_entry.pack(side="left", fill="x", expand=True, ipady=5)
        
        search_btn = tk.Button(search_frame, text="Buscar",
                              font=('Arial', 10),
                              bg='#3b82f6',
                              fg='white',
                              relief='flat',
                              cursor='hand2',
                              padx=15,
                              command=self.buscar_relatorios)
        search_btn.pack(side="left", padx=(10, 0))
        
        # Lista de relatórios
        self.create_relatorios_list(content_frame)
        
    def create_relatorios_list(self, parent):
        # Treeview
        columns = ("id", "numero", "cliente", "tipo", "data", "status", "cotacao")
        self.relatorios_tree = ttk.Treeview(parent, 
                                           columns=columns,
                                           show="headings")
        
        # Cabeçalhos
        self.relatorios_tree.heading("id", text="ID")
        self.relatorios_tree.heading("numero", text="Número")
        self.relatorios_tree.heading("cliente", text="Cliente")
        self.relatorios_tree.heading("tipo", text="Tipo")
        self.relatorios_tree.heading("data", text="Data")
        self.relatorios_tree.heading("status", text="Status")
        self.relatorios_tree.heading("cotacao", text="Cotação")
        
        # Larguras
        self.relatorios_tree.column("id", width=50)
        self.relatorios_tree.column("numero", width=120)
        self.relatorios_tree.column("cliente", width=200)
        self.relatorios_tree.column("tipo", width=150)
        self.relatorios_tree.column("data", width=100)
        self.relatorios_tree.column("status", width=100)
        self.relatorios_tree.column("cotacao", width=150)
        
        # Scrollbar
        scrollbar_rel = ttk.Scrollbar(parent, orient="vertical", 
                                     command=self.relatorios_tree.yview)
        self.relatorios_tree.configure(yscrollcommand=scrollbar_rel.set)
        
        # Pack
        self.relatorios_tree.pack(side="left", fill="both", expand=True)
        scrollbar_rel.pack(side="right", fill="y")
        
        # Bind duplo clique
        self.relatorios_tree.bind("<Double-1>", self.editar_relatorio)
        
        # Menu de contexto
        self.context_menu_rel = tk.Menu(self.relatorios_tree, tearoff=0)
        self.context_menu_rel.add_command(label="Editar", command=self.editar_relatorio)
        self.context_menu_rel.add_command(label="Gerar PDF", command=self.gerar_pdf_selecionado)
        self.context_menu_rel.add_separator()
        self.context_menu_rel.add_command(label="Excluir", command=self.excluir_relatorio)
        
        self.relatorios_tree.bind("<Button-3>", self.show_context_menu_rel)
        
        # Carregar relatórios
        self.carregar_relatorios()
        
    def show_context_menu_rel(self, event):
        # Selecionar o item clicado
        item = self.relatorios_tree.identify_row(event.y)
        if item:
            self.relatorios_tree.selection_set(item)
            self.context_menu_rel.post(event.x_root, event.y_root)
        
    def on_cliente_search_change(self, event=None):
        # Busca automática enquanto digita
        search_term = self.cliente_search_var.get()
        if len(search_term) >= 2:  # Buscar apenas com 2+ caracteres
            self.buscar_clientes()
        elif len(search_term) == 0:
            # Limpar lista se campo vazio
            for item in self.clientes_tree.get_children():
                self.clientes_tree.delete(item)
        
    def buscar_clientes(self):
        search_term = self.cliente_search_var.get()
        
        # Limpar lista
        for item in self.clientes_tree.get_children():
            self.clientes_tree.delete(item)
            
        if not search_term:
            return
            
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            c.execute("""
                SELECT id, nome, cnpj FROM clientes 
                WHERE LOWER(nome) LIKE ? OR LOWER(cnpj) LIKE ?
                ORDER BY nome
            """, (f"%{search_term.lower()}%", f"%{search_term.lower()}%"))
            
            for row in c.fetchall():
                self.clientes_tree.insert("", "end", values=row)
                
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao buscar clientes: {e}")
        finally:
            conn.close()
            
    def selecionar_cliente(self, event):
        selected = self.clientes_tree.selection()
        if not selected:
            return
            
        item = self.clientes_tree.item(selected[0])
        cliente_id, nome, cnpj = item['values']
        
        self.cliente_selecionado_id = cliente_id
        self.cliente_selecionado_var.set(f"{nome} - {cnpj}")
        
        # Carregar cotações do cliente
        self.carregar_cotacoes_cliente(cliente_id)
        
    def on_cotacao_search_change(self, event=None):
        # Busca automática enquanto digita
        search_term = self.cotacao_search_var.get()
        if len(search_term) >= 2 and hasattr(self, 'cliente_selecionado_id'):
            self.buscar_cotacoes()
        elif len(search_term) == 0 and hasattr(self, 'cliente_selecionado_id'):
            # Mostrar todas as cotações do cliente se campo vazio
            self.carregar_cotacoes_cliente(self.cliente_selecionado_id)
        
    def buscar_cotacoes(self):
        if not hasattr(self, 'cliente_selecionado_id'):
            messagebox.showwarning("Aviso", "Selecione um cliente primeiro.")
            return
            
        search_term = self.cotacao_search_var.get().lower()
        
        # Limpar lista
        for item in self.cotacoes_tree.get_children():
            self.cotacoes_tree.delete(item)
            
        if not search_term:
            self.carregar_cotacoes_cliente(self.cliente_selecionado_id)
            return
            
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            c.execute("""
                SELECT id, numero_proposta, valor_total, data_criacao FROM cotacoes 
                WHERE cliente_id = ? AND LOWER(numero_proposta) LIKE ?
                ORDER BY data_criacao DESC
            """, (self.cliente_selecionado_id, f"%{search_term}%"))
            
            for row in c.fetchall():
                self.cotacoes_tree.insert("", "end", values=row)
                
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao buscar cotações: {e}")
        finally:
            conn.close()
        
    def carregar_cotacoes_cliente(self, cliente_id):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            # Limpar lista
            for item in self.cotacoes_tree.get_children():
                self.cotacoes_tree.delete(item)
                
            c.execute("""
                SELECT id, numero_proposta, valor_total, data_criacao FROM cotacoes 
                WHERE cliente_id = ?
                ORDER BY data_criacao DESC
            """, (cliente_id,))
            
            for row in c.fetchall():
                self.cotacoes_tree.insert("", "end", values=row)
                
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao carregar cotações: {e}")
        finally:
            conn.close()
            
    def selecionar_cotacao(self, event):
        selected = self.cotacoes_tree.selection()
        if not selected:
            return
            
        item = self.cotacoes_tree.item(selected[0])
        cotacao_id, numero, valor_str, data = item['values']  # valor é string
        
        try:
            # Tentar converter para float
            valor = float(valor_str)
            valor_formatado = f"R$ {valor:.2f}"
        except (ValueError, TypeError):
            # Se falhar, usar o valor original
            valor_formatado = valor_str
            
        self.cotacao_selecionada_id = cotacao_id
        self.cotacao_vinculada_var.set(f"{numero} - {valor_formatado}")
        
    def adicionar_tecnico(self):
        # Janela para selecionar técnico
        tecnico_window = tk.Toplevel(self.frame)
        tecnico_window.title("Selecionar Técnico")
        tecnico_window.geometry("500x400")
        tecnico_window.transient(self.frame)
        tecnico_window.grab_set()
        
        # Frame principal
        main_frame = tk.Frame(tecnico_window, bg='white', padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        tk.Label(main_frame, text="Selecione um Técnico:", 
                 font=('Arial', 12, 'bold'), bg='white').pack(anchor="w", pady=(0, 10))
        
        # Lista de técnicos
        tecnicos_tree = ttk.Treeview(main_frame, 
                                    columns=("id", "nome", "especialidade"),
                                    show="headings")
        
        tecnicos_tree.heading("id", text="ID")
        tecnicos_tree.heading("nome", text="Nome")
        tecnicos_tree.heading("especialidade", text="Especialidade")
        
        tecnicos_tree.column("id", width=50)
        tecnicos_tree.column("nome", width=200)
        tecnicos_tree.column("especialidade", width=200)
        
        tecnicos_tree.pack(fill="both", expand=True, pady=(0, 20))
        
        # Carregar técnicos
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            c.execute("SELECT id, nome, especialidade FROM tecnicos ORDER BY nome")
            for row in c.fetchall():
                tecnicos_tree.insert("", "end", values=row)
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao carregar técnicos: {e}")
        finally:
            conn.close()
            
        def selecionar_tecnico():
            selected = tecnicos_tree.selection()
            if not selected:
                messagebox.showwarning("Aviso", "Selecione um técnico.")
                return
                
            item = tecnicos_tree.item(selected[0])
            tecnico_id, nome, especialidade = item['values']
            
            # Verificar se já foi adicionado
            if tecnico_id in self.tecnicos_eventos:
                messagebox.showwarning("Aviso", "Este técnico já foi adicionado.")
                return
                
            # Adicionar aba para o técnico
            self.criar_aba_tecnico(tecnico_id, nome)
            tecnico_window.destroy()
            
        # Botão selecionar
        tk.Button(main_frame, text="Selecionar Técnico",
                 font=('Arial', 10, 'bold'),
                 bg='#3b82f6',
                 fg='white',
                 relief='flat',
                 cursor='hand2',
                 padx=20,
                 pady=8,
                 command=selecionar_tecnico).pack()
                 
    def criar_aba_tecnico(self, tecnico_id, nome):
        # Frame da aba
        tecnico_frame = tk.Frame(self.tecnicos_notebook, bg='white')
        self.tecnicos_notebook.add(tecnico_frame, text=nome)
        
        content_frame = tk.Frame(tecnico_frame, bg='white', padx=15, pady=15)
        content_frame.pack(fill="both", expand=True)
        
        # Campos para adicionar evento
        add_frame = tk.LabelFrame(content_frame, text="Adicionar Evento", 
                                 font=('Arial', 10, 'bold'), bg='white')
        add_frame.pack(fill="x", pady=(0, 15))
        
        fields_frame = tk.Frame(add_frame, bg='white', padx=10, pady=10)
        fields_frame.pack(fill="x")
        
        # Variáveis para evento
        hora_var = tk.StringVar()
        evento_var = tk.StringVar()
        tipo_var = tk.StringVar()
        
        # Campos
        tk.Label(fields_frame, text="Data/Hora:", font=('Arial', 10), bg='white').grid(row=0, column=0, sticky="w", padx=5)
        hora_entry = tk.Entry(fields_frame, textvariable=hora_var, font=('Arial', 10), width=20)
        hora_entry.grid(row=0, column=1, padx=5)
        hora_var.set(datetime.now().strftime("%d/%m/%Y %H:%M"))
        
        tk.Label(fields_frame, text="Evento:", font=('Arial', 10), bg='white').grid(row=0, column=2, sticky="w", padx=5)
        tk.Entry(fields_frame, textvariable=evento_var, font=('Arial', 10), width=30).grid(row=0, column=3, padx=5)
        
        tk.Label(fields_frame, text="Tipo:", font=('Arial', 10), bg='white').grid(row=0, column=4, sticky="w", padx=5)
        tipo_combo = ttk.Combobox(fields_frame, textvariable=tipo_var, 
                                 values=["Checkin", "Checkout"], width=12)
        tipo_combo.grid(row=0, column=5, padx=5)
        tipo_var.set("Checkin")
        
        def adicionar_evento():
            hora = hora_var.get()
            evento = evento_var.get()
            tipo = tipo_var.get()
            
            if not hora or not evento:
                messagebox.showwarning("Aviso", "Preencha todos os campos.")
                return
                
            # Adicionar à lista
            eventos_tree.insert("", "end", values=(hora, evento, tipo))
            
            # Limpar campos
            evento_var.set("")
            hora_var.set(datetime.now().strftime("%d/%m/%Y %H:%M"))
            
            # CALCULAR TEMPOS NOVAMENTE
            self.calcular_tempo_total()
            
        tk.Button(fields_frame, text="Adicionar",
                 font=('Arial', 10),
                 bg='#10b981',
                 fg='white',
                 relief='flat',
                 cursor='hand2',
                 padx=15,
                 command=adicionar_evento).grid(row=0, column=6, padx=10)
        
        # Lista de eventos
        eventos_frame = tk.Frame(content_frame, bg='white')
        eventos_frame.pack(fill="both", expand=True)
        
        tk.Label(eventos_frame, text="Eventos:", font=('Arial', 10, 'bold'), bg='white').pack(anchor="w")
        
        eventos_tree = ttk.Treeview(eventos_frame, 
                                   columns=("hora", "evento", "tipo"),
                                   show="headings",
                                   height=8)
        
        eventos_tree.heading("hora", text="Data/Hora")
        eventos_tree.heading("evento", text="Evento")
        eventos_tree.heading("tipo", text="Tipo")
        
        eventos_tree.column("hora", width=150)
        eventos_tree.column("evento", width=300)
        eventos_tree.column("tipo", width=100)
        
        eventos_tree.pack(fill="both", expand=True, pady=(5, 0))
        self.calcular_tempo_total()
        
        # Botão remover evento
        def remover_evento():
            selected = eventos_tree.selection()
            if selected:
                eventos_tree.delete(selected)
                # CALCULAR TEMPOS NOVAMENTE
            self.calcular_tempo_total()
                
        tk.Button(eventos_frame, text="Remover Evento Selecionado",
                 font=('Arial', 10),
                 bg='#dc2626',
                 fg='white',
                 relief='flat',
                 cursor='hand2',
                 padx=15,
                 command=remover_evento).pack(pady=(10, 0))
        
        # Armazenar referência
        self.tecnicos_eventos[tecnico_id] = eventos_tree
        self.calcular_tempo_total()

    def calcular_tempo_total(self):
        total_trabalho = 0
        total_deslocamento = 0
        
        for tecnico_id, tree in self.tecnicos_eventos.items():
            eventos = []
            for item in tree.get_children():
                data_hora, evento, tipo = tree.item(item)['values']
                eventos.append((data_hora, tipo))
            
            # Ordenar eventos por data/hora
            eventos.sort(key=lambda x: datetime.strptime(x[0], "%d/%m/%Y %H:%M"))
            
            # Calcular tempo de trabalho (entre checkin e checkout consecutivos)
            checkin_time = None
            for data_hora_str, evento_tipo in eventos:
                data_hora = datetime.strptime(data_hora_str, "%d/%m/%Y %H:%M")
                
                if evento_tipo == "Checkin":
                    checkin_time = data_hora
                elif evento_tipo == "Checkout" and checkin_time:
                    diferenca = data_hora - checkin_time
                    total_trabalho += diferenca.total_seconds() / 3600  # converter para horas
                    checkin_time = None
            
            # Calcular tempo de deslocamento (cada par checkin-checkout conta como 1 deslocamento)
            # Considerando 0.5 horas por deslocamento (ajuste conforme necessário)
            pares = sum(1 for i in range(1, len(eventos)) 
                    if eventos[i-1][1] == "Checkin" and eventos[i][1] == "Checkout")
            total_deslocamento += pares * 0.5
        
        # Atualizar interface
        self.tempo_trabalho_var.set(f"{total_trabalho:.2f} h")
        self.tempo_deslocamento_var.set(f"{total_deslocamento:.2f} h")
        
        # Atualizar totais (se necessário)
        self.total_trabalho_var.set(f"{total_trabalho:.2f} h")
        self.total_deslocamento_var.set(f"{total_deslocamento:.2f} h")
        
    def novo_relatorio(self):
        # Limpar campos do equipamento
        if hasattr(self, 'equipamento_vars'):
            for var in self.equipamento_vars.values():
                var.set("")
        else:
            self.equipamento_vars = {}
        
        # Limpar outros campos
        self.current_relatorio_id = None
        self.cliente_search_var.set("")
        self.cliente_selecionado_var.set("")
        self.form_servico_var.set("")
        self.tipo_servico_var.set("")
        self.data_recebimento_var.set("")
        self.descricao_text.delete("1.0", tk.END)
        self.cotacao_search_var.set("")
        self.cotacao_vinculada_var.set("")
        self.tempo_trabalho_var.set("")
        self.tempo_deslocamento_var.set("")
        self.total_trabalho_var.set("")
        self.total_deslocamento_var.set("")
        self.servicos_text.delete("1.0", tk.END)
        self.pecas_text.delete("1.0", tk.END)
        self.data_pecas_var.set("")
        
        # Limpar técnicos
        for tab in self.tecnicos_notebook.tabs():
            self.tecnicos_notebook.forget(tab)
        self.tecnicos_eventos = {}
        
        # Limpar listas
        for item in self.clientes_tree.get_children():
            self.clientes_tree.delete(item)
        for item in self.cotacoes_tree.get_children():
            self.cotacoes_tree.delete(item)
        
        # Limpar fotos de todas as abas
        for frame in [self.fotos_aba1_frame, self.fotos_aba2_frame, 
                     self.fotos_aba3_frame, self.fotos_aba4_frame]:
            for widget in frame.winfo_children():
                widget.destroy()
        
        messagebox.showinfo("Novo Relatório", "Campos limpos para novo relatório.")
        
    def salvar_relatorio(self):
        # Verificar se o dicionário existe
        if not hasattr(self, 'equipamento_vars'):
            self.equipamento_vars = {}
        
        if not hasattr(self, 'cliente_selecionado_id'):
            messagebox.showwarning("Aviso", "Selecione um cliente.")
            return
            
        # Dados do relatório
        cliente_id = self.cliente_selecionado_id
        form_servico = self.form_servico_var.get()
        tipo_servico = self.tipo_servico_var.get()
        descricao_servico = self.descricao_text.get("1.0", tk.END).strip()
        data_recebimento = self.data_recebimento_var.get()
        
        # Dados do equipamento
        dados_equipamento = {campo: var.get() for campo, var in self.equipamento_vars.items()}
        
        # Tempos de trabalho
        tempo_trabalho = self.tempo_trabalho_var.get()
        total_trabalho = self.total_trabalho_var.get()
        tempo_deslocamento = self.tempo_deslocamento_var.get()
        total_deslocamento = self.total_deslocamento_var.get()
        
        # Serviços e peças
        servicos = self.servicos_text.get("1.0", tk.END).strip()
        pecas = self.pecas_text.get("1.0", tk.END).strip()
        data_pecas = self.data_pecas_var.get()
        
        # Fotos - armazenar caminhos
        caminhos_fotos = []
        for frame in [self.fotos_aba1_frame, self.fotos_aba2_frame, 
                     self.fotos_aba3_frame, self.fotos_aba4_frame]:
            for widget in frame.winfo_children():
                if hasattr(widget, 'caminho_foto'):
                    caminhos_fotos.append(widget.caminho_foto)
        caminhos_str = ";".join(caminhos_fotos)
        
        # Cotação vinculada
        cotacao_id = self.cotacao_selecionada_id if hasattr(self, 'cotacao_selecionada_id') else None
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            # Verificar quais colunas existem na tabela
            c.execute("PRAGMA table_info(relatorios_tecnicos)")
            columns_info = c.fetchall()
            column_names = [column[1] for column in columns_info]
            
            # Preparar dados em um dicionário
            data = {
                'numero_relatorio': f"REL-{datetime.now().strftime('%Y%m%d%H%M%S')}" if not self.current_relatorio_id else None,
                'cliente_id': cliente_id,
                'responsavel_id': self.user_id,
                'data_criacao': datetime.now().strftime('%Y-%m-%d') if not self.current_relatorio_id else None,
                'formulario_servico': form_servico,
                'tipo_servico': tipo_servico,
                'descricao_servico': descricao_servico,
                'data_recebimento': data_recebimento,
                'condicao_encontrada': dados_equipamento.get("Cond. Encontrada:", ""),
                'placa_identificacao': dados_equipamento.get("Placa/N.Série:", ""),
                'acoplamento': dados_equipamento.get("Acoplamento:", ""),
                'aspectos_rotores': dados_equipamento.get("Aspectos Rotores:", ""),
                'valvulas_acopladas': dados_equipamento.get("Válvulas Acopladas:", ""),
                'data_recebimento_equip': dados_equipamento.get("Data Recebimento:", ""),
                'parafusos_pinos': dados_equipamento.get("Parafusos/Pinos:", ""),
                'superficie_vedacao': dados_equipamento.get("Superfície Vedação:", ""),
                'cotacao_id': cotacao_id,
                'tempo_trabalho_total': f"{tempo_trabalho}/{total_trabalho}",
                'tempo_deslocamento_total': f"{tempo_deslocamento}/{total_deslocamento}",
                'servicos_propostos': servicos,
                'pecas_recomendadas': pecas,
                'data_pecas': data_pecas,
                'fotos': caminhos_str
            }
            
            if self.current_relatorio_id:
                # Atualizar - removendo os campos None e que não existem na tabela
                update_parts = []
                update_values = []
                
                for key, value in data.items():
                    if value is not None and key in column_names:
                        update_parts.append(f"{key}=?")
                        update_values.append(value)
                
                if update_parts:
                    query = f"UPDATE relatorios_tecnicos SET {', '.join(update_parts)} WHERE id=?"
                    update_values.append(self.current_relatorio_id)
                    c.execute(query, update_values)
                    
                # Remover eventos antigos
                c.execute("DELETE FROM eventos_campo WHERE relatorio_id=?", (self.current_relatorio_id,))
            else:
                # Inserir - filtrar colunas que existem na tabela
                filtered_data = {}
                for key, value in data.items():
                    if key in column_names:
                        filtered_data[key] = value
                
                columns = list(filtered_data.keys())
                placeholders = ['?'] * len(columns)
                values = [filtered_data[col] for col in columns]
                
                query = f"INSERT INTO relatorios_tecnicos ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
                c.execute(query, values)
                self.current_relatorio_id = c.lastrowid
            
            self.current_relatorio_id = c.lastrowid
            
            # Inserir eventos dos técnicos
            for tecnico_id, eventos_tree in self.tecnicos_eventos.items():
                for item in eventos_tree.get_children():
                    hora, evento, tipo = eventos_tree.item(item)['values']
                    c.execute("""
                        INSERT INTO eventos_campo (relatorio_id, tecnico_id, data_hora, evento, tipo)
                        VALUES (?, ?, ?, ?, ?)
                    """, (self.current_relatorio_id, tecnico_id, hora, evento, tipo))
            
            conn.commit()
            messagebox.showinfo("Sucesso", "Relatório salvo com sucesso!")
            self.carregar_relatorios()
            
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao salvar relatório: {e}")
            import traceback
            print(f"Erro completo: {traceback.format_exc()}")
        finally:
            conn.close()
            
    def gerar_pdf_relatorio(self):
        if not self.current_relatorio_id:
            messagebox.showwarning("Aviso", "Salve o relatório antes de gerar o PDF.")
            return
            
        try:
            sucesso, resultado = gerar_pdf_relatorio(self.current_relatorio_id, DB_NAME)
            
            if sucesso:
                messagebox.showinfo("Sucesso", f"PDF gerado com sucesso!\nArquivo: {resultado}")
                # Abrir o arquivo PDF
                import os
                os.startfile(resultado)
            else:
                messagebox.showerror("Erro", f"Erro ao gerar PDF: {resultado}")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {e}")
            
    def gerar_pdf_selecionado(self):
        selected = self.relatorios_tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um relatório para gerar o PDF.")
            return
            
        relatorio_id = self.relatorios_tree.item(selected[0])['values'][0]
        
        try:
            sucesso, resultado = gerar_pdf_relatorio(relatorio_id, DB_NAME)
            
            if sucesso:
                messagebox.showinfo("Sucesso", f"PDF gerado com sucesso!\nArquivo: {resultado}")
                # Abrir o arquivo PDF
                import os
                os.startfile(resultado)
            else:
                messagebox.showerror("Erro", f"Erro ao gerar PDF: {resultado}")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {e}")
            
    def carregar_relatorios(self):
        # Limpar lista
        for item in self.relatorios_tree.get_children():
            self.relatorios_tree.delete(item)
            
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            c.execute("""
                SELECT 
                    r.id, r.numero_relatorio, cl.nome, r.tipo_servico, r.data_criacao,
                    CASE WHEN r.cotacao_id IS NOT NULL THEN 'Vinculado' ELSE 'Pendente' END,
                    COALESCE(cot.numero_proposta, 'Não vinculado')
                FROM relatorios_tecnicos r
                JOIN clientes cl ON r.cliente_id = cl.id
                LEFT JOIN cotacoes cot ON r.cotacao_id = cot.id
                ORDER BY r.data_criacao DESC
            """)
            
            for row in c.fetchall():
                self.relatorios_tree.insert("", "end", values=row)
                
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao carregar relatórios: {e}")
        finally:
            conn.close()
            
    def buscar_relatorios(self):
        # Implementar busca
        self.carregar_relatorios()
        
    def editar_relatorio(self, event=None):
        selected = self.relatorios_tree.selection()
        if not selected:
            return
            
        relatorio_id = self.relatorios_tree.item(selected[0])['values'][0]
        self.notebook.select(0)  # Switch to edit tab first
        self.novo_relatorio()  # Clear form before editing
        self.carregar_relatorio_para_edicao(relatorio_id)
        
    def excluir_relatorio(self):
        selected = self.relatorios_tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um relatório para excluir.")
            return
            
        if messagebox.askyesno("Confirmar", "Deseja realmente excluir este relatório?"):
            relatorio_id = self.relatorios_tree.item(selected[0])['values'][0]
            
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            
            try:
                c.execute("DELETE FROM eventos_campo WHERE relatorio_id=?", (relatorio_id,))
                c.execute("DELETE FROM relatorios_tecnicos WHERE id=?", (relatorio_id,))
                conn.commit()
                
                messagebox.showinfo("Sucesso", "Relatório excluído com sucesso!")
                self.carregar_relatorios()
                
            except sqlite3.Error as e:
                messagebox.showerror("Erro", f"Erro ao excluir relatório: {e}")
            finally:
                conn.close()
        
    def carregar_relatorio_para_edicao(self, relatorio_id):
        if not hasattr(self, 'equipamento_vars'):
            self.equipamento_vars = {}
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            # Primeiro obter os nomes das colunas existentes na tabela
            c.execute("PRAGMA table_info(relatorios_tecnicos)")
            columns_info = c.fetchall()
            column_names = [column[1] for column in columns_info]
            
            # Construir a query com colunas explícitas
            columns_sql = ', '.join([f"r.{col}" for col in column_names])
            
            # Carregar dados principais do relatório com JOIN para cliente
            c.execute(f"""
                SELECT {columns_sql}, c.nome as cliente_nome
                FROM relatorios_tecnicos r
                JOIN clientes c ON r.cliente_id = c.id
                WHERE r.id = ?
            """, (relatorio_id,))
            
            row = c.fetchone()
            if not row:
                messagebox.showerror("Erro", "Relatório não encontrado!")
                return
            
            # Criar um dicionário para acessar os dados com segurança
            relatorio = {}
            for i, col in enumerate(column_names):
                if i < len(row) - 1:  # -1 porque adicionamos cliente_nome no final
                    relatorio[col] = row[i]
            cliente_nome = row[len(column_names)] if len(row) > len(column_names) else ""
            
            self.current_relatorio_id = relatorio_id
            
            # Limpar todos os campos antes de preencher
            self.novo_relatorio()
            
            # Preencher campos básicos usando o dicionário
            self.form_servico_var.set(relatorio.get('formulario_servico') or "")
            self.tipo_servico_var.set(relatorio.get('tipo_servico') or "")
            self.descricao_text.insert("1.0", relatorio.get('descricao_servico') or "")
            self.data_recebimento_var.set(relatorio.get('data_recebimento') or "")
            
            # Preencher cliente
            cliente_id = relatorio.get('cliente_id')
            if cliente_id:
                c.execute("SELECT id, nome, cnpj FROM clientes WHERE id = ?", (cliente_id,))
                cliente = c.fetchone()
                if cliente:
                    cliente_id, nome, cnpj = cliente
                    self.cliente_selecionado_id = cliente_id
                    self.cliente_selecionado_var.set(f"{nome} - {cnpj}")
                    self.carregar_cotacoes_cliente(cliente_id)
            
            # Preencher cotação vinculada
            cotacao_id = relatorio.get('cotacao_id')
            if cotacao_id:
                c.execute("SELECT id, numero_proposta, valor_total FROM cotacoes WHERE id = ?", (cotacao_id,))
                cotacao = c.fetchone()
                if cotacao:
                    self.cotacao_selecionada_id = cotacao[0]
                    try:
                        valor = float(cotacao[2]) if cotacao[2] else 0.0
                        self.cotacao_vinculada_var.set(f"{cotacao[1]} - R$ {valor:.2f}")
                    except (TypeError, ValueError):
                        self.cotacao_vinculada_var.set(f"{cotacao[1]} - {cotacao[2]}")
            
            # Mapeamento de campos do equipamento usando dicionário para acessar de forma segura
            campos_equipamento = {
                # Nome campo na UI: nome coluna no banco
                "Cond. Encontrada:": "condicao_encontrada",
                "Placa/N.Série:": "placa_identificacao",
                "Acoplamento:": "acoplamento",
                "Aspectos Rotores:": "aspectos_rotores",
                "Válvulas Acopladas:": "valvulas_acopladas",
                "Cond. Inicial:": "condicao_inicial",
                "Cond. Atual:": "condicao_atual",
            }
            
            # Preencher campos do equipamento de forma segura
            for campo_ui, coluna_db in campos_equipamento.items():
                if campo_ui in self.equipamento_vars and coluna_db in relatorio:
                    valor = relatorio.get(coluna_db)
                    if valor not in (None, ""):
                        self.equipamento_vars[campo_ui].set(valor)
            
            # Preencher tempos usando o dicionário
            if 'tempo_trabalho_total' in relatorio and relatorio['tempo_trabalho_total']:
                self.tempo_trabalho_var.set(relatorio['tempo_trabalho_total'])
            if 'tempo_deslocamento_total' in relatorio and relatorio['tempo_deslocamento_total']:
                self.tempo_deslocamento_var.set(relatorio['tempo_deslocamento_total'])
            
            # Preencher serviços e peças
            self.servicos_text.delete("1.0", tk.END)
            if 'servicos_propostos' in relatorio and relatorio['servicos_propostos']:
                self.servicos_text.insert("1.0", relatorio['servicos_propostos'])
            
            self.pecas_text.delete("1.0", tk.END)
            if 'pecas_recomendadas' in relatorio and relatorio['pecas_recomendadas']:
                self.pecas_text.insert("1.0", relatorio['pecas_recomendadas'])
            
            if 'data_pecas' in relatorio and relatorio['data_pecas']:
                self.data_pecas_var.set(relatorio['data_pecas'])
            
            # Carregar fotos
            if 'fotos' in relatorio and relatorio['fotos']:
                for path in relatorio['fotos'].split(';'):
                    if path.strip():
                        self.adicionar_foto_por_caminho(path)
            
            # Carregar técnicos e eventos
            try:
                c.execute("""
                    SELECT e.tecnico_id, t.nome, e.data_hora, e.evento, e.tipo 
                    FROM eventos_campo e
                    JOIN tecnicos t ON e.tecnico_id = t.id
                    WHERE e.relatorio_id = ?
                """, (relatorio_id,))
                eventos = c.fetchall()
                
                # Agrupar eventos por técnico
                tecnicos_data = {}
                for evento in eventos:
                    tecnico_id, nome, data_hora, evento_desc, tipo = evento
                    if tecnico_id not in tecnicos_data:
                        tecnicos_data[tecnico_id] = {
                            "nome": nome,
                            "eventos": []
                        }
                    tecnicos_data[tecnico_id]["eventos"].append((data_hora, evento_desc, tipo))
            except sqlite3.Error as e:
                print(f"Erro ao carregar eventos: {e}")
                tecnicos_data = {}
            
            # Criar abas para cada técnico
            for tecnico_id, data in tecnicos_data.items():
                try:
                    self.criar_aba_tecnico(tecnico_id, data["nome"])
                    tree = self.tecnicos_eventos.get(tecnico_id)
                    if tree:
                        for data_hora, evento_desc, tipo in data["eventos"]:
                            tree.insert("", "end", values=(data_hora, evento_desc, tipo))
                except Exception as e:
                    print(f"Erro ao criar aba para técnico {tecnico_id}: {e}")
            
            # Mudar para a aba de edição
            self.notebook.select(0)
            
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao carregar relatório: {e}")
        finally:
            conn.close()