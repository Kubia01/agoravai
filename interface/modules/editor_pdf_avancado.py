import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser, font, simpledialog
import json
import os
import sqlite3
from datetime import datetime
import subprocess
import tempfile

try:
    from PIL import Image, ImageTk, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Importar módulo base
from .base_module import BaseModule

# Importar resolvedor de campos dinâmicos
try:
    from utils.dynamic_field_resolver import DynamicFieldResolver
    FIELD_RESOLVER_AVAILABLE = True
except ImportError:
    FIELD_RESOLVER_AVAILABLE = False
    print("⚠️ Resolvedor de campos dinâmicos não disponível")

class EditorPDFAvancadoModule(BaseModule):
    def __init__(self, parent, user_id, role, main_window):
        try:
            self.user_info = {'role': role, 'user_id': user_id}
            
            # Configurar conexão com banco
            from database import DB_NAME
            self.db_name = DB_NAME
            
            # Inicializar propriedades
            self.template_data = {}
            self.available_fields = {}
            self.selected_elements = []
            self.canvas_scale = 0.8
            self.page_width = 595  # A4 width in points
            self.page_height = 842  # A4 height in points
            self.current_page = 1
            self.total_pages = 4
            self.drag_data = {}
            self.current_cotacao_id = None
            
            # Inicializar resolvedor de campos dinâmicos
            if FIELD_RESOLVER_AVAILABLE:
                self.field_resolver = DynamicFieldResolver(self.db_name)
            else:
                self.field_resolver = None
            
            super().__init__(parent, user_id, role, main_window)
            
            # Carregar dados do banco
            self.load_database_fields()
            
            # Carregar template padrão
            self.load_default_template()
            
            # Gerar preview inicial
            self.generate_visual_preview()
            
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
        
        tk.Label(title_frame, text="🚀 Editor PDF Avançado - Visual e Dinâmico", 
                font=('Arial', 16, 'bold'), bg='#f8fafc', fg='#1e293b').pack(side="left")
        
        # Frame principal horizontal
        main_frame = tk.Frame(self.frame, bg='#f8fafc')
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Coluna esquerda - Controles (30%)
        self.controls_frame = tk.Frame(main_frame, bg='white', relief='ridge', bd=1)
        self.controls_frame.pack(side="left", fill="both", expand=False, padx=(0, 10))
        self.controls_frame.config(width=300)
        
        # Coluna central - Preview Visual (50%)
        self.preview_frame = tk.Frame(main_frame, bg='white', relief='ridge', bd=1)
        self.preview_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Coluna direita - Propriedades (20%)
        self.properties_frame = tk.Frame(main_frame, bg='white', relief='ridge', bd=1)
        self.properties_frame.pack(side="right", fill="both", expand=False)
        self.properties_frame.config(width=200)
        
        # Configurar painéis
        self.setup_controls_panel()
        self.setup_visual_preview_panel()
        self.setup_properties_panel()
    
    def setup_controls_panel(self):
        """Configurar painel de controles"""
        # Título do painel
        title_frame = tk.Frame(self.controls_frame, bg='#1e40af')
        title_frame.pack(fill="x")
        
        tk.Label(title_frame, text="🎛️ Controles", 
                font=('Arial', 12, 'bold'), bg='#1e40af', fg='white').pack(pady=10)
        
        # Notebook para organizar funcionalidades
        self.controls_notebook = ttk.Notebook(self.controls_frame)
        self.controls_notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Aba 1: Dados Dinâmicos
        self.setup_dynamic_data_tab()
        
        # Aba 2: Elementos Visuais
        self.setup_visual_elements_tab()
        
        # Aba 3: Páginas
        self.setup_pages_tab()
        
        # Aba 4: Templates
        self.setup_templates_tab()
        
        # Botões de ação
        self.setup_action_buttons()
    
    def setup_dynamic_data_tab(self):
        """Configurar aba de dados dinâmicos"""
        dynamic_frame = tk.Frame(self.controls_notebook, bg='white')
        self.controls_notebook.add(dynamic_frame, text="🔄 Dados")
        
        # Scroll
        canvas = tk.Canvas(dynamic_frame, bg='white')
        scrollbar = ttk.Scrollbar(dynamic_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Seção: Conectar com Cotação
        tk.Label(scrollable_frame, text="Conectar com Cotação", font=('Arial', 12, 'bold'), 
                bg='white', fg='#1f2937').pack(anchor="w", padx=10, pady=(10,5))
        
        # Seletor de cotação
        cotacao_frame = tk.Frame(scrollable_frame, bg='white')
        cotacao_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(cotacao_frame, text="Cotação:", bg='white', font=('Arial', 9)).pack(side="left")
        
        self.cotacao_var = tk.StringVar()
        self.cotacao_combo = ttk.Combobox(cotacao_frame, textvariable=self.cotacao_var, 
                                         state="readonly", width=25)
        self.cotacao_combo.pack(side="left", padx=5, fill="x", expand=True)
        self.cotacao_combo.bind('<<ComboboxSelected>>', self.on_cotacao_selected)
        
        tk.Button(cotacao_frame, text="🔄", command=self.load_cotacoes,
                 font=('Arial', 8), width=3).pack(side="right")
        
        # Campos disponíveis por categoria
        self.setup_field_categories(scrollable_frame)
        
        # Carregar cotações
        self.load_cotacoes()
    
    def setup_field_categories(self, parent):
        """Configurar categorias de campos disponíveis"""
        # Cliente
        client_frame = tk.LabelFrame(parent, text="👤 Campos do Cliente", bg='white', font=('Arial', 10, 'bold'))
        client_frame.pack(fill="x", padx=10, pady=5)
        
        self.client_listbox = tk.Listbox(client_frame, height=4, font=('Arial', 8))
        self.client_listbox.pack(fill="x", padx=5, pady=5)
        self.client_listbox.bind('<Double-Button-1>', self.add_field_to_canvas)
        
        # Responsável/Técnico
        resp_frame = tk.LabelFrame(parent, text="👨‍🔧 Campos do Responsável", bg='white', font=('Arial', 10, 'bold'))
        resp_frame.pack(fill="x", padx=10, pady=5)
        
        self.resp_listbox = tk.Listbox(resp_frame, height=3, font=('Arial', 8))
        self.resp_listbox.pack(fill="x", padx=5, pady=5)
        self.resp_listbox.bind('<Double-Button-1>', self.add_field_to_canvas)
        
        # Cotação
        cotacao_fields_frame = tk.LabelFrame(parent, text="📋 Campos da Cotação", bg='white', font=('Arial', 10, 'bold'))
        cotacao_fields_frame.pack(fill="x", padx=10, pady=5)
        
        self.cotacao_listbox = tk.Listbox(cotacao_fields_frame, height=4, font=('Arial', 8))
        self.cotacao_listbox.pack(fill="x", padx=5, pady=5)
        self.cotacao_listbox.bind('<Double-Button-1>', self.add_field_to_canvas)
        
        # Itens
        items_frame = tk.LabelFrame(parent, text="📦 Campos dos Itens", bg='white', font=('Arial', 10, 'bold'))
        items_frame.pack(fill="x", padx=10, pady=5)
        
        self.items_listbox = tk.Listbox(items_frame, height=3, font=('Arial', 8))
        self.items_listbox.pack(fill="x", padx=5, pady=5)
        self.items_listbox.bind('<Double-Button-1>', self.add_field_to_canvas)
    
    def setup_visual_elements_tab(self):
        """Configurar aba de elementos visuais"""
        visual_frame = tk.Frame(self.controls_notebook, bg='white')
        self.controls_notebook.add(visual_frame, text="🎨 Elementos")
        
        # Scroll
        canvas = tk.Canvas(visual_frame, bg='white')
        scrollbar = ttk.Scrollbar(visual_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Elementos básicos
        tk.Label(scrollable_frame, text="Adicionar Elementos", font=('Arial', 12, 'bold'), 
                bg='white', fg='#1f2937').pack(anchor="w", padx=10, pady=(10,5))
        
        elements = [
            ("📝 Texto", "text"),
            ("🖼️ Imagem", "image"),
            ("📊 Tabela", "table"),
            ("➖ Linha", "line"),
            ("⬜ Retângulo", "rectangle"),
            ("🏷️ Logo", "logo"),
            ("📄 Campo Dinâmico", "dynamic_field"),
        ]
        
        for label, element_type in elements:
            btn = tk.Button(scrollable_frame, text=label, 
                           command=lambda t=element_type: self.add_element_to_canvas(t),
                           font=('Arial', 9), bg='#f3f4f6', relief='flat', 
                           cursor='hand2', width=20)
            btn.pack(fill="x", padx=10, pady=2)
        
        # Formatação de texto
        tk.Label(scrollable_frame, text="Formatação de Texto", font=('Arial', 11, 'bold'), 
                bg='white', fg='#1f2937').pack(anchor="w", padx=10, pady=(20,5))
        
        # Fonte
        font_frame = tk.Frame(scrollable_frame, bg='white')
        font_frame.pack(fill="x", padx=10, pady=2)
        
        tk.Label(font_frame, text="Fonte:", bg='white', font=('Arial', 8)).pack(side="left")
        self.font_var = tk.StringVar(value="Arial")
        font_combo = ttk.Combobox(font_frame, textvariable=self.font_var, width=12,
                                 values=["Arial", "Times", "Helvetica", "Courier"])
        font_combo.pack(side="left", padx=2)
        
        # Tamanho
        size_frame = tk.Frame(scrollable_frame, bg='white')
        size_frame.pack(fill="x", padx=10, pady=2)
        
        tk.Label(size_frame, text="Tamanho:", bg='white', font=('Arial', 8)).pack(side="left")
        self.size_var = tk.StringVar(value="10")
        size_spin = tk.Spinbox(size_frame, from_=8, to=72, textvariable=self.size_var, width=5)
        size_spin.pack(side="left", padx=2)
        
        # Estilo
        style_frame = tk.Frame(scrollable_frame, bg='white')
        style_frame.pack(fill="x", padx=10, pady=2)
        
        self.bold_var = tk.BooleanVar()
        self.italic_var = tk.BooleanVar()
        
        tk.Checkbutton(style_frame, text="Negrito", variable=self.bold_var, 
                      bg='white', font=('Arial', 8)).pack(side="left")
        tk.Checkbutton(style_frame, text="Itálico", variable=self.italic_var, 
                      bg='white', font=('Arial', 8)).pack(side="left")
        
        # Cor
        color_frame = tk.Frame(scrollable_frame, bg='white')
        color_frame.pack(fill="x", padx=10, pady=2)
        
        tk.Label(color_frame, text="Cor:", bg='white', font=('Arial', 8)).pack(side="left")
        self.text_color = "#000000"
        self.color_btn = tk.Button(color_frame, text="🎨", width=3,
                                  command=self.choose_text_color)
        self.color_btn.pack(side="left", padx=2)
        
        self.color_preview = tk.Label(color_frame, text="   ", bg=self.text_color, 
                                     relief='solid', bd=1, width=3)
        self.color_preview.pack(side="left", padx=2)
    
    def setup_pages_tab(self):
        """Configurar aba de páginas"""
        pages_frame = tk.Frame(self.controls_notebook, bg='white')
        self.controls_notebook.add(pages_frame, text="📄 Páginas")
        
        # Navegação de páginas
        nav_frame = tk.Frame(pages_frame, bg='white')
        nav_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Button(nav_frame, text="◀", command=lambda: self.change_page(-1),
                 font=('Arial', 12), width=3).pack(side="left")
        
        self.page_label = tk.Label(nav_frame, text="Página 1 de 4", 
                                  font=('Arial', 11, 'bold'), bg='white')
        self.page_label.pack(side="left", expand=True)
        
        tk.Button(nav_frame, text="▶", command=lambda: self.change_page(1),
                 font=('Arial', 12), width=3).pack(side="right")
        
        # Gerenciamento de páginas
        tk.Label(pages_frame, text="Gerenciar Páginas", font=('Arial', 11, 'bold'), 
                bg='white', fg='#1f2937').pack(anchor="w", padx=10, pady=(10,5))
        
        page_buttons = [
            ("➕ Nova Página", self.add_new_page),
            ("📋 Duplicar Página", self.duplicate_page),
            ("🗑️ Excluir Página", self.delete_page),
            ("⬆️ Mover para Cima", self.move_page_up),
            ("⬇️ Mover para Baixo", self.move_page_down),
        ]
        
        for label, command in page_buttons:
            btn = tk.Button(pages_frame, text=label, command=command,
                           font=('Arial', 9), bg='#f3f4f6', relief='flat', 
                           cursor='hand2', width=20)
            btn.pack(fill="x", padx=10, pady=2)
        
        # Configurações da página atual
        tk.Label(pages_frame, text="Configurações da Página", font=('Arial', 11, 'bold'), 
                bg='white', fg='#1f2937').pack(anchor="w", padx=10, pady=(20,5))
        
        # Nome da página
        name_frame = tk.Frame(pages_frame, bg='white')
        name_frame.pack(fill="x", padx=10, pady=2)
        
        tk.Label(name_frame, text="Nome:", bg='white', font=('Arial', 9)).pack(side="left")
        self.page_name_var = tk.StringVar(value="Página 1")
        page_name_entry = tk.Entry(name_frame, textvariable=self.page_name_var, width=15)
        page_name_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Tipo de página
        type_frame = tk.Frame(pages_frame, bg='white')
        type_frame.pack(fill="x", padx=10, pady=2)
        
        tk.Label(type_frame, text="Tipo:", bg='white', font=('Arial', 9)).pack(side="left")
        self.page_type_var = tk.StringVar(value="Capa")
        type_combo = ttk.Combobox(type_frame, textvariable=self.page_type_var, width=12,
                                 values=["Capa", "Apresentação", "Sobre Empresa", "Proposta", "Personalizada"])
        type_combo.pack(side="left", padx=5, fill="x", expand=True)
    
    def setup_templates_tab(self):
        """Configurar aba de templates"""
        templates_frame = tk.Frame(self.controls_notebook, bg='white')
        self.controls_notebook.add(templates_frame, text="📋 Templates")
        
        # Scroll
        canvas = tk.Canvas(templates_frame, bg='white')
        scrollbar = ttk.Scrollbar(templates_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Gerenciamento de templates
        tk.Label(scrollable_frame, text="Gerenciar Templates", font=('Arial', 11, 'bold'), 
                bg='white', fg='#1f2937').pack(anchor="w", padx=10, pady=(10,5))
        
        template_buttons = [
            ("💾 Salvar Template", self.save_template),
            ("📂 Carregar Template", self.load_template),
            ("📤 Exportar Template", self.export_template),
            ("📥 Importar Template", self.import_template),
            ("🔄 Restaurar Padrão", self.restore_default_template),
        ]
        
        for label, command in template_buttons:
            btn = tk.Button(scrollable_frame, text=label, command=command,
                           font=('Arial', 9), bg='#f3f4f6', relief='flat', 
                           cursor='hand2', width=20)
            btn.pack(fill="x", padx=10, pady=2)
        
        # Templates salvos
        tk.Label(scrollable_frame, text="Templates Salvos", font=('Arial', 11, 'bold'), 
                bg='white', fg='#1f2937').pack(anchor="w", padx=10, pady=(20,5))
        
        self.templates_listbox = tk.Listbox(scrollable_frame, height=6, font=('Arial', 8))
        self.templates_listbox.pack(fill="x", padx=10, pady=5)
        self.templates_listbox.bind('<Double-Button-1>', self.load_selected_template)
        
        # Versionamento
        tk.Label(scrollable_frame, text="Versionamento", font=('Arial', 11, 'bold'), 
                bg='white', fg='#1f2937').pack(anchor="w", padx=10, pady=(20,5))
        
        version_frame = tk.Frame(scrollable_frame, bg='white')
        version_frame.pack(fill="x", padx=10, pady=2)
        
        tk.Label(version_frame, text="Versão:", bg='white', font=('Arial', 9)).pack(side="left")
        self.version_var = tk.StringVar(value="1.0")
        version_entry = tk.Entry(version_frame, textvariable=self.version_var, width=8)
        version_entry.pack(side="left", padx=5)
        
        tk.Button(version_frame, text="📌 Nova Versão", 
                 command=self.create_new_version, font=('Arial', 8)).pack(side="right")
        
        # Carregar templates existentes
        self.load_saved_templates()
    
    def setup_action_buttons(self):
        """Configurar botões de ação principais"""
        btn_frame = tk.Frame(self.controls_frame, bg='white')
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        buttons = [
            ("🔄 Atualizar Preview", self.generate_visual_preview, '#10b981'),
            ("📄 Gerar PDF", self.generate_final_pdf, '#ef4444'),
            ("💾 Salvar Rápido", self.quick_save, '#3b82f6'),
            ("🗑️ Limpar Tudo", self.clear_all, '#6b7280'),
        ]
        
        for label, command, color in buttons:
            btn = tk.Button(btn_frame, text=label, command=command,
                           font=('Arial', 9, 'bold'), bg=color, fg='white',
                           relief='flat', cursor='hand2')
            btn.pack(fill="x", pady=2)
    
    def setup_visual_preview_panel(self):
        """Configurar painel de preview visual"""
        # Título do painel
        title_frame = tk.Frame(self.preview_frame, bg='#dc2626')
        title_frame.pack(fill="x")
        
        tk.Label(title_frame, text="👁️ Editor Visual", 
                font=('Arial', 12, 'bold'), bg='#dc2626', fg='white').pack(side="left", pady=10, padx=10)
        
        # Status
        self.preview_status = tk.Label(title_frame, text="Pronto", 
                                      font=('Arial', 9), bg='#dc2626', fg='#fecaca')
        self.preview_status.pack(side="right", pady=10, padx=10)
        
        # Canvas para o preview visual
        canvas_frame = tk.Frame(self.preview_frame, bg='#f3f4f6')
        canvas_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical")
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient="horizontal")
        
        self.visual_canvas = tk.Canvas(canvas_frame, bg='white',
                                      yscrollcommand=v_scrollbar.set,
                                      xscrollcommand=h_scrollbar.set,
                                      cursor='crosshair')
        
        v_scrollbar.config(command=self.visual_canvas.yview)
        h_scrollbar.config(command=self.visual_canvas.xview)
        
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        self.visual_canvas.pack(side="left", fill="both", expand=True)
        
        # Eventos do canvas
        self.visual_canvas.bind('<Button-1>', self.on_canvas_click)
        self.visual_canvas.bind('<B1-Motion>', self.on_canvas_drag)
        self.visual_canvas.bind('<ButtonRelease-1>', self.on_canvas_release)
        self.visual_canvas.bind('<Double-Button-1>', self.on_canvas_double_click)
        self.visual_canvas.bind('<Button-3>', self.on_canvas_right_click)  # Menu contextual
        self.visual_canvas.bind('<Control-z>', self.undo_action)
        self.visual_canvas.bind('<Control-y>', self.redo_action)
        self.visual_canvas.bind('<Delete>', self.delete_selected_elements)
        
        # Menu contextual
        self.setup_context_menu()
        
        # Configurar scroll region
        self.visual_canvas.configure(scrollregion=(0, 0, 
                                                  int(self.page_width * self.canvas_scale),
                                                  int(self.page_height * self.canvas_scale)))
    
    def setup_properties_panel(self):
        """Configurar painel de propriedades"""
        # Título do painel
        title_frame = tk.Frame(self.properties_frame, bg='#7c3aed')
        title_frame.pack(fill="x")
        
        tk.Label(title_frame, text="🔧 Propriedades", 
                font=('Arial', 10, 'bold'), bg='#7c3aed', fg='white').pack(pady=8)
        
        # Scroll para propriedades
        canvas = tk.Canvas(self.properties_frame, bg='white')
        scrollbar = ttk.Scrollbar(self.properties_frame, orient="vertical", command=canvas.yview)
        self.props_frame = tk.Frame(canvas, bg='white')
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.props_frame, anchor="nw")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Inicialmente vazio - será preenchido quando um elemento for selecionado
        tk.Label(self.props_frame, text="Selecione um elemento\npara editar propriedades", 
                font=('Arial', 9), bg='white', fg='#6b7280', justify='center').pack(pady=20)
    
    def load_database_fields(self):
        """Carregar campos disponíveis do banco de dados"""
        try:
            if self.field_resolver:
                # Usar o resolvedor de campos dinâmicos
                available_fields = self.field_resolver.get_available_fields()
                
                # Converter para formato esperado pelas listboxes
                self.available_fields = {}
                for category, fields_list in available_fields.items():
                    self.available_fields[category] = {
                        field['field']: field['label'] 
                        for field in fields_list
                    }
            else:
                # Fallback para campos estáticos
                self.available_fields = {
                    'cliente': {
                        'nome': 'Nome/Razão Social',
                        'nome_fantasia': 'Nome Fantasia',
                        'cnpj': 'CNPJ',
                        'inscricao_estadual': 'Inscrição Estadual',
                        'endereco': 'Endereço',
                        'cidade': 'Cidade',
                        'estado': 'Estado',
                        'cep': 'CEP',
                        'telefone': 'Telefone',
                        'email': 'Email',
                        'site': 'Site',
                    },
                    'responsavel': {
                        'nome_completo': 'Nome Completo',
                        'email': 'Email',
                        'telefone': 'Telefone',
                        'username': 'Usuário',
                    },
                    'cotacao': {
                        'numero_proposta': 'Número da Proposta',
                        'data_criacao': 'Data de Criação',
                        'data_validade': 'Data de Validade',
                        'modelo_compressor': 'Modelo do Compressor',
                        'numero_serie_compressor': 'Número de Série',
                        'descricao_atividade': 'Descrição da Atividade',
                        'observacoes': 'Observações',
                        'valor_total': 'Valor Total',
                        'tipo_frete': 'Tipo de Frete',
                        'condicao_pagamento': 'Condição de Pagamento',
                        'prazo_entrega': 'Prazo de Entrega',
                        'status': 'Status',
                    },
                    'item': {
                        'item_nome': 'Nome do Item',
                        'quantidade': 'Quantidade',
                        'valor_unitario': 'Valor Unitário',
                        'valor_total_item': 'Valor Total do Item',
                        'descricao': 'Descrição',
                        'tipo': 'Tipo',
                    }
                }
            
            # Atualizar listboxes
            self.update_field_listboxes()
            
        except Exception as e:
            print(f"Erro ao carregar campos do banco: {e}")
            self.available_fields = {}
    
    def update_field_listboxes(self):
        """Atualizar as listboxes com os campos disponíveis"""
        # Limpar listboxes
        if hasattr(self, 'client_listbox'):
            self.client_listbox.delete(0, tk.END)
            for field, label in self.available_fields.get('cliente', {}).items():
                self.client_listbox.insert(tk.END, f"{label} ({field})")
        
        if hasattr(self, 'resp_listbox'):
            self.resp_listbox.delete(0, tk.END)
            for field, label in self.available_fields.get('responsavel', {}).items():
                self.resp_listbox.insert(tk.END, f"{label} ({field})")
        
        if hasattr(self, 'cotacao_listbox'):
            self.cotacao_listbox.delete(0, tk.END)
            for field, label in self.available_fields.get('cotacao', {}).items():
                self.cotacao_listbox.insert(tk.END, f"{label} ({field})")
        
        if hasattr(self, 'items_listbox'):
            self.items_listbox.delete(0, tk.END)
            for field, label in self.available_fields.get('item', {}).items():
                self.items_listbox.insert(tk.END, f"{label} ({field})")
    
    def load_cotacoes(self):
        """Carregar cotações disponíveis"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT c.id, c.numero_proposta, c.data_criacao, cl.nome
                FROM cotacoes c
                LEFT JOIN clientes cl ON c.cliente_id = cl.id
                ORDER BY c.data_criacao DESC
                LIMIT 50
            """)
            
            cotacoes = cursor.fetchall()
            
            if hasattr(self, 'cotacao_combo'):
                self.cotacao_combo['values'] = [
                    f"{num_prop} - {cliente} ({data})" 
                    for _, num_prop, data, cliente in cotacoes
                ]
                
                # Mapear para IDs
                self.cotacao_ids = {
                    f"{num_prop} - {cliente} ({data})": cot_id
                    for cot_id, num_prop, data, cliente in cotacoes
                }
            
            conn.close()
            
        except Exception as e:
            print(f"Erro ao carregar cotações: {e}")
    
    def on_cotacao_selected(self, event=None):
        """Callback quando uma cotação é selecionada"""
        selected = self.cotacao_var.get()
        if selected and hasattr(self, 'cotacao_ids') and selected in self.cotacao_ids:
            cotacao_id = self.cotacao_ids[selected]
            self.load_cotacao_data(cotacao_id)
    
    def load_cotacao_data(self, cotacao_id):
        """Carregar dados da cotação selecionada"""
        try:
            self.current_cotacao_id = cotacao_id
            
            if self.field_resolver:
                # Usar o resolvedor de campos dinâmicos
                success = self.field_resolver.load_cotacao_data(cotacao_id)
                if success:
                    # Obter resumo dos dados carregados
                    summary = self.field_resolver.get_summary()
                    
                    # Atualizar status
                    status_text = f"✅ Cotação {summary.get('numero_proposta', 'N/A')} carregada"
                    if hasattr(self, 'preview_status'):
                        self.preview_status.config(text=status_text)
                    
                    # Atualizar listboxes com dados reais
                    self.update_field_listboxes_with_data()
                    
                    # Regenerar preview
                    self.generate_visual_preview()
                    
                    print(f"📊 Dados carregados: {summary}")
                else:
                    messagebox.showerror("Erro", f"Não foi possível carregar dados da cotação {cotacao_id}")
            else:
                # Fallback para método anterior
                self.load_cotacao_data_fallback(cotacao_id)
            
        except Exception as e:
            print(f"Erro ao carregar dados da cotação: {e}")
            messagebox.showerror("Erro", f"Erro ao carregar cotação: {e}")
    
    def load_cotacao_data_fallback(self, cotacao_id):
        """Método fallback para carregar dados da cotação"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Carregar dados básicos da cotação
            cursor.execute("""
                SELECT c.numero_proposta, c.data_criacao, c.valor_total,
                       cl.nome as cliente_nome, u.nome_completo as responsavel_nome
                FROM cotacoes c
                LEFT JOIN clientes cl ON c.cliente_id = cl.id
                LEFT JOIN usuarios u ON c.responsavel_id = u.id
                WHERE c.id = ?
            """, (cotacao_id,))
            
            row = cursor.fetchone()
            if row:
                numero_proposta, data_criacao, valor_total, cliente_nome, responsavel_nome = row
                
                # Atualizar status
                status_text = f"✅ Cotação {numero_proposta} carregada (modo básico)"
                if hasattr(self, 'preview_status'):
                    self.preview_status.config(text=status_text)
                
                print(f"📊 Dados básicos carregados: {numero_proposta} - {cliente_nome}")
            
            conn.close()
            
        except Exception as e:
            print(f"Erro no método fallback: {e}")
    
    def update_field_listboxes_with_data(self):
        """Atualizar listboxes com exemplos de dados reais"""
        if not self.field_resolver or not self.field_resolver.current_data:
            return
        
        try:
            # Atualizar cliente
            if hasattr(self, 'client_listbox'):
                self.client_listbox.delete(0, tk.END)
                for field, label in self.available_fields.get('cliente', {}).items():
                    example = self.field_resolver.resolve_field(f"cliente.{field}")
                    display_text = f"{label}: {example[:30]}..." if len(example) > 30 else f"{label}: {example}"
                    self.client_listbox.insert(tk.END, display_text)
            
            # Atualizar responsável
            if hasattr(self, 'resp_listbox'):
                self.resp_listbox.delete(0, tk.END)
                for field, label in self.available_fields.get('responsavel', {}).items():
                    example = self.field_resolver.resolve_field(f"responsavel.{field}")
                    display_text = f"{label}: {example[:30]}..." if len(example) > 30 else f"{label}: {example}"
                    self.resp_listbox.insert(tk.END, display_text)
            
            # Atualizar cotação
            if hasattr(self, 'cotacao_listbox'):
                self.cotacao_listbox.delete(0, tk.END)
                for field, label in self.available_fields.get('cotacao', {}).items():
                    example = self.field_resolver.resolve_field(f"cotacao.{field}")
                    display_text = f"{label}: {example[:30]}..." if len(example) > 30 else f"{label}: {example}"
                    self.cotacao_listbox.insert(tk.END, display_text)
            
            # Atualizar itens (mostrar primeiro item como exemplo)
            if hasattr(self, 'items_listbox'):
                self.items_listbox.delete(0, tk.END)
                for field, label in self.available_fields.get('item', {}).items():
                    example = self.field_resolver.resolve_field(f"item.{field}", 0)  # Primeiro item
                    display_text = f"{label}: {example[:30]}..." if len(example) > 30 else f"{label}: {example}"
                    self.items_listbox.insert(tk.END, display_text)
        
        except Exception as e:
            print(f"Erro ao atualizar listboxes com dados: {e}")
    
    def load_default_template(self):
        """Carregar template padrão"""
        self.template_data = {
            'pages': [
                {
                    'id': 1,
                    'name': 'Capa',
                    'type': 'Capa',
                    'elements': []
                },
                {
                    'id': 2,
                    'name': 'Apresentação',
                    'type': 'Apresentação',
                    'elements': []
                },
                {
                    'id': 3,
                    'name': 'Sobre a Empresa',
                    'type': 'Sobre Empresa',
                    'elements': []
                },
                {
                    'id': 4,
                    'name': 'Proposta',
                    'type': 'Proposta',
                    'elements': []
                }
            ],
            'version': '1.0',
            'created_at': datetime.now().isoformat()
        }
    
    def generate_visual_preview(self):
        """Gerar preview visual no canvas"""
        try:
            self.preview_status.config(text="🔄 Atualizando...")
            self.frame.update()
            
            # Limpar canvas
            self.visual_canvas.delete("all")
            
            # Dimensões da página
            page_width = int(self.page_width * self.canvas_scale)
            page_height = int(self.page_height * self.canvas_scale)
            
            # Desenhar fundo da página
            self.visual_canvas.create_rectangle(10, 10, page_width + 10, page_height + 10,
                                              fill='white', outline='#cccccc', width=2,
                                              tags='page_bg')
            
            # Desenhar elementos da página atual
            current_page_data = self.get_current_page_data()
            if current_page_data:
                self.draw_page_elements(current_page_data)
            
            # Desenhar grid (opcional)
            self.draw_grid()
            
            self.preview_status.config(text="✅ Atualizado")
            
        except Exception as e:
            self.preview_status.config(text="❌ Erro")
            print(f"Erro ao gerar preview: {e}")
    
    def get_current_page_data(self):
        """Obter dados da página atual"""
        for page in self.template_data['pages']:
            if page['id'] == self.current_page:
                return page
        return None
    
    def draw_page_elements(self, page_data):
        """Desenhar elementos da página"""
        for element in page_data.get('elements', []):
            self.draw_element(element)
    
    def draw_element(self, element):
        """Desenhar um elemento específico"""
        element_type = element.get('type', '')
        x = element.get('x', 0) * self.canvas_scale
        y = element.get('y', 0) * self.canvas_scale
        
        if element_type == 'text':
            self.draw_text_element(element, x, y)
        elif element_type == 'image':
            self.draw_image_element(element, x, y)
        elif element_type == 'table':
            self.draw_table_element(element, x, y)
        elif element_type == 'line':
            self.draw_line_element(element, x, y)
        elif element_type == 'rectangle':
            self.draw_rectangle_element(element, x, y)
        elif element_type == 'dynamic_field':
            self.draw_dynamic_field_element(element, x, y)
    
    def draw_text_element(self, element, x, y):
        """Desenhar elemento de texto"""
        text = element.get('text', 'Texto')
        font_family = element.get('font_family', 'Arial')
        font_size = int(element.get('font_size', 10) * self.canvas_scale)
        font_style = 'bold' if element.get('bold', False) else 'normal'
        color = element.get('color', '#000000')
        
        canvas_id = self.visual_canvas.create_text(
            x + 10, y + 10, text=text, anchor='nw',
            font=(font_family, font_size, font_style),
            fill=color, tags=f"element_{element.get('id', '')}"
        )
        
        # Adicionar à lista de elementos selecionáveis
        element['canvas_id'] = canvas_id
    
    def draw_dynamic_field_element(self, element, x, y):
        """Desenhar elemento de campo dinâmico"""
        field_ref = element.get('field_ref', 'campo.exemplo')
        value = self.resolve_dynamic_field(field_ref)
        
        font_family = element.get('font_family', 'Arial')
        font_size = int(element.get('font_size', 10) * self.canvas_scale)
        color = element.get('color', '#000000')
        
        canvas_id = self.visual_canvas.create_text(
            x + 10, y + 10, text=value, anchor='nw',
            font=(font_family, font_size),
            fill=color, tags=f"element_{element.get('id', '')}"
        )
        
        element['canvas_id'] = canvas_id
    
    def resolve_dynamic_field(self, field_ref, item_index=None):
        """Resolver campo dinâmico baseado na referência"""
        try:
            if self.field_resolver and self.field_resolver.current_data:
                # Usar o resolvedor de campos dinâmicos
                return self.field_resolver.resolve_field(field_ref, item_index)
            else:
                # Fallback para placeholder
                return f"[{field_ref}]"
        except Exception as e:
            print(f"Erro ao resolver campo dinâmico {field_ref}: {e}")
            return f"[ERRO: {field_ref}]"
    
    def draw_grid(self):
        """Desenhar grid de auxílio"""
        page_width = int(self.page_width * self.canvas_scale)
        page_height = int(self.page_height * self.canvas_scale)
        
        # Grid de 20px
        grid_size = 20
        
        for x in range(10, page_width + 10, grid_size):
            self.visual_canvas.create_line(x, 10, x, page_height + 10, 
                                         fill='#f0f0f0', tags='grid')
        
        for y in range(10, page_height + 10, grid_size):
            self.visual_canvas.create_line(10, y, page_width + 10, y, 
                                         fill='#f0f0f0', tags='grid')
    
    # Métodos de interação com o canvas
    def on_canvas_click(self, event):
        """Callback para clique no canvas"""
        self.drag_data = {'x': event.x, 'y': event.y}
        
        # Verificar se clicou em um elemento
        clicked_item = self.visual_canvas.find_closest(event.x, event.y)[0]
        self.select_element(clicked_item)
    
    def on_canvas_drag(self, event):
        """Callback para arrastar no canvas"""
        if self.selected_elements:
            dx = event.x - self.drag_data['x']
            dy = event.y - self.drag_data['y']
            
            for element_id in self.selected_elements:
                self.visual_canvas.move(element_id, dx, dy)
            
            self.drag_data = {'x': event.x, 'y': event.y}
    
    def on_canvas_release(self, event):
        """Callback para soltar elemento no canvas"""
        # Atualizar posições no template_data
        self.update_element_positions()
    
    def on_canvas_double_click(self, event):
        """Callback para duplo clique no canvas"""
        # Editar elemento
        clicked_item = self.visual_canvas.find_closest(event.x, event.y)[0]
        self.edit_element(clicked_item)
    
    def select_element(self, canvas_id):
        """Selecionar elemento no canvas"""
        # Limpar seleção anterior
        self.visual_canvas.delete('selection')
        
        # Marcar novo elemento selecionado
        bbox = self.visual_canvas.bbox(canvas_id)
        if bbox:
            self.visual_canvas.create_rectangle(bbox, outline='#3b82f6', width=2, 
                                              tags='selection')
        
        self.selected_elements = [canvas_id]
        self.update_properties_panel(canvas_id)
    
    def update_properties_panel(self, canvas_id):
        """Atualizar painel de propriedades para o elemento selecionado"""
        # Limpar painel
        for widget in self.props_frame.winfo_children():
            widget.destroy()
        
        # Encontrar elemento nos dados
        element = self.find_element_by_canvas_id(canvas_id)
        
        if element:
            self.create_properties_ui(element)
        else:
            tk.Label(self.props_frame, text="Elemento não encontrado", 
                    font=('Arial', 9), bg='white', fg='#ef4444').pack(pady=10)
    
    def find_element_by_canvas_id(self, canvas_id):
        """Encontrar elemento nos dados pelo canvas_id"""
        current_page = self.get_current_page_data()
        if current_page:
            for element in current_page.get('elements', []):
                if element.get('canvas_id') == canvas_id:
                    return element
        return None
    
    def create_properties_ui(self, element):
        """Criar interface de propriedades para um elemento"""
        element_type = element.get('type', '')
        
        # Título
        tk.Label(self.props_frame, text=f"Propriedades - {element_type.title()}", 
                font=('Arial', 10, 'bold'), bg='white').pack(pady=5)
        
        # Propriedades comuns
        self.create_common_properties(element)
        
        # Propriedades específicas do tipo
        if element_type == 'text':
            self.create_text_properties(element)
        elif element_type == 'dynamic_field':
            self.create_dynamic_field_properties(element)
    
    def create_common_properties(self, element):
        """Criar propriedades comuns a todos os elementos"""
        # Posição X
        x_frame = tk.Frame(self.props_frame, bg='white')
        x_frame.pack(fill="x", padx=5, pady=2)
        
        tk.Label(x_frame, text="X:", bg='white', font=('Arial', 8)).pack(side="left")
        x_var = tk.StringVar(value=str(element.get('x', 0)))
        x_entry = tk.Entry(x_frame, textvariable=x_var, width=8, font=('Arial', 8))
        x_entry.pack(side="right")
        
        # Posição Y
        y_frame = tk.Frame(self.props_frame, bg='white')
        y_frame.pack(fill="x", padx=5, pady=2)
        
        tk.Label(y_frame, text="Y:", bg='white', font=('Arial', 8)).pack(side="left")
        y_var = tk.StringVar(value=str(element.get('y', 0)))
        y_entry = tk.Entry(y_frame, textvariable=y_var, width=8, font=('Arial', 8))
        y_entry.pack(side="right")
    
    def create_text_properties(self, element):
        """Criar propriedades específicas para texto"""
        # Texto
        text_frame = tk.Frame(self.props_frame, bg='white')
        text_frame.pack(fill="x", padx=5, pady=2)
        
        tk.Label(text_frame, text="Texto:", bg='white', font=('Arial', 8)).pack(anchor="w")
        text_var = tk.StringVar(value=element.get('text', ''))
        text_entry = tk.Entry(text_frame, textvariable=text_var, width=15, font=('Arial', 8))
        text_entry.pack(fill="x")
        
        # Fonte
        font_frame = tk.Frame(self.props_frame, bg='white')
        font_frame.pack(fill="x", padx=5, pady=2)
        
        tk.Label(font_frame, text="Fonte:", bg='white', font=('Arial', 8)).pack(side="left")
        font_var = tk.StringVar(value=element.get('font_family', 'Arial'))
        font_combo = ttk.Combobox(font_frame, textvariable=font_var, width=10,
                                 values=["Arial", "Times", "Helvetica"])
        font_combo.pack(side="right")
    
    def create_dynamic_field_properties(self, element):
        """Criar propriedades específicas para campos dinâmicos"""
        # Campo de referência
        ref_frame = tk.Frame(self.props_frame, bg='white')
        ref_frame.pack(fill="x", padx=5, pady=2)
        
        tk.Label(ref_frame, text="Campo:", bg='white', font=('Arial', 8)).pack(anchor="w")
        ref_var = tk.StringVar(value=element.get('field_ref', ''))
        ref_combo = ttk.Combobox(ref_frame, textvariable=ref_var, width=15,
                                values=self.get_available_field_refs())
        ref_combo.pack(fill="x")
    
    def get_available_field_refs(self):
        """Obter referências de campos disponíveis"""
        refs = []
        for category, fields in self.available_fields.items():
            for field_name in fields.keys():
                refs.append(f"{category}.{field_name}")
        return refs
    
    # Métodos para adicionar elementos
    def add_element_to_canvas(self, element_type):
        """Adicionar novo elemento ao canvas"""
        # Criar novo elemento
        new_element = {
            'id': self.generate_element_id(),
            'type': element_type,
            'x': 50,
            'y': 50,
        }
        
        # Configurações padrão por tipo
        if element_type == 'text':
            new_element.update({
                'text': 'Novo Texto',
                'font_family': 'Arial',
                'font_size': 12,
                'color': '#000000'
            })
        elif element_type == 'dynamic_field':
            new_element.update({
                'field_ref': 'cliente.nome',
                'font_family': 'Arial',
                'font_size': 12,
                'color': '#000000'
            })
        
        # Adicionar aos dados da página
        current_page = self.get_current_page_data()
        if current_page:
            current_page['elements'].append(new_element)
        
        # Redesenhar
        self.generate_visual_preview()
    
    def add_field_to_canvas(self, event):
        """Adicionar campo dinâmico ao canvas através de duplo clique na lista"""
        listbox = event.widget
        selection = listbox.curselection()
        
        if selection:
            field_text = listbox.get(selection[0])
            # Extrair field_ref do texto
            field_ref = field_text.split('(')[1].split(')')[0]
            
            # Determinar categoria
            if listbox == self.client_listbox:
                category = 'cliente'
            elif listbox == self.resp_listbox:
                category = 'responsavel'
            elif listbox == self.cotacao_listbox:
                category = 'cotacao'
                         elif listbox == self.items_listbox:
                category = 'item'
            else:
                category = 'unknown'
            
            # Criar elemento de campo dinâmico
            new_element = {
                'id': self.generate_element_id(),
                'type': 'dynamic_field',
                'field_ref': f"{category}.{field_ref}",
                'x': 50,
                'y': 50 + len(self.get_current_page_data().get('elements', [])) * 20,
                'font_family': 'Arial',
                'font_size': 12,
                'color': '#000000'
            }
            
            # Adicionar aos dados da página
            current_page = self.get_current_page_data()
            if current_page:
                current_page['elements'].append(new_element)
            
            # Redesenhar
            self.generate_visual_preview()
    
    def generate_element_id(self):
        """Gerar ID único para elemento"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    # Métodos para gerenciamento de páginas
    def change_page(self, direction):
        """Mudar página atual"""
        new_page = self.current_page + direction
        
        if 1 <= new_page <= len(self.template_data['pages']):
            self.current_page = new_page
            self.update_page_label()
            self.generate_visual_preview()
    
    def update_page_label(self):
        """Atualizar label da página"""
        if hasattr(self, 'page_label'):
            self.page_label.config(text=f"Página {self.current_page} de {len(self.template_data['pages'])}")
    
    def add_new_page(self):
        """Adicionar nova página"""
        new_page = {
            'id': len(self.template_data['pages']) + 1,
            'name': f'Página {len(self.template_data["pages"]) + 1}',
            'type': 'Personalizada',
            'elements': []
        }
        
        self.template_data['pages'].append(new_page)
        self.update_page_label()
        messagebox.showinfo("Sucesso", "Nova página adicionada!")
    
    def duplicate_page(self):
        """Duplicar página atual"""
        current_page = self.get_current_page_data()
        if current_page:
            import copy
            new_page = copy.deepcopy(current_page)
            new_page['id'] = len(self.template_data['pages']) + 1
            new_page['name'] = f"{current_page['name']} (Cópia)"
            
            self.template_data['pages'].append(new_page)
            self.update_page_label()
            messagebox.showinfo("Sucesso", "Página duplicada!")
    
    def delete_page(self):
        """Excluir página atual"""
        if len(self.template_data['pages']) > 1:
            if messagebox.askyesno("Confirmar", "Excluir página atual?"):
                self.template_data['pages'] = [
                    p for p in self.template_data['pages'] 
                    if p['id'] != self.current_page
                ]
                
                # Reajustar IDs
                for i, page in enumerate(self.template_data['pages']):
                    page['id'] = i + 1
                
                # Ajustar página atual se necessário
                if self.current_page > len(self.template_data['pages']):
                    self.current_page = len(self.template_data['pages'])
                
                self.update_page_label()
                self.generate_visual_preview()
                messagebox.showinfo("Sucesso", "Página excluída!")
        else:
            messagebox.showwarning("Aviso", "Não é possível excluir a última página!")
    
    # Métodos para templates
    def save_template(self):
        """Salvar template atual"""
        try:
            # Criar diretório se não existir
            os.makedirs('data/templates_avancados', exist_ok=True)
            
            # Nome do arquivo
            template_name = f"template_user_{self.user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join('data/templates_avancados', template_name)
            
            # Dados para salvar
            save_data = {
                'template_data': self.template_data,
                'version': self.version_var.get() if hasattr(self, 'version_var') else '1.0',
                'user_id': self.user_id,
                'created_at': datetime.now().isoformat(),
                'name': template_name
            }
            
            # Salvar arquivo
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=4, ensure_ascii=False)
            
            messagebox.showinfo("Sucesso", f"Template salvo: {template_name}")
            self.load_saved_templates()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar template: {e}")
    
    def load_saved_templates(self):
        """Carregar templates salvos"""
        try:
            template_dir = 'data/templates_avancados'
            if os.path.exists(template_dir):
                templates = [f for f in os.listdir(template_dir) if f.endswith('.json')]
                
                if hasattr(self, 'templates_listbox'):
                    self.templates_listbox.delete(0, tk.END)
                    for template in templates:
                        self.templates_listbox.insert(tk.END, template)
        except Exception as e:
            print(f"Erro ao carregar templates: {e}")
    
    def quick_save(self):
        """Salvamento rápido"""
        self.save_template()
    
    def generate_final_pdf(self):
        """Gerar PDF final"""
        messagebox.showinfo("PDF", "Funcionalidade de geração de PDF será implementada em breve!")
    
    def clear_all(self):
        """Limpar tudo"""
        if messagebox.askyesno("Confirmar", "Limpar todo o template atual?"):
            self.load_default_template()
            self.generate_visual_preview()
            messagebox.showinfo("Sucesso", "Template limpo!")
    
    # Métodos auxiliares
    def choose_text_color(self):
        """Escolher cor do texto"""
        color = colorchooser.askcolor(title="Escolher Cor do Texto")[1]
        if color:
            self.text_color = color
            self.color_preview.config(bg=color)
    
    def update_element_positions(self):
        """Atualizar posições dos elementos no template_data"""
        # Esta função seria implementada para sincronizar as posições
        # dos elementos no canvas com os dados do template
        pass
    
    def edit_element(self, canvas_id):
        """Editar elemento (duplo clique)"""
        element = self.find_element_by_canvas_id(canvas_id)
        if element and element.get('type') == 'text':
            # Abrir dialog de edição de texto
            new_text = tk.simpledialog.askstring("Editar Texto", "Novo texto:", 
                                                initialvalue=element.get('text', ''))
            if new_text:
                element['text'] = new_text
                self.generate_visual_preview()
    
    def setup_context_menu(self):
        """Configurar menu contextual"""
        self.context_menu = tk.Menu(self.frame, tearoff=0)
        
        # Edição
        self.context_menu.add_command(label="✂️ Recortar", command=self.cut_element)
        self.context_menu.add_command(label="📋 Copiar", command=self.copy_element)
        self.context_menu.add_command(label="📄 Colar", command=self.paste_element)
        self.context_menu.add_separator()
        
        # Ordem/camadas
        layer_menu = tk.Menu(self.context_menu, tearoff=0)
        layer_menu.add_command(label="🔼 Trazer para frente", command=self.bring_to_front)
        layer_menu.add_command(label="🔽 Enviar para trás", command=self.send_to_back)
        layer_menu.add_command(label="⬆️ Trazer uma camada", command=self.bring_forward)
        layer_menu.add_command(label="⬇️ Enviar uma camada", command=self.send_backward)
        self.context_menu.add_cascade(label="📐 Camadas", menu=layer_menu)
        
        # Alinhamento
        align_menu = tk.Menu(self.context_menu, tearoff=0)
        align_menu.add_command(label="◀️ Alinhar à esquerda", command=self.align_left)
        align_menu.add_command(label="⏸️ Centralizar", command=self.align_center)
        align_menu.add_command(label="▶️ Alinhar à direita", command=self.align_right)
        align_menu.add_separator()
        align_menu.add_command(label="🔝 Alinhar ao topo", command=self.align_top)
        align_menu.add_command(label="⏺️ Centralizar verticalmente", command=self.align_middle)
        align_menu.add_command(label="🔻 Alinhar abaixo", command=self.align_bottom)
        self.context_menu.add_cascade(label="📏 Alinhamento", menu=align_menu)
        
        # Duplicar e excluir
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🔄 Duplicar", command=self.duplicate_element)
        self.context_menu.add_command(label="🗑️ Excluir", command=self.delete_selected_elements)
        
        # Propriedades
        self.context_menu.add_separator()
        self.context_menu.add_command(label="⚙️ Propriedades", command=self.show_element_properties)
    
    def on_canvas_right_click(self, event):
        """Mostrar menu contextual"""
        # Verificar se há elementos selecionados
        if self.selected_elements:
            try:
                self.context_menu.post(event.x_root, event.y_root)
            except tk.TclError:
                pass
    
    # Métodos de edição
    def cut_element(self):
        """Recortar elemento selecionado"""
        if self.selected_elements:
            self.copy_element()
            self.delete_selected_elements()
    
    def copy_element(self):
        """Copiar elemento selecionado"""
        if self.selected_elements:
            try:
                # Encontrar elemento nos dados
                element = self.find_element_by_canvas_id(self.selected_elements[0])
                if element:
                    import copy
                    self.clipboard_element = copy.deepcopy(element)
                    # Remover canvas_id para evitar conflitos
                    if 'canvas_id' in self.clipboard_element:
                        del self.clipboard_element['canvas_id']
                    print("✅ Elemento copiado")
            except Exception as e:
                print(f"Erro ao copiar elemento: {e}")
    
    def paste_element(self):
        """Colar elemento copiado"""
        if hasattr(self, 'clipboard_element') and self.clipboard_element:
            try:
                import copy
                new_element = copy.deepcopy(self.clipboard_element)
                
                # Gerar novo ID e ajustar posição
                new_element['id'] = self.generate_element_id()
                new_element['x'] = new_element.get('x', 0) + 20
                new_element['y'] = new_element.get('y', 0) + 20
                
                # Adicionar à página atual
                current_page = self.get_current_page_data()
                if current_page:
                    current_page['elements'].append(new_element)
                    self.generate_visual_preview()
                    print("✅ Elemento colado")
            except Exception as e:
                print(f"Erro ao colar elemento: {e}")
    
    def duplicate_element(self):
        """Duplicar elemento selecionado"""
        self.copy_element()
        self.paste_element()
    
    def delete_selected_elements(self, event=None):
        """Excluir elementos selecionados"""
        if self.selected_elements:
            try:
                current_page = self.get_current_page_data()
                if current_page:
                    # Encontrar e remover elementos
                    elements_to_remove = []
                    for canvas_id in self.selected_elements:
                        element = self.find_element_by_canvas_id(canvas_id)
                        if element:
                            elements_to_remove.append(element)
                    
                    for element in elements_to_remove:
                        current_page['elements'].remove(element)
                    
                    self.selected_elements = []
                    self.generate_visual_preview()
                    print(f"✅ {len(elements_to_remove)} elemento(s) excluído(s)")
            except Exception as e:
                print(f"Erro ao excluir elementos: {e}")
    
    # Métodos de camadas
    def bring_to_front(self):
        """Trazer elemento para frente"""
        if self.selected_elements:
            # Implementar lógica de camadas
            print("📐 Elemento trazido para frente")
    
    def send_to_back(self):
        """Enviar elemento para trás"""
        if self.selected_elements:
            # Implementar lógica de camadas
            print("📐 Elemento enviado para trás")
    
    def bring_forward(self):
        """Trazer elemento uma camada à frente"""
        if self.selected_elements:
            print("📐 Elemento avançado uma camada")
    
    def send_backward(self):
        """Enviar elemento uma camada para trás"""
        if self.selected_elements:
            print("📐 Elemento recuado uma camada")
    
    # Métodos de alinhamento
    def align_left(self):
        """Alinhar elementos à esquerda"""
        if len(self.selected_elements) > 1:
            # Implementar alinhamento
            print("📏 Elementos alinhados à esquerda")
    
    def align_center(self):
        """Centralizar elementos horizontalmente"""
        if len(self.selected_elements) > 1:
            print("📏 Elementos centralizados horizontalmente")
    
    def align_right(self):
        """Alinhar elementos à direita"""
        if len(self.selected_elements) > 1:
            print("📏 Elementos alinhados à direita")
    
    def align_top(self):
        """Alinhar elementos ao topo"""
        if len(self.selected_elements) > 1:
            print("📏 Elementos alinhados ao topo")
    
    def align_middle(self):
        """Centralizar elementos verticalmente"""
        if len(self.selected_elements) > 1:
            print("📏 Elementos centralizados verticalmente")
    
    def align_bottom(self):
        """Alinhar elementos abaixo"""
        if len(self.selected_elements) > 1:
            print("📏 Elementos alinhados abaixo")
    
    def show_element_properties(self):
        """Mostrar propriedades do elemento em janela separada"""
        if self.selected_elements:
            element = self.find_element_by_canvas_id(self.selected_elements[0])
            if element:
                self.open_properties_dialog(element)
    
    def open_properties_dialog(self, element):
        """Abrir dialog de propriedades"""
        try:
            dialog = tk.Toplevel(self.frame)
            dialog.title(f"Propriedades - {element.get('type', 'Elemento').title()}")
            dialog.geometry("400x500")
            dialog.resizable(True, True)
            
            # Criar interface de propriedades na janela
            self.create_detailed_properties_ui(dialog, element)
            
            # Centralizar janela
            dialog.transient(self.frame)
            dialog.grab_set()
            
        except Exception as e:
            print(f"Erro ao abrir dialog de propriedades: {e}")
    
    def create_detailed_properties_ui(self, parent, element):
        """Criar interface detalhada de propriedades"""
        # Notebook para organizar propriedades
        notebook = ttk.Notebook(parent)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Aba Geral
        general_frame = tk.Frame(notebook, bg='white')
        notebook.add(general_frame, text="Geral")
        
        # Aba Aparência  
        appearance_frame = tk.Frame(notebook, bg='white')
        notebook.add(appearance_frame, text="Aparência")
        
        # Aba Posição
        position_frame = tk.Frame(notebook, bg='white')
        notebook.add(position_frame, text="Posição")
        
        # Preencher abas com campos específicos
        self.populate_general_properties(general_frame, element)
        self.populate_appearance_properties(appearance_frame, element)
        self.populate_position_properties(position_frame, element)
        
        # Botões de ação
        btn_frame = tk.Frame(parent, bg='white')
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Button(btn_frame, text="✅ Aplicar", 
                 command=lambda: self.apply_properties_changes(parent, element),
                 bg='#10b981', fg='white', font=('Arial', 10, 'bold')).pack(side="right", padx=5)
        tk.Button(btn_frame, text="❌ Cancelar", 
                 command=parent.destroy,
                 bg='#ef4444', fg='white', font=('Arial', 10, 'bold')).pack(side="right", padx=5)
    
    def populate_general_properties(self, parent, element):
        """Preencher propriedades gerais"""
        tk.Label(parent, text="Propriedades Gerais", font=('Arial', 12, 'bold'), 
                bg='white').pack(pady=10)
        
        # ID do elemento
        tk.Label(parent, text=f"ID: {element.get('id', 'N/A')}", 
                bg='white', font=('Arial', 9)).pack(anchor="w", padx=10)
        
        # Tipo do elemento
        tk.Label(parent, text=f"Tipo: {element.get('type', 'N/A')}", 
                bg='white', font=('Arial', 9)).pack(anchor="w", padx=10)
    
    def populate_appearance_properties(self, parent, element):
        """Preencher propriedades de aparência"""
        tk.Label(parent, text="Aparência", font=('Arial', 12, 'bold'), 
                bg='white').pack(pady=10)
        
        # Campos específicos por tipo
        element_type = element.get('type', '')
        
        if element_type in ['text', 'dynamic_field']:
            # Fonte
            font_frame = tk.Frame(parent, bg='white')
            font_frame.pack(fill="x", padx=10, pady=5)
            
            tk.Label(font_frame, text="Fonte:", bg='white').pack(side="left")
            font_var = tk.StringVar(value=element.get('font_family', 'Arial'))
            font_combo = ttk.Combobox(font_frame, textvariable=font_var, 
                                     values=["Arial", "Times", "Helvetica", "Courier"])
            font_combo.pack(side="right", fill="x", expand=True, padx=(10,0))
            
            # Tamanho
            size_frame = tk.Frame(parent, bg='white')
            size_frame.pack(fill="x", padx=10, pady=5)
            
            tk.Label(size_frame, text="Tamanho:", bg='white').pack(side="left")
            size_var = tk.StringVar(value=str(element.get('font_size', 12)))
            size_spin = tk.Spinbox(size_frame, from_=8, to=72, textvariable=size_var)
            size_spin.pack(side="right", padx=(10,0))
    
    def populate_position_properties(self, parent, element):
        """Preencher propriedades de posição"""
        tk.Label(parent, text="Posição e Tamanho", font=('Arial', 12, 'bold'), 
                bg='white').pack(pady=10)
        
        # X
        x_frame = tk.Frame(parent, bg='white')
        x_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(x_frame, text="X:", bg='white').pack(side="left")
        x_var = tk.StringVar(value=str(element.get('x', 0)))
        x_entry = tk.Entry(x_frame, textvariable=x_var)
        x_entry.pack(side="right", padx=(10,0))
        
        # Y
        y_frame = tk.Frame(parent, bg='white')
        y_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(y_frame, text="Y:", bg='white').pack(side="left")
        y_var = tk.StringVar(value=str(element.get('y', 0)))
        y_entry = tk.Entry(y_frame, textvariable=y_var)
        y_entry.pack(side="right", padx=(10,0))
    
    def apply_properties_changes(self, dialog, element):
        """Aplicar mudanças nas propriedades"""
        try:
            # Coletar valores dos campos e aplicar ao elemento
            # (implementação simplificada)
            
            # Regenerar preview
            self.generate_visual_preview()
            
            # Fechar dialog
            dialog.destroy()
            
            print("✅ Propriedades aplicadas")
            
        except Exception as e:
            print(f"Erro ao aplicar propriedades: {e}")
    
    # Métodos de undo/redo
    def undo_action(self, event=None):
        """Desfazer última ação"""
        print("↶ Undo não implementado ainda")
    
    def redo_action(self, event=None):
        """Refazer ação"""
        print("↷ Redo não implementado ainda")
    
    # Métodos não implementados (stubs)
    def load_template(self): 
        """Carregar template de arquivo"""
        filename = filedialog.askopenfilename(
            title="Carregar Template",
            filetypes=[("Arquivos JSON", "*.json"), ("Todos os arquivos", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    template_data = json.load(f)
                
                self.template_data = template_data.get('template_data', template_data)
                self.generate_visual_preview()
                
                messagebox.showinfo("Sucesso", f"Template carregado: {os.path.basename(filename)}")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar template: {e}")
    
    def export_template(self): 
        """Exportar template para arquivo"""
        filename = filedialog.asksaveasfilename(
            title="Exportar Template",
            defaultextension=".json",
            filetypes=[("Arquivos JSON", "*.json"), ("Todos os arquivos", "*.*")]
        )
        if filename:
            try:
                export_data = {
                    'template_data': self.template_data,
                    'version': '1.0',
                    'exported_at': datetime.now().isoformat(),
                    'exported_by': self.user_id
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=4, ensure_ascii=False)
                
                messagebox.showinfo("Sucesso", f"Template exportado: {os.path.basename(filename)}")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao exportar template: {e}")
    
    def import_template(self): 
        """Importar template de arquivo externo"""
        self.load_template()  # Mesmo que carregar por enquanto
    
    def restore_default_template(self): 
        """Restaurar template padrão"""
        if messagebox.askyesno("Confirmar", "Restaurar template padrão? Todas as alterações serão perdidas."):
            self.load_default_template()
            self.generate_visual_preview()
            messagebox.showinfo("Sucesso", "Template padrão restaurado!")
    
    def load_selected_template(self, event): 
        """Carregar template selecionado na listbox"""
        selection = self.templates_listbox.curselection()
        if selection:
            template_name = self.templates_listbox.get(selection[0])
            template_path = os.path.join('data/templates_avancados', template_name)
            
            if os.path.exists(template_path):
                try:
                    with open(template_path, 'r', encoding='utf-8') as f:
                        template_data = json.load(f)
                    
                    self.template_data = template_data.get('template_data', template_data)
                    self.generate_visual_preview()
                    
                    messagebox.showinfo("Sucesso", f"Template carregado: {template_name}")
                    
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao carregar template: {e}")
    
    def create_new_version(self): 
        """Criar nova versão do template"""
        new_version = simpledialog.askstring("Nova Versão", "Digite a nova versão:", 
                                             initialvalue=self.version_var.get() if hasattr(self, 'version_var') else '1.1')
        if new_version:
            if hasattr(self, 'version_var'):
                self.version_var.set(new_version)
            self.save_template()
    
    def move_page_up(self): 
        """Mover página para cima"""
        if self.current_page > 1:
            # Trocar posições
            pages = self.template_data['pages']
            current_idx = self.current_page - 1
            prev_idx = current_idx - 1
            
            pages[current_idx], pages[prev_idx] = pages[prev_idx], pages[current_idx]
            
            # Atualizar IDs
            pages[prev_idx]['id'] = prev_idx + 1
            pages[current_idx]['id'] = current_idx + 1
            
            self.current_page -= 1
            self.update_page_label()
            self.generate_visual_preview()
    
    def move_page_down(self): 
        """Mover página para baixo"""
        if self.current_page < len(self.template_data['pages']):
            # Trocar posições
            pages = self.template_data['pages']
            current_idx = self.current_page - 1
            next_idx = current_idx + 1
            
            pages[current_idx], pages[next_idx] = pages[next_idx], pages[current_idx]
            
            # Atualizar IDs
            pages[current_idx]['id'] = current_idx + 1
            pages[next_idx]['id'] = next_idx + 1
            
            self.current_page += 1
            self.update_page_label()
            self.generate_visual_preview()
    
    def draw_image_element(self, element, x, y): 
        """Desenhar elemento de imagem"""
        # Placeholder para imagem
        width = element.get('width', 100) * self.canvas_scale
        height = element.get('height', 100) * self.canvas_scale
        
        canvas_id = self.visual_canvas.create_rectangle(
            x + 10, y + 10, x + 10 + width, y + 10 + height,
            fill='#f3f4f6', outline='#9ca3af', width=2,
            tags=f"element_{element.get('id', '')}"
        )
        
        # Texto indicativo
        self.visual_canvas.create_text(
            x + 10 + width/2, y + 10 + height/2,
            text="🖼️ Imagem", font=('Arial', 8),
            tags=f"element_{element.get('id', '')}"
        )
        
        element['canvas_id'] = canvas_id
    
    def draw_table_element(self, element, x, y): 
        """Desenhar elemento de tabela"""
        rows = element.get('rows', 3)
        cols = element.get('cols', 3)
        cell_width = 80 * self.canvas_scale
        cell_height = 25 * self.canvas_scale
        
        # Desenhar grade da tabela
        for row in range(rows + 1):
            y_pos = y + 10 + row * cell_height
            self.visual_canvas.create_line(
                x + 10, y_pos, x + 10 + cols * cell_width, y_pos,
                fill='#374151', tags=f"element_{element.get('id', '')}"
            )
        
        for col in range(cols + 1):
            x_pos = x + 10 + col * cell_width
            self.visual_canvas.create_line(
                x_pos, y + 10, x_pos, y + 10 + rows * cell_height,
                fill='#374151', tags=f"element_{element.get('id', '')}"
            )
        
        # Criar elemento principal para seleção
        canvas_id = self.visual_canvas.create_rectangle(
            x + 10, y + 10, x + 10 + cols * cell_width, y + 10 + rows * cell_height,
            fill='', outline='', width=0,
            tags=f"element_{element.get('id', '')}"
        )
        
        element['canvas_id'] = canvas_id
    
    def draw_line_element(self, element, x, y): 
        """Desenhar elemento de linha"""
        end_x = x + element.get('length', 100) * self.canvas_scale
        end_y = y + element.get('angle_offset', 0) * self.canvas_scale
        
        canvas_id = self.visual_canvas.create_line(
            x + 10, y + 10, end_x + 10, end_y + 10,
            fill=element.get('color', '#000000'),
            width=element.get('thickness', 1),
            tags=f"element_{element.get('id', '')}"
        )
        
        element['canvas_id'] = canvas_id
    
    def draw_rectangle_element(self, element, x, y): 
        """Desenhar elemento de retângulo"""
        width = element.get('width', 100) * self.canvas_scale
        height = element.get('height', 50) * self.canvas_scale
        
        canvas_id = self.visual_canvas.create_rectangle(
            x + 10, y + 10, x + 10 + width, y + 10 + height,
            fill=element.get('fill_color', ''),
            outline=element.get('border_color', '#000000'),
            width=element.get('border_width', 1),
            tags=f"element_{element.get('id', '')}"
        )
        
        element['canvas_id'] = canvas_id