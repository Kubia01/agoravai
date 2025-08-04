import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog, colorchooser
import sqlite3
import json
import os
from datetime import datetime

# Importar módulo base
from .base_module import BaseModule

class EditorTemplatePDFModule(BaseModule):
    def __init__(self, parent, user_id, role, main_window):
        """Editor de Templates PDF - Padronização de modelos futuros"""
        try:
            self.user_id = user_id
            self.role = role
            self.main_window = main_window
            
            # Configurar conexão com banco
            from database import DB_NAME
            self.db_name = DB_NAME
            
            # Template atual sendo editado
            self.current_template = None
            self.template_data = {}
            
            # Elementos das páginas
            self.page_elements = {
                1: [],  # Página 1 - Capa (não editável)
                2: [],  # Página 2 - Introdução  
                3: [],  # Página 3 - Sobre a empresa
                4: []   # Página 4 - Proposta
            }
            
            # Canvas para visualização
            self.canvas = None
            self.current_page = 2  # Iniciar na página 2 (primeira editável)
            self.scale_factor = 1.0  # Escala real para melhor visualização
            
            # Dimensões reais do papel A4 em mm convertidas para pontos (1mm = 2.83 pontos)
            self.paper_width_mm = 210  # A4 width in mm
            self.paper_height_mm = 297  # A4 height in mm
            self.paper_width_pt = 595  # A4 width in points
            self.paper_height_pt = 842  # A4 height in points
            
            # Elemento selecionado
            self.selected_element = None
            self.drag_data = {}
            
            # Inicializar módulo base
            super().__init__(parent, user_id, role, main_window)
            
            # Inicializar banco de templates
            self.init_template_database()
            
            # Carregar template padrão
            self.load_default_template()
            
        except Exception as e:
            print(f"Erro ao inicializar Editor de Templates: {e}")
            self.create_error_interface(parent, str(e))
    
    def setup_ui(self):
        """Criar interface principal"""
        # Container principal
        main_container = tk.PanedWindow(self.frame, orient='horizontal', bg='#f8fafc')
        main_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Painel esquerdo - Controles
        self.create_control_panel(main_container)
        
        # Painel direito - Visualização
        self.create_preview_panel(main_container)
    
    def create_control_panel(self, parent):
        """Criar painel de controles"""
        control_frame = tk.Frame(parent, bg='#f8fafc', width=350)
        control_frame.pack_propagate(False)
        parent.add(control_frame)
        
        # Título
        title_label = tk.Label(control_frame, 
                              text="🎨 Editor de Templates PDF", 
                              font=('Arial', 16, 'bold'),
                              bg='#f8fafc', fg='#1e293b')
        title_label.pack(pady=(10, 20))
        
        # Gerenciamento de Templates
        self.create_template_manager(control_frame)
        
        # Seletor de páginas
        self.create_page_selector(control_frame)
        
        # Lista de elementos
        self.create_element_list(control_frame)
        
        # Propriedades do elemento
        self.create_element_properties(control_frame)
        
        # Botões de ação
        self.create_action_buttons(control_frame)
    
    def create_template_manager(self, parent):
        """Criar gerenciador de templates"""
        manager_frame = tk.LabelFrame(parent, text="📋 Templates", 
                                     font=('Arial', 11, 'bold'),
                                     bg='#f8fafc', fg='#374151')
        manager_frame.pack(fill="x", padx=10, pady=(0, 15))
        
        # Combobox para templates
        template_frame = tk.Frame(manager_frame, bg='#f8fafc')
        template_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(template_frame, text="Template:", 
                font=('Arial', 10), bg='#f8fafc').pack(side="left")
        
        self.template_var = tk.StringVar()
        self.template_combo = ttk.Combobox(template_frame, textvariable=self.template_var,
                                          width=25, state="readonly")
        self.template_combo.pack(side="left", padx=(5, 0), fill="x", expand=True)
        self.template_combo.bind('<<ComboboxSelected>>', self.on_template_selected)
        
        # Botões
        button_frame = tk.Frame(manager_frame, bg='#f8fafc')
        button_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        tk.Button(button_frame, text="📁 Novo", command=self.create_new_template,
                 bg='#10b981', fg='white', font=('Arial', 9, 'bold')).pack(side="left", padx=(0, 5))
        
        tk.Button(button_frame, text="💾 Salvar", command=self.save_template,
                 bg='#3b82f6', fg='white', font=('Arial', 9, 'bold')).pack(side="left", padx=(0, 5))
        
        tk.Button(button_frame, text="🗑️ Excluir", command=self.delete_template,
                 bg='#ef4444', fg='white', font=('Arial', 9, 'bold')).pack(side="left")
        
        # Carregar templates
        self.load_template_list()
    
    def create_page_selector(self, parent):
        """Criar seletor de páginas"""
        page_frame = tk.LabelFrame(parent, text="📄 Páginas", 
                                  font=('Arial', 11, 'bold'),
                                  bg='#f8fafc', fg='#374151')
        page_frame.pack(fill="x", padx=10, pady=(0, 15))
        
        button_frame = tk.Frame(page_frame, bg='#f8fafc')
        button_frame.pack(padx=10, pady=10)
        
        # Botões das páginas
        pages = [
            (1, "📄 Capa", "#9ca3af", "Não editável"),
            (2, "📝 Introdução", "#3b82f6", "Editável"),
            (3, "🏢 Sobre Empresa", "#10b981", "Editável"),
            (4, "💰 Proposta", "#f59e0b", "Editável")
        ]
        
        for page_num, title, color, status in pages:
            btn = tk.Button(button_frame, text=f"{title}\n({status})",
                           command=lambda p=page_num: self.select_page(p),
                           bg=color, fg='white', font=('Arial', 9, 'bold'),
                           width=12, height=2)
            btn.pack(pady=2)
            
            if page_num == self.current_page:
                btn.config(relief='sunken')
        
        # Status da página atual
        self.page_status = tk.Label(page_frame, text=f"Página atual: {self.current_page}",
                                   font=('Arial', 10), bg='#f8fafc', fg='#6b7280')
        self.page_status.pack(pady=(0, 10))
    
    def create_element_list(self, parent):
        """Criar lista de elementos da página"""
        list_frame = tk.LabelFrame(parent, text="🧩 Elementos da Página", 
                                  font=('Arial', 11, 'bold'),
                                  bg='#f8fafc', fg='#374151')
        list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 15))
        
        # Listbox com scrollbar
        list_container = tk.Frame(list_frame, bg='#f8fafc')
        list_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.element_listbox = tk.Listbox(list_container, font=('Arial', 9),
                                         selectmode='single', height=8)
        scrollbar = ttk.Scrollbar(list_container, orient="vertical", 
                                 command=self.element_listbox.yview)
        self.element_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.element_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.element_listbox.bind('<<ListboxSelect>>', self.on_element_selected)
        
        # Botões de elemento
        elem_buttons = tk.Frame(list_frame, bg='#f8fafc')
        elem_buttons.pack(fill="x", padx=10, pady=(0, 10))
        
        tk.Button(elem_buttons, text="➕ Adicionar", command=self.add_element,
                 bg='#10b981', fg='white', font=('Arial', 9, 'bold')).pack(side="left", padx=(0, 5))
        
        tk.Button(elem_buttons, text="🗑️ Remover", command=self.remove_element,
                 bg='#ef4444', fg='white', font=('Arial', 9, 'bold')).pack(side="left")
    
    def create_element_properties(self, parent):
        """Criar painel de propriedades do elemento"""
        props_frame = tk.LabelFrame(parent, text="⚙️ Propriedades", 
                                   font=('Arial', 11, 'bold'),
                                   bg='#f8fafc', fg='#374151')
        props_frame.pack(fill="x", padx=10, pady=(0, 15))
        
        # Container com scroll
        self.props_container = tk.Frame(props_frame, bg='white')
        self.props_container.pack(fill="x", padx=10, pady=10)
        
        # Placeholder
        tk.Label(self.props_container, text="Selecione um elemento",
                font=('Arial', 10), bg='white', fg='#6b7280').pack(pady=20)
    
    def create_action_buttons(self, parent):
        """Criar botões de ação"""
        button_frame = tk.Frame(parent, bg='#f8fafc')
        button_frame.pack(fill="x", padx=10, pady=10)
        
        # Controles de zoom
        zoom_frame = tk.Frame(button_frame, bg='#f8fafc')
        zoom_frame.pack(side="left", padx=(0, 10))
        
        tk.Label(zoom_frame, text="Zoom:", font=('Arial', 9),
                bg='#f8fafc').pack(side="left")
        
        tk.Button(zoom_frame, text="🔍-", command=self.zoom_out,
                 bg='#6b7280', fg='white', font=('Arial', 8, 'bold')).pack(side="left", padx=(5, 2))
        
        self.zoom_label = tk.Label(zoom_frame, text="80%", font=('Arial', 9),
                                  bg='#f8fafc', width=4)
        self.zoom_label.pack(side="left", padx=2)
        
        tk.Button(zoom_frame, text="🔍+", command=self.zoom_in,
                 bg='#6b7280', fg='white', font=('Arial', 8, 'bold')).pack(side="left", padx=(2, 5))
        
        tk.Button(button_frame, text="🔄 Recarregar", command=self.reload_preview,
                 bg='#6b7280', fg='white', font=('Arial', 10, 'bold')).pack(side="left", padx=(0, 5))
        
        tk.Button(button_frame, text="📋 Mapear PDF", command=self.map_existing_pdf,
                 bg='#8b5cf6', fg='white', font=('Arial', 10, 'bold')).pack(side="right")
    
    def create_preview_panel(self, parent):
        """Criar painel de visualização"""
        preview_frame = tk.Frame(parent, bg='white', relief='sunken', bd=2)
        parent.add(preview_frame)
        
        # Título
        preview_title = tk.Label(preview_frame, 
                               text="🔍 Visualização da Página",
                               font=('Arial', 14, 'bold'),
                               bg='white', fg='#1e293b')
        preview_title.pack(pady=10)
        
        # Canvas para visualização
        canvas_frame = tk.Frame(preview_frame, bg='white')
        canvas_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Canvas com barras de rolagem (proporção A4 real)
        canvas_width = int(self.paper_width_pt * 0.8)  # 476px para largura A4
        canvas_height = int(self.paper_height_pt * 0.8)  # 674px para altura A4
        self.canvas = tk.Canvas(canvas_frame, bg='white', relief='solid', bd=2,
                               width=canvas_width, height=canvas_height)
        
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient="horizontal", 
                                   command=self.canvas.xview)
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", 
                                   command=self.canvas.yview)
        
        self.canvas.configure(xscrollcommand=h_scrollbar.set,
                             yscrollcommand=v_scrollbar.set)
        
        # Grid layout
        self.canvas.grid(row=0, column=0, sticky="nsew")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)
        
        # Eventos do canvas
        self.canvas.bind('<Button-1>', self.on_canvas_click)
        self.canvas.bind('<B1-Motion>', self.on_canvas_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_canvas_release)
        
        # Configurar scroll region
        self.canvas.configure(scrollregion=(0, 0, 595, 842))  # A4 em pontos
        
        # Desenhar página inicial
        self.draw_page()
    
    def init_template_database(self):
        """Inicializar banco de dados para templates"""
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            
            # Tabela de templates
            c.execute("""
                CREATE TABLE IF NOT EXISTS pdf_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    template_data TEXT,
                    created_by INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (created_by) REFERENCES usuarios (id)
                )
            """)
            
            # Tabela de elementos dos templates
            c.execute("""
                CREATE TABLE IF NOT EXISTS pdf_template_elements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    template_id INTEGER,
                    page_number INTEGER,
                    element_type TEXT,
                    element_data TEXT,
                    position_x REAL,
                    position_y REAL,
                    width REAL,
                    height REAL,
                    font_family TEXT DEFAULT 'Arial',
                    font_size INTEGER DEFAULT 11,
                    font_style TEXT DEFAULT 'normal',
                    color TEXT DEFAULT '#000000',
                    z_index INTEGER DEFAULT 0,
                    FOREIGN KEY (template_id) REFERENCES pdf_templates (id)
                )
            """)
            
            conn.commit()
            
        except Exception as e:
            print(f"Erro ao inicializar banco de templates: {e}")
        finally:
            if 'conn' in locals():
                conn.close()
    
    def load_default_template(self):
        """Carregar template padrão baseado no PDF atual com proporções A4 corretas"""
        try:
            # Mapear elementos do PDF atual com coordenadas proporcionais ao A4 (595x842 pontos)
            self.template_data = {
                "name": "Template Padrão",
                "description": "Template baseado no gerador atual - Layout A4",
                "pages": {
                    # Página 1 - Capa (não editável)
                    "1": {
                        "editable": False,
                        "elements": []
                    },
                    
                    # Página 2 - Introdução (sem cabeçalho, apenas rodapé)
                    "2": {
                        "editable": True,
                        "has_header": False,
                        "has_footer": True,
                        "elements": [
                            # LOGO CENTRAL
                            {
                                "id": "logo_empresa",
                                "type": "image",
                                "label": "Logo da Empresa",
                                "x": 250, "y": 80, "w": 95, "h": 60,
                                "data_type": "fixed",
                                "content": "assets/logos/world_comp_brasil.jpg"
                            },
                            
                            # SEÇÃO CLIENTE (COLUNA ESQUERDA)
                            {
                                "id": "apresentado_para_titulo",
                                "type": "text",
                                "label": "Título 'Apresentado Para'",
                                "x": 40, "y": 200, "w": 240, "h": 25,
                                "data_type": "fixed",
                                "content": "APRESENTADO PARA:",
                                "font_family": "Arial",
                                "font_size": 14,
                                "font_style": "bold"
                            },
                            {
                                "id": "cliente_nome",
                                "type": "text",
                                "label": "Nome do Cliente",
                                "x": 40, "y": 235, "w": 240, "h": 30,
                                "data_type": "dynamic",
                                "field_options": ["cliente_nome", "cliente_nome_fantasia"],
                                "current_field": "cliente_nome",
                                "font_family": "Arial",
                                "font_size": 16,
                                "font_style": "bold"
                            },
                            {
                                "id": "cliente_cnpj",
                                "type": "text",
                                "label": "CNPJ do Cliente",
                                "x": 40, "y": 275, "w": 240, "h": 25,
                                "data_type": "dynamic",
                                "field_options": ["cliente_cnpj", "cliente_cpf"],
                                "current_field": "cliente_cnpj",
                                "content_template": "CNPJ: {value}",
                                "font_family": "Arial",
                                "font_size": 12,
                                "font_style": "normal"
                            },
                            {
                                "id": "cliente_telefone",
                                "type": "text",
                                "label": "Telefone do Cliente",
                                "x": 40, "y": 310, "w": 240, "h": 25,
                                "data_type": "dynamic",
                                "field_options": ["cliente_telefone", "contato_telefone"],
                                "current_field": "cliente_telefone",
                                "content_template": "Telefone: {value}",
                                "font_family": "Arial",
                                "font_size": 12,
                                "font_style": "normal"
                            },
                            {
                                "id": "contato_pessoa",
                                "type": "text",
                                "label": "Pessoa de Contato",
                                "x": 40, "y": 345, "w": 240, "h": 25,
                                "data_type": "dynamic",
                                "field_options": ["contato_nome", "cliente_responsavel"],
                                "current_field": "contato_nome",
                                "content_template": "Contato: {value}",
                                "font_family": "Arial",
                                "font_size": 12,
                                "font_style": "normal"
                            },
                            
                            # SEÇÃO NOSSA EMPRESA (COLUNA DIREITA)
                            {
                                "id": "nossa_empresa_titulo",
                                "type": "text",
                                "label": "Título Nossa Empresa",
                                "x": 315, "y": 200, "w": 240, "h": 25,
                                "data_type": "fixed",
                                "content": "NOSSA EMPRESA:",
                                "font_family": "Arial",
                                "font_size": 14,
                                "font_style": "bold"
                            },
                            {
                                "id": "nossa_empresa_nome",
                                "type": "text",
                                "label": "Nome da Nossa Empresa",
                                "x": 315, "y": 235, "w": 240, "h": 30,
                                "data_type": "dynamic",
                                "field_options": ["filial_nome", "empresa_nome"],
                                "current_field": "filial_nome",
                                "font_family": "Arial",
                                "font_size": 16,
                                "font_style": "bold"
                            },
                            {
                                "id": "nossa_empresa_cnpj",
                                "type": "text",
                                "label": "CNPJ da Nossa Empresa",
                                "x": 315, "y": 275, "w": 240, "h": 25,
                                "data_type": "dynamic",
                                "field_options": ["filial_cnpj", "empresa_cnpj"],
                                "current_field": "filial_cnpj",
                                "content_template": "CNPJ: {value}",
                                "font_family": "Arial",
                                "font_size": 12,
                                "font_style": "normal"
                            },
                            {
                                "id": "nossa_empresa_telefones",
                                "type": "text",
                                "label": "Telefones da Nossa Empresa",
                                "x": 315, "y": 310, "w": 240, "h": 25,
                                "data_type": "dynamic",
                                "field_options": ["filial_telefones", "empresa_telefones"],
                                "current_field": "filial_telefones",
                                "content_template": "Telefone: {value}",
                                "font_family": "Arial",
                                "font_size": 12,
                                "font_style": "normal"
                            },
                            {
                                "id": "responsavel_email",
                                "type": "text",
                                "label": "Email do Responsável",
                                "x": 315, "y": 345, "w": 240, "h": 25,
                                "data_type": "dynamic",
                                "field_options": ["responsavel_email", "vendedor_email"],
                                "current_field": "responsavel_email",
                                "content_template": "Email: {value}",
                                "font_family": "Arial",
                                "font_size": 12,
                                "font_style": "normal"
                            },
                            
                            # RODAPÉ
                            {
                                "id": "rodape_linha",
                                "type": "line",
                                "label": "Linha do Rodapé",
                                "x": 40, "y": 760, "w": 515, "h": 2,
                                "data_type": "fixed",
                                "content": "line"
                            },
                            {
                                "id": "rodape_info",
                                "type": "text",
                                "label": "Informações do Rodapé",
                                "x": 40, "y": 775, "w": 515, "h": 25,
                                "data_type": "dynamic",
                                "field_options": ["numero_proposta", "codigo_proposta"],
                                "current_field": "numero_proposta",
                                "content_template": "Proposta: {value} | Página 2 - Introdução",
                                "font_family": "Arial",
                                "font_size": 10,
                                "font_style": "normal"
                            }
                        ]
                    },
                    
                    # Página 3 - Sobre a Empresa
                    "3": {
                        "editable": True,
                        "has_header": True,
                        "has_footer": True,
                        "elements": [
                            # CABEÇALHO
                            {
                                "id": "cabecalho_logo",
                                "type": "image",
                                "label": "Logo no Cabeçalho",
                                "x": 40, "y": 40, "w": 80, "h": 50,
                                "data_type": "fixed",
                                "content": "assets/logos/world_comp_brasil.jpg"
                            },
                            {
                                "id": "cabecalho_empresa",
                                "type": "text",
                                "label": "Nome da Empresa (Cabeçalho)",
                                "x": 140, "y": 50, "w": 300, "h": 30,
                                "data_type": "dynamic",
                                "field_options": ["filial_nome", "empresa_nome"],
                                "current_field": "filial_nome",
                                "font_family": "Arial",
                                "font_size": 16,
                                "font_style": "bold"
                            },
                            {
                                "id": "cabecalho_linha",
                                "type": "line",
                                "label": "Linha do Cabeçalho",
                                "x": 40, "y": 100, "w": 515, "h": 2,
                                "data_type": "fixed",
                                "content": "line"
                            },
                            
                            # CONTEÚDO PRINCIPAL
                            {
                                "id": "sobre_titulo",
                                "type": "text",
                                "label": "Título Sobre a Empresa",
                                "x": 40, "y": 140, "w": 515, "h": 35,
                                "data_type": "fixed",
                                "content": "SOBRE A WORLD COMP",
                                "font_family": "Arial",
                                "font_size": 18,
                                "font_style": "bold"
                            },
                            {
                                "id": "sobre_introducao",
                                "type": "text",
                                "label": "Introdução da Empresa",
                                "x": 40, "y": 190, "w": 515, "h": 50,
                                "data_type": "fixed",
                                "content": "Há mais de uma década no mercado de manutenção de compressores de ar de parafuso, de diversas marcas, atendemos clientes em todo território brasileiro.",
                                "font_family": "Arial",
                                "font_size": 12,
                                "font_style": "normal"
                            },
                            {
                                "id": "servicos_titulo",
                                "type": "text",
                                "label": "Título Serviços",
                                "x": 40, "y": 260, "w": 515, "h": 30,
                                "data_type": "fixed",
                                "content": "FORNECIMENTO, SERVIÇO E LOCAÇÃO",
                                "font_family": "Arial",
                                "font_size": 14,
                                "font_style": "bold"
                            },
                            {
                                "id": "servicos_texto",
                                "type": "text",
                                "label": "Descrição dos Serviços",
                                "x": 40, "y": 300, "w": 515, "h": 80,
                                "data_type": "fixed",
                                "content": "A World Comp oferece os serviços de Manutenção Preventiva e Corretiva em Compressores e Unidades Compressoras, Venda de peças, Locação de compressores, Recuperação de Unidades Compressoras.",
                                "font_family": "Arial",
                                "font_size": 12,
                                "font_style": "normal"
                            },
                            {
                                "id": "qualidade_titulo",
                                "type": "text",
                                "label": "Título Qualidade",
                                "x": 40, "y": 400, "w": 515, "h": 30,
                                "data_type": "fixed",
                                "content": "QUALIDADE DE SERVIÇOS",
                                "font_family": "Arial",
                                "font_size": 14,
                                "font_style": "bold"
                            },
                            {
                                "id": "qualidade_texto",
                                "type": "text",
                                "label": "Texto sobre Qualidade",
                                "x": 40, "y": 440, "w": 515, "h": 80,
                                "data_type": "fixed",
                                "content": "Com uma equipe de técnicos altamente qualificados e constantemente treinados para atendimentos em todos os modelos de compressores de ar, oferecemos garantia de excelente atendimento.",
                                "font_family": "Arial",
                                "font_size": 12,
                                "font_style": "normal"
                            },
                            {
                                "id": "missao_texto",
                                "type": "text",
                                "label": "Nossa Missão",
                                "x": 40, "y": 540, "w": 515, "h": 60,
                                "data_type": "fixed",
                                "content": "Nossa missão é ser sua melhor parceria com sinônimo de qualidade, garantia e o melhor custo benefício.",
                                "font_family": "Arial",
                                "font_size": 12,
                                "font_style": "italic"
                            },
                            
                            # RODAPÉ
                            {
                                "id": "rodape_linha",
                                "type": "line",
                                "label": "Linha do Rodapé",
                                "x": 40, "y": 760, "w": 515, "h": 2,
                                "data_type": "fixed",
                                "content": "line"
                            },
                            {
                                "id": "rodape_texto",
                                "type": "text",
                                "label": "Texto do Rodapé",
                                "x": 40, "y": 775, "w": 515, "h": 25,
                                "data_type": "fixed",
                                "content": "World Comp - Manutenção de Compressores | Página 3 - Sobre a Empresa",
                                "font_family": "Arial",
                                "font_size": 10,
                                "font_style": "normal"
                            }
                        ]
                    },
                    
                    # Página 4 - Proposta
                    "4": {
                        "editable": True,
                        "has_header": True,
                        "has_footer": True,
                        "elements": [
                            # CABEÇALHO
                            {
                                "id": "cabecalho_logo",
                                "type": "image",
                                "label": "Logo no Cabeçalho",
                                "x": 40, "y": 40, "w": 80, "h": 50,
                                "data_type": "fixed",
                                "content": "assets/logos/world_comp_brasil.jpg"
                            },
                            {
                                "id": "cabecalho_empresa",
                                "type": "text",
                                "label": "Nome da Empresa (Cabeçalho)",
                                "x": 140, "y": 50, "w": 300, "h": 30,
                                "data_type": "dynamic",
                                "field_options": ["filial_nome", "empresa_nome"],
                                "current_field": "filial_nome",
                                "font_family": "Arial",
                                "font_size": 16,
                                "font_style": "bold"
                            },
                            {
                                "id": "cabecalho_linha",
                                "type": "line",
                                "label": "Linha do Cabeçalho",
                                "x": 40, "y": 100, "w": 515, "h": 2,
                                "data_type": "fixed",
                                "content": "line"
                            },
                            
                            # TÍTULO DA PROPOSTA
                            {
                                "id": "proposta_titulo",
                                "type": "text",
                                "label": "Título da Proposta",
                                "x": 40, "y": 140, "w": 515, "h": 35,
                                "data_type": "dynamic",
                                "field_options": ["numero_proposta", "codigo_proposta"],
                                "current_field": "numero_proposta",
                                "content_template": "PROPOSTA Nº {value}",
                                "font_family": "Arial",
                                "font_size": 18,
                                "font_style": "bold"
                            },
                            
                            # DADOS DA PROPOSTA (LINHA 1)
                            {
                                "id": "data_proposta",
                                "type": "text",
                                "label": "Data da Proposta",
                                "x": 40, "y": 190, "w": 170, "h": 25,
                                "data_type": "dynamic",
                                "field_options": ["data_criacao", "data_proposta"],
                                "current_field": "data_criacao",
                                "content_template": "Data: {value}",
                                "font_family": "Arial",
                                "font_size": 12,
                                "font_style": "normal"
                            },
                            {
                                "id": "responsavel_proposta",
                                "type": "text",
                                "label": "Responsável pela Proposta",
                                "x": 225, "y": 190, "w": 160, "h": 25,
                                "data_type": "dynamic",
                                "field_options": ["responsavel_nome", "vendedor_nome"],
                                "current_field": "responsavel_nome",
                                "content_template": "Responsável: {value}",
                                "font_family": "Arial",
                                "font_size": 12,
                                "font_style": "normal"
                            },
                            {
                                "id": "telefone_responsavel",
                                "type": "text",
                                "label": "Telefone do Responsável",
                                "x": 400, "y": 190, "w": 155, "h": 25,
                                "data_type": "dynamic",
                                "field_options": ["responsavel_telefone", "empresa_telefone"],
                                "current_field": "responsavel_telefone",
                                "content_template": "Tel: {value}",
                                "font_family": "Arial",
                                "font_size": 12,
                                "font_style": "normal"
                            },
                            
                            # DADOS DO CLIENTE
                            {
                                "id": "dados_cliente_titulo",
                                "type": "text",
                                "label": "Título Dados do Cliente",
                                "x": 40, "y": 240, "w": 515, "h": 25,
                                "data_type": "fixed",
                                "content": "DADOS DO CLIENTE",
                                "font_family": "Arial",
                                "font_size": 14,
                                "font_style": "bold"
                            },
                            {
                                "id": "cliente_empresa",
                                "type": "text",
                                "label": "Nome da Empresa Cliente",
                                "x": 40, "y": 275, "w": 515, "h": 25,
                                "data_type": "dynamic",
                                "field_options": ["cliente_nome", "cliente_nome_fantasia"],
                                "current_field": "cliente_nome",
                                "content_template": "Empresa: {value}",
                                "font_family": "Arial",
                                "font_size": 12,
                                "font_style": "normal"
                            },
                            {
                                "id": "cliente_cnpj_proposta",
                                "type": "text",
                                "label": "CNPJ do Cliente",
                                "x": 40, "y": 305, "w": 250, "h": 25,
                                "data_type": "dynamic",
                                "field_options": ["cliente_cnpj", "cliente_cpf"],
                                "current_field": "cliente_cnpj",
                                "content_template": "CNPJ: {value}",
                                "font_family": "Arial",
                                "font_size": 12,
                                "font_style": "normal"
                            },
                            {
                                "id": "cliente_contato_proposta",
                                "type": "text",
                                "label": "Contato do Cliente",
                                "x": 305, "y": 305, "w": 250, "h": 25,
                                "data_type": "dynamic",
                                "field_options": ["contato_nome", "cliente_responsavel"],
                                "current_field": "contato_nome",
                                "content_template": "Contato: {value}",
                                "font_family": "Arial",
                                "font_size": 12,
                                "font_style": "normal"
                            },
                            
                            # DADOS DO COMPRESSOR
                            {
                                "id": "dados_compressor_titulo",
                                "type": "text",
                                "label": "Título Dados do Compressor",
                                "x": 40, "y": 355, "w": 515, "h": 25,
                                "data_type": "fixed",
                                "content": "DADOS DO COMPRESSOR",
                                "font_family": "Arial",
                                "font_size": 14,
                                "font_style": "bold"
                            },
                            {
                                "id": "modelo_compressor",
                                "type": "text",
                                "label": "Modelo do Compressor",
                                "x": 40, "y": 390, "w": 250, "h": 25,
                                "data_type": "dynamic",
                                "field_options": ["modelo_compressor", "tipo_compressor"],
                                "current_field": "modelo_compressor",
                                "content_template": "Modelo: {value}",
                                "font_family": "Arial",
                                "font_size": 12,
                                "font_style": "normal"
                            },
                            {
                                "id": "serie_compressor",
                                "type": "text",
                                "label": "Número de Série",
                                "x": 305, "y": 390, "w": 250, "h": 25,
                                "data_type": "dynamic",
                                "field_options": ["numero_serie_compressor", "serie_equipamento"],
                                "current_field": "numero_serie_compressor",
                                "content_template": "Nº de Série: {value}",
                                "font_family": "Arial",
                                "font_size": 12,
                                "font_style": "normal"
                            },
                            
                            # DESCRIÇÃO DO SERVIÇO
                            {
                                "id": "descricao_titulo",
                                "type": "text",
                                "label": "Título Descrição",
                                "x": 40, "y": 440, "w": 515, "h": 25,
                                "data_type": "fixed",
                                "content": "DESCRIÇÃO DO SERVIÇO",
                                "font_family": "Arial",
                                "font_size": 14,
                                "font_style": "bold"
                            },
                            {
                                "id": "descricao_atividade",
                                "type": "text",
                                "label": "Descrição da Atividade",
                                "x": 40, "y": 475, "w": 515, "h": 80,
                                "data_type": "dynamic",
                                "field_options": ["descricao_atividade", "servicos_inclusos"],
                                "current_field": "descricao_atividade",
                                "font_family": "Arial",
                                "font_size": 12,
                                "font_style": "normal"
                            },
                            
                            # ITENS DA PROPOSTA
                            {
                                "id": "itens_titulo",
                                "type": "text",
                                "label": "Título Itens da Proposta",
                                "x": 40, "y": 580, "w": 515, "h": 35,
                                "data_type": "fixed",
                                "content": "ITENS DA PROPOSTA",
                                "font_family": "Arial",
                                "font_size": 16,
                                "font_style": "bold"
                            },
                            
                            # RODAPÉ
                            {
                                "id": "rodape_linha",
                                "type": "line",
                                "label": "Linha do Rodapé",
                                "x": 40, "y": 760, "w": 515, "h": 2,
                                "data_type": "fixed",
                                "content": "line"
                            },
                            {
                                "id": "rodape_texto",
                                "type": "text",
                                "label": "Texto do Rodapé",
                                "x": 40, "y": 775, "w": 515, "h": 25,
                                "data_type": "fixed",
                                "content": "World Comp - Manutenção de Compressores | Página 4 - Proposta",
                                "font_family": "Arial",
                                "font_size": 10,
                                "font_style": "normal"
                            }
                        ]
                    }
                }
            }
            
            self.current_page = 2
            self.select_page(self.current_page)
            
        except Exception as e:
            print(f"Erro ao carregar template padrão: {e}")
            messagebox.showerror("Erro", f"Erro ao carregar template: {e}")
    
    def select_page(self, page_num):
        """Selecionar página para edição"""
        if page_num == 1:
            messagebox.showinfo("Página Bloqueada", 
                "A página 1 (Capa) não é editável.\nEla é configurada por template externo.")
            return
        
        self.current_page = page_num
        self.update_page_buttons()
        self.update_element_list()
        self.draw_page()
        
        self.page_status.config(text=f"Página atual: {page_num}")
    
    def update_page_buttons(self):
        """Atualizar botões de página"""
        # Redesenhar seletor de páginas
        # (Simplificado - em implementação real, atualizaria apenas o estado dos botões)
        pass
    
    def update_element_list(self):
        """Atualizar lista de elementos da página atual"""
        self.element_listbox.delete(0, tk.END)
        
        if str(self.current_page) in self.template_data.get("pages", {}):
            page_data = self.template_data["pages"][str(self.current_page)]
            elements = page_data.get("elements", [])
            
            for element in elements:
                display_text = f"{element.get('label', element.get('id'))}"
                if element.get('data_type') == 'dynamic':
                    display_text += " 📊"
                else:
                    display_text += " 📝"
                
                self.element_listbox.insert(tk.END, display_text)
    
    def draw_page(self):
        """Desenhar página no canvas"""
        self.canvas.delete("all")
        
        # Usar dimensões reais A4 com escala
        page_width = self.paper_width_pt * self.scale_factor
        page_height = self.paper_height_pt * self.scale_factor
        
        # Desenhar fundo da página com margem visual
        margin = 20
        self.canvas.create_rectangle(margin, margin, margin + page_width, margin + page_height,
                                   fill='white', outline='#2563eb', width=3,
                                   tags='page_background')
        
        # Desenhar margens de segurança
        margin_size = 40 * self.scale_factor
        self.canvas.create_rectangle(margin + margin_size, margin + margin_size, 
                                   margin + page_width - margin_size, margin + page_height - margin_size,
                                   fill='', outline='#94a3b8', width=1, dash=(5, 5),
                                   tags='page_margins')
        
        # Desenhar elementos da página atual
        if str(self.current_page) in self.template_data.get("pages", {}):
            page_data = self.template_data["pages"][str(self.current_page)]
            elements = page_data.get("elements", [])
            
            for i, element in enumerate(elements):
                self.draw_element(element, i)
        
        # Informações da página com detalhes de cabeçalho/rodapé
        page_data = self.template_data.get("pages", {}).get(str(self.current_page), {})
        has_header = page_data.get("has_header", False)
        has_footer = page_data.get("has_footer", False)
        
        page_info = f"Página {self.current_page}"
        if self.current_page == 2:
            page_info += " - Introdução"
        elif self.current_page == 3:
            page_info += " - Sobre a Empresa"
        elif self.current_page == 4:
            page_info += " - Proposta"
        
        # Adicionar informações de cabeçalho/rodapé
        layout_info = []
        if has_header:
            layout_info.append("📄 Cabeçalho")
        if has_footer:
            layout_info.append("📑 Rodapé")
        
        if layout_info:
            page_info += f" ({', '.join(layout_info)})"
        else:
            page_info += " (sem cabeçalho/rodapé)"
        
        margin = 20
        self.canvas.create_text(margin + page_width/2, margin + page_height + 30,
                               text=page_info, font=('Arial', 12, 'bold'),
                               fill='#1e293b', tags='page_info')
        
        # Adicionar contagem de elementos
        element_count = len(page_data.get("elements", []))
        count_info = f"{element_count} elementos mapeados"
        self.canvas.create_text(margin + page_width/2, margin + page_height + 50,
                               text=count_info, font=('Arial', 10),
                               fill='#64748b', tags='page_info')
        
        # Legenda em colunas
        legend_y = margin + page_height + 80
        col1_x = margin + 20
        col2_x = margin + 200
        col3_x = margin + 400
        
        self.canvas.create_text(col1_x, legend_y,
                               text="LEGENDA:", font=('Arial', 10, 'bold'),
                               fill='#1e293b', anchor='w', tags='page_info')
        
        self.canvas.create_text(col1_x, legend_y + 20,
                               text="📊 Dados Dinâmicos", 
                               font=('Arial', 10), fill='#3b82f6', anchor='w', tags='page_info')
        
        self.canvas.create_text(col2_x, legend_y + 20,
                               text="📝 Dados Fixos", 
                               font=('Arial', 10), fill='#10b981', anchor='w', tags='page_info')
        
        self.canvas.create_text(col3_x, legend_y + 20,
                               text="🔗 Separadores", 
                               font=('Arial', 10), fill='#6b7280', anchor='w', tags='page_info')
        
        # Atualizar scroll region
        self.canvas.configure(scrollregion=(0, 0, margin + page_width + 40, legend_y + 50))
    
    def draw_element(self, element, index):
        """Desenhar elemento no canvas"""
        # Margem da página
        margin = 20
        
        # Coordenadas escaladas com margem
        x = margin + (element['x'] * self.scale_factor)
        y = margin + (element['y'] * self.scale_factor)
        w = element['w'] * self.scale_factor
        h = element['h'] * self.scale_factor
        
        # Cor baseada no tipo de dados
        if element.get('data_type') == 'dynamic':
            fill_color = '#dbeafe'  # Azul claro
            border_color = '#3b82f6'  # Azul
            text_color = '#1e40af'
        else:
            fill_color = '#dcfce7'  # Verde claro
            border_color = '#10b981'  # Verde
            text_color = '#047857'
        
        # Tratamento especial para linhas
        if element.get('type') == 'line':
            # Desenhar linha
            line_id = self.canvas.create_line(x, y + h/2, x + w, y + h/2,
                                            fill=border_color, width=2,
                                            tags=f'element_{index}')
            # Texto pequeno para identificar
            text_id = self.canvas.create_text(x + w/2, y + h/2 - 8,
                                            text="🔗 Linha",
                                            font=('Arial', 8),
                                            fill=text_color,
                                            tags=f'element_{index}')
        else:
            # Retângulo do elemento
            rect_id = self.canvas.create_rectangle(x, y, x + w, y + h,
                                                 fill=fill_color, outline=border_color,
                                                 width=1, tags=f'element_{index}')
            
            # Determinar conteúdo a exibir
            if element.get('data_type') == 'dynamic':
                # Para campos dinâmicos, mostrar exemplo com template
                template = element.get('content_template', '{value}')
                field_name = element.get('current_field', 'campo')
                sample_value = self.get_sample_value(field_name)
                display_content = template.format(value=sample_value)
                icon = "📊"
            else:
                # Para campos fixos, mostrar conteúdo atual
                display_content = element.get('content', element.get('label', ''))
                icon = "📝"
            
            # Texto principal (conteúdo real) - tamanho mais legível
            base_font_size = element.get('font_size', 12)
            font_size = max(10, int(base_font_size * self.scale_factor * 0.9))
            
            # Se o texto for muito longo, quebrar em linhas
            words = display_content.split()
            lines = []
            current_line = ""
            
            for word in words:
                test_line = f"{current_line} {word}".strip()
                if len(test_line) * font_size * 0.6 > w - 4:  # Aproximação de largura
                    if current_line:
                        lines.append(current_line)
                        current_line = word
                    else:
                        lines.append(word)
                else:
                    current_line = test_line
            
            if current_line:
                lines.append(current_line)
            
            # Limitar número de linhas baseado na altura
            max_lines = max(1, int(h / (font_size + 2)))
            lines = lines[:max_lines]
            
            # Desenhar texto linha por linha
            for i, line in enumerate(lines):
                line_y = y + (h / len(lines)) * (i + 0.5)
                text_id = self.canvas.create_text(x + w/2, line_y,
                                                text=line,
                                                font=('Arial', font_size),
                                                fill=text_color,
                                                width=w-4,
                                                tags=f'element_{index}')
            
            # Ícone pequeno no canto para indicar tipo
            icon_size = max(8, int(font_size * 0.8))
            icon_id = self.canvas.create_text(x + 2, y + 2,
                                            text=icon,
                                            font=('Arial', icon_size),
                                            fill=border_color,
                                            anchor='nw',
                                            tags=f'element_{index}')
    
    def get_sample_value(self, field_name):
        """Obter valor de exemplo para campo dinâmico"""
        samples = {
            'cliente_nome': 'EMPRESA EXEMPLO LTDA',
            'cliente_nome_fantasia': 'Exemplo Corp',
            'cliente_cnpj': '12.345.678/0001-90',
            'cliente_telefone': '(11) 3456-7890',
            'numero_proposta': 'PROP-2024-001',
            'data_criacao': '15/01/2024',
            'responsavel_nome': 'João Silva',
            'responsavel_telefone': '(11) 98765-4321',
            'responsavel_email': 'joao@worldcomp.com.br',
            'filial_nome': 'WORLD COMP BRASIL',
            'filial_cnpj': '98.765.432/0001-10',
            'filial_telefones': '(11) 1234-5678',
            'contato_nome': 'Maria Santos',
            'modelo_compressor': 'Atlas Copco GA15',
            'numero_serie_compressor': 'AC2024001',
            'descricao_atividade': 'Manutenção preventiva e corretiva do sistema de ar comprimido, incluindo troca de filtros, óleos e verificação geral.',
            'valor_total': 'R$ 15.500,00'
        }
        return samples.get(field_name, f'[{field_name}]')
    
    def on_canvas_click(self, event):
        """Evento de clique no canvas"""
        clicked_item = self.canvas.find_closest(event.x, event.y)[0]
        
        # Verificar se clicou em um elemento
        tags = self.canvas.gettags(clicked_item)
        for tag in tags:
            if tag.startswith('element_'):
                element_index = int(tag.split('_')[1])
                self.select_element(element_index)
                self.drag_data = {'x': event.x, 'y': event.y, 'element': element_index}
                break
    
    def on_canvas_drag(self, event):
        """Evento de arrastar no canvas"""
        if 'element' in self.drag_data:
            dx = event.x - self.drag_data['x']
            dy = event.y - self.drag_data['y']
            
            # Mover elemento no canvas
            element_index = self.drag_data['element']
            self.canvas.move(f'element_{element_index}', dx, dy)
            
            self.drag_data['x'] = event.x
            self.drag_data['y'] = event.y
    
    def on_canvas_release(self, event):
        """Evento de soltar no canvas"""
        if 'element' in self.drag_data:
            element_index = self.drag_data['element']
            
            # Atualizar posição no template_data
            if str(self.current_page) in self.template_data.get("pages", {}):
                elements = self.template_data["pages"][str(self.current_page)]["elements"]
                if element_index < len(elements):
                    # Calcular nova posição
                    coords = self.canvas.coords(f'element_{element_index}')
                    if coords:
                        new_x = (coords[0] - 10) / self.scale_factor
                        new_y = (coords[1] - 10) / self.scale_factor
                        
                        elements[element_index]['x'] = new_x
                        elements[element_index]['y'] = new_y
            
            self.drag_data = {}
    
    def select_element(self, element_index):
        """Selecionar elemento"""
        self.selected_element = element_index
        self.element_listbox.selection_clear(0, tk.END)
        self.element_listbox.selection_set(element_index)
        self.update_properties_panel()
    
    def on_element_selected(self, event):
        """Quando elemento é selecionado na lista"""
        selection = self.element_listbox.curselection()
        if selection:
            self.selected_element = selection[0]
            self.update_properties_panel()
    
    def update_properties_panel(self):
        """Atualizar painel de propriedades"""
        # Limpar container
        for widget in self.props_container.winfo_children():
            widget.destroy()
        
        if self.selected_element is None:
            tk.Label(self.props_container, text="Selecione um elemento",
                    font=('Arial', 10), bg='white', fg='#6b7280').pack(pady=20)
            return
        
        # Obter elemento selecionado
        if str(self.current_page) not in self.template_data.get("pages", {}):
            return
        
        elements = self.template_data["pages"][str(self.current_page)]["elements"]
        if self.selected_element >= len(elements):
            return
        
        element = elements[self.selected_element]
        
        # Título
        title_frame = tk.Frame(self.props_container, bg='white')
        title_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(title_frame, text=f"📝 {element.get('label', element.get('id'))}",
                font=('Arial', 11, 'bold'), bg='white').pack()
        
        # Tipo de dados
        type_frame = tk.Frame(self.props_container, bg='white')
        type_frame.pack(fill="x", pady=5)
        
        data_type = element.get('data_type', 'fixed')
        type_color = '#3b82f6' if data_type == 'dynamic' else '#10b981'
        type_text = '📊 Dinâmico' if data_type == 'dynamic' else '📝 Fixo'
        
        tk.Label(type_frame, text="Tipo:", font=('Arial', 10, 'bold'), 
                bg='white').pack(side="left")
        tk.Label(type_frame, text=type_text, font=('Arial', 10),
                bg='white', fg=type_color).pack(side="left", padx=(5, 0))
        
        # Propriedades específicas
        if data_type == 'dynamic':
            self.create_dynamic_properties(element)
        else:
            self.create_fixed_properties(element)
        
        # Propriedades de fonte
        self.create_font_properties(element)
        
        # Posição e tamanho
        self.create_position_properties(element)
    
    def create_dynamic_properties(self, element):
        """Criar propriedades para elementos dinâmicos"""
        # Campo atual
        field_frame = tk.Frame(self.props_container, bg='white')
        field_frame.pack(fill="x", pady=5)
        
        tk.Label(field_frame, text="Campo:", font=('Arial', 10, 'bold'),
                bg='white').pack(anchor='w')
        
        current_field = element.get('current_field', '')
        field_options = element.get('field_options', [current_field])
        
        self.field_var = tk.StringVar(value=current_field)
        field_combo = ttk.Combobox(field_frame, textvariable=self.field_var,
                                  values=field_options, state="readonly")
        field_combo.pack(fill="x", pady=(2, 0))
        field_combo.bind('<<ComboboxSelected>>', 
                        lambda e: self.update_element_field())
    
    def create_fixed_properties(self, element):
        """Criar propriedades para elementos fixos"""
        # Conteúdo
        content_frame = tk.Frame(self.props_container, bg='white')
        content_frame.pack(fill="x", pady=5)
        
        tk.Label(content_frame, text="Conteúdo:", font=('Arial', 10, 'bold'),
                bg='white').pack(anchor='w')
        
        self.content_var = tk.StringVar(value=element.get('content', ''))
        content_entry = tk.Entry(content_frame, textvariable=self.content_var,
                                font=('Arial', 10))
        content_entry.pack(fill="x", pady=(2, 0))
        content_entry.bind('<KeyRelease>', lambda e: self.update_element_content())
    
    def create_font_properties(self, element):
        """Criar propriedades de fonte"""
        font_frame = tk.LabelFrame(self.props_container, text="🔤 Fonte",
                                  font=('Arial', 10, 'bold'), bg='white')
        font_frame.pack(fill="x", pady=10)
        
        # Família da fonte
        family_frame = tk.Frame(font_frame, bg='white')
        family_frame.pack(fill="x", padx=5, pady=2)
        
        tk.Label(family_frame, text="Família:", font=('Arial', 9),
                bg='white').pack(side="left")
        
        self.font_family_var = tk.StringVar(value=element.get('font_family', 'Arial'))
        font_families = ['Arial', 'Times', 'Courier', 'Helvetica']
        family_combo = ttk.Combobox(family_frame, textvariable=self.font_family_var,
                                   values=font_families, width=10)
        family_combo.pack(side="right")
        family_combo.bind('<<ComboboxSelected>>', lambda e: self.update_font_properties())
        
        # Tamanho da fonte
        size_frame = tk.Frame(font_frame, bg='white')
        size_frame.pack(fill="x", padx=5, pady=2)
        
        tk.Label(size_frame, text="Tamanho:", font=('Arial', 9),
                bg='white').pack(side="left")
        
        self.font_size_var = tk.StringVar(value=str(element.get('font_size', 11)))
        size_spinbox = tk.Spinbox(size_frame, textvariable=self.font_size_var,
                                 from_=6, to=72, width=8,
                                 command=self.update_font_properties)
        size_spinbox.pack(side="right")
        
        # Estilo da fonte
        style_frame = tk.Frame(font_frame, bg='white')
        style_frame.pack(fill="x", padx=5, pady=2)
        
        tk.Label(style_frame, text="Estilo:", font=('Arial', 9),
                bg='white').pack(side="left")
        
        self.font_style_var = tk.StringVar(value=element.get('font_style', 'normal'))
        styles = ['normal', 'bold', 'italic', 'bold italic']
        style_combo = ttk.Combobox(style_frame, textvariable=self.font_style_var,
                                  values=styles, width=10)
        style_combo.pack(side="right")
        style_combo.bind('<<ComboboxSelected>>', lambda e: self.update_font_properties())
    
    def create_position_properties(self, element):
        """Criar propriedades de posição"""
        pos_frame = tk.LabelFrame(self.props_container, text="📍 Posição & Tamanho",
                                 font=('Arial', 10, 'bold'), bg='white')
        pos_frame.pack(fill="x", pady=10)
        
        # X, Y, W, H
        coords = [
            ('X:', element.get('x', 0)),
            ('Y:', element.get('y', 0)),
            ('W:', element.get('w', 100)),
            ('H:', element.get('h', 20))
        ]
        
        self.pos_vars = {}
        for i, (label, value) in enumerate(coords):
            row_frame = tk.Frame(pos_frame, bg='white')
            row_frame.pack(fill="x", padx=5, pady=2)
            
            tk.Label(row_frame, text=label, font=('Arial', 9),
                    bg='white', width=3).pack(side="left")
            
            var_name = ['x', 'y', 'w', 'h'][i]
            self.pos_vars[var_name] = tk.StringVar(value=str(value))
            
            spinbox = tk.Spinbox(row_frame, textvariable=self.pos_vars[var_name],
                               from_=0, to=1000, width=8,
                               command=self.update_position_properties)
            spinbox.pack(side="right")
    
    def update_element_field(self):
        """Atualizar campo do elemento dinâmico"""
        if self.selected_element is not None:
            elements = self.template_data["pages"][str(self.current_page)]["elements"]
            elements[self.selected_element]['current_field'] = self.field_var.get()
            self.draw_page()
    
    def update_element_content(self):
        """Atualizar conteúdo do elemento fixo"""
        if self.selected_element is not None:
            elements = self.template_data["pages"][str(self.current_page)]["elements"]
            elements[self.selected_element]['content'] = self.content_var.get()
            self.draw_page()
    
    def update_font_properties(self):
        """Atualizar propriedades de fonte"""
        if self.selected_element is not None:
            elements = self.template_data["pages"][str(self.current_page)]["elements"]
            element = elements[self.selected_element]
            
            element['font_family'] = self.font_family_var.get()
            element['font_size'] = int(self.font_size_var.get())
            element['font_style'] = self.font_style_var.get()
            
            self.draw_page()
    
    def update_position_properties(self):
        """Atualizar propriedades de posição"""
        if self.selected_element is not None:
            elements = self.template_data["pages"][str(self.current_page)]["elements"]
            element = elements[self.selected_element]
            
            element['x'] = float(self.pos_vars['x'].get())
            element['y'] = float(self.pos_vars['y'].get())
            element['w'] = float(self.pos_vars['w'].get())
            element['h'] = float(self.pos_vars['h'].get())
            
            self.draw_page()
    
    def add_element(self):
        """Adicionar novo elemento"""
        if self.current_page == 1:
            messagebox.showwarning("Página Bloqueada", "Não é possível adicionar elementos na capa.")
            return
        
        # Diálogo para escolher tipo de elemento
        element_window = tk.Toplevel(self.frame)
        element_window.title("Adicionar Elemento")
        element_window.geometry("400x300")
        element_window.transient(self.frame)
        element_window.grab_set()
        
        # Centralizar janela
        element_window.update_idletasks()
        x = (element_window.winfo_screenwidth() // 2) - (400 // 2)
        y = (element_window.winfo_screenheight() // 2) - (300 // 2)
        element_window.geometry(f"400x300+{x}+{y}")
        
        tk.Label(element_window, text="Tipo de Elemento:",
                font=('Arial', 12, 'bold')).pack(pady=10)
        
        element_type = tk.StringVar(value="text")
        
        # Opções de tipo
        types = [
            ("text", "📝 Texto"),
            ("image", "🖼️ Imagem"),
            ("line", "📏 Linha"),
            ("rectangle", "🔲 Retângulo")
        ]
        
        for value, text in types:
            tk.Radiobutton(element_window, text=text, variable=element_type,
                          value=value, font=('Arial', 11)).pack(pady=5)
        
        # Data type
        tk.Label(element_window, text="Tipo de Dados:",
                font=('Arial', 12, 'bold')).pack(pady=(20, 5))
        
        data_type = tk.StringVar(value="fixed")
        
        tk.Radiobutton(element_window, text="📝 Fixo (texto editável)",
                      variable=data_type, value="fixed",
                      font=('Arial', 11)).pack(pady=2)
        
        tk.Radiobutton(element_window, text="📊 Dinâmico (dados do sistema)",
                      variable=data_type, value="dynamic",
                      font=('Arial', 11)).pack(pady=2)
        
        # Botões
        button_frame = tk.Frame(element_window)
        button_frame.pack(pady=20)
        
        def create_element():
            self.create_new_element(element_type.get(), data_type.get())
            element_window.destroy()
        
        tk.Button(button_frame, text="Criar", command=create_element,
                 bg='#10b981', fg='white', font=('Arial', 11, 'bold')).pack(side="left", padx=5)
        
        tk.Button(button_frame, text="Cancelar", command=element_window.destroy,
                 bg='#6b7280', fg='white', font=('Arial', 11, 'bold')).pack(side="left", padx=5)
    
    def create_new_element(self, element_type, data_type):
        """Criar novo elemento"""
        label = simpledialog.askstring("Nome do Elemento", "Digite o nome do elemento:")
        if not label:
            return
        
        # Elemento base
        new_element = {
            "id": f"element_{len(self.template_data['pages'][str(self.current_page)]['elements'])}",
            "type": element_type,
            "label": label,
            "x": 50, "y": 100, "w": 100, "h": 20,
            "data_type": data_type,
            "font_family": "Arial",
            "font_size": 11,
            "font_style": "normal"
        }
        
        if data_type == "dynamic":
            # Campos dinâmicos disponíveis
            available_fields = [
                "cliente_nome", "cliente_nome_fantasia", "cliente_cnpj",
                "numero_proposta", "data_criacao", "responsavel_nome",
                "valor_total", "descricao_atividade"
            ]
            new_element["field_options"] = available_fields
            new_element["current_field"] = available_fields[0]
        else:
            new_element["content"] = "Novo texto"
        
        # Adicionar ao template
        self.template_data["pages"][str(self.current_page)]["elements"].append(new_element)
        
        # Atualizar interface
        self.update_element_list()
        self.draw_page()
    
    def remove_element(self):
        """Remover elemento selecionado"""
        if self.selected_element is not None:
            elements = self.template_data["pages"][str(self.current_page)]["elements"]
            del elements[self.selected_element]
            
            self.selected_element = None
            self.update_element_list()
            self.update_properties_panel()
            self.draw_page()
    
    def load_template_list(self):
        """Carregar lista de templates"""
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            
            c.execute("SELECT name FROM pdf_templates ORDER BY name")
            templates = [row[0] for row in c.fetchall()]
            
            self.template_combo['values'] = ["Template Padrão"] + templates
            self.template_combo.set("Template Padrão")
            
        except Exception as e:
            print(f"Erro ao carregar templates: {e}")
        finally:
            if 'conn' in locals():
                conn.close()
    
    def on_template_selected(self, event):
        """Quando template é selecionado"""
        template_name = self.template_var.get()
        if template_name == "Template Padrão":
            self.load_default_template()
        else:
            self.load_template(template_name)
    
    def load_template(self, template_name):
        """Carregar template do banco"""
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            
            c.execute("SELECT template_data FROM pdf_templates WHERE name = ?", 
                     (template_name,))
            result = c.fetchone()
            
            if result:
                self.template_data = json.loads(result[0])
                self.update_element_list()
                self.draw_page()
            
        except Exception as e:
            print(f"Erro ao carregar template: {e}")
            messagebox.showerror("Erro", f"Erro ao carregar template: {e}")
        finally:
            if 'conn' in locals():
                conn.close()
    
    def create_new_template(self):
        """Criar novo template"""
        name = simpledialog.askstring("Novo Template", "Nome do template:")
        if name:
            self.template_data["name"] = name
            self.template_data["description"] = ""
            self.save_template()
    
    def save_template(self):
        """Salvar template atual"""
        if not self.template_data.get("name"):
            messagebox.showwarning("Aviso", "Template precisa ter um nome!")
            return
        
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            
            template_json = json.dumps(self.template_data, indent=2)
            
            # Inserir ou atualizar
            c.execute("""
                INSERT OR REPLACE INTO pdf_templates (name, template_data, created_by)
                VALUES (?, ?, ?)
            """, (self.template_data["name"], template_json, self.user_id))
            
            conn.commit()
            
            messagebox.showinfo("Sucesso", "Template salvo com sucesso!")
            self.load_template_list()
            
        except Exception as e:
            print(f"Erro ao salvar template: {e}")
            messagebox.showerror("Erro", f"Erro ao salvar template: {e}")
        finally:
            if 'conn' in locals():
                conn.close()
    
    def delete_template(self):
        """Excluir template"""
        template_name = self.template_var.get()
        if template_name == "Template Padrão":
            messagebox.showwarning("Aviso", "Não é possível excluir o template padrão!")
            return
        
        if messagebox.askyesno("Confirmar", f"Excluir template '{template_name}'?"):
            try:
                conn = sqlite3.connect(self.db_name)
                c = conn.cursor()
                
                c.execute("DELETE FROM pdf_templates WHERE name = ?", (template_name,))
                conn.commit()
                
                messagebox.showinfo("Sucesso", "Template excluído!")
                self.load_template_list()
                self.load_default_template()
                
            except Exception as e:
                print(f"Erro ao excluir template: {e}")
                messagebox.showerror("Erro", f"Erro ao excluir template: {e}")
            finally:
                if 'conn' in locals():
                    conn.close()
    
    def zoom_in(self):
        """Aumentar zoom"""
        if self.scale_factor < 1.5:
            self.scale_factor += 0.1
            self.update_zoom_display()
            self.draw_page()
    
    def zoom_out(self):
        """Diminuir zoom"""
        if self.scale_factor > 0.3:
            self.scale_factor -= 0.1
            self.update_zoom_display()
            self.draw_page()
    
    def update_zoom_display(self):
        """Atualizar display do zoom"""
        zoom_percent = int(self.scale_factor * 100)
        self.zoom_label.config(text=f"{zoom_percent}%")
        
        # Atualizar scroll region do canvas com novas dimensões
        margin = 20
        new_width = self.paper_width_pt * self.scale_factor
        new_height = self.paper_height_pt * self.scale_factor
        legend_height = 120  # Espaço para legenda
        self.canvas.configure(scrollregion=(0, 0, margin + new_width + 40, margin + new_height + legend_height))
    
    def reload_preview(self):
        """Recarregar visualização"""
        self.draw_page()
    
    def map_existing_pdf(self):
        """Mapear PDF existente para criar template"""
        messagebox.showinfo("Mapeamento PDF", 
            "Esta funcionalidade analisará o gerador atual\n"
            "e criará um mapeamento completo de todos os elementos.")
        
        # Implementar análise do PDF atual
        self.load_default_template()
    
    def create_error_interface(self, parent, error_msg):
        """Criar interface de erro"""
        error_frame = tk.Frame(parent, bg='#fef2f2')
        error_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(error_frame, text="❌ Erro no Editor de Templates", 
                font=('Arial', 16, 'bold'), 
                bg='#fef2f2', fg='#dc2626').pack(pady=20)
        
        tk.Label(error_frame, text=f"Detalhes do erro:\n{error_msg}", 
                font=('Arial', 11), 
                bg='#fef2f2', fg='#7f1d1d',
                wraplength=500, justify='left').pack(pady=10)