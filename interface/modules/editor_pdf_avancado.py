import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
import json
import os
import sqlite3
from datetime import datetime
import subprocess
import tempfile

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Importar módulo base
from .base_module import BaseModule

class EditorPDFAvancadoModule(BaseModule):
    def __init__(self, parent, user_id, role, main_window):
        try:
            self.user_info = {'role': role, 'user_id': user_id}
            
            # Configurar conexão com banco
            from database import DB_NAME
            self.db_name = DB_NAME
            
            # Inicializar propriedades
            self.pdf_template = None
            self.sample_data = {}
            self.preview_image = None
            self.canvas_scale = 0.7
            self.page_width = 595  # A4 width in points
            self.page_height = 842  # A4 height in points
            
            super().__init__(parent, user_id, role, main_window)
            
            # Carregar dados de exemplo
            self.load_sample_data()
            
            # Carregar template
            self.load_template()
            
            # Gerar preview inicial
            self.generate_preview()
            
        except Exception as e:
            print(f"Erro na inicialização do Editor PDF Avançado: {e}")
            self.create_error_interface(parent, str(e))
    
    def create_error_interface(self, parent, error_message):
        """Criar interface simples de erro"""
        try:
            self.frame = tk.Frame(parent, bg='#f8fafc')
            self.frame.pack(fill="both", expand=True)
            
            error_frame = tk.Frame(self.frame, bg='white')
            error_frame.pack(expand=True, fill="both", padx=50, pady=50)
            
            tk.Label(error_frame, text="⚠️ Erro no Editor PDF Avançado", 
                    font=('Arial', 18, 'bold'), bg='white', fg='#ef4444').pack(pady=20)
            tk.Label(error_frame, text="Houve um problema ao carregar o editor avançado:", 
                    font=('Arial', 12), bg='white', fg='#64748b').pack(pady=10)
            tk.Label(error_frame, text=error_message, 
                    font=('Arial', 10), bg='white', fg='#64748b', wraplength=400).pack(pady=10)
            tk.Label(error_frame, text="Use o 'Editor PDF' básico ou contate o suporte técnico.", 
                    font=('Arial', 10), bg='white', fg='#64748b').pack(pady=20)
        except:
            self.frame = tk.Frame(parent, bg='#f8fafc')
            self.frame.pack(fill="both", expand=True)
            tk.Label(self.frame, text="Erro no Editor PDF Avançado", 
                    font=('Arial', 14), bg='#f8fafc', fg='#ef4444').pack(expand=True)
    
    def setup_ui(self):
        """Configurar interface do editor avançado"""
        # Título principal
        title_frame = tk.Frame(self.frame, bg='#f8fafc')
        title_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(title_frame, text="🚀 Editor PDF Avançado - Visualização e Edição", 
                font=('Arial', 16, 'bold'), bg='#f8fafc', fg='#1e293b').pack(side="left")
        
        # Frame principal com duas colunas
        main_frame = tk.Frame(self.frame, bg='#f8fafc')
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Coluna esquerda - Controles de edição (40%)
        self.controls_frame = tk.Frame(main_frame, bg='white', relief='ridge', bd=1)
        self.controls_frame.pack(side="left", fill="both", expand=False, padx=(0, 10))
        self.controls_frame.config(width=400)
        
        # Coluna direita - Preview do PDF (60%)
        self.preview_frame = tk.Frame(main_frame, bg='white', relief='ridge', bd=1)
        self.preview_frame.pack(side="right", fill="both", expand=True)
        
        # Configurar painéis
        self.setup_controls_panel()
        self.setup_preview_panel()
    
    def setup_controls_panel(self):
        """Configurar painel de controles de edição"""
        # Título do painel
        title_frame = tk.Frame(self.controls_frame, bg='#3b82f6')
        title_frame.pack(fill="x")
        
        tk.Label(title_frame, text="✏️ Controles de Edição", 
                font=('Arial', 12, 'bold'), bg='#3b82f6', fg='white').pack(pady=10)
        
        # Notebook para organizar controles
        self.controls_notebook = ttk.Notebook(self.controls_frame)
        self.controls_notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Aba 1: Dados da Empresa
        self.setup_company_tab()
        
        # Aba 2: Dados do Cliente
        self.setup_client_tab()
        
        # Aba 3: Dados da Proposta
        self.setup_proposal_tab()
        
        # Aba 4: Estilo e Cores
        self.setup_style_tab()
        
        # Botões de ação
        self.setup_action_buttons()
    
    def setup_company_tab(self):
        """Configurar aba de dados da empresa"""
        company_frame = tk.Frame(self.controls_notebook, bg='white')
        self.controls_notebook.add(company_frame, text="🏢 Empresa")
        
        # Scroll para a aba
        canvas = tk.Canvas(company_frame, bg='white')
        scrollbar = ttk.Scrollbar(company_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Campos da empresa
        self.company_fields = {}
        
        fields = [
            ("Nome da Empresa", "empresa_nome", "WORLD COMP BRASIL LTDA"),
            ("Endereço", "empresa_endereco", "Rua das Empresas, 123, Centro - São Paulo/SP"),
            ("CNPJ", "empresa_cnpj", "12.345.678/0001-90"),
            ("Telefone", "empresa_telefone", "(11) 3456-7890"),
            ("Email", "empresa_email", "contato@worldcomp.com.br"),
            ("Website", "empresa_website", "www.worldcomp.com.br")
        ]
        
        for i, (label, key, default) in enumerate(fields):
            # Label
            tk.Label(scrollable_frame, text=label, font=('Arial', 9, 'bold'), 
                    bg='white', fg='#374151').pack(anchor="w", padx=10, pady=(10,2))
            
            # Entry
            entry = tk.Entry(scrollable_frame, font=('Arial', 9), bg='#f9fafb', 
                           relief='solid', bd=1, width=45)
            entry.pack(fill="x", padx=10, pady=(0,5))
            entry.insert(0, default)
            entry.bind('<KeyRelease>', self.on_data_change)
            
            self.company_fields[key] = entry
    
    def setup_client_tab(self):
        """Configurar aba de dados do cliente"""
        client_frame = tk.Frame(self.controls_notebook, bg='white')
        self.controls_notebook.add(client_frame, text="👤 Cliente")
        
        # Scroll para a aba
        canvas = tk.Canvas(client_frame, bg='white')
        scrollbar = ttk.Scrollbar(client_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Campos do cliente
        self.client_fields = {}
        
        fields = [
            ("Nome/Razão Social", "cliente_nome", "EMPRESA EXEMPLO LTDA"),
            ("CNPJ/CPF", "cliente_cnpj", "98.765.432/0001-10"),
            ("Contato", "cliente_contato", "Sr. João da Silva"),
            ("Cargo", "cliente_cargo", "Gerente de Compras"),
            ("Telefone", "cliente_telefone", "(11) 9876-5432"),
            ("Email", "cliente_email", "joao@empresaexemplo.com.br"),
            ("Endereço", "cliente_endereco", "Av. Principal, 456, Bairro - Cidade/UF")
        ]
        
        for i, (label, key, default) in enumerate(fields):
            # Label
            tk.Label(scrollable_frame, text=label, font=('Arial', 9, 'bold'), 
                    bg='white', fg='#374151').pack(anchor="w", padx=10, pady=(10,2))
            
            # Entry
            entry = tk.Entry(scrollable_frame, font=('Arial', 9), bg='#f9fafb', 
                           relief='solid', bd=1, width=45)
            entry.pack(fill="x", padx=10, pady=(0,5))
            entry.insert(0, default)
            entry.bind('<KeyRelease>', self.on_data_change)
            
            self.client_fields[key] = entry
    
    def setup_proposal_tab(self):
        """Configurar aba de dados da proposta"""
        proposal_frame = tk.Frame(self.controls_notebook, bg='white')
        self.controls_notebook.add(proposal_frame, text="📋 Proposta")
        
        # Scroll para a aba
        canvas = tk.Canvas(proposal_frame, bg='white')
        scrollbar = ttk.Scrollbar(proposal_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Campos da proposta
        self.proposal_fields = {}
        
        fields = [
            ("Número da Proposta", "proposta_numero", "PROP-2025-001"),
            ("Data", "proposta_data", datetime.now().strftime("%d/%m/%Y")),
            ("Validade", "proposta_validade", "30 dias"),
            ("Condições de Pagamento", "proposta_pagamento", "30 dias após entrega"),
            ("Prazo de Entrega", "proposta_prazo", "15 dias úteis"),
            ("Garantia", "proposta_garantia", "12 meses"),
        ]
        
        for i, (label, key, default) in enumerate(fields):
            # Label
            tk.Label(scrollable_frame, text=label, font=('Arial', 9, 'bold'), 
                    bg='white', fg='#374151').pack(anchor="w", padx=10, pady=(10,2))
            
            # Entry
            entry = tk.Entry(scrollable_frame, font=('Arial', 9), bg='#f9fafb', 
                           relief='solid', bd=1, width=45)
            entry.pack(fill="x", padx=10, pady=(0,5))
            entry.insert(0, default)
            entry.bind('<KeyRelease>', self.on_data_change)
            
            self.proposal_fields[key] = entry
        
        # Seção de itens da proposta
        tk.Label(scrollable_frame, text="Itens da Proposta", font=('Arial', 10, 'bold'), 
                bg='white', fg='#1f2937').pack(anchor="w", padx=10, pady=(20,5))
        
        # Frame para itens
        items_frame = tk.Frame(scrollable_frame, bg='#f3f4f6', relief='solid', bd=1)
        items_frame.pack(fill="x", padx=10, pady=5)
        
        # Cabeçalho da tabela
        header_frame = tk.Frame(items_frame, bg='#e5e7eb')
        header_frame.pack(fill="x", padx=2, pady=2)
        
        tk.Label(header_frame, text="Item", font=('Arial', 8, 'bold'), 
                bg='#e5e7eb', width=20).pack(side="left", padx=2)
        tk.Label(header_frame, text="Qtd", font=('Arial', 8, 'bold'), 
                bg='#e5e7eb', width=5).pack(side="left", padx=2)
        tk.Label(header_frame, text="Valor Unit.", font=('Arial', 8, 'bold'), 
                bg='#e5e7eb', width=10).pack(side="left", padx=2)
        
        # Itens de exemplo
        self.proposal_items = []
        sample_items = [
            ("Compressor de Ar 10HP", "1", "R$ 2.500,00"),
            ("Filtro de Ar", "2", "R$ 150,00"),
            ("Óleo Lubrificante 20L", "1", "R$ 380,00")
        ]
        
        for item, qty, price in sample_items:
            item_frame = tk.Frame(items_frame, bg='white')
            item_frame.pack(fill="x", padx=2, pady=1)
            
            item_entry = tk.Entry(item_frame, font=('Arial', 8), width=20)
            item_entry.pack(side="left", padx=2)
            item_entry.insert(0, item)
            item_entry.bind('<KeyRelease>', self.on_data_change)
            
            qty_entry = tk.Entry(item_frame, font=('Arial', 8), width=5)
            qty_entry.pack(side="left", padx=2)
            qty_entry.insert(0, qty)
            qty_entry.bind('<KeyRelease>', self.on_data_change)
            
            price_entry = tk.Entry(item_frame, font=('Arial', 8), width=10)
            price_entry.pack(side="left", padx=2)
            price_entry.insert(0, price)
            price_entry.bind('<KeyRelease>', self.on_data_change)
            
            self.proposal_items.append((item_entry, qty_entry, price_entry))
        
        # Valor total
        tk.Label(scrollable_frame, text="Valor Total", font=('Arial', 10, 'bold'), 
                bg='white', fg='#1f2937').pack(anchor="w", padx=10, pady=(15,2))
        
        self.total_entry = tk.Entry(scrollable_frame, font=('Arial', 10, 'bold'), 
                                   bg='#fef3c7', relief='solid', bd=1, width=45)
        self.total_entry.pack(fill="x", padx=10, pady=(0,5))
        self.total_entry.insert(0, "R$ 3.480,00")
        self.total_entry.bind('<KeyRelease>', self.on_data_change)
    
    def setup_style_tab(self):
        """Configurar aba de estilo e cores"""
        style_frame = tk.Frame(self.controls_notebook, bg='white')
        self.controls_notebook.add(style_frame, text="🎨 Estilo")
        
        # Scroll para a aba
        canvas = tk.Canvas(style_frame, bg='white')
        scrollbar = ttk.Scrollbar(style_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configurações de estilo
        self.style_fields = {}
        
        # Cores
        tk.Label(scrollable_frame, text="Cores do Template", font=('Arial', 10, 'bold'), 
                bg='white', fg='#1f2937').pack(anchor="w", padx=10, pady=(10,5))
        
        colors = [
            ("Cor Principal", "cor_principal", "#3b82f6"),
            ("Cor Secundária", "cor_secundaria", "#1e40af"),
            ("Cor do Texto", "cor_texto", "#1f2937"),
            ("Cor de Fundo", "cor_fundo", "#ffffff")
        ]
        
        for label, key, default in colors:
            color_frame = tk.Frame(scrollable_frame, bg='white')
            color_frame.pack(fill="x", padx=10, pady=2)
            
            tk.Label(color_frame, text=label, font=('Arial', 9), 
                    bg='white', fg='#374151', width=15).pack(side="left")
            
            color_var = tk.StringVar(value=default)
            color_entry = tk.Entry(color_frame, textvariable=color_var, 
                                 font=('Arial', 9), width=10)
            color_entry.pack(side="left", padx=5)
            color_entry.bind('<KeyRelease>', self.on_data_change)
            
            def choose_color(var=color_var):
                color = colorchooser.askcolor(title="Escolher Cor")[1]
                if color:
                    var.set(color)
                    self.on_data_change()
            
            color_btn = tk.Button(color_frame, text="🎨", command=choose_color, 
                                width=3, font=('Arial', 8))
            color_btn.pack(side="left", padx=2)
            
            # Preview da cor
            color_preview = tk.Label(color_frame, text="  ", bg=default, 
                                   relief='solid', bd=1, width=3)
            color_preview.pack(side="left", padx=5)
            
            self.style_fields[key] = (color_var, color_preview)
        
        # Fontes
        tk.Label(scrollable_frame, text="Configurações de Fonte", font=('Arial', 10, 'bold'), 
                bg='white', fg='#1f2937').pack(anchor="w", padx=10, pady=(20,5))
        
        fonts = [
            ("Tamanho Título", "font_titulo", "16"),
            ("Tamanho Texto", "font_texto", "10"),
            ("Tamanho Rodapé", "font_rodape", "8")
        ]
        
        for label, key, default in fonts:
            font_frame = tk.Frame(scrollable_frame, bg='white')
            font_frame.pack(fill="x", padx=10, pady=2)
            
            tk.Label(font_frame, text=label, font=('Arial', 9), 
                    bg='white', fg='#374151', width=15).pack(side="left")
            
            font_entry = tk.Entry(font_frame, font=('Arial', 9), width=10)
            font_entry.pack(side="left", padx=5)
            font_entry.insert(0, default)
            font_entry.bind('<KeyRelease>', self.on_data_change)
            
            self.style_fields[key] = font_entry
        
        # Logo
        tk.Label(scrollable_frame, text="Logo da Empresa", font=('Arial', 10, 'bold'), 
                bg='white', fg='#1f2937').pack(anchor="w", padx=10, pady=(20,5))
        
        logo_frame = tk.Frame(scrollable_frame, bg='white')
        logo_frame.pack(fill="x", padx=10, pady=5)
        
        self.logo_path = tk.StringVar(value="assets/logos/world_comp_brasil.jpg")
        logo_entry = tk.Entry(logo_frame, textvariable=self.logo_path, 
                             font=('Arial', 9), width=30)
        logo_entry.pack(side="left", fill="x", expand=True)
        logo_entry.bind('<KeyRelease>', self.on_data_change)
        
        def choose_logo():
            filename = filedialog.askopenfilename(
                title="Selecionar Logo",
                filetypes=[("Imagens", "*.png *.jpg *.jpeg *.gif *.bmp")]
            )
            if filename:
                self.logo_path.set(filename)
                self.on_data_change()
        
        logo_btn = tk.Button(logo_frame, text="📁 Buscar", command=choose_logo)
        logo_btn.pack(side="right", padx=(5,0))
    
    def setup_action_buttons(self):
        """Configurar botões de ação"""
        btn_frame = tk.Frame(self.controls_frame, bg='white')
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        # Botão de atualizar preview
        update_btn = tk.Button(btn_frame, text="🔄 Atualizar Preview", 
                              command=self.generate_preview,
                              font=('Arial', 10, 'bold'), bg='#10b981', fg='white',
                              relief='flat', cursor='hand2')
        update_btn.pack(fill="x", pady=2)
        
        # Botão de salvar template
        save_btn = tk.Button(btn_frame, text="💾 Salvar Template", 
                            command=self.save_template,
                            font=('Arial', 10, 'bold'), bg='#3b82f6', fg='white',
                            relief='flat', cursor='hand2')
        save_btn.pack(fill="x", pady=2)
        
        # Botão de gerar PDF final
        pdf_btn = tk.Button(btn_frame, text="📄 Gerar PDF", 
                           command=self.generate_final_pdf,
                           font=('Arial', 10, 'bold'), bg='#ef4444', fg='white',
                           relief='flat', cursor='hand2')
        pdf_btn.pack(fill="x", pady=2)
        
        # Botão de reset
        reset_btn = tk.Button(btn_frame, text="🔄 Resetar Dados", 
                             command=self.reset_data,
                             font=('Arial', 9), bg='#6b7280', fg='white',
                             relief='flat', cursor='hand2')
        reset_btn.pack(fill="x", pady=2)
    
    def setup_preview_panel(self):
        """Configurar painel de preview"""
        # Título do painel
        title_frame = tk.Frame(self.preview_frame, bg='#1e40af')
        title_frame.pack(fill="x")
        
        tk.Label(title_frame, text="👁️ Preview do PDF", 
                font=('Arial', 12, 'bold'), bg='#1e40af', fg='white').pack(side="left", pady=10, padx=10)
        
        # Status
        self.preview_status = tk.Label(title_frame, text="Carregando...", 
                                      font=('Arial', 9), bg='#1e40af', fg='#bfdbfe')
        self.preview_status.pack(side="right", pady=10, padx=10)
        
        # Canvas para o preview
        canvas_frame = tk.Frame(self.preview_frame, bg='#f3f4f6')
        canvas_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical")
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient="horizontal")
        
        self.preview_canvas = tk.Canvas(canvas_frame, bg='white',
                                       yscrollcommand=v_scrollbar.set,
                                       xscrollcommand=h_scrollbar.set)
        
        v_scrollbar.config(command=self.preview_canvas.yview)
        h_scrollbar.config(command=self.preview_canvas.xview)
        
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        self.preview_canvas.pack(side="left", fill="both", expand=True)
        
        # Navegação de páginas
        nav_frame = tk.Frame(self.preview_frame, bg='white')
        nav_frame.pack(fill="x", padx=5, pady=5)
        
        tk.Button(nav_frame, text="◀ Anterior", command=lambda: self.change_page(-1),
                 font=('Arial', 9)).pack(side="left", padx=5)
        
        self.page_label = tk.Label(nav_frame, text="Página 1 de 4", 
                                  font=('Arial', 9, 'bold'), bg='white')
        self.page_label.pack(side="left", expand=True)
        
        tk.Button(nav_frame, text="Próxima ▶", command=lambda: self.change_page(1),
                 font=('Arial', 9)).pack(side="right", padx=5)
        
        # Página atual
        self.current_page = 1
        self.total_pages = 4
    
    def load_sample_data(self):
        """Carregar dados de exemplo"""
        self.sample_data = {
            'empresa': {
                'nome': 'WORLD COMP BRASIL LTDA',
                'endereco': 'Rua das Empresas, 123, Centro - São Paulo/SP',
                'cnpj': '12.345.678/0001-90',
                'telefone': '(11) 3456-7890',
                'email': 'contato@worldcomp.com.br',
                'website': 'www.worldcomp.com.br'
            },
            'cliente': {
                'nome': 'EMPRESA EXEMPLO LTDA',
                'cnpj': '98.765.432/0001-10',
                'contato': 'Sr. João da Silva',
                'cargo': 'Gerente de Compras',
                'telefone': '(11) 9876-5432',
                'email': 'joao@empresaexemplo.com.br',
                'endereco': 'Av. Principal, 456, Bairro - Cidade/UF'
            },
            'proposta': {
                'numero': 'PROP-2025-001',
                'data': datetime.now().strftime("%d/%m/%Y"),
                'validade': '30 dias',
                'pagamento': '30 dias após entrega',
                'prazo': '15 dias úteis',
                'garantia': '12 meses',
                'valor_total': 'R$ 3.480,00'
            },
            'itens': [
                {'nome': 'Compressor de Ar 10HP', 'quantidade': '1', 'valor': 'R$ 2.500,00'},
                {'nome': 'Filtro de Ar', 'quantidade': '2', 'valor': 'R$ 150,00'},
                {'nome': 'Óleo Lubrificante 20L', 'quantidade': '1', 'valor': 'R$ 380,00'}
            ]
        }
    
    def load_template(self):
        """Carregar template padrão"""
        self.pdf_template = {
            'cores': {
                'principal': '#3b82f6',
                'secundaria': '#1e40af',
                'texto': '#1f2937',
                'fundo': '#ffffff'
            },
            'fontes': {
                'titulo': 16,
                'texto': 10,
                'rodape': 8
            },
            'logo': 'assets/logos/world_comp_brasil.jpg'
        }
    
    def on_data_change(self, event=None):
        """Callback quando dados são alterados"""
        # Debounce para evitar muitas atualizações
        if hasattr(self, '_update_timer'):
            self.frame.after_cancel(self._update_timer)
        
        self._update_timer = self.frame.after(1000, self.update_sample_data)
    
    def update_sample_data(self):
        """Atualizar dados de exemplo com valores dos campos"""
        try:
            # Atualizar dados da empresa
            if hasattr(self, 'company_fields'):
                for key, entry in self.company_fields.items():
                    field_name = key.replace('empresa_', '')
                    self.sample_data['empresa'][field_name] = entry.get()
            
            # Atualizar dados do cliente
            if hasattr(self, 'client_fields'):
                for key, entry in self.client_fields.items():
                    field_name = key.replace('cliente_', '')
                    self.sample_data['cliente'][field_name] = entry.get()
            
            # Atualizar dados da proposta
            if hasattr(self, 'proposal_fields'):
                for key, entry in self.proposal_fields.items():
                    field_name = key.replace('proposta_', '')
                    self.sample_data['proposta'][field_name] = entry.get()
            
            # Atualizar valor total
            if hasattr(self, 'total_entry'):
                self.sample_data['proposta']['valor_total'] = self.total_entry.get()
            
            # Atualizar itens
            if hasattr(self, 'proposal_items'):
                self.sample_data['itens'] = []
                for item_entry, qty_entry, price_entry in self.proposal_items:
                    self.sample_data['itens'].append({
                        'nome': item_entry.get(),
                        'quantidade': qty_entry.get(),
                        'valor': price_entry.get()
                    })
            
            # Atualizar cores
            if hasattr(self, 'style_fields'):
                for key, field in self.style_fields.items():
                    if key.startswith('cor_'):
                        color_name = key.replace('cor_', '')
                        if isinstance(field, tuple):  # Campo de cor com preview
                            color_var, preview = field
                            color = color_var.get()
                            self.pdf_template['cores'][color_name] = color
                            preview.config(bg=color)
                    elif key.startswith('font_'):
                        font_name = key.replace('font_', '')
                        try:
                            size = int(field.get())
                            self.pdf_template['fontes'][font_name] = size
                        except:
                            pass
            
            # Atualizar logo
            if hasattr(self, 'logo_path'):
                self.pdf_template['logo'] = self.logo_path.get()
            
            print("Dados atualizados automaticamente")
            
        except Exception as e:
            print(f"Erro ao atualizar dados: {e}")
    
    def generate_preview(self):
        """Gerar preview do PDF"""
        try:
            self.preview_status.config(text="🔄 Gerando preview...")
            self.frame.update()
            
            # Atualizar dados primeiro
            self.update_sample_data()
            
            # Simular geração de PDF e converter para imagem
            preview_text = self.create_preview_text()
            
            # Criar uma imagem de texto simples como preview
            self.create_text_preview(preview_text)
            
            self.preview_status.config(text="✅ Preview atualizado")
            
        except Exception as e:
            self.preview_status.config(text="❌ Erro no preview")
            print(f"Erro ao gerar preview: {e}")
    
    def create_preview_text(self):
        """Criar texto de preview baseado na página atual"""
        data = self.sample_data
        
        if self.current_page == 1:
            # Página de Capa
            return f"""
PROPOSTA COMERCIAL

{data['empresa']['nome']}

Proposta: {data['proposta']['numero']}
Data: {data['proposta']['data']}

A/C Sr. {data['cliente']['contato']}
{data['cliente']['nome']}

═══════════════════════════════════════
            """
        
        elif self.current_page == 2:
            # Página de Apresentação
            return f"""
APRESENTAÇÃO

{data['empresa']['nome']}
{data['empresa']['endereco']}
{data['empresa']['telefone']}
{data['empresa']['email']}

Prezados Senhores,

Agradecemos a oportunidade de apresentar 
nossa proposta comercial.

Nossa empresa está preparada para atender
suas necessidades com qualidade e
pontualidade.

═══════════════════════════════════════
            """
        
        elif self.current_page == 3:
            # Página Sobre a Empresa
            return f"""
SOBRE A {data['empresa']['nome']}

Há mais de uma década no mercado, nossa
empresa se destaca pela qualidade dos
serviços prestados e pelo atendimento
diferenciado aos clientes.

NOSSOS DIFERENCIAIS:
• Equipe técnica especializada
• Equipamentos de última geração
• Garantia dos serviços prestados
• Atendimento 24 horas

CONTATO:
{data['empresa']['telefone']}
{data['empresa']['email']}
{data['empresa']['website']}

═══════════════════════════════════════
            """
        
        elif self.current_page == 4:
            # Página da Proposta
            items_text = ""
            for item in data['itens']:
                items_text += f"• {item['nome']} - Qtd: {item['quantidade']} - {item['valor']}\n"
            
            return f"""
PROPOSTA COMERCIAL

Cliente: {data['cliente']['nome']}
CNPJ: {data['cliente']['cnpj']}
Contato: {data['cliente']['contato']}

ITENS PROPOSTOS:
{items_text}

VALOR TOTAL: {data['proposta']['valor_total']}

CONDIÇÕES:
• Validade: {data['proposta']['validade']}
• Pagamento: {data['proposta']['pagamento']}
• Prazo: {data['proposta']['prazo']}
• Garantia: {data['proposta']['garantia']}

═══════════════════════════════════════
            """
        
        return "Página não encontrada"
    
    def create_text_preview(self, text):
        """Criar preview visual do texto"""
        # Limpar canvas
        self.preview_canvas.delete("all")
        
        # Configurações de cores do template
        bg_color = self.pdf_template['cores']['fundo']
        text_color = self.pdf_template['cores']['texto']
        
        # Configurar fundo
        self.preview_canvas.config(bg=bg_color)
        
        # Dimensões da página
        page_width = int(self.page_width * self.canvas_scale)
        page_height = int(self.page_height * self.canvas_scale)
        
        # Criar retângulo da página
        self.preview_canvas.create_rectangle(10, 10, page_width + 10, page_height + 10,
                                           fill=bg_color, outline='#d1d5db', width=2)
        
        # Adicionar texto
        lines = text.strip().split('\n')
        y_pos = 30
        
        for line in lines:
            if line.strip():
                if line.startswith('PROPOSTA COMERCIAL') or line.startswith('APRESENTAÇÃO') or line.startswith('SOBRE A'):
                    # Título
                    font_size = self.pdf_template['fontes']['titulo']
                    self.preview_canvas.create_text(page_width//2 + 10, y_pos, 
                                                  text=line.strip(), 
                                                  font=('Arial', font_size, 'bold'),
                                                  fill=self.pdf_template['cores']['principal'],
                                                  anchor='n')
                    y_pos += 40
                elif line.startswith('═'):
                    # Linha divisória
                    self.preview_canvas.create_line(30, y_pos, page_width - 20, y_pos,
                                                  fill=self.pdf_template['cores']['secundaria'], width=2)
                    y_pos += 20
                else:
                    # Texto normal
                    font_size = self.pdf_template['fontes']['texto']
                    self.preview_canvas.create_text(30, y_pos, 
                                                  text=line.strip(), 
                                                  font=('Arial', font_size),
                                                  fill=text_color,
                                                  anchor='nw')
                    y_pos += 20
            else:
                y_pos += 10
        
        # Configurar scroll region
        self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all"))
        
        # Atualizar label da página
        self.page_label.config(text=f"Página {self.current_page} de {self.total_pages}")
    
    def change_page(self, direction):
        """Mudar página do preview"""
        new_page = self.current_page + direction
        
        if 1 <= new_page <= self.total_pages:
            self.current_page = new_page
            self.generate_preview()
    
    def save_template(self):
        """Salvar template atual"""
        try:
            # Criar diretório se não existir
            os.makedirs('data/templates', exist_ok=True)
            
            # Dados para salvar
            template_data = {
                'empresa': self.sample_data['empresa'],
                'template': self.pdf_template,
                'data_criacao': datetime.now().isoformat()
            }
            
            # Salvar arquivo
            filename = f"data/templates/template_usuario_{self.user_id}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, indent=4, ensure_ascii=False)
            
            messagebox.showinfo("Sucesso", "Template salvo com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar template: {e}")
    
    def generate_final_pdf(self):
        """Gerar PDF final"""
        try:
            # Atualizar dados
            self.update_sample_data()
            
            # Usar o gerador de PDF existente
            from pdf_generators.cotacao_nova import gerar_cotacao_pdf
            
            # Converter dados para formato esperado
            cotacao_data = {
                'numero': self.sample_data['proposta']['numero'],
                'data': self.sample_data['proposta']['data'],
                'cliente': self.sample_data['cliente']['nome'],
                'cnpj': self.sample_data['cliente']['cnpj'],
                'contato': self.sample_data['cliente']['contato'],
                'valor_total': self.sample_data['proposta']['valor_total'],
                'itens': self.sample_data['itens']
            }
            
            # Gerar PDF
            filename = f"temp/proposta_{self.sample_data['proposta']['numero']}.pdf"
            os.makedirs('temp', exist_ok=True)
            
            gerar_cotacao_pdf(cotacao_data, filename)
            
            # Abrir PDF
            if os.path.exists(filename):
                if os.name == 'nt':  # Windows
                    os.startfile(filename)
                else:  # Linux/Mac
                    subprocess.run(['xdg-open', filename])
                
                messagebox.showinfo("Sucesso", f"PDF gerado com sucesso!\n{filename}")
            else:
                messagebox.showerror("Erro", "Arquivo PDF não foi criado.")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar PDF: {e}")
    
    def reset_data(self):
        """Resetar dados para valores padrão"""
        if messagebox.askyesno("Confirmar", "Resetar todos os dados para os valores padrão?"):
            # Recarregar dados de exemplo
            self.load_sample_data()
            self.load_template()
            
            # Atualizar campos
            if hasattr(self, 'company_fields'):
                for key, entry in self.company_fields.items():
                    field_name = key.replace('empresa_', '')
                    entry.delete(0, tk.END)
                    entry.insert(0, self.sample_data['empresa'][field_name])
            
            if hasattr(self, 'client_fields'):
                for key, entry in self.client_fields.items():
                    field_name = key.replace('cliente_', '')
                    entry.delete(0, tk.END)
                    entry.insert(0, self.sample_data['cliente'][field_name])
            
            if hasattr(self, 'proposal_fields'):
                for key, entry in self.proposal_fields.items():
                    field_name = key.replace('proposta_', '')
                    entry.delete(0, tk.END)
                    entry.insert(0, self.sample_data['proposta'][field_name])
            
            # Gerar novo preview
            self.generate_preview()
            
            messagebox.showinfo("Sucesso", "Dados resetados com sucesso!")
    
    def show_success(self, message):
        """Mostrar mensagem de sucesso"""
        print(f"✅ {message}")
    
    def show_error(self, message):
        """Mostrar mensagem de erro"""
        print(f"❌ {message}")