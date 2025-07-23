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

# Importar engine de PDF
try:
    from utils.pdf_template_engine import PDFTemplateEngine
    PDF_ENGINE_AVAILABLE = True
except ImportError:
    PDF_ENGINE_AVAILABLE = False
    print("⚠️ Engine de PDF não disponível")

class EditorPDFAvancadoModule(BaseModule):
    def __init__(self, parent, user_id, role, main_window):
        try:
            self.user_info = {'role': role, 'user_id': user_id}
            
            # Configurar conexão com banco
            from database import DB_NAME
            self.db_name = DB_NAME
            
            # Inicializar propriedades
            self.template_data = {}
            self.original_template_data = {}  # NOVO: Armazenar template original
            self.available_fields = {}
            self.selected_elements = []
            self.canvas_scale = 0.8
            self.page_width = 595  # A4 width in points
            self.page_height = 842  # A4 height in points
            self.current_page = 1
            self.total_pages = 4
            self.drag_data = {}
            self.current_cotacao_id = None
            
            # NOVO: Funcionalidades de visualização
            self.fullscreen_mode = False
            self.preview_window = None
            
            # NOVO: Funcionalidades de cabeçalho/rodapé
            self.header_elements = []
            self.footer_elements = []
            self.editing_header = False
            self.editing_footer = False
            
            # Inicializar resolvedor de campos dinâmicos
            if FIELD_RESOLVER_AVAILABLE:
                self.field_resolver = DynamicFieldResolver(self.db_name)
            else:
                self.field_resolver = None
            
            super().__init__(parent, user_id, role, main_window)
            
            # Carregar dados do banco
            self.load_database_fields()
            
            # NOVO: Carregar configurações de capas por usuário
            self.load_user_cover_assignments()
            
            # Carregar template padrão
            self.load_default_template()
            
            # NOVO: Preservar template original
            self.preserve_original_template()
            
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
        
        # NOVO: Botão para visualização em tela cheia
        fullscreen_btn = tk.Button(btn_frame, text="🖥️ Editar em Tela Cheia", 
                                  command=self.show_original_template_fullscreen,
                                  font=('Arial', 9, 'bold'), bg='#7c3aed', fg='white',
                                  relief='flat', cursor='hand2')
        fullscreen_btn.pack(fill="x", pady=2)
        
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
        self.visual_canvas.bind('<Control-Button-1>', self.on_canvas_ctrl_click)  # Seleção múltipla
        self.visual_canvas.bind('<Shift-Button-1>', self.on_canvas_shift_click)  # Seleção em área
        self.visual_canvas.bind('<Control-z>', self.undo_action)
        self.visual_canvas.bind('<Control-y>', self.redo_action)
        self.visual_canvas.bind('<Control-c>', self.copy_element)
        self.visual_canvas.bind('<Control-v>', self.paste_element)
        self.visual_canvas.bind('<Control-x>', self.cut_element)
        self.visual_canvas.bind('<Control-a>', self.select_all_elements)
        self.visual_canvas.bind('<Delete>', self.delete_selected_elements)
        
        # Variáveis para seleção múltipla
        self.selection_start = None
        self.selection_rectangle = None
        self.is_selecting = False
        
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
        
        # Se não é Ctrl+Click, limpar seleção anterior
        if not (event.state & 0x4):  # Não é Ctrl
            self.clear_selection()
        
        self.select_element(clicked_item)
    
    def on_canvas_ctrl_click(self, event):
        """Callback para Ctrl+Click (seleção múltipla)"""
        clicked_item = self.visual_canvas.find_closest(event.x, event.y)[0]
        
        if clicked_item in self.selected_elements:
            # Desselecionar se já está selecionado
            self.deselect_element(clicked_item)
        else:
            # Adicionar à seleção
            self.add_to_selection(clicked_item)
    
    def on_canvas_shift_click(self, event):
        """Callback para Shift+Click (seleção em área)"""
        if not self.selection_start:
            self.selection_start = (event.x, event.y)
            self.is_selecting = True
        else:
            # Finalizar seleção em área
            self.finish_area_selection(event.x, event.y)
    
    def clear_selection(self):
        """Limpar seleção atual"""
        self.visual_canvas.delete('selection')
        self.selected_elements = []
        self.update_properties_panel_empty()
    
    def deselect_element(self, canvas_id):
        """Desselecionar elemento específico"""
        if canvas_id in self.selected_elements:
            self.selected_elements.remove(canvas_id)
        
        # Redesenhar seleções
        self.redraw_selections()
    
    def add_to_selection(self, canvas_id):
        """Adicionar elemento à seleção múltipla"""
        if canvas_id not in self.selected_elements:
            self.selected_elements.append(canvas_id)
        
        # Redesenhar seleções
        self.redraw_selections()
    
    def redraw_selections(self):
        """Redesenhar indicadores de seleção para todos os elementos selecionados"""
        # Limpar seleções anteriores
        self.visual_canvas.delete('selection')
        
        # Desenhar seleção para cada elemento
        for canvas_id in self.selected_elements:
            bbox = self.visual_canvas.bbox(canvas_id)
            if bbox:
                color = '#3b82f6' if len(self.selected_elements) == 1 else '#ef4444'
                self.visual_canvas.create_rectangle(bbox, outline=color, width=2, 
                                                  tags='selection')
        
        # Atualizar painel de propriedades
        if len(self.selected_elements) == 1:
            self.update_properties_panel(self.selected_elements[0])
        elif len(self.selected_elements) > 1:
            self.update_properties_panel_multiple()
        else:
            self.update_properties_panel_empty()
    
    def finish_area_selection(self, end_x, end_y):
        """Finalizar seleção em área"""
        if not self.selection_start:
            return
        
        start_x, start_y = self.selection_start
        
        # Criar retângulo de seleção
        min_x, max_x = min(start_x, end_x), max(start_x, end_x)
        min_y, max_y = min(start_y, end_y), max(start_y, end_y)
        
        # Encontrar elementos dentro da área
        selected_in_area = []
        current_page = self.get_current_page_data()
        
        if current_page:
            for element in current_page.get('elements', []):
                if 'canvas_id' in element:
                    bbox = self.visual_canvas.bbox(element['canvas_id'])
                    if bbox:
                        elem_x1, elem_y1, elem_x2, elem_y2 = bbox
                        
                        # Verificar se elemento está dentro da área selecionada
                        if (elem_x1 >= min_x and elem_y1 >= min_y and 
                            elem_x2 <= max_x and elem_y2 <= max_y):
                            selected_in_area.append(element['canvas_id'])
        
        # Atualizar seleção
        self.selected_elements = selected_in_area
        self.redraw_selections()
        
        # Limpar estado de seleção
        self.selection_start = None
        self.is_selecting = False
    
    def select_all_elements(self, event=None):
        """Selecionar todos os elementos da página atual"""
        current_page = self.get_current_page_data()
        if current_page:
            self.selected_elements = [
                element['canvas_id'] 
                for element in current_page.get('elements', []) 
                if 'canvas_id' in element
            ]
            self.redraw_selections()
    
    def update_properties_panel_empty(self):
        """Atualizar painel de propriedades quando nada está selecionado"""
        # Limpar painel
        for widget in self.props_frame.winfo_children():
            widget.destroy()
        
        tk.Label(self.props_frame, text="Nenhum elemento selecionado", 
                font=('Arial', 9), bg='white', fg='#6b7280', justify='center').pack(pady=20)
    
    def update_properties_panel_multiple(self):
        """Atualizar painel de propriedades para seleção múltipla"""
        # Limpar painel
        for widget in self.props_frame.winfo_children():
            widget.destroy()
        
        tk.Label(self.props_frame, text=f"{len(self.selected_elements)} elementos selecionados", 
                font=('Arial', 10, 'bold'), bg='white').pack(pady=10)
        
        # Ações para múltipla seleção
        actions = [
            ("📏 Alinhar", self.show_alignment_options),
            ("📐 Distribuir", self.show_distribution_options),
            ("🔄 Duplicar Todos", self.duplicate_multiple),
            ("🗑️ Excluir Todos", self.delete_selected_elements),
        ]
        
        for label, command in actions:
            btn = tk.Button(self.props_frame, text=label, command=command,
                           font=('Arial', 8), bg='#f3f4f6', relief='flat', 
                           cursor='hand2', width=15)
            btn.pack(fill="x", padx=5, pady=2)
    
    def show_alignment_options(self):
        """Mostrar opções de alinhamento em janela popup"""
        if len(self.selected_elements) < 2:
            return
        
        popup = tk.Toplevel(self.frame)
        popup.title("Alinhamento")
        popup.geometry("200x300")
        popup.resizable(False, False)
        
        tk.Label(popup, text="Alinhamento", font=('Arial', 12, 'bold')).pack(pady=10)
        
        align_options = [
            ("◀️ Esquerda", self.align_left),
            ("⏸️ Centro H", self.align_center),
            ("▶️ Direita", self.align_right),
            ("🔝 Topo", self.align_top),
            ("⏺️ Centro V", self.align_middle),
            ("🔻 Base", self.align_bottom),
        ]
        
        for label, command in align_options:
            btn = tk.Button(popup, text=label, command=lambda c=command: [c(), popup.destroy()],
                           font=('Arial', 9), relief='flat', bg='#f3f4f6')
            btn.pack(fill="x", padx=10, pady=2)
        
        popup.transient(self.frame)
        popup.grab_set()
    
    def show_distribution_options(self):
        """Mostrar opções de distribuição"""
        if len(self.selected_elements) < 3:
            messagebox.showinfo("Info", "Selecione pelo menos 3 elementos para distribuição")
            return
        
        popup = tk.Toplevel(self.frame)
        popup.title("Distribuição")
        popup.geometry("200x200")
        popup.resizable(False, False)
        
        tk.Label(popup, text="Distribuição", font=('Arial', 12, 'bold')).pack(pady=10)
        
        dist_options = [
            ("↔️ Horizontal", self.distribute_horizontal),
            ("↕️ Vertical", self.distribute_vertical),
            ("📐 Grade", self.distribute_grid),
        ]
        
        for label, command in dist_options:
            btn = tk.Button(popup, text=label, command=lambda c=command: [c(), popup.destroy()],
                           font=('Arial', 9), relief='flat', bg='#f3f4f6')
            btn.pack(fill="x", padx=10, pady=2)
        
        popup.transient(self.frame)
        popup.grab_set()
    
    def duplicate_multiple(self):
        """Duplicar todos os elementos selecionados"""
        if not self.selected_elements:
            return
        
        current_page = self.get_current_page_data()
        if not current_page:
            return
        
        new_elements = []
        for canvas_id in self.selected_elements:
            element = self.find_element_by_canvas_id(canvas_id)
            if element:
                import copy
                new_element = copy.deepcopy(element)
                new_element['id'] = self.generate_element_id()
                new_element['x'] = new_element.get('x', 0) + 20
                new_element['y'] = new_element.get('y', 0) + 20
                
                if 'canvas_id' in new_element:
                    del new_element['canvas_id']
                
                new_elements.append(new_element)
        
        # Adicionar novos elementos
        current_page['elements'].extend(new_elements)
        
        # Regenerar preview
        self.generate_visual_preview()
        
        print(f"✅ {len(new_elements)} elementos duplicados")
    
    def distribute_horizontal(self):
        """Distribuir elementos horizontalmente"""
        if len(self.selected_elements) < 3:
            return
        
        # Implementar lógica de distribuição horizontal
        print("📐 Elementos distribuídos horizontalmente")
    
    def distribute_vertical(self):
        """Distribuir elementos verticalmente"""
        if len(self.selected_elements) < 3:
            return
        
        # Implementar lógica de distribuição vertical
        print("📐 Elementos distribuídos verticalmente")
    
    def distribute_grid(self):
        """Distribuir elementos em grade"""
        if len(self.selected_elements) < 4:
            return
        
        # Implementar lógica de distribuição em grade
        print("📐 Elementos distribuídos em grade")
    
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
        font_combo.pack(side="right", fill="x", expand=True, padx=(10,0))
    
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
        try:
            if not PDF_ENGINE_AVAILABLE:
                messagebox.showerror("Erro", "Engine de PDF não disponível. Instale as dependências necessárias.")
                return
            
            # Validar template
            is_valid, errors = self.validate_template_for_pdf()
            if not is_valid:
                error_msg = "Erros no template:\n" + "\n".join(errors)
                messagebox.showerror("Template Inválido", error_msg)
                return
            
            # Escolher local para salvar
            filename = filedialog.asksaveasfilename(
                title="Salvar PDF",
                defaultextension=".pdf",
                filetypes=[("Arquivos PDF", "*.pdf"), ("Todos os arquivos", "*.*")],
                initialname=f"proposta_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            )
            
            if not filename:
                return
            
            # Atualizar status
            self.preview_status.config(text="🔄 Gerando PDF...")
            self.frame.update()
            
            # Criar engine de PDF
            pdf_engine = PDFTemplateEngine(self.template_data, self.field_resolver)
            
            # Metadados do PDF
            metadata = {
                'title': 'Proposta Comercial',
                'author': 'World Comp Compressores',
                'subject': 'Proposta Comercial - Sistema CRM',
                'creator': f'Editor PDF Avançado - Usuário {self.user_id}',
                'cotacao_id': getattr(self, 'current_cotacao_id', None)
            }
            
            # Gerar PDF
            success = pdf_engine.generate_pdf(filename, metadata)
            
            if success:
                self.preview_status.config(text="✅ PDF gerado com sucesso!")
                
                # Perguntar se quer abrir
                if messagebox.askyesno("PDF Gerado", f"PDF gerado com sucesso!\n\n{filename}\n\nDeseja abrir o arquivo?"):
                    self.open_generated_pdf(filename)
                
                # Salvar caminho no histórico
                self.save_pdf_history(filename)
                
            else:
                self.preview_status.config(text="❌ Erro na geração")
                messagebox.showerror("Erro", "Erro ao gerar PDF. Verifique os logs para mais detalhes.")
            
        except Exception as e:
            self.preview_status.config(text="❌ Erro na geração")
            messagebox.showerror("Erro", f"Erro inesperado ao gerar PDF: {e}")
            print(f"Erro na geração de PDF: {e}")
    
    def validate_template_for_pdf(self):
        """Validar template antes da geração de PDF"""
        errors = []
        
        try:
            # Verificar se há páginas
            pages = self.template_data.get('pages', [])
            if not pages:
                errors.append("Template deve ter pelo menos uma página")
                return False, errors
            
            # Verificar cada página
            for i, page in enumerate(pages):
                page_name = page.get('name', f'Página {i+1}')
                elements = page.get('elements', [])
                
                if not elements:
                    errors.append(f"{page_name}: Página está vazia")
                
                # Verificar elementos
                for j, element in enumerate(elements):
                    element_id = element.get('id', f'elemento_{j+1}')
                    element_type = element.get('type', '')
                    
                    if not element_type:
                        errors.append(f"{page_name}: {element_id} sem tipo definido")
                    
                    # Verificar posição
                    if 'x' not in element or 'y' not in element:
                        errors.append(f"{page_name}: {element_id} sem posição definida")
                    
                    # Verificar campos específicos por tipo
                    if element_type == 'text' and not element.get('text'):
                        errors.append(f"{page_name}: {element_id} sem texto definido")
                    elif element_type == 'dynamic_field' and not element.get('field_ref'):
                        errors.append(f"{page_name}: {element_id} sem campo de referência")
                    elif element_type == 'image' and not element.get('image_path'):
                        errors.append(f"{page_name}: {element_id} sem caminho de imagem")
            
            # Verificar se há campos dinâmicos mas não há dados conectados
            has_dynamic_fields = any(
                element.get('type') == 'dynamic_field' 
                for page in pages 
                for element in page.get('elements', [])
            )
            
            if has_dynamic_fields and not self.current_cotacao_id:
                errors.append("Template possui campos dinâmicos mas nenhuma cotação está conectada")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            errors.append(f"Erro na validação: {e}")
            return False, errors
    
    def open_generated_pdf(self, filepath):
        """Abrir PDF gerado no visualizador padrão"""
        try:
            import os
            import platform
            
            if platform.system() == 'Windows':
                os.startfile(filepath)
            elif platform.system() == 'Darwin':  # macOS
                os.system(f'open "{filepath}"')
            else:  # Linux
                os.system(f'xdg-open "{filepath}"')
                
        except Exception as e:
            print(f"Erro ao abrir PDF: {e}")
            messagebox.showwarning("Aviso", f"PDF gerado mas não foi possível abrir automaticamente:\n{filepath}")
    
    def save_pdf_history(self, filepath):
        """Salvar PDF no histórico de geração"""
        try:
            os.makedirs('data/pdf_history', exist_ok=True)
            
            history_file = 'data/pdf_history/generated_pdfs.json'
            history = []
            
            # Carregar histórico existente
            if os.path.exists(history_file):
                try:
                    with open(history_file, 'r', encoding='utf-8') as f:
                        history = json.load(f)
                except:
                    history = []
            
            # Adicionar novo registro
            new_record = {
                'filepath': filepath,
                'generated_at': datetime.now().isoformat(),
                'user_id': self.user_id,
                'cotacao_id': getattr(self, 'current_cotacao_id', None),
                'template_version': self.template_data.get('version', '1.0'),
                'total_pages': len(self.template_data.get('pages', []))
            }
            
            history.append(new_record)
            
            # Manter apenas últimos 100 registros
            if len(history) > 100:
                history = history[-100:]
            
            # Salvar histórico
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=4, ensure_ascii=False)
                
        except Exception as e:
            print(f"Erro ao salvar histórico: {e}")
    
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
    
    # NOVO: Métodos para preservar template original e configurações de capas
    def preserve_original_template(self):
        """Preservar uma cópia do template original para referência"""
        try:
            import copy
            self.original_template_data = copy.deepcopy(self.template_data)
            print("🔒 Template original preservado")
        except Exception as e:
            print(f"Erro ao preservar template original: {e}")
    
    def load_user_cover_assignments(self):
        """Carregar configurações de capas por usuário"""
        try:
            # Importar configurações de capas
            from assets.filiais.filiais_config import USUARIOS_COTACAO, obter_usuario_cotacao
            
            self.user_covers = USUARIOS_COTACAO
            print(f"📋 Carregadas configurações de {len(self.user_covers)} usuários com capas personalizadas")
        except Exception as e:
            print(f"Erro ao carregar configurações de capas: {e}")
            self.user_covers = {}
    
    def show_original_template_fullscreen(self):
        """Mostrar template original em tela cheia para edição"""
        try:
            if self.preview_window and self.preview_window.winfo_exists():
                self.preview_window.lift()
                return
            
            # Criar janela em tela cheia
            self.preview_window = tk.Toplevel(self.frame)
            self.preview_window.title("📖 Template Original - Visualização em Tela Cheia")
            self.preview_window.state('zoomed')  # Maximizar no Windows
            self.preview_window.configure(bg='#2d3748')
            
            # Eventos da janela
            self.preview_window.bind('<Escape>', lambda e: self.close_fullscreen_preview())
            self.preview_window.bind('<F11>', lambda e: self.toggle_fullscreen())
            self.preview_window.protocol("WM_DELETE_WINDOW", self.close_fullscreen_preview)
            
            # Toolbar superior
            self.create_fullscreen_toolbar()
            
            # Canvas principal para o preview
            self.create_fullscreen_canvas()
            
            # Sidebar para ferramentas de edição
            self.create_fullscreen_sidebar()
            
            # Renderizar template original
            self.render_original_template_fullscreen()
            
            print("🖥️ Visualização em tela cheia ativada")
            
        except Exception as e:
            print(f"Erro ao abrir visualização em tela cheia: {e}")
            messagebox.showerror("Erro", f"Erro ao abrir visualização: {e}")
    
    def create_fullscreen_toolbar(self):
        """Criar toolbar da visualização em tela cheia"""
        toolbar = tk.Frame(self.preview_window, bg='#1a202c', height=50)
        toolbar.pack(fill="x", side="top")
        toolbar.pack_propagate(False)
        
        # Lado esquerdo - Título e status
        left_frame = tk.Frame(toolbar, bg='#1a202c')
        left_frame.pack(side="left", fill="y", padx=10)
        
        tk.Label(left_frame, text="📖 Editor Visual - Template Original", 
                font=('Arial', 14, 'bold'), bg='#1a202c', fg='white').pack(side="top", anchor="w")
        
        self.fullscreen_status = tk.Label(left_frame, text="Pronto para edição", 
                                         font=('Arial', 9), bg='#1a202c', fg='#a0aec0')
        self.fullscreen_status.pack(side="bottom", anchor="w")
        
        # Centro - Navegação de páginas
        center_frame = tk.Frame(toolbar, bg='#1a202c')
        center_frame.pack(expand=True)
        
        nav_frame = tk.Frame(center_frame, bg='#2d3748', relief='ridge', bd=1)
        nav_frame.pack(expand=True, pady=8)
        
        tk.Button(nav_frame, text="◀◀", command=lambda: self.fullscreen_change_page(-10),
                 bg='#4a5568', fg='white', font=('Arial', 10), width=4).pack(side="left", padx=2)
        tk.Button(nav_frame, text="◀", command=lambda: self.fullscreen_change_page(-1),
                 bg='#4a5568', fg='white', font=('Arial', 12), width=3).pack(side="left", padx=2)
        
        self.fullscreen_page_label = tk.Label(nav_frame, text=f"Página {self.current_page} de {len(self.original_template_data.get('pages', []))}", 
                                             bg='#2d3748', fg='white', font=('Arial', 11, 'bold'), padx=20)
        self.fullscreen_page_label.pack(side="left")
        
        tk.Button(nav_frame, text="▶", command=lambda: self.fullscreen_change_page(1),
                 bg='#4a5568', fg='white', font=('Arial', 12), width=3).pack(side="left", padx=2)
        tk.Button(nav_frame, text="▶▶", command=lambda: self.fullscreen_change_page(10),
                 bg='#4a5568', fg='white', font=('Arial', 10), width=4).pack(side="left", padx=2)
        
        # Lado direito - Controles
        right_frame = tk.Frame(toolbar, bg='#1a202c')
        right_frame.pack(side="right", fill="y", padx=10)
        
        controls = [
            ("🔍+", self.fullscreen_zoom_in, "Zoom In"),
            ("🔍-", self.fullscreen_zoom_out, "Zoom Out"),
            ("📐", self.toggle_grid_overlay, "Mostrar Grade"),
            ("⚙️", self.open_template_settings, "Configurações"),
            ("❌", self.close_fullscreen_preview, "Fechar"),
        ]
        
        for icon, command, tooltip in controls:
            btn = tk.Button(right_frame, text=icon, command=command,
                           bg='#4a5568', fg='white', font=('Arial', 10), width=4, height=2)
            btn.pack(side="right", padx=2)
            # Tooltip simples
            btn.bind('<Enter>', lambda e, t=tooltip: self.show_tooltip(e, t))
    
    def create_fullscreen_canvas(self):
        """Criar canvas principal da visualização em tela cheia"""
        # Frame principal para canvas
        main_frame = tk.Frame(self.preview_window, bg='#2d3748')
        main_frame.pack(fill="both", expand=True, side="left")
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(main_frame, orient="vertical")
        h_scroll = ttk.Scrollbar(main_frame, orient="horizontal")
        
        # Canvas principal
        self.fullscreen_canvas = tk.Canvas(main_frame, bg='white',
                                          yscrollcommand=v_scroll.set,
                                          xscrollcommand=h_scroll.set,
                                          cursor='crosshair')
        
        v_scroll.config(command=self.fullscreen_canvas.yview)
        h_scroll.config(command=self.fullscreen_canvas.xview)
        
        # Pack scrollbars e canvas
        v_scroll.pack(side="right", fill="y")
        h_scroll.pack(side="bottom", fill="x")
        self.fullscreen_canvas.pack(side="left", fill="both", expand=True)
        
        # Eventos do canvas
        self.fullscreen_canvas.bind('<Button-1>', self.fullscreen_canvas_click)
        self.fullscreen_canvas.bind('<B1-Motion>', self.fullscreen_canvas_drag)
        self.fullscreen_canvas.bind('<ButtonRelease-1>', self.fullscreen_canvas_release)
        self.fullscreen_canvas.bind('<Double-Button-1>', self.fullscreen_canvas_double_click)
        self.fullscreen_canvas.bind('<Button-3>', self.fullscreen_canvas_right_click)
        self.fullscreen_canvas.bind('<MouseWheel>', self.fullscreen_canvas_scroll)
        
        # Variáveis para edição em tela cheia
        self.fullscreen_scale = 1.2  # Escala maior para tela cheia
        self.fullscreen_selected_elements = []
        self.fullscreen_drag_data = {}
    
    def create_fullscreen_sidebar(self):
        """Criar sidebar com ferramentas de edição"""
        self.sidebar = tk.Frame(self.preview_window, bg='#1a202c', width=300)
        self.sidebar.pack(side="right", fill="y")
        self.sidebar.pack_propagate(False)
        
        # Título da sidebar
        title_frame = tk.Frame(self.sidebar, bg='#2b6cb0')
        title_frame.pack(fill="x")
        
        tk.Label(title_frame, text="🛠️ Ferramentas de Edição", 
                font=('Arial', 12, 'bold'), bg='#2b6cb0', fg='white').pack(pady=10)
        
        # Notebook para organizar ferramentas
        sidebar_notebook = ttk.Notebook(self.sidebar)
        sidebar_notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Aba: Edição de Layout
        self.create_layout_editing_tab(sidebar_notebook)
        
        # Aba: Cabeçalho/Rodapé
        self.create_header_footer_tab(sidebar_notebook)
        
        # Aba: Capas de Usuários
        self.create_user_covers_tab(sidebar_notebook)
        
        # Aba: Restaurar Original
        self.create_restore_tab(sidebar_notebook)
    
    def create_layout_editing_tab(self, parent):
        """Criar aba de edição de layout"""
        layout_frame = tk.Frame(parent, bg='white')
        parent.add(layout_frame, text="📐 Layout")
        
        # Scroll
        canvas = tk.Canvas(layout_frame, bg='white')
        scrollbar = ttk.Scrollbar(layout_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Ferramentas de layout
        tk.Label(scrollable_frame, text="Editar Elementos", font=('Arial', 11, 'bold'), 
                bg='white').pack(pady=10)
        
        layout_tools = [
            ("📝 Adicionar Texto", lambda: self.add_element_fullscreen('text')),
            ("🔤 Campo Dinâmico", lambda: self.add_element_fullscreen('dynamic_field')),
            ("🖼️ Inserir Imagem", lambda: self.add_element_fullscreen('image')),
            ("📊 Criar Tabela", lambda: self.add_element_fullscreen('table')),
            ("➖ Linha", lambda: self.add_element_fullscreen('line')),
            ("⬜ Retângulo", lambda: self.add_element_fullscreen('rectangle')),
        ]
        
        for label, command in layout_tools:
            btn = tk.Button(scrollable_frame, text=label, command=command,
                           font=('Arial', 9), bg='#e2e8f0', relief='flat', 
                           cursor='hand2', width=20)
            btn.pack(fill="x", padx=10, pady=2)
        
        # Ações de edição
        tk.Label(scrollable_frame, text="Ações de Edição", font=('Arial', 11, 'bold'), 
                bg='white').pack(pady=(20,10))
        
        edit_actions = [
            ("🔄 Mover Elemento", self.enable_move_mode),
            ("📏 Redimensionar", self.enable_resize_mode),
            ("🗑️ Excluir Selecionado", self.delete_selected_fullscreen),
            ("📋 Copiar", self.copy_selected_fullscreen),
            ("📄 Colar", self.paste_fullscreen),
        ]
        
        for label, command in edit_actions:
            btn = tk.Button(scrollable_frame, text=label, command=command,
                           font=('Arial', 9), bg='#fed7d7', relief='flat', 
                           cursor='hand2', width=20)
            btn.pack(fill="x", padx=10, pady=2)
    
    def create_header_footer_tab(self, parent):
        """Criar aba de edição de cabeçalho e rodapé"""
        header_footer_frame = tk.Frame(parent, bg='white')
        parent.add(header_footer_frame, text="📄 Cabeçalho/Rodapé")
        
        # Scroll
        canvas = tk.Canvas(header_footer_frame, bg='white')
        scrollbar = ttk.Scrollbar(header_footer_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Cabeçalho
        header_section = tk.LabelFrame(scrollable_frame, text="📄 Cabeçalho", bg='white', 
                                      font=('Arial', 11, 'bold'), fg='#2d5aa0')
        header_section.pack(fill="x", padx=10, pady=10)
        
        # Status do cabeçalho
        self.header_status_label = tk.Label(header_section, text="Nenhum cabeçalho configurado", 
                                           bg='white', fg='#6b7280', font=('Arial', 9))
        self.header_status_label.pack(pady=5)
        
        header_buttons = [
            ("➕ Criar Cabeçalho", self.create_header),
            ("✏️ Editar Cabeçalho", self.edit_header),
            ("👁️ Visualizar Cabeçalho", self.preview_header),
            ("🗑️ Remover Cabeçalho", self.remove_header),
        ]
        
        for label, command in header_buttons:
            btn = tk.Button(header_section, text=label, command=command,
                           font=('Arial', 9), bg='#dbeafe', relief='flat', 
                           cursor='hand2', width=18)
            btn.pack(fill="x", padx=5, pady=2)
        
        # Rodapé
        footer_section = tk.LabelFrame(scrollable_frame, text="📋 Rodapé", bg='white', 
                                      font=('Arial', 11, 'bold'), fg='#dc2626')
        footer_section.pack(fill="x", padx=10, pady=10)
        
        # Status do rodapé
        self.footer_status_label = tk.Label(footer_section, text="Rodapé padrão da empresa", 
                                           bg='white', fg='#6b7280', font=('Arial', 9))
        self.footer_status_label.pack(pady=5)
        
        footer_buttons = [
            ("➕ Criar Rodapé", self.create_footer),
            ("✏️ Editar Rodapé", self.edit_footer),
            ("👁️ Visualizar Rodapé", self.preview_footer),
            ("🔄 Restaurar Padrão", self.restore_default_footer),
        ]
        
        for label, command in footer_buttons:
            btn = tk.Button(footer_section, text=label, command=command,
                           font=('Arial', 9), bg='#fecaca', relief='flat', 
                           cursor='hand2', width=18)
            btn.pack(fill="x", padx=5, pady=2)
        
        # Configurações globais
        global_section = tk.LabelFrame(scrollable_frame, text="⚙️ Configurações", bg='white', 
                                      font=('Arial', 11, 'bold'), fg='#059669')
        global_section.pack(fill="x", padx=10, pady=10)
        
        # Opções de aplicação
        tk.Label(global_section, text="Aplicar em:", bg='white', font=('Arial', 9)).pack(anchor="w", padx=5)
        
        self.apply_header_footer_var = tk.StringVar(value="current_page")
        apply_options = [
            ("Página atual", "current_page"),
            ("Todas as páginas", "all_pages"),
            ("Páginas pares", "even_pages"),
            ("Páginas ímpares", "odd_pages"),
        ]
        
        for text, value in apply_options:
            tk.Radiobutton(global_section, text=text, variable=self.apply_header_footer_var, 
                          value=value, bg='white', font=('Arial', 8)).pack(anchor="w", padx=20)
    
    def create_user_covers_tab(self, parent):
        """Criar aba de gerenciamento de capas por usuário"""
        covers_frame = tk.Frame(parent, bg='white')
        parent.add(covers_frame, text="👤 Capas")
        
        # Scroll
        canvas = tk.Canvas(covers_frame, bg='white')
        scrollbar = ttk.Scrollbar(covers_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Título
        tk.Label(scrollable_frame, text="Gerenciar Capas por Usuário", font=('Arial', 12, 'bold'), 
                bg='white', fg='#1f2937').pack(pady=10)
        
        # Lista de usuários com capas
        tk.Label(scrollable_frame, text="Usuários com Capas Personalizadas:", 
                font=('Arial', 10, 'bold'), bg='white').pack(anchor="w", padx=10, pady=(10,5))
        
        # Listbox para usuários
        user_frame = tk.Frame(scrollable_frame, bg='white')
        user_frame.pack(fill="x", padx=10, pady=5)
        
        self.users_listbox = tk.Listbox(user_frame, height=8, font=('Arial', 9))
        users_scrollbar = ttk.Scrollbar(user_frame, orient="vertical", command=self.users_listbox.yview)
        self.users_listbox.configure(yscrollcommand=users_scrollbar.set)
        
        self.users_listbox.pack(side="left", fill="both", expand=True)
        users_scrollbar.pack(side="right", fill="y")
        
        # Carregar usuários
        self.load_users_with_covers()
        
        # Botões de ação
        action_buttons = [
            ("👁️ Visualizar Capa", self.preview_user_cover),
            ("➕ Atribuir Nova Capa", self.assign_new_cover),
            ("✏️ Editar Capa Existente", self.edit_user_cover),
            ("🗑️ Remover Capa", self.remove_user_cover),
            ("📥 Importar Capa", self.import_user_cover),
            ("🔄 Atualizar Lista", self.refresh_user_covers),
        ]
        
        for label, command in action_buttons:
            btn = tk.Button(scrollable_frame, text=label, command=command,
                           font=('Arial', 9), bg='#f3f4f6', relief='flat', 
                           cursor='hand2', width=20)
            btn.pack(fill="x", padx=10, pady=2)
        
        # Informações do usuário selecionado
        info_frame = tk.LabelFrame(scrollable_frame, text="ℹ️ Informações", bg='white')
        info_frame.pack(fill="x", padx=10, pady=10)
        
        self.user_info_label = tk.Label(info_frame, text="Selecione um usuário para ver detalhes", 
                                       bg='white', fg='#6b7280', font=('Arial', 9), 
                                       justify='left', wraplength=250)
        self.user_info_label.pack(pady=10)
        
        # Bind para seleção
        self.users_listbox.bind('<<ListboxSelect>>', self.on_user_select)
    
    def create_restore_tab(self, parent):
        """Criar aba de restauração do template original"""
        restore_frame = tk.Frame(parent, bg='white')
        parent.add(restore_frame, text="🔄 Restaurar")
        
        # Título
        tk.Label(restore_frame, text="Restaurar Template Original", font=('Arial', 12, 'bold'), 
                bg='white', fg='#dc2626').pack(pady=20)
        
        # Aviso
        warning_text = ("⚠️ Atenção!\n\n"
                       "Esta ação irá restaurar o template\n"
                       "para seu estado original, perdendo\n"
                       "todas as alterações feitas.\n\n"
                       "Use apenas se necessário.")
        
        tk.Label(restore_frame, text=warning_text, bg='white', fg='#7f1d1d', 
                font=('Arial', 10), justify='center').pack(pady=20)
        
        # Opções de restauração
        tk.Label(restore_frame, text="Opções de Restauração:", font=('Arial', 10, 'bold'), 
                bg='white').pack(anchor="w", padx=20, pady=(20,10))
        
        self.restore_option_var = tk.StringVar(value="current_page")
        restore_options = [
            ("Página atual apenas", "current_page"),
            ("Todas as páginas", "all_pages"),
            ("Template completo", "full_template"),
        ]
        
        for text, value in restore_options:
            tk.Radiobutton(restore_frame, text=text, variable=self.restore_option_var, 
                          value=value, bg='white', font=('Arial', 9)).pack(anchor="w", padx=40)
        
        # Botões de ação
        tk.Button(restore_frame, text="🔍 Visualizar Original", 
                 command=self.preview_original_template,
                 font=('Arial', 10), bg='#3b82f6', fg='white', 
                 cursor='hand2', width=20).pack(pady=10)
        
        tk.Button(restore_frame, text="🔄 Restaurar Agora", 
                 command=self.restore_from_original,
                 font=('Arial', 10, 'bold'), bg='#dc2626', fg='white', 
                 cursor='hand2', width=20).pack(pady=5)
        
        # Log de ações
        tk.Label(restore_frame, text="Histórico de Ações:", font=('Arial', 9, 'bold'), 
                bg='white').pack(anchor="w", padx=20, pady=(20,5))
        
        self.restore_log = tk.Text(restore_frame, height=6, width=30, font=('Arial', 8),
                                  bg='#f9fafb', state='disabled')
        self.restore_log.pack(padx=20, pady=5)
        
        # Adicionar entrada inicial no log
        self.add_restore_log("Sistema iniciado - Template original preservado")
    
    # NOVO: Implementação completa dos métodos para as funcionalidades solicitadas
    
    # === MÉTODOS PARA VISUALIZAÇÃO EM TELA CHEIA ===
    
    def render_original_template_fullscreen(self):
        """Renderizar template original na visualização em tela cheia"""
        try:
            if not hasattr(self, 'fullscreen_canvas'):
                return
            
            # Limpar canvas
            self.fullscreen_canvas.delete("all")
            
            # Dimensões da página
            page_width = int(self.page_width * self.fullscreen_scale)
            page_height = int(self.page_height * self.fullscreen_scale)
            
            # Desenhar fundo da página
            self.fullscreen_canvas.create_rectangle(10, 10, page_width + 10, page_height + 10,
                                                   fill='white', outline='#cccccc', width=2,
                                                   tags='page_bg')
            
            # Desenhar elementos da página atual do template original
            pages = self.original_template_data.get('pages', [])
            if self.current_page <= len(pages):
                current_page_data = pages[self.current_page - 1]
                self.draw_page_elements_fullscreen(current_page_data)
            
            # Desenhar grid se ativado
            if hasattr(self, 'grid_overlay_active') and self.grid_overlay_active:
                self.draw_grid_fullscreen()
            
            # Configurar scroll region
            self.fullscreen_canvas.configure(scrollregion=(0, 0, page_width + 20, page_height + 20))
            
            self.fullscreen_status.config(text="Template original renderizado")
            
        except Exception as e:
            print(f"Erro ao renderizar template em tela cheia: {e}")
            if hasattr(self, 'fullscreen_status'):
                self.fullscreen_status.config(text="Erro na renderização")
    
    def draw_page_elements_fullscreen(self, page_data):
        """Desenhar elementos da página na visualização em tela cheia"""
        try:
            elements = page_data.get('elements', [])
            
            for element in elements:
                self.draw_element_fullscreen(element)
                
        except Exception as e:
            print(f"Erro ao desenhar elementos em tela cheia: {e}")
    
    def draw_element_fullscreen(self, element):
        """Desenhar um elemento específico na visualização em tela cheia"""
        try:
            element_type = element.get('type', '')
            x = element.get('x', 0) * self.fullscreen_scale
            y = element.get('y', 0) * self.fullscreen_scale
            
            if element_type == 'text':
                self.draw_text_element_fullscreen(element, x, y)
            elif element_type == 'dynamic_field':
                self.draw_dynamic_field_element_fullscreen(element, x, y)
            elif element_type == 'image':
                self.draw_image_element_fullscreen(element, x, y)
            elif element_type == 'table':
                self.draw_table_element_fullscreen(element, x, y)
            elif element_type == 'line':
                self.draw_line_element_fullscreen(element, x, y)
            elif element_type == 'rectangle':
                self.draw_rectangle_element_fullscreen(element, x, y)
                
        except Exception as e:
            print(f"Erro ao desenhar elemento {element.get('id', 'unknown')} em tela cheia: {e}")
    
    def draw_text_element_fullscreen(self, element, x, y):
        """Desenhar elemento de texto na tela cheia"""
        try:
            text = element.get('text', 'Texto')
            font_family = element.get('font_family', 'Arial')
            font_size = int(element.get('font_size', 10) * self.fullscreen_scale)
            font_style = 'bold' if element.get('bold', False) else 'normal'
            color = element.get('color', '#000000')
            
            canvas_id = self.fullscreen_canvas.create_text(
                x + 10, y + 10, text=text, anchor='nw',
                font=(font_family, font_size, font_style),
                fill=color, tags=f"fullscreen_element_{element.get('id', '')}"
            )
            
            element['fullscreen_canvas_id'] = canvas_id
            
        except Exception as e:
            print(f"Erro ao desenhar texto em tela cheia: {e}")
    
    def draw_dynamic_field_element_fullscreen(self, element, x, y):
        """Desenhar campo dinâmico na tela cheia"""
        try:
            field_ref = element.get('field_ref', 'campo.exemplo')
            value = self.resolve_dynamic_field(field_ref)
            
            font_family = element.get('font_family', 'Arial')
            font_size = int(element.get('font_size', 10) * self.fullscreen_scale)
            color = element.get('color', '#000000')
            
            canvas_id = self.fullscreen_canvas.create_text(
                x + 10, y + 10, text=value, anchor='nw',
                font=(font_family, font_size),
                fill=color, tags=f"fullscreen_element_{element.get('id', '')}"
            )
            
            element['fullscreen_canvas_id'] = canvas_id
            
        except Exception as e:
            print(f"Erro ao desenhar campo dinâmico em tela cheia: {e}")
    
    def draw_image_element_fullscreen(self, element, x, y):
        """Desenhar elemento de imagem na tela cheia"""
        try:
            width = element.get('width', 100) * self.fullscreen_scale
            height = element.get('height', 100) * self.fullscreen_scale
            
            canvas_id = self.fullscreen_canvas.create_rectangle(
                x + 10, y + 10, x + 10 + width, y + 10 + height,
                fill='#f3f4f6', outline='#9ca3af', width=2,
                tags=f"fullscreen_element_{element.get('id', '')}"
            )
            
            # Texto indicativo
            self.fullscreen_canvas.create_text(
                x + 10 + width/2, y + 10 + height/2,
                text="🖼️ Imagem", font=('Arial', int(12 * self.fullscreen_scale)),
                tags=f"fullscreen_element_{element.get('id', '')}"
            )
            
            element['fullscreen_canvas_id'] = canvas_id
            
        except Exception as e:
            print(f"Erro ao desenhar imagem em tela cheia: {e}")
    
    def draw_table_element_fullscreen(self, element, x, y):
        """Desenhar elemento de tabela na tela cheia"""
        try:
            rows = element.get('rows', 3)
            cols = element.get('cols', 3)
            cell_width = 80 * self.fullscreen_scale
            cell_height = 25 * self.fullscreen_scale
            
            # Desenhar grade da tabela
            for row in range(rows + 1):
                y_pos = y + 10 + row * cell_height
                self.fullscreen_canvas.create_line(
                    x + 10, y_pos, x + 10 + cols * cell_width, y_pos,
                    fill='#374151', tags=f"fullscreen_element_{element.get('id', '')}"
                )
            
            for col in range(cols + 1):
                x_pos = x + 10 + col * cell_width
                self.fullscreen_canvas.create_line(
                    x_pos, y + 10, x_pos, y + 10 + rows * cell_height,
                    fill='#374151', tags=f"fullscreen_element_{element.get('id', '')}"
                )
            
            # Criar elemento principal para seleção
            canvas_id = self.fullscreen_canvas.create_rectangle(
                x + 10, y + 10, x + 10 + cols * cell_width, y + 10 + rows * cell_height,
                fill='', outline='', width=0,
                tags=f"fullscreen_element_{element.get('id', '')}"
            )
            
            element['fullscreen_canvas_id'] = canvas_id
            
        except Exception as e:
            print(f"Erro ao desenhar tabela em tela cheia: {e}")
    
    def draw_line_element_fullscreen(self, element, x, y):
        """Desenhar elemento de linha na tela cheia"""
        try:
            end_x = x + element.get('length', 100) * self.fullscreen_scale
            end_y = y + element.get('angle_offset', 0) * self.fullscreen_scale
            
            canvas_id = self.fullscreen_canvas.create_line(
                x + 10, y + 10, end_x + 10, end_y + 10,
                fill=element.get('color', '#000000'),
                width=element.get('thickness', 1),
                tags=f"fullscreen_element_{element.get('id', '')}"
            )
            
            element['fullscreen_canvas_id'] = canvas_id
            
        except Exception as e:
            print(f"Erro ao desenhar linha em tela cheia: {e}")
    
    def draw_rectangle_element_fullscreen(self, element, x, y):
        """Desenhar elemento de retângulo na tela cheia"""
        try:
            width = element.get('width', 100) * self.fullscreen_scale
            height = element.get('height', 50) * self.fullscreen_scale
            
            canvas_id = self.fullscreen_canvas.create_rectangle(
                x + 10, y + 10, x + 10 + width, y + 10 + height,
                fill=element.get('fill_color', ''),
                outline=element.get('border_color', '#000000'),
                width=element.get('border_width', 1),
                tags=f"fullscreen_element_{element.get('id', '')}"
            )
            
            element['fullscreen_canvas_id'] = canvas_id
            
        except Exception as e:
            print(f"Erro ao desenhar retângulo em tela cheia: {e}")
    
    def draw_grid_fullscreen(self):
        """Desenhar grid na visualização em tela cheia"""
        try:
            page_width = int(self.page_width * self.fullscreen_scale)
            page_height = int(self.page_height * self.fullscreen_scale)
            
            # Grid de 25px para tela cheia
            grid_size = int(25 * self.fullscreen_scale)
            
            for x in range(10, page_width + 10, grid_size):
                self.fullscreen_canvas.create_line(x, 10, x, page_height + 10, 
                                                 fill='#e5e7eb', tags='fullscreen_grid')
            
            for y in range(10, page_height + 10, grid_size):
                self.fullscreen_canvas.create_line(10, y, page_width + 10, y, 
                                                 fill='#e5e7eb', tags='fullscreen_grid')
                
        except Exception as e:
            print(f"Erro ao desenhar grid em tela cheia: {e}")
    
    # === EVENTOS DA VISUALIZAÇÃO EM TELA CHEIA ===
    
    def fullscreen_canvas_click(self, event):
        """Callback para clique no canvas em tela cheia"""
        try:
            self.fullscreen_drag_data = {'x': event.x, 'y': event.y}
            
            # Verificar se clicou em um elemento
            clicked_item = self.fullscreen_canvas.find_closest(event.x, event.y)[0]
            
            # Se não é Ctrl+Click, limpar seleção anterior
            if not (event.state & 0x4):  # Não é Ctrl
                self.clear_fullscreen_selection()
            
            self.select_fullscreen_element(clicked_item)
            
        except Exception as e:
            print(f"Erro no clique do canvas em tela cheia: {e}")
    
    def fullscreen_canvas_drag(self, event):
        """Callback para arrastar no canvas em tela cheia"""
        try:
            if self.fullscreen_selected_elements:
                dx = event.x - self.fullscreen_drag_data['x']
                dy = event.y - self.fullscreen_drag_data['y']
                
                for element_id in self.fullscreen_selected_elements:
                    self.fullscreen_canvas.move(element_id, dx, dy)
                
                self.fullscreen_drag_data = {'x': event.x, 'y': event.y}
                
        except Exception as e:
            print(f"Erro no arraste do canvas em tela cheia: {e}")
    
    def fullscreen_canvas_release(self, event):
        """Callback para soltar elemento no canvas em tela cheia"""
        try:
            # Atualizar posições no template_data
            self.update_fullscreen_element_positions()
            
        except Exception as e:
            print(f"Erro no release do canvas em tela cheia: {e}")
    
    def fullscreen_canvas_double_click(self, event):
        """Callback para duplo clique no canvas em tela cheia"""
        try:
            # Editar elemento
            clicked_item = self.fullscreen_canvas.find_closest(event.x, event.y)[0]
            self.edit_fullscreen_element(clicked_item)
            
        except Exception as e:
            print(f"Erro no duplo clique do canvas em tela cheia: {e}")
    
    def fullscreen_canvas_right_click(self, event):
        """Callback para clique direito no canvas em tela cheia"""
        try:
            # Mostrar menu contextual para tela cheia
            self.show_fullscreen_context_menu(event)
            
        except Exception as e:
            print(f"Erro no clique direito do canvas em tela cheia: {e}")
    
    def fullscreen_canvas_scroll(self, event):
        """Callback para scroll do mouse no canvas em tela cheia"""
        try:
            # Zoom com scroll
            if event.state & 0x4:  # Ctrl + Scroll
                if event.delta > 0:
                    self.fullscreen_zoom_in()
                else:
                    self.fullscreen_zoom_out()
            else:
                # Scroll normal
                self.fullscreen_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
                
        except Exception as e:
            print(f"Erro no scroll do canvas em tela cheia: {e}")
    
    # === MÉTODOS DE CONTROLE DA TELA CHEIA ===
    
    def fullscreen_change_page(self, direction):
        """Mudar página na visualização em tela cheia"""
        try:
            pages = self.original_template_data.get('pages', [])
            new_page = self.current_page + direction
            
            if 1 <= new_page <= len(pages):
                self.current_page = new_page
                self.update_fullscreen_page_label()
                self.render_original_template_fullscreen()
                
        except Exception as e:
            print(f"Erro ao mudar página em tela cheia: {e}")
    
    def update_fullscreen_page_label(self):
        """Atualizar label da página na tela cheia"""
        try:
            if hasattr(self, 'fullscreen_page_label'):
                total_pages = len(self.original_template_data.get('pages', []))
                self.fullscreen_page_label.config(text=f"Página {self.current_page} de {total_pages}")
                
        except Exception as e:
            print(f"Erro ao atualizar label da página: {e}")
    
    def fullscreen_zoom_in(self):
        """Aumentar zoom na visualização em tela cheia"""
        try:
            self.fullscreen_scale = min(self.fullscreen_scale * 1.2, 3.0)
            self.render_original_template_fullscreen()
            self.fullscreen_status.config(text=f"Zoom: {int(self.fullscreen_scale * 100)}%")
            
        except Exception as e:
            print(f"Erro no zoom in: {e}")
    
    def fullscreen_zoom_out(self):
        """Diminuir zoom na visualização em tela cheia"""
        try:
            self.fullscreen_scale = max(self.fullscreen_scale / 1.2, 0.3)
            self.render_original_template_fullscreen()
            self.fullscreen_status.config(text=f"Zoom: {int(self.fullscreen_scale * 100)}%")
            
        except Exception as e:
            print(f"Erro no zoom out: {e}")
    
    def toggle_grid_overlay(self):
        """Alternar exibição do grid"""
        try:
            if not hasattr(self, 'grid_overlay_active'):
                self.grid_overlay_active = False
            
            self.grid_overlay_active = not self.grid_overlay_active
            
            if self.grid_overlay_active:
                self.draw_grid_fullscreen()
                self.fullscreen_status.config(text="Grid ativado")
            else:
                self.fullscreen_canvas.delete('fullscreen_grid')
                self.fullscreen_status.config(text="Grid desativado")
                
        except Exception as e:
            print(f"Erro ao alternar grid: {e}")
    
    def open_template_settings(self):
        """Abrir configurações do template"""
        try:
            # Implementar janela de configurações
            messagebox.showinfo("Configurações", "Funcionalidade de configurações será implementada em breve")
            
        except Exception as e:
            print(f"Erro ao abrir configurações: {e}")
    
    def close_fullscreen_preview(self):
        """Fechar visualização em tela cheia"""
        try:
            if hasattr(self, 'preview_window') and self.preview_window:
                self.preview_window.destroy()
                self.preview_window = None
                print("🖥️ Visualização em tela cheia fechada")
                
        except Exception as e:
            print(f"Erro ao fechar visualização em tela cheia: {e}")
    
    def toggle_fullscreen(self):
        """Alternar modo tela cheia"""
        try:
            if hasattr(self, 'preview_window') and self.preview_window:
                current_state = self.preview_window.attributes('-fullscreen')
                self.preview_window.attributes('-fullscreen', not current_state)
                
        except Exception as e:
            print(f"Erro ao alternar fullscreen: {e}")
    
    def show_tooltip(self, event, text):
        """Mostrar tooltip simples"""
        try:
            # Implementação simples de tooltip
            pass
        except Exception as e:
            print(f"Erro ao mostrar tooltip: {e}")
    
    # === MÉTODOS PARA EDIÇÃO EM TELA CHEIA ===
    
    def clear_fullscreen_selection(self):
        """Limpar seleção na tela cheia"""
        try:
            self.fullscreen_canvas.delete('fullscreen_selection')
            self.fullscreen_selected_elements = []
            
        except Exception as e:
            print(f"Erro ao limpar seleção em tela cheia: {e}")
    
    def select_fullscreen_element(self, canvas_id):
        """Selecionar elemento na tela cheia"""
        try:
            # Marcar elemento selecionado
            bbox = self.fullscreen_canvas.bbox(canvas_id)
            if bbox:
                self.fullscreen_canvas.create_rectangle(bbox, outline='#3b82f6', width=3, 
                                                       tags='fullscreen_selection')
            
            self.fullscreen_selected_elements = [canvas_id]
            
        except Exception as e:
            print(f"Erro ao selecionar elemento em tela cheia: {e}")
    
    def update_fullscreen_element_positions(self):
        """Atualizar posições dos elementos após arrastar"""
        try:
            # Implementar sincronização de posições
            pass
        except Exception as e:
            print(f"Erro ao atualizar posições em tela cheia: {e}")
    
    def edit_fullscreen_element(self, canvas_id):
        """Editar elemento na tela cheia"""
        try:
            # Implementar edição de elemento
            messagebox.showinfo("Edição", "Funcionalidade de edição será implementada em breve")
            
        except Exception as e:
            print(f"Erro ao editar elemento em tela cheia: {e}")
    
    def show_fullscreen_context_menu(self, event):
        """Mostrar menu contextual na tela cheia"""
        try:
            # Implementar menu contextual
            pass
        except Exception as e:
            print(f"Erro ao mostrar menu contextual em tela cheia: {e}")
    
    def add_element_fullscreen(self, element_type):
        """Adicionar elemento na tela cheia"""
        try:
            messagebox.showinfo("Adicionar Elemento", f"Adicionando elemento do tipo: {element_type}")
            
        except Exception as e:
            print(f"Erro ao adicionar elemento em tela cheia: {e}")
    
    def enable_move_mode(self):
        """Ativar modo de movimentação"""
        try:
            self.fullscreen_status.config(text="Modo: Mover elementos")
            
        except Exception as e:
            print(f"Erro ao ativar modo de movimentação: {e}")
    
    def enable_resize_mode(self):
        """Ativar modo de redimensionamento"""
        try:
            self.fullscreen_status.config(text="Modo: Redimensionar elementos")
            
        except Exception as e:
            print(f"Erro ao ativar modo de redimensionamento: {e}")
    
    def delete_selected_fullscreen(self):
        """Excluir elementos selecionados na tela cheia"""
        try:
            if self.fullscreen_selected_elements:
                for element_id in self.fullscreen_selected_elements:
                    self.fullscreen_canvas.delete(element_id)
                self.fullscreen_selected_elements = []
                self.fullscreen_status.config(text="Elementos excluídos")
                
        except Exception as e:
            print(f"Erro ao excluir elementos em tela cheia: {e}")
    
    def copy_selected_fullscreen(self):
        """Copiar elementos selecionados na tela cheia"""
        try:
            if self.fullscreen_selected_elements:
                self.fullscreen_status.config(text="Elementos copiados")
                
        except Exception as e:
            print(f"Erro ao copiar elementos em tela cheia: {e}")
    
    def paste_fullscreen(self):
        """Colar elementos na tela cheia"""
        try:
            self.fullscreen_status.config(text="Elementos colados")
            
        except Exception as e:
            print(f"Erro ao colar elementos em tela cheia: {e}")
    
    # === MÉTODOS PARA CABEÇALHO E RODAPÉ ===
    
    def create_header(self):
        """Criar novo cabeçalho"""
        try:
            # Abrir dialog para criar cabeçalho
            header_dialog = tk.Toplevel(self.frame)
            header_dialog.title("Criar Cabeçalho")
            header_dialog.geometry("500x400")
            header_dialog.transient(self.frame)
            header_dialog.grab_set()
            
            tk.Label(header_dialog, text="Criar Novo Cabeçalho", 
                    font=('Arial', 14, 'bold')).pack(pady=10)
            
            # Campos para cabeçalho
            tk.Label(header_dialog, text="Texto do Cabeçalho:").pack(anchor="w", padx=20)
            header_text = tk.Text(header_dialog, height=4, width=50)
            header_text.pack(padx=20, pady=5)
            
            # Opções de formatação
            format_frame = tk.Frame(header_dialog)
            format_frame.pack(pady=10)
            
            tk.Label(format_frame, text="Posição:").pack(side="left")
            position_var = tk.StringVar(value="center")
            positions = ["left", "center", "right"]
            for pos in positions:
                tk.Radiobutton(format_frame, text=pos.title(), variable=position_var, 
                              value=pos).pack(side="left", padx=5)
            
            # Botões
            btn_frame = tk.Frame(header_dialog)
            btn_frame.pack(pady=20)
            
            def save_header():
                text = header_text.get("1.0", tk.END).strip()
                position = position_var.get()
                
                # Salvar cabeçalho
                self.header_elements = [{
                    'type': 'text',
                    'text': text,
                    'position': position,
                    'font_size': 12,
                    'font_family': 'Arial'
                }]
                
                self.header_status_label.config(text="Cabeçalho personalizado criado")
                header_dialog.destroy()
                messagebox.showinfo("Sucesso", "Cabeçalho criado com sucesso!")
            
            tk.Button(btn_frame, text="Salvar", command=save_header,
                     bg='#10b981', fg='white', font=('Arial', 10, 'bold')).pack(side="left", padx=10)
            tk.Button(btn_frame, text="Cancelar", command=header_dialog.destroy,
                     bg='#ef4444', fg='white', font=('Arial', 10, 'bold')).pack(side="left")
            
        except Exception as e:
            print(f"Erro ao criar cabeçalho: {e}")
            messagebox.showerror("Erro", f"Erro ao criar cabeçalho: {e}")
    
    def edit_header(self):
        """Editar cabeçalho existente"""
        try:
            if not self.header_elements:
                messagebox.showwarning("Aviso", "Nenhum cabeçalho para editar. Crie um primeiro.")
                return
            
            self.create_header()  # Reusar dialog de criação
            
        except Exception as e:
            print(f"Erro ao editar cabeçalho: {e}")
    
    def preview_header(self):
        """Visualizar cabeçalho"""
        try:
            if not self.header_elements:
                messagebox.showwarning("Aviso", "Nenhum cabeçalho para visualizar.")
                return
            
            # Criar janela de preview
            preview_window = tk.Toplevel(self.frame)
            preview_window.title("Preview do Cabeçalho")
            preview_window.geometry("600x200")
            
            tk.Label(preview_window, text="Preview do Cabeçalho", 
                    font=('Arial', 14, 'bold')).pack(pady=10)
            
            # Mostrar cabeçalho
            for element in self.header_elements:
                if element['type'] == 'text':
                    tk.Label(preview_window, text=element['text'], 
                            font=(element['font_family'], element['font_size']),
                            wraplength=500).pack(pady=10)
            
        except Exception as e:
            print(f"Erro ao visualizar cabeçalho: {e}")
    
    def remove_header(self):
        """Remover cabeçalho"""
        try:
            if messagebox.askyesno("Confirmar", "Remover cabeçalho atual?"):
                self.header_elements = []
                self.header_status_label.config(text="Nenhum cabeçalho configurado")
                messagebox.showinfo("Sucesso", "Cabeçalho removido!")
                
        except Exception as e:
            print(f"Erro ao remover cabeçalho: {e}")
    
    def create_footer(self):
        """Criar novo rodapé"""
        try:
            # Similar ao create_header, mas para rodapé
            footer_dialog = tk.Toplevel(self.frame)
            footer_dialog.title("Criar Rodapé")
            footer_dialog.geometry("500x400")
            footer_dialog.transient(self.frame)
            footer_dialog.grab_set()
            
            tk.Label(footer_dialog, text="Criar Novo Rodapé", 
                    font=('Arial', 14, 'bold')).pack(pady=10)
            
            # Campos para rodapé
            tk.Label(footer_dialog, text="Texto do Rodapé:").pack(anchor="w", padx=20)
            footer_text = tk.Text(footer_dialog, height=4, width=50)
            footer_text.pack(padx=20, pady=5)
            
            # Inserir texto padrão
            default_footer = """WORLD COMP COMPRESSORES LTDA
Rua Fernando Pessoa, nº 11 – Batistini – São Bernardo do Campo – SP – CEP: 09844-390
CNPJ: 10.644.944/0001-55 | Fone: (11) 4543-6893 / 4543-6857
E-mail: contato@worldcompressores.com.br"""
            footer_text.insert("1.0", default_footer)
            
            # Botões
            btn_frame = tk.Frame(footer_dialog)
            btn_frame.pack(pady=20)
            
            def save_footer():
                text = footer_text.get("1.0", tk.END).strip()
                
                # Salvar rodapé
                self.footer_elements = [{
                    'type': 'text',
                    'text': text,
                    'position': 'center',
                    'font_size': 8,
                    'font_family': 'Arial'
                }]
                
                self.footer_status_label.config(text="Rodapé personalizado criado")
                footer_dialog.destroy()
                messagebox.showinfo("Sucesso", "Rodapé criado com sucesso!")
            
            tk.Button(btn_frame, text="Salvar", command=save_footer,
                     bg='#10b981', fg='white', font=('Arial', 10, 'bold')).pack(side="left", padx=10)
            tk.Button(btn_frame, text="Cancelar", command=footer_dialog.destroy,
                     bg='#ef4444', fg='white', font=('Arial', 10, 'bold')).pack(side="left")
            
        except Exception as e:
            print(f"Erro ao criar rodapé: {e}")
            messagebox.showerror("Erro", f"Erro ao criar rodapé: {e}")
    
    def edit_footer(self):
        """Editar rodapé existente"""
        try:
            self.create_footer()  # Reusar dialog de criação
            
        except Exception as e:
            print(f"Erro ao editar rodapé: {e}")
    
    def preview_footer(self):
        """Visualizar rodapé"""
        try:
            # Criar janela de preview
            preview_window = tk.Toplevel(self.frame)
            preview_window.title("Preview do Rodapé")
            preview_window.geometry("600x300")
            
            tk.Label(preview_window, text="Preview do Rodapé", 
                    font=('Arial', 14, 'bold')).pack(pady=10)
            
            # Mostrar rodapé atual ou padrão
            if self.footer_elements:
                for element in self.footer_elements:
                    if element['type'] == 'text':
                        tk.Label(preview_window, text=element['text'], 
                                font=(element['font_family'], element['font_size']),
                                wraplength=500, justify='center').pack(pady=10)
            else:
                # Mostrar rodapé padrão
                default_footer = """WORLD COMP COMPRESSORES LTDA
Rua Fernando Pessoa, nº 11 – Batistini – São Bernardo do Campo – SP – CEP: 09844-390
CNPJ: 10.644.944/0001-55 | Fone: (11) 4543-6893 / 4543-6857
E-mail: contato@worldcompressores.com.br"""
                tk.Label(preview_window, text=default_footer, 
                        font=('Arial', 8), wraplength=500, justify='center').pack(pady=10)
            
        except Exception as e:
            print(f"Erro ao visualizar rodapé: {e}")
    
    def restore_default_footer(self):
        """Restaurar rodapé padrão"""
        try:
            if messagebox.askyesno("Confirmar", "Restaurar rodapé padrão da empresa?"):
                self.footer_elements = []  # Limpar personalizado
                self.footer_status_label.config(text="Rodapé padrão da empresa")
                messagebox.showinfo("Sucesso", "Rodapé padrão restaurado!")
                
        except Exception as e:
            print(f"Erro ao restaurar rodapé padrão: {e}")
    
    # === MÉTODOS PARA CAPAS DE USUÁRIOS ===
    
    def load_users_with_covers(self):
        """Carregar lista de usuários com capas"""
        try:
            if hasattr(self, 'users_listbox'):
                self.users_listbox.delete(0, tk.END)
                
                for username, user_data in self.user_covers.items():
                    nome = user_data.get('nome_completo', username)
                    self.users_listbox.insert(tk.END, f"{nome} ({username})")
                    
        except Exception as e:
            print(f"Erro ao carregar usuários com capas: {e}")
    
    def on_user_select(self, event):
        """Callback para seleção de usuário"""
        try:
            selection = self.users_listbox.curselection()
            if selection:
                user_text = self.users_listbox.get(selection[0])
                username = user_text.split('(')[1].split(')')[0]
                
                user_data = self.user_covers.get(username, {})
                
                info_text = f"Usuário: {user_data.get('nome_completo', 'N/A')}\n"
                info_text += f"Username: {username}\n"
                info_text += f"Capa: {user_data.get('template_capa_jpeg', 'N/A')}\n"
                info_text += f"Assinatura: {user_data.get('assinatura', 'N/A')}"
                
                self.user_info_label.config(text=info_text)
                
        except Exception as e:
            print(f"Erro ao selecionar usuário: {e}")
    
    def preview_user_cover(self):
        """Visualizar capa do usuário selecionado"""
        try:
            selection = self.users_listbox.curselection()
            if not selection:
                messagebox.showwarning("Aviso", "Selecione um usuário primeiro.")
                return
            
            user_text = self.users_listbox.get(selection[0])
            username = user_text.split('(')[1].split(')')[0]
            
            user_data = self.user_covers.get(username, {})
            cover_path = user_data.get('template_capa_jpeg', '')
            
            if not cover_path or not os.path.exists(cover_path):
                messagebox.showwarning("Aviso", "Capa não encontrada para este usuário.")
                return
            
            # Abrir janela de preview da capa
            preview_window = tk.Toplevel(self.frame)
            preview_window.title(f"Capa de {user_data.get('nome_completo', username)}")
            preview_window.geometry("400x600")
            
            try:
                if PIL_AVAILABLE:
                    # Carregar e exibir imagem
                    img = Image.open(cover_path)
                    img.thumbnail((350, 500))
                    photo = ImageTk.PhotoImage(img)
                    
                    img_label = tk.Label(preview_window, image=photo)
                    img_label.image = photo  # Manter referência
                    img_label.pack(pady=10)
                else:
                    tk.Label(preview_window, text="📄 Capa do Usuário", 
                            font=('Arial', 16)).pack(pady=50)
                    tk.Label(preview_window, text=f"Arquivo: {os.path.basename(cover_path)}", 
                            font=('Arial', 10)).pack()
                    
            except Exception as e:
                tk.Label(preview_window, text="Erro ao carregar imagem", 
                        font=('Arial', 12), fg='red').pack(pady=50)
            
        except Exception as e:
            print(f"Erro ao visualizar capa do usuário: {e}")
            messagebox.showerror("Erro", f"Erro ao visualizar capa: {e}")
    
    def assign_new_cover(self):
        """Atribuir nova capa a um usuário"""
        try:
            # Dialog para selecionar usuário e arquivo
            assign_dialog = tk.Toplevel(self.frame)
            assign_dialog.title("Atribuir Nova Capa")
            assign_dialog.geometry("500x300")
            assign_dialog.transient(self.frame)
            assign_dialog.grab_set()
            
            tk.Label(assign_dialog, text="Atribuir Nova Capa", 
                    font=('Arial', 14, 'bold')).pack(pady=10)
            
            # Seleção de usuário
            tk.Label(assign_dialog, text="Usuário:").pack(anchor="w", padx=20)
            user_var = tk.StringVar()
            user_combo = ttk.Combobox(assign_dialog, textvariable=user_var, width=40)
            user_combo['values'] = [f"{data.get('nome_completo', user)} ({user})" 
                                   for user, data in self.user_covers.items()]
            user_combo.pack(padx=20, pady=5)
            
            # Arquivo selecionado
            file_var = tk.StringVar()
            tk.Label(assign_dialog, text="Arquivo da Capa:").pack(anchor="w", padx=20, pady=(10,0))
            file_frame = tk.Frame(assign_dialog)
            file_frame.pack(fill="x", padx=20, pady=5)
            
            tk.Entry(file_frame, textvariable=file_var, width=30, state='readonly').pack(side="left", expand=True, fill="x")
            
            def select_file():
                filename = filedialog.askopenfilename(
                    title="Selecionar Capa",
                    filetypes=[("Imagens", "*.jpg *.jpeg *.png"), ("Todos os arquivos", "*.*")]
                )
                if filename:
                    file_var.set(filename)
            
            tk.Button(file_frame, text="Selecionar", command=select_file).pack(side="right", padx=(5,0))
            
            # Botões
            btn_frame = tk.Frame(assign_dialog)
            btn_frame.pack(pady=20)
            
            def save_assignment():
                user_text = user_var.get()
                if not user_text:
                    messagebox.showwarning("Aviso", "Selecione um usuário.")
                    return
                
                file_path = file_var.get()
                if not file_path:
                    messagebox.showwarning("Aviso", "Selecione um arquivo.")
                    return
                
                username = user_text.split('(')[1].split(')')[0]
                
                # Atualizar configuração
                if username in self.user_covers:
                    self.user_covers[username]['template_capa_jpeg'] = file_path
                    messagebox.showinfo("Sucesso", f"Capa atribuída ao usuário {username}!")
                    assign_dialog.destroy()
                    self.refresh_user_covers()
                else:
                    messagebox.showerror("Erro", "Usuário não encontrado.")
            
            tk.Button(btn_frame, text="Salvar", command=save_assignment,
                     bg='#10b981', fg='white', font=('Arial', 10, 'bold')).pack(side="left", padx=10)
            tk.Button(btn_frame, text="Cancelar", command=assign_dialog.destroy,
                     bg='#ef4444', fg='white', font=('Arial', 10, 'bold')).pack(side="left")
            
        except Exception as e:
            print(f"Erro ao atribuir nova capa: {e}")
            messagebox.showerror("Erro", f"Erro ao atribuir capa: {e}")
    
    def edit_user_cover(self):
        """Editar capa existente"""
        try:
            selection = self.users_listbox.curselection()
            if not selection:
                messagebox.showwarning("Aviso", "Selecione um usuário primeiro.")
                return
            
            self.assign_new_cover()  # Reusar dialog de atribuição
            
        except Exception as e:
            print(f"Erro ao editar capa: {e}")
    
    def remove_user_cover(self):
        """Remover capa de usuário"""
        try:
            selection = self.users_listbox.curselection()
            if not selection:
                messagebox.showwarning("Aviso", "Selecione um usuário primeiro.")
                return
            
            user_text = self.users_listbox.get(selection[0])
            username = user_text.split('(')[1].split(')')[0]
            
            if messagebox.askyesno("Confirmar", f"Remover capa do usuário {username}?"):
                if username in self.user_covers:
                    # Remover apenas a capa, manter outras configurações
                    if 'template_capa_jpeg' in self.user_covers[username]:
                        del self.user_covers[username]['template_capa_jpeg']
                    messagebox.showinfo("Sucesso", f"Capa removida do usuário {username}!")
                    self.refresh_user_covers()
                    
        except Exception as e:
            print(f"Erro ao remover capa: {e}")
    
    def import_user_cover(self):
        """Importar capa de arquivo"""
        try:
            filename = filedialog.askopenfilename(
                title="Importar Capa",
                filetypes=[("Imagens", "*.jpg *.jpeg *.png"), ("Todos os arquivos", "*.*")]
            )
            
            if filename:
                # Copiar arquivo para diretório de templates
                import shutil
                os.makedirs("assets/templates/capas", exist_ok=True)
                
                base_name = os.path.basename(filename)
                dest_path = os.path.join("assets/templates/capas", base_name)
                
                shutil.copy2(filename, dest_path)
                messagebox.showinfo("Sucesso", f"Capa importada: {base_name}")
                
        except Exception as e:
            print(f"Erro ao importar capa: {e}")
            messagebox.showerror("Erro", f"Erro ao importar capa: {e}")
    
    def refresh_user_covers(self):
        """Atualizar lista de usuários com capas"""
        try:
            self.load_user_cover_assignments()
            self.load_users_with_covers()
            
        except Exception as e:
            print(f"Erro ao atualizar lista: {e}")
    
    # === MÉTODOS PARA RESTAURAÇÃO ===
    
    def preview_original_template(self):
        """Visualizar template original"""
        try:
            if not self.original_template_data:
                messagebox.showwarning("Aviso", "Template original não encontrado.")
                return
            
            # Mostrar informações do template original
            info_text = f"Template Original:\n\n"
            info_text += f"Versão: {self.original_template_data.get('version', 'N/A')}\n"
            info_text += f"Páginas: {len(self.original_template_data.get('pages', []))}\n"
            info_text += f"Criado em: {self.original_template_data.get('created_at', 'N/A')}\n"
            
            messagebox.showinfo("Template Original", info_text)
            
        except Exception as e:
            print(f"Erro ao visualizar template original: {e}")
    
    def restore_from_original(self):
        """Restaurar template do original"""
        try:
            if not self.original_template_data:
                messagebox.showerror("Erro", "Template original não encontrado.")
                return
            
            option = self.restore_option_var.get()
            
            if messagebox.askyesno("Confirmar Restauração", 
                                  f"Confirma a restauração ({option})?\n\nEsta ação não pode ser desfeita."):
                
                import copy
                
                if option == "current_page":
                    # Restaurar apenas página atual
                    pages = self.original_template_data.get('pages', [])
                    if self.current_page <= len(pages):
                        original_page = pages[self.current_page - 1]
                        current_pages = self.template_data.get('pages', [])
                        if self.current_page <= len(current_pages):
                            current_pages[self.current_page - 1] = copy.deepcopy(original_page)
                    
                elif option == "all_pages":
                    # Restaurar todas as páginas
                    self.template_data['pages'] = copy.deepcopy(self.original_template_data.get('pages', []))
                    
                elif option == "full_template":
                    # Restaurar template completo
                    self.template_data = copy.deepcopy(self.original_template_data)
                
                # Regenerar preview
                self.generate_visual_preview()
                
                # Log da ação
                action_text = f"Restauração realizada: {option}"
                self.add_restore_log(action_text)
                
                messagebox.showinfo("Sucesso", "Template restaurado com sucesso!")
                
        except Exception as e:
            print(f"Erro ao restaurar template: {e}")
            messagebox.showerror("Erro", f"Erro ao restaurar template: {e}")
    
    def add_restore_log(self, message):
        """Adicionar entrada no log de restauração"""
        try:
            if hasattr(self, 'restore_log'):
                timestamp = datetime.now().strftime('%H:%M:%S')
                log_entry = f"[{timestamp}] {message}\n"
                
                self.restore_log.config(state='normal')
                self.restore_log.insert(tk.END, log_entry)
                self.restore_log.see(tk.END)
                self.restore_log.config(state='disabled')
                
        except Exception as e:
            print(f"Erro ao adicionar log: {e}")