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
            self.scale_factor = 0.5  # Escala para visualização
            
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
        
        # Canvas com barras de rolagem
        self.canvas = tk.Canvas(canvas_frame, bg='white', relief='solid', bd=1,
                               width=400, height=600)
        
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
        """Carregar template padrão baseado no PDF atual"""
        try:
            # Mapear elementos do PDF atual
            self.template_data = {
                "name": "Template Padrão",
                "description": "Template baseado no gerador atual",
                "pages": {
                    # Página 1 - Capa (não editável)
                    "1": {
                        "editable": False,
                        "elements": []
                    },
                    
                                         # Página 2 - Introdução (sem cabeçalho, apenas rodapé)
                     "2": {
                         "editable": True,
                         "elements": [
                             {
                                 "id": "logo_empresa",
                                 "type": "image",
                                 "label": "Logo da Empresa",
                                 "x": 105, "y": 20, "w": 45, "h": 30,
                                 "data_type": "fixed",
                                 "content": "assets/logos/world_comp_brasil.jpg"
                             },
                             {
                                 "id": "apresentado_para_titulo",
                                 "type": "text",
                                 "label": "Título 'Apresentado Para'",
                                 "x": 10, "y": 80, "w": 95, "h": 7,
                                 "data_type": "fixed",
                                 "content": "APRESENTADO PARA:",
                                 "font_family": "Arial",
                                 "font_size": 10,
                                 "font_style": "bold"
                             },
                             {
                                 "id": "apresentado_por_titulo",
                                 "type": "text",
                                 "label": "Título 'Apresentado Por'",
                                 "x": 105, "y": 80, "w": 95, "h": 7,
                                 "data_type": "fixed",
                                 "content": "APRESENTADO POR:",
                                 "font_family": "Arial",
                                 "font_size": 10,
                                 "font_style": "bold"
                             },
                             {
                                 "id": "cliente_nome",
                                 "type": "text",
                                 "label": "Nome do Cliente",
                                 "x": 10, "y": 87, "w": 95, "h": 5,
                                 "data_type": "dynamic",
                                 "field_options": ["cliente_nome", "cliente_nome_fantasia", "cliente_codigo"],
                                 "current_field": "cliente_nome",
                                 "font_family": "Arial",
                                 "font_size": 10,
                                 "font_style": "bold"
                             },
                             {
                                 "id": "empresa_nome",
                                 "type": "text",
                                 "label": "Nome da Empresa",
                                 "x": 105, "y": 87, "w": 95, "h": 5,
                                 "data_type": "dynamic",
                                 "field_options": ["filial_nome", "empresa_nome"],
                                 "current_field": "filial_nome",
                                 "font_family": "Arial",
                                 "font_size": 10,
                                 "font_style": "bold"
                             },
                             {
                                 "id": "cliente_cnpj",
                                 "type": "text",
                                 "label": "CNPJ do Cliente",
                                 "x": 10, "y": 92, "w": 95, "h": 5,
                                 "data_type": "dynamic",
                                 "field_options": ["cliente_cnpj", "cliente_cpf"],
                                 "current_field": "cliente_cnpj",
                                 "content_template": "CNPJ: {value}",
                                 "font_family": "Arial",
                                 "font_size": 10,
                                 "font_style": "normal"
                             },
                             {
                                 "id": "empresa_cnpj",
                                 "type": "text",
                                 "label": "CNPJ da Empresa",
                                 "x": 105, "y": 92, "w": 95, "h": 5,
                                 "data_type": "dynamic",
                                 "field_options": ["filial_cnpj", "empresa_cnpj"],
                                 "current_field": "filial_cnpj",
                                 "content_template": "CNPJ: {value}",
                                 "font_family": "Arial",
                                 "font_size": 10,
                                 "font_style": "normal"
                             },
                             {
                                 "id": "cliente_telefone",
                                 "type": "text",
                                 "label": "Telefone do Cliente",
                                 "x": 10, "y": 97, "w": 95, "h": 5,
                                 "data_type": "dynamic",
                                 "field_options": ["cliente_telefone", "cliente_celular"],
                                 "current_field": "cliente_telefone",
                                 "content_template": "FONE: {value}",
                                 "font_family": "Arial",
                                 "font_size": 10,
                                 "font_style": "normal"
                             },
                             {
                                 "id": "empresa_telefone",
                                 "type": "text",
                                 "label": "Telefone da Empresa",
                                 "x": 105, "y": 97, "w": 95, "h": 5,
                                 "data_type": "dynamic",
                                 "field_options": ["filial_telefones", "empresa_telefone"],
                                 "current_field": "filial_telefones",
                                 "content_template": "FONE: {value}",
                                 "font_family": "Arial",
                                 "font_size": 10,
                                 "font_style": "normal"
                             },
                             {
                                 "id": "contato_nome",
                                 "type": "text",
                                 "label": "Nome do Contato",
                                 "x": 10, "y": 102, "w": 95, "h": 5,
                                 "data_type": "dynamic",
                                 "field_options": ["contato_nome", "cliente_contato"],
                                 "current_field": "contato_nome",
                                 "content_template": "Sr(a). {value}",
                                 "font_family": "Arial",
                                 "font_size": 10,
                                 "font_style": "normal"
                             },
                             {
                                 "id": "responsavel_email",
                                 "type": "text",
                                 "label": "Email do Responsável",
                                 "x": 105, "y": 102, "w": 95, "h": 5,
                                 "data_type": "dynamic",
                                 "field_options": ["responsavel_email", "empresa_email"],
                                 "current_field": "responsavel_email",
                                 "font_family": "Arial",
                                 "font_size": 10,
                                 "font_style": "normal"
                             },
                             {
                                 "id": "assinatura_responsavel",
                                 "type": "text",
                                 "label": "Assinatura do Responsável",
                                 "x": 10, "y": 240, "w": 100, "h": 20,
                                 "data_type": "dynamic",
                                 "field_options": ["responsavel_nome", "vendedor_nome"],
                                 "current_field": "responsavel_nome",
                                 "font_family": "Arial",
                                 "font_size": 11,
                                 "font_style": "bold"
                             }
                         ]
                     },
                    
                    # Página 3 - Sobre a Empresa
                    "3": {
                        "editable": True,
                        "elements": [
                            {
                                "id": "sobre_titulo",
                                "type": "text",
                                "label": "Título 'Sobre a World Comp'",
                                "x": 10, "y": 45, "w": 190, "h": 8,
                                "data_type": "fixed",
                                "content": "SOBRE A WORLD COMP",
                                "font_family": "Arial",
                                "font_size": 12,
                                "font_style": "bold"
                            },
                            {
                                "id": "sobre_introducao",
                                "type": "text",
                                "label": "Introdução da Empresa",
                                "x": 10, "y": 55, "w": 190, "h": 20,
                                "data_type": "fixed",
                                "content": "Há mais de uma década no mercado de manutenção de compressores de ar de parafuso, de diversas marcas, atendemos clientes em todo território brasileiro.",
                                "font_family": "Arial",
                                "font_size": 11,
                                "font_style": "normal"
                            }
                        ]
                    },
                    
                    # Página 4 - Proposta
                    "4": {
                        "editable": True,
                        "elements": [
                            {
                                "id": "proposta_titulo",
                                "type": "text",
                                "label": "Título da Proposta",
                                "x": 10, "y": 45, "w": 190, "h": 8,
                                "data_type": "dynamic",
                                "field_options": ["numero_proposta", "codigo_proposta"],
                                "current_field": "numero_proposta",
                                "content_template": "PROPOSTA Nº {value}",
                                "font_family": "Arial",
                                "font_size": 12,
                                "font_style": "bold"
                            },
                            {
                                "id": "data_proposta",
                                "type": "text",
                                "label": "Data da Proposta",
                                "x": 10, "y": 55, "w": 95, "h": 6,
                                "data_type": "dynamic",
                                "field_options": ["data_criacao", "data_proposta"],
                                "current_field": "data_criacao",
                                "content_template": "Data: {value}",
                                "font_family": "Arial",
                                "font_size": 11,
                                "font_style": "normal"
                            }
                        ]
                    }
                }
            }
            
            # Atualizar visualização
            self.update_element_list()
            self.draw_page()
            
        except Exception as e:
            print(f"Erro ao carregar template padrão: {e}")
    
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
        
        # Desenhar fundo da página (A4)
        page_width = 595 * self.scale_factor
        page_height = 842 * self.scale_factor
        
        self.canvas.create_rectangle(10, 10, 10 + page_width, 10 + page_height,
                                   fill='white', outline='#ddd', width=2,
                                   tags='page_background')
        
        # Desenhar elementos da página atual
        if str(self.current_page) in self.template_data.get("pages", {}):
            page_data = self.template_data["pages"][str(self.current_page)]
            elements = page_data.get("elements", [])
            
            for i, element in enumerate(elements):
                self.draw_element(element, i)
        
        # Informações da página
        page_info = f"Página {self.current_page}"
        if self.current_page == 2:
            page_info += " - Introdução (sem cabeçalho, apenas rodapé)"
        elif self.current_page == 3:
            page_info += " - Sobre a Empresa"
        elif self.current_page == 4:
            page_info += " - Proposta"
        
        self.canvas.create_text(10 + page_width/2, 10 + page_height + 20,
                               text=page_info, font=('Arial', 10, 'bold'),
                               fill='#6b7280', tags='page_info')
    
    def draw_element(self, element, index):
        """Desenhar elemento no canvas"""
        x = 10 + (element['x'] * self.scale_factor)
        y = 10 + (element['y'] * self.scale_factor)
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
        
        # Retângulo do elemento
        rect_id = self.canvas.create_rectangle(x, y, x + w, y + h,
                                             fill=fill_color, outline=border_color,
                                             width=2, tags=f'element_{index}')
        
        # Texto do elemento
        display_text = element.get('label', element.get('id', ''))
        if element.get('data_type') == 'dynamic':
            display_text = f"📊 {display_text}"
        else:
            display_text = f"📝 {display_text}"
        
        text_id = self.canvas.create_text(x + w/2, y + h/2,
                                        text=display_text,
                                        font=('Arial', int(8 * self.scale_factor)),
                                        fill=text_color,
                                        width=w-4,
                                        tags=f'element_{index}')
    
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