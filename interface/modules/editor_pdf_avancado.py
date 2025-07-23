import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import json
import os
import sqlite3
from .base_module import BaseModule

# Tentar importar PIL/Pillow
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

class EditorPDFAvancadoModule(BaseModule):
    def __init__(self, parent, user_id, role, main_window):
        self.user_info = {'role': role, 'user_id': user_id}
        
        # Configurar conexão com banco
        from database import DB_NAME
        self.db_name = DB_NAME
        
        # Inicializar gerenciador de templates
        from utils.template_manager import TemplateManager
        self.template_manager = TemplateManager(DB_NAME)
        
        # Inicializar propriedades ANTES de chamar super().__init__
        self.pdf_template = None
        self.current_page = 1
        self.total_pages = 4
        self.page_data = {}
        self.available_fields = {}
        self.canvas_scale = 0.6
        self.page_width = 595  # A4 width in points
        self.page_height = 842  # A4 height in points
        
        super().__init__(parent, user_id, role, main_window)
        
        # Carregar dados disponíveis no sistema
        self.load_available_fields()
        
        # Carregar template após inicialização completa
        self.pdf_template = self.template_manager.load_base_template()
        
        # Atualizar interface
        if hasattr(self, 'canvas'):
            self.refresh_page_preview()
    
    def setup_ui(self):
        """Configurar interface do editor avançado"""
        # Título
        title_frame = tk.Frame(self.frame, bg='white')
        title_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        tk.Label(title_frame, text="Editor de PDF Avançado", 
                font=('Arial', 16, 'bold'), bg='white', fg='#1e293b').pack(side="left")
        
        # Frame principal
        main_content = tk.Frame(self.frame, bg='white')
        main_content.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Barra de ferramentas superior
        self.setup_toolbar(main_content)
        
        # Frame de conteúdo com três painéis
        content_frame = tk.Frame(main_content, bg='white')
        content_frame.pack(fill="both", expand=True, pady=10)
        
        # Painel esquerdo - Navegação de páginas
        self.setup_page_navigation(content_frame)
        
        # Painel central - Preview da página
        self.setup_page_preview(content_frame)
        
        # Painel direito - Editor de elementos
        self.setup_element_editor(content_frame)
    
    def setup_toolbar(self, parent):
        """Configurar barra de ferramentas"""
        toolbar_frame = tk.Frame(parent, bg='#f8fafc', relief="raised", bd=1)
        toolbar_frame.pack(fill="x", pady=(0, 10))
        
        # Grupo de template
        template_group = tk.LabelFrame(toolbar_frame, text="Template", bg='#f8fafc', font=('Arial', 9))
        template_group.pack(side="left", padx=5, pady=5)
        
        load_btn = self.create_button(template_group, "Carregar", self.load_template, bg='#3b82f6', width=10)
        load_btn.pack(side="left", padx=2, pady=2)
        
        save_btn = self.create_button(template_group, "Salvar", self.save_template, bg='#10b981', width=10)
        save_btn.pack(side="left", padx=2, pady=2)
        
        reset_btn = self.create_button(template_group, "Restaurar", self.reset_template, bg='#f59e0b', width=10)
        reset_btn.pack(side="left", padx=2, pady=2)
        
        # Grupo de validação
        validation_group = tk.LabelFrame(toolbar_frame, text="Validação", bg='#f8fafc', font=('Arial', 9))
        validation_group.pack(side="left", padx=5, pady=5)
        
        validate_btn = self.create_button(validation_group, "Validar", self.validate_template, bg='#8b5cf6', width=10)
        validate_btn.pack(side="left", padx=2, pady=2)
        
        preview_btn = self.create_button(validation_group, "Preview PDF", self.generate_preview_pdf, bg='#7c3aed', width=10)
        preview_btn.pack(side="left", padx=2, pady=2)
    
    def setup_page_navigation(self, parent):
        """Configurar painel de navegação de páginas"""
        nav_frame = tk.LabelFrame(parent, text="Páginas do PDF", 
                                 font=('Arial', 12, 'bold'), bg='white', fg='#1e293b')
        nav_frame.pack(side="left", fill="y", padx=(0, 10))
        
        # Lista de páginas
        pages_info = [
            ("Página 1", "Capa", "🎨"),
            ("Página 2", "Apresentação", "📋"),
            ("Página 3", "Sobre a Empresa", "🏢"),
            ("Página 4", "Proposta Comercial", "💰")
        ]
        
        self.page_buttons = []
        for i, (page_num, page_name, icon) in enumerate(pages_info, 1):
            page_frame = tk.Frame(nav_frame, bg='white')
            page_frame.pack(fill="x", padx=5, pady=2)
            
            # Botão da página
            btn_text = f"{icon} {page_num}\n{page_name}"
            page_btn = tk.Button(page_frame, text=btn_text, 
                               command=lambda p=i: self.select_page(p),
                               font=('Arial', 9), bg='#f8fafc', fg='#1e293b',
                               relief='flat', cursor='hand2', width=15, height=3)
            page_btn.pack(fill="x", pady=1)
            self.page_buttons.append(page_btn)
            
            # Status da página
            status_label = tk.Label(page_frame, text="✓ Editável", 
                                  font=('Arial', 8), bg='white', fg='#10b981')
            status_label.pack()
        
        # Destacar primeira página
        self.select_page(1)
        
        # Informações da página atual
        info_frame = tk.LabelFrame(nav_frame, text="Informações", bg='white', font=('Arial', 10, 'bold'))
        info_frame.pack(fill="x", padx=5, pady=10)
        
        self.page_info_label = tk.Label(info_frame, text="", font=('Arial', 9), 
                                       bg='white', fg='#64748b', justify="left")
        self.page_info_label.pack(padx=5, pady=5)
    
    def setup_page_preview(self, parent):
        """Configurar painel de preview da página"""
        preview_frame = tk.LabelFrame(parent, text="Preview da Página", 
                                    font=('Arial', 12, 'bold'), bg='white', fg='#1e293b')
        preview_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Canvas com scrollbars
        canvas_frame = tk.Frame(preview_frame, bg='white')
        canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.canvas = tk.Canvas(canvas_frame, bg='white', 
                               width=int(self.page_width * self.canvas_scale),
                               height=int(self.page_height * self.canvas_scale),
                               relief="sunken", bd=2)
        
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient="horizontal", command=self.canvas.xview)
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        
        self.canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
        
        self.canvas.pack(side="top", fill="both", expand=True)
        h_scrollbar.pack(side="bottom", fill="x")
        v_scrollbar.pack(side="right", fill="y")
        
        # Eventos do canvas
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Double-Button-1>", self.on_canvas_double_click)
        
        # Configurar scroll region
        self.canvas.configure(scrollregion=(0, 0, 
                                          int(self.page_width * self.canvas_scale),
                                          int(self.page_height * self.canvas_scale)))
        
        # Controles de zoom
        zoom_frame = tk.Frame(preview_frame, bg='white')
        zoom_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(zoom_frame, text="Zoom:", bg='white', font=('Arial', 9)).pack(side="left")
        
        zoom_out_btn = self.create_button(zoom_frame, "-", self.zoom_out, bg='#64748b', width=3)
        zoom_out_btn.pack(side="left", padx=(5, 2))
        
        self.zoom_label = tk.Label(zoom_frame, text=f"{int(self.canvas_scale*100)}%", 
                                  bg='white', font=('Arial', 9), width=5)
        self.zoom_label.pack(side="left", padx=2)
        
        zoom_in_btn = self.create_button(zoom_frame, "+", self.zoom_in, bg='#64748b', width=3)
        zoom_in_btn.pack(side="left", padx=(2, 5))
    
    def setup_element_editor(self, parent):
        """Configurar painel de edição de elementos"""
        editor_frame = tk.LabelFrame(parent, text="Editor de Elementos", 
                                   font=('Arial', 12, 'bold'), bg='white', fg='#1e293b')
        editor_frame.pack(side="right", fill="y")
        
        # Notebook para diferentes tipos de edição
        self.editor_notebook = ttk.Notebook(editor_frame)
        self.editor_notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Aba 1: Cabeçalho
        self.setup_header_editor()
        
        # Aba 2: Rodapé
        self.setup_footer_editor()
        
        # Aba 3: Conteúdo
        self.setup_content_editor()
        
        # Aba 4: Layout
        self.setup_layout_editor()
    
    def setup_header_editor(self):
        """Configurar editor de cabeçalho"""
        header_frame = tk.Frame(self.editor_notebook, bg='white')
        self.editor_notebook.add(header_frame, text="Cabeçalho")
        
        # Scroll frame
        canvas = tk.Canvas(header_frame, bg='white')
        scrollbar = ttk.Scrollbar(header_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Campos editáveis do cabeçalho
        tk.Label(scrollable_frame, text="Campos Disponíveis:", 
                font=('Arial', 10, 'bold'), bg='white').pack(anchor="w", padx=5, pady=(5, 2))
        
        # Lista de campos disponíveis
        self.header_fields_frame = tk.Frame(scrollable_frame, bg='white')
        self.header_fields_frame.pack(fill="x", padx=5, pady=5)
        
        # Botões de ação
        action_frame = tk.Frame(scrollable_frame, bg='white')
        action_frame.pack(fill="x", padx=5, pady=10)
        
        refresh_btn = self.create_button(action_frame, "Atualizar Campos", 
                                       self.refresh_available_fields, bg='#3b82f6')
        refresh_btn.pack(fill="x", pady=2)
        
        apply_btn = self.create_button(action_frame, "Aplicar Alterações", 
                                     self.apply_header_changes, bg='#10b981')
        apply_btn.pack(fill="x", pady=2)
    
    def setup_footer_editor(self):
        """Configurar editor de rodapé"""
        footer_frame = tk.Frame(self.editor_notebook, bg='white')
        self.editor_notebook.add(footer_frame, text="Rodapé")
        
        # Campos do rodapé
        tk.Label(footer_frame, text="Informações da Empresa:", 
                font=('Arial', 10, 'bold'), bg='white').pack(anchor="w", padx=5, pady=5)
        
        # Lista de campos do rodapé
        self.footer_fields_frame = tk.Frame(footer_frame, bg='white')
        self.footer_fields_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Botões de ação
        footer_action_frame = tk.Frame(footer_frame, bg='white')
        footer_action_frame.pack(fill="x", padx=5, pady=10)
        
        apply_footer_btn = self.create_button(footer_action_frame, "Aplicar Rodapé", 
                                            self.apply_footer_changes, bg='#10b981')
        apply_footer_btn.pack(fill="x", pady=2)
    
    def setup_content_editor(self):
        """Configurar editor de conteúdo"""
        content_frame = tk.Frame(self.editor_notebook, bg='white')
        self.editor_notebook.add(content_frame, text="Conteúdo")
        
        # Editor baseado na página atual
        tk.Label(content_frame, text="Editor de Conteúdo por Página:", 
                font=('Arial', 10, 'bold'), bg='white').pack(anchor="w", padx=5, pady=5)
        
        self.content_editor_frame = tk.Frame(content_frame, bg='white')
        self.content_editor_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Texto de instruções
        self.content_instructions = tk.Label(content_frame, 
                                           text="Selecione uma página para editar seu conteúdo.",
                                           font=('Arial', 9), bg='white', fg='#64748b')
        self.content_instructions.pack(padx=5, pady=5)
    
    def setup_layout_editor(self):
        """Configurar editor de layout"""
        layout_frame = tk.Frame(self.editor_notebook, bg='white')
        self.editor_notebook.add(layout_frame, text="Layout")
        
        # Controles de layout
        tk.Label(layout_frame, text="Configurações de Layout:", 
                font=('Arial', 10, 'bold'), bg='white').pack(anchor="w", padx=5, pady=5)
        
        # Posicionamento de elementos
        position_frame = tk.LabelFrame(layout_frame, text="Posicionamento", bg='white')
        position_frame.pack(fill="x", padx=5, pady=5)
        
        # Opções de layout para página 4 (Proposta)
        tk.Label(position_frame, text="Ordem dos elementos na Proposta:", 
                font=('Arial', 9), bg='white').pack(anchor="w", padx=5, pady=2)
        
        self.layout_order_frame = tk.Frame(position_frame, bg='white')
        self.layout_order_frame.pack(fill="x", padx=5, pady=5)
    
    def load_available_fields(self):
        """Carregar campos disponíveis no sistema"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Campos da empresa/filial
            self.available_fields['empresa'] = {
                'nome': 'WORLD COMP COMPRESSORES LTDA',
                'endereco': 'Rua Fernando Pessoa, nº 11 – Batistini – São Bernardo do Campo – SP',
                'cep': '09844-390',
                'cnpj': '10.644.944/0001-55',
                'inscricao_estadual': '635.970.206.110',
                'telefones': '(11) 4543-6893 / 4543-6857',
                'email': 'contato@worldcompressores.com.br'
            }
            
            # Campos de usuários
            cursor.execute("SELECT DISTINCT username, nome_completo, email, telefone FROM usuarios")
            usuarios = cursor.fetchall()
            self.available_fields['usuarios'] = {}
            for username, nome, email, telefone in usuarios:
                self.available_fields['usuarios'][username] = {
                    'nome': nome,
                    'email': email,
                    'telefone': telefone
                }
            
            # Campos de clientes (exemplos baseados no banco)
            cursor.execute("SELECT DISTINCT nome, cnpj, endereco, telefone FROM clientes LIMIT 10")
            clientes = cursor.fetchall()
            self.available_fields['clientes'] = {}
            for nome, cnpj, endereco, telefone in clientes:
                if nome:
                    self.available_fields['clientes'][nome] = {
                        'cnpj': cnpj,
                        'endereco': endereco,
                        'telefone': telefone
                    }
            
            conn.close()
            
        except Exception as e:
            print(f"Erro ao carregar campos disponíveis: {e}")
            self.available_fields = {
                'empresa': {},
                'usuarios': {},
                'clientes': {}
            }
    
    def load_pdf_template(self):
        """Carregar template do PDF"""
        template_file = "data/pdf_template_avancado.json"
        
        default_template = {
            "pagina_1": {
                "tipo": "capa",
                "editavel": ["background_image", "overlay_image"],
                "elementos": {
                    "background_image": None,
                    "overlay_image": None,
                    "texto_empresa": "{{empresa.nome}}",
                    "texto_contato": "A/C SR. {{cliente.contato}}",
                    "data": "{{proposta.data}}"
                }
            },
            "pagina_2": {
                "tipo": "apresentacao",
                "editavel": ["texto_apresentacao", "logo"],
                "elementos": {
                    "logo": "assets/logos/world_comp_brasil.jpg",
                    "empresa_nome": "{{empresa.nome}}",
                    "empresa_endereco": "{{empresa.endereco}}",
                    "empresa_telefone": "{{empresa.telefones}}",
                    "texto_apresentacao": "Prezados Senhores,\n\nAgradecemos a sua solicitação e apresentamos nossas condições comerciais..."
                }
            },
            "pagina_3": {
                "tipo": "sobre_empresa",
                "editavel": ["conteudo_completo"],
                "elementos": {
                    "titulo": "SOBRE A WORLD COMP",
                    "conteudo": "Há mais de uma década no mercado de manutenção de compressores..."
                }
            },
            "pagina_4": {
                "tipo": "proposta",
                "editavel": ["ordem_elementos"],
                "elementos": {
                    "ordem": ["dados_proposta", "dados_cliente", "tabela_itens", "valor_total", "condicoes"],
                    "dados_proposta": "{{proposta.numero}} - {{proposta.data}}",
                    "dados_cliente": "{{cliente.nome}} - {{cliente.cnpj}}",
                    "tabela_itens": "{{itens_cotacao}}",
                    "valor_total": "{{proposta.valor_total}}",
                    "condicoes": "Condições comerciais..."
                }
            },
            "cabecalho": {
                "template": "{{empresa.nome}} | PROPOSTA COMERCIAL | NUMERO: {{proposta.numero}} | DATA: {{proposta.data}}",
                "campos_editaveis": ["empresa.nome", "proposta.numero", "proposta.data"],
                "posicao": "top",
                "altura": 20
            },
            "rodape": {
                "template": "{{empresa.endereco}} | CNPJ: {{empresa.cnpj}} | E-mail: {{empresa.email}} | Fone: {{empresa.telefones}}",
                "campos_editaveis": ["empresa.endereco", "empresa.cnpj", "empresa.email", "empresa.telefones"],
                "posicao": "bottom",
                "altura": 15
            }
        }
        
        try:
            if os.path.exists(template_file):
                with open(template_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return default_template
        except Exception as e:
            print(f"Erro ao carregar template: {e}")
            return default_template
    
    def save_template(self):
        """Salvar template atual"""
        # Dialog para escolher tipo de salvamento
        save_window = tk.Toplevel(self.frame)
        save_window.title("Salvar Template")
        save_window.geometry("400x300")
        save_window.transient(self.frame)
        
        tk.Label(save_window, text="Como deseja salvar o template?", 
                font=('Arial', 12, 'bold')).pack(pady=20)
        
        # Opções de salvamento
        save_type = tk.StringVar(value="base")
        
        tk.Radiobutton(save_window, text="Atualizar Template Base (todos os usuários)", 
                      variable=save_type, value="base", font=('Arial', 10)).pack(anchor="w", padx=20, pady=5)
        
        tk.Radiobutton(save_window, text="Salvar como Template do Usuário Atual", 
                      variable=save_type, value="usuario", font=('Arial', 10)).pack(anchor="w", padx=20, pady=5)
        
        tk.Radiobutton(save_window, text="Salvar como Template para Cliente Específico", 
                      variable=save_type, value="cliente", font=('Arial', 10)).pack(anchor="w", padx=20, pady=5)
        
        # Campo para cliente (se necessário)
        client_frame = tk.Frame(save_window)
        client_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(client_frame, text="ID do Cliente (apenas para template de cliente):", 
                font=('Arial', 9)).pack(anchor="w")
        client_id_entry = tk.Entry(client_frame, width=20)
        client_id_entry.pack(anchor="w", pady=5)
        
        def execute_save():
            save_type_value = save_type.get()
            success = False
            
            if save_type_value == "base":
                success = self.template_manager.save_base_template(self.pdf_template)
                message = "Template base atualizado!"
            elif save_type_value == "usuario":
                username = getattr(self, 'username', 'admin')  # Pegar username do usuário atual
                success = self.template_manager.save_user_template(username, self.pdf_template)
                message = f"Template do usuário {username} salvo!"
            elif save_type_value == "cliente":
                client_id = client_id_entry.get().strip()
                if not client_id:
                    self.show_warning("Validação", "Digite o ID do cliente.")
                    return
                success = self.template_manager.save_client_template(client_id, self.pdf_template)
                message = f"Template do cliente {client_id} salvo!"
            
            if success:
                self.show_success(message)
                save_window.destroy()
            else:
                self.show_error("Erro", "Erro ao salvar template.")
        
        # Botões
        btn_frame = tk.Frame(save_window)
        btn_frame.pack(fill="x", padx=20, pady=20)
        
        tk.Button(btn_frame, text="Salvar", command=execute_save, 
                 bg='#10b981', fg='white', font=('Arial', 10, 'bold')).pack(side="right", padx=(5, 0))
        tk.Button(btn_frame, text="Cancelar", command=save_window.destroy, 
                 bg='#ef4444', fg='white', font=('Arial', 10, 'bold')).pack(side="right")
    
    def select_page(self, page_num):
        """Selecionar página para edição"""
        self.current_page = page_num
        
        # Atualizar botões
        for i, btn in enumerate(self.page_buttons, 1):
            if i == page_num:
                btn.config(bg='#3b82f6', fg='white')
            else:
                btn.config(bg='#f8fafc', fg='#1e293b')
        
        # Atualizar informações da página
        page_info = self.get_page_info(page_num)
        self.page_info_label.config(text=page_info)
        
        # Atualizar preview
        self.refresh_page_preview()
        
        # Atualizar editor de conteúdo
        self.update_content_editor()
    
    def get_page_info(self, page_num):
        """Obter informações da página"""
        page_infos = {
            1: "Capa\n• Template editável\n• Imagem de fundo\n• Dados dinâmicos",
            2: "Apresentação\n• Texto totalmente editável\n• Logo da empresa\n• Dados automáticos",
            3: "Sobre a Empresa\n• Conteúdo editável\n• Seções personalizáveis\n• Formatação livre",
            4: "Proposta Comercial\n• Ordem dos elementos\n• Dados fixos da proposta\n• Layout personalizável"
        }
        return page_infos.get(page_num, "Página não encontrada")
    
    def refresh_page_preview(self):
        """Atualizar preview da página atual"""
        if not hasattr(self, 'canvas') or not self.pdf_template:
            return
            
        self.canvas.delete("all")
        
        # Desenhar fundo da página
        page_width_px = int(self.page_width * self.canvas_scale)
        page_height_px = int(self.page_height * self.canvas_scale)
        
        self.canvas.create_rectangle(0, 0, page_width_px, page_height_px, 
                                   fill="white", outline="#ccc", width=1)
        
        # Desenhar elementos da página atual
        page_key = f"pagina_{self.current_page}"
        if page_key in self.pdf_template:
            self.draw_page_elements(self.pdf_template[page_key])
        
        # Desenhar cabeçalho e rodapé
        self.draw_header_footer()
    
    def draw_page_elements(self, page_data):
        """Desenhar elementos da página"""
        if self.current_page == 1:
            self.draw_capa_elements(page_data)
        elif self.current_page == 2:
            self.draw_apresentacao_elements(page_data)
        elif self.current_page == 3:
            self.draw_sobre_empresa_elements(page_data)
        elif self.current_page == 4:
            self.draw_proposta_elements(page_data)
    
    def draw_capa_elements(self, page_data):
        """Desenhar elementos da capa"""
        # Simular imagem de fundo
        if page_data.get('elementos', {}).get('background_image'):
            self.canvas.create_rectangle(0, 0, 
                                       int(self.page_width * self.canvas_scale),
                                       int(self.page_height * self.canvas_scale),
                                       fill="#4a90e2", outline="", tags="background")
        
        # Título principal
        title_y = int(100 * self.canvas_scale)
        self.canvas.create_text(int(self.page_width * self.canvas_scale / 2), title_y,
                              text="PROPOSTA COMERCIAL", font=("Arial", 16, "bold"),
                              fill="white", tags="titulo")
        
        # Informações dinâmicas
        info_y = int(250 * self.canvas_scale)
        empresa_text = self.resolve_template_field(page_data.get('elementos', {}).get('texto_empresa', ''))
        self.canvas.create_text(int(self.page_width * self.canvas_scale / 2), info_y,
                              text=empresa_text, font=("Arial", 12),
                              fill="white", tags="empresa")
    
    def draw_apresentacao_elements(self, page_data):
        """Desenhar elementos da apresentação"""
        # Logo simulado
        logo_y = int(50 * self.canvas_scale)
        self.canvas.create_rectangle(int(80 * self.canvas_scale), logo_y,
                                   int(200 * self.canvas_scale), int(80 * self.canvas_scale),
                                   fill="#cccccc", outline="#999", tags="logo")
        self.canvas.create_text(int(140 * self.canvas_scale), int(65 * self.canvas_scale),
                              text="LOGO", font=("Arial", 10), tags="logo_text")
        
        # Texto de apresentação
        text_y = int(120 * self.canvas_scale)
        texto = page_data.get('elementos', {}).get('texto_apresentacao', 'Texto de apresentação...')
        lines = texto[:100] + "..." if len(texto) > 100 else texto
        self.canvas.create_text(int(50 * self.canvas_scale), text_y,
                              text=lines, font=("Arial", 10), anchor="nw",
                              width=int(500 * self.canvas_scale), tags="texto")
    
    def draw_sobre_empresa_elements(self, page_data):
        """Desenhar elementos sobre a empresa"""
        # Título
        title_y = int(50 * self.canvas_scale)
        self.canvas.create_text(int(50 * self.canvas_scale), title_y,
                              text="SOBRE A WORLD COMP", font=("Arial", 14, "bold"),
                              anchor="nw", tags="titulo")
        
        # Conteúdo
        content_y = int(80 * self.canvas_scale)
        conteudo = page_data.get('elementos', {}).get('conteudo', 'Conteúdo sobre a empresa...')
        lines = conteudo[:200] + "..." if len(conteudo) > 200 else conteudo
        self.canvas.create_text(int(50 * self.canvas_scale), content_y,
                              text=lines, font=("Arial", 10), anchor="nw",
                              width=int(500 * self.canvas_scale), tags="conteudo")
    
    def draw_proposta_elements(self, page_data):
        """Desenhar elementos da proposta"""
        elementos = page_data.get('elementos', {})
        ordem = elementos.get('ordem', ['dados_proposta', 'dados_cliente', 'tabela_itens', 'valor_total'])
        
        y_pos = 50
        for elemento in ordem:
            y_scaled = int(y_pos * self.canvas_scale)
            
            if elemento == 'dados_proposta':
                self.canvas.create_text(int(50 * self.canvas_scale), y_scaled,
                                      text="PROPOSTA Nº 100 - 2025-01-21", 
                                      font=("Arial", 12, "bold"), anchor="nw", tags="dados_proposta")
                y_pos += 25
                
            elif elemento == 'dados_cliente':
                self.canvas.create_text(int(50 * self.canvas_scale), y_scaled,
                                      text="CLIENTE: Empresa Exemplo LTDA", 
                                      font=("Arial", 10), anchor="nw", tags="dados_cliente")
                y_pos += 20
                
            elif elemento == 'tabela_itens':
                # Simular tabela
                table_width = int(500 * self.canvas_scale)
                table_height = int(100 * self.canvas_scale)
                self.canvas.create_rectangle(int(50 * self.canvas_scale), y_scaled,
                                           int(50 * self.canvas_scale) + table_width, y_scaled + table_height,
                                           outline="#333", fill="#f9f9f9", tags="tabela")
                self.canvas.create_text(int(300 * self.canvas_scale), y_scaled + int(50 * self.canvas_scale),
                                      text="TABELA DE ITENS", font=("Arial", 10), tags="tabela_text")
                y_pos += 120
                
            elif elemento == 'valor_total':
                self.canvas.create_text(int(400 * self.canvas_scale), y_scaled,
                                      text="TOTAL: R$ 10.000,00", 
                                      font=("Arial", 12, "bold"), anchor="nw", tags="valor_total")
                y_pos += 30
    
    def draw_header_footer(self):
        """Desenhar cabeçalho e rodapé"""
        # Cabeçalho
        if 'cabecalho' in self.pdf_template:
            header_template = self.pdf_template['cabecalho'].get('template', '')
            header_text = self.resolve_template_field(header_template)
            
            self.canvas.create_rectangle(0, 0, int(self.page_width * self.canvas_scale), int(20 * self.canvas_scale),
                                       fill="#f0f0f0", outline="#ccc", tags="header_bg")
            self.canvas.create_text(int(self.page_width * self.canvas_scale / 2), int(10 * self.canvas_scale),
                                  text=header_text, font=("Arial", 8), tags="header_text")
        
        # Rodapé
        if 'rodape' in self.pdf_template:
            footer_template = self.pdf_template['rodape'].get('template', '')
            footer_text = self.resolve_template_field(footer_template)
            
            footer_y = int((self.page_height - 15) * self.canvas_scale)
            self.canvas.create_rectangle(0, footer_y, int(self.page_width * self.canvas_scale), 
                                       int(self.page_height * self.canvas_scale),
                                       fill="#f0f0f0", outline="#ccc", tags="footer_bg")
            self.canvas.create_text(int(self.page_width * self.canvas_scale / 2), 
                                  footer_y + int(7 * self.canvas_scale),
                                  text=footer_text, font=("Arial", 8), tags="footer_text")
    
    def resolve_template_field(self, template_text):
        """Resolver campos do template"""
        if not template_text:
            return ""
        
        # Substituições de exemplo
        replacements = {
            '{{empresa.nome}}': self.available_fields.get('empresa', {}).get('nome', 'WORLD COMP COMPRESSORES LTDA'),
            '{{empresa.endereco}}': self.available_fields.get('empresa', {}).get('endereco', 'Endereço da empresa'),
            '{{empresa.cnpj}}': self.available_fields.get('empresa', {}).get('cnpj', '10.644.944/0001-55'),
            '{{empresa.email}}': self.available_fields.get('empresa', {}).get('email', 'contato@empresa.com'),
            '{{empresa.telefones}}': self.available_fields.get('empresa', {}).get('telefones', '(11) 1234-5678'),
            '{{proposta.numero}}': '100',
            '{{proposta.data}}': '2025-01-21',
            '{{cliente.nome}}': 'Cliente Exemplo',
            '{{cliente.contato}}': 'João Silva'
        }
        
        result = template_text
        for placeholder, value in replacements.items():
            result = result.replace(placeholder, str(value))
        
        return result
    
    def update_content_editor(self):
        """Atualizar editor de conteúdo baseado na página"""
        # Limpar frame atual
        for widget in self.content_editor_frame.winfo_children():
            widget.destroy()
        
        page_key = f"pagina_{self.current_page}"
        if page_key not in self.pdf_template:
            return
        
        page_data = self.pdf_template[page_key]
        editaveis = page_data.get('editavel', [])
        
        if self.current_page == 1:  # Capa
            tk.Label(self.content_editor_frame, text="Elementos da Capa:", 
                    font=('Arial', 10, 'bold'), bg='white').pack(anchor="w", pady=5)
            
            if 'background_image' in editaveis:
                img_btn = self.create_button(self.content_editor_frame, "Alterar Fundo", 
                                           self.change_background, bg='#6366f1')
                img_btn.pack(fill="x", pady=2)
            
            if 'overlay_image' in editaveis:
                overlay_btn = self.create_button(self.content_editor_frame, "Alterar Sobreposição", 
                                               self.change_overlay, bg='#8b5cf6')
                overlay_btn.pack(fill="x", pady=2)
        
        elif self.current_page in [2, 3]:  # Apresentação e Sobre Empresa
            tk.Label(self.content_editor_frame, text="Texto Editável:", 
                    font=('Arial', 10, 'bold'), bg='white').pack(anchor="w", pady=5)
            
            # Text editor
            text_key = 'texto_apresentacao' if self.current_page == 2 else 'conteudo'
            current_text = page_data.get('elementos', {}).get(text_key, '')
            
            text_widget = tk.Text(self.content_editor_frame, height=10, width=30, font=('Arial', 9))
            text_widget.pack(fill="both", expand=True, pady=5)
            text_widget.insert("1.0", current_text)
            
            # Salvar referência
            setattr(self, f'text_editor_{self.current_page}', text_widget)
            
            save_btn = self.create_button(self.content_editor_frame, "Salvar Texto", 
                                        lambda: self.save_page_text(self.current_page), bg='#10b981')
            save_btn.pack(fill="x", pady=5)
        
        elif self.current_page == 4:  # Proposta
            tk.Label(self.content_editor_frame, text="Ordem dos Elementos:", 
                    font=('Arial', 10, 'bold'), bg='white').pack(anchor="w", pady=5)
            
            elementos = page_data.get('elementos', {}).get('ordem', [])
            for i, elemento in enumerate(elementos):
                elem_frame = tk.Frame(self.content_editor_frame, bg='white')
                elem_frame.pack(fill="x", pady=2)
                
                tk.Label(elem_frame, text=f"{i+1}. {elemento.replace('_', ' ').title()}", 
                        bg='white', font=('Arial', 9)).pack(side="left")
                
                if i > 0:
                    up_btn = self.create_button(elem_frame, "↑", 
                                              lambda idx=i: self.move_element_up(idx), 
                                              bg='#64748b', width=3)
                    up_btn.pack(side="right", padx=1)
                
                if i < len(elementos) - 1:
                    down_btn = self.create_button(elem_frame, "↓", 
                                                lambda idx=i: self.move_element_down(idx), 
                                                bg='#64748b', width=3)
                    down_btn.pack(side="right", padx=1)
    
    def refresh_available_fields(self):
        """Atualizar campos disponíveis"""
        self.load_available_fields()
        self.update_header_fields()
        self.update_footer_fields()
        self.show_success("Campos atualizados!")
    
    def update_header_fields(self):
        """Atualizar campos do cabeçalho"""
        # Limpar frame atual
        for widget in self.header_fields_frame.winfo_children():
            widget.destroy()
        
        # Mostrar campos editáveis
        if 'cabecalho' in self.pdf_template:
            campos_editaveis = self.pdf_template['cabecalho'].get('campos_editaveis', [])
            
            for campo in campos_editaveis:
                field_frame = tk.Frame(self.header_fields_frame, bg='white')
                field_frame.pack(fill="x", pady=2)
                
                tk.Label(field_frame, text=f"{campo}:", bg='white', font=('Arial', 9)).pack(side="left")
                
                # Verificar se o campo existe no sistema
                field_exists = self.check_field_exists(campo)
                status_color = "#10b981" if field_exists else "#ef4444"
                status_text = "✓" if field_exists else "✗"
                
                tk.Label(field_frame, text=status_text, bg='white', fg=status_color, 
                        font=('Arial', 9, 'bold')).pack(side="right")
    
    def update_footer_fields(self):
        """Atualizar campos do rodapé"""
        # Limpar frame atual
        for widget in self.footer_fields_frame.winfo_children():
            widget.destroy()
        
        # Mostrar campos editáveis
        if 'rodape' in self.pdf_template:
            campos_editaveis = self.pdf_template['rodape'].get('campos_editaveis', [])
            
            for campo in campos_editaveis:
                field_frame = tk.Frame(self.footer_fields_frame, bg='white')
                field_frame.pack(fill="x", pady=2)
                
                tk.Label(field_frame, text=f"{campo}:", bg='white', font=('Arial', 9)).pack(side="left")
                
                # Verificar se o campo existe no sistema
                field_exists = self.check_field_exists(campo)
                status_color = "#10b981" if field_exists else "#ef4444"
                status_text = "✓" if field_exists else "✗"
                
                tk.Label(field_frame, text=status_text, bg='white', fg=status_color, 
                        font=('Arial', 9, 'bold')).pack(side="right")
                
                # Entry para editar se existe
                if field_exists:
                    current_value = self.get_field_value(campo)
                    entry = tk.Entry(field_frame, font=('Arial', 8), width=20)
                    entry.pack(side="right", padx=5)
                    entry.insert(0, current_value)
                    
                    # Salvar referência
                    setattr(self, f'footer_entry_{campo.replace(".", "_")}', entry)
    
    def check_field_exists(self, field_path):
        """Verificar se um campo existe no sistema"""
        parts = field_path.split('.')
        if len(parts) != 2:
            return False
        
        category, field = parts
        return category in self.available_fields and field in self.available_fields[category]
    
    def get_field_value(self, field_path):
        """Obter valor de um campo"""
        parts = field_path.split('.')
        if len(parts) != 2:
            return ""
        
        category, field = parts
        return self.available_fields.get(category, {}).get(field, "")
    
    def apply_header_changes(self):
        """Aplicar alterações no cabeçalho"""
        self.refresh_page_preview()
        self.show_success("Cabeçalho atualizado!")
    
    def apply_footer_changes(self):
        """Aplicar alterações no rodapé"""
        # Atualizar valores dos campos editados
        if 'rodape' in self.pdf_template:
            campos_editaveis = self.pdf_template['rodape'].get('campos_editaveis', [])
            
            for campo in campos_editaveis:
                entry_name = f'footer_entry_{campo.replace(".", "_")}'
                if hasattr(self, entry_name):
                    entry = getattr(self, entry_name)
                    new_value = entry.get()
                    
                    # Atualizar no available_fields
                    parts = campo.split('.')
                    if len(parts) == 2:
                        category, field = parts
                        if category in self.available_fields:
                            self.available_fields[category][field] = new_value
        
        self.refresh_page_preview()
        self.show_success("Rodapé atualizado!")
    
    def save_page_text(self, page_num):
        """Salvar texto da página"""
        text_editor = getattr(self, f'text_editor_{page_num}', None)
        if text_editor:
            new_text = text_editor.get("1.0", tk.END).strip()
            
            page_key = f"pagina_{page_num}"
            if page_key in self.pdf_template:
                if page_num == 2:
                    self.pdf_template[page_key]['elementos']['texto_apresentacao'] = new_text
                elif page_num == 3:
                    self.pdf_template[page_key]['elementos']['conteudo'] = new_text
            
            self.refresh_page_preview()
            self.show_success(f"Texto da página {page_num} salvo!")
    
    def move_element_up(self, index):
        """Mover elemento para cima na ordem"""
        page_key = f"pagina_{self.current_page}"
        if page_key in self.pdf_template and index > 0:
            ordem = self.pdf_template[page_key]['elementos']['ordem']
            ordem[index], ordem[index-1] = ordem[index-1], ordem[index]
            self.update_content_editor()
            self.refresh_page_preview()
    
    def move_element_down(self, index):
        """Mover elemento para baixo na ordem"""
        page_key = f"pagina_{self.current_page}"
        if page_key in self.pdf_template:
            ordem = self.pdf_template[page_key]['elementos']['ordem']
            if index < len(ordem) - 1:
                ordem[index], ordem[index+1] = ordem[index+1], ordem[index]
                self.update_content_editor()
                self.refresh_page_preview()
    
    def change_background(self):
        """Alterar imagem de fundo da capa"""
        if not PIL_AVAILABLE:
            self.show_warning("PIL/Pillow Necessário", "Para usar imagens, instale: pip install Pillow")
            return
        
        file_path = filedialog.askopenfilename(
            title="Selecionar imagem de fundo",
            filetypes=[("Imagens", "*.jpg *.jpeg *.png"), ("Todos os arquivos", "*.*")]
        )
        
        if file_path:
            self.pdf_template['pagina_1']['elementos']['background_image'] = file_path
            self.refresh_page_preview()
            self.show_success("Imagem de fundo atualizada!")
    
    def change_overlay(self):
        """Alterar imagem de sobreposição da capa"""
        if not PIL_AVAILABLE:
            self.show_warning("PIL/Pillow Necessário", "Para usar imagens, instale: pip install Pillow")
            return
        
        file_path = filedialog.askopenfilename(
            title="Selecionar imagem de sobreposição",
            filetypes=[("Imagens", "*.jpg *.jpeg *.png"), ("Todos os arquivos", "*.*")]
        )
        
        if file_path:
            self.pdf_template['pagina_1']['elementos']['overlay_image'] = file_path
            self.refresh_page_preview()
            self.show_success("Imagem de sobreposição atualizada!")
    
    def validate_template(self):
        """Validar template atual"""
        report = self.template_manager.get_template_validation_report(self.pdf_template, self.available_fields)
        
        if report['valido']:
            self.show_success("Template válido! Todas as verificações passaram.")
        else:
            problemas = []
            if report['erros']:
                problemas.extend([f"ERRO: {erro}" for erro in report['erros']])
            if report['campos_invalidos']:
                problemas.extend([f"CAMPO INVÁLIDO: {campo}" for campo in report['campos_invalidos']])
            if report['avisos']:
                problemas.extend([f"AVISO: {aviso}" for aviso in report['avisos']])
            
            self.show_warning("Problemas de Validação", "\n".join(problemas))
    
    def generate_preview_pdf(self):
        """Gerar preview do PDF"""
        self.show_info("Preview PDF", "Funcionalidade de geração de preview será implementada em versão futura.")
    
    def load_template(self):
        """Carregar template de arquivo ou usuário/cliente"""
        # Dialog para escolher tipo de carregamento
        load_window = tk.Toplevel(self.frame)
        load_window.title("Carregar Template")
        load_window.geometry("450x400")
        load_window.transient(self.frame)
        
        tk.Label(load_window, text="Qual template deseja carregar?", 
                font=('Arial', 12, 'bold')).pack(pady=20)
        
        # Notebook para diferentes tipos
        notebook = ttk.Notebook(load_window)
        notebook.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Aba 1: Template de arquivo
        file_frame = tk.Frame(notebook)
        notebook.add(file_frame, text="Arquivo")
        
        tk.Label(file_frame, text="Carregar template de arquivo JSON:", 
                font=('Arial', 10)).pack(pady=10)
        
        file_path_var = tk.StringVar()
        file_entry = tk.Entry(file_frame, textvariable=file_path_var, width=40, state="readonly")
        file_entry.pack(pady=5)
        
        def browse_file():
            file_path = filedialog.askopenfilename(
                title="Carregar Template",
                filetypes=[("JSON", "*.json"), ("Todos os arquivos", "*.*")]
            )
            if file_path:
                file_path_var.set(file_path)
        
        tk.Button(file_frame, text="Procurar Arquivo", command=browse_file, 
                 bg='#3b82f6', fg='white').pack(pady=5)
        
        # Aba 2: Templates de usuários
        user_frame = tk.Frame(notebook)
        notebook.add(user_frame, text="Usuários")
        
        tk.Label(user_frame, text="Templates de usuários disponíveis:", 
                font=('Arial', 10)).pack(pady=5)
        
        user_listbox = tk.Listbox(user_frame, height=8)
        user_listbox.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Carregar templates de usuários
        user_templates = self.template_manager.list_user_templates()
        for username, path, created in user_templates:
            user_listbox.insert(tk.END, f"{username} ({created[:10]})")
        
        # Aba 3: Templates de clientes
        client_frame = tk.Frame(notebook)
        notebook.add(client_frame, text="Clientes")
        
        tk.Label(client_frame, text="Templates de clientes disponíveis:", 
                font=('Arial', 10)).pack(pady=5)
        
        client_listbox = tk.Listbox(client_frame, height=8)
        client_listbox.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Carregar templates de clientes
        client_templates = self.template_manager.list_client_templates()
        for client_id, path, created in client_templates:
            client_listbox.insert(tk.END, f"Cliente {client_id} ({created[:10]})")
        
        def execute_load():
            current_tab = notebook.index(notebook.select())
            success = False
            
            if current_tab == 0:  # Arquivo
                file_path = file_path_var.get()
                if not file_path:
                    self.show_warning("Validação", "Selecione um arquivo.")
                    return
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        template = json.load(f)
                    
                    if self.template_manager.validate_template(template):
                        self.pdf_template = template
                        success = True
                    else:
                        self.show_error("Erro", "Template inválido.")
                        return
                except Exception as e:
                    self.show_error("Erro", f"Erro ao carregar arquivo: {str(e)}")
                    return
                    
            elif current_tab == 1:  # Usuário
                selection = user_listbox.curselection()
                if not selection:
                    self.show_warning("Validação", "Selecione um template de usuário.")
                    return
                
                username = user_templates[selection[0]][0]
                self.pdf_template = self.template_manager.load_user_template(username)
                success = True
                
            elif current_tab == 2:  # Cliente
                selection = client_listbox.curselection()
                if not selection:
                    self.show_warning("Validação", "Selecione um template de cliente.")
                    return
                
                client_id = client_templates[selection[0]][0]
                self.pdf_template = self.template_manager.load_client_template(client_id)
                success = True
            
            if success:
                self.refresh_page_preview()
                self.update_content_editor()
                self.show_success("Template carregado com sucesso!")
                load_window.destroy()
        
        # Botões
        btn_frame = tk.Frame(load_window)
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Button(btn_frame, text="Carregar", command=execute_load, 
                 bg='#10b981', fg='white', font=('Arial', 10, 'bold')).pack(side="right", padx=(5, 0))
        tk.Button(btn_frame, text="Cancelar", command=load_window.destroy, 
                 bg='#ef4444', fg='white', font=('Arial', 10, 'bold')).pack(side="right")
    
    def reset_template(self):
        """Restaurar template padrão"""
        if messagebox.askyesno("Confirmar", "Deseja restaurar o template padrão? Todas as alterações serão perdidas."):
            self.pdf_template = self.template_manager.load_base_template()
            self.refresh_page_preview()
            self.update_content_editor()
            self.show_success("Template restaurado para o padrão!")
    
    def zoom_in(self):
        """Aumentar zoom"""
        self.canvas_scale = min(1.5, self.canvas_scale * 1.2)
        self.zoom_label.config(text=f"{int(self.canvas_scale*100)}%")
        self.refresh_page_preview()
    
    def zoom_out(self):
        """Diminuir zoom"""
        self.canvas_scale = max(0.3, self.canvas_scale / 1.2)
        self.zoom_label.config(text=f"{int(self.canvas_scale*100)}%")
        self.refresh_page_preview()
    
    def on_canvas_click(self, event):
        """Clique no canvas"""
        # Funcionalidade futura para seleção de elementos
        pass
    
    def on_canvas_double_click(self, event):
        """Duplo clique no canvas"""
        # Funcionalidade futura para edição rápida
        pass