import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from database import DB_NAME

class MainWindow:
    def __init__(self, root, user_id, username, role, nome_completo):
        self.root = root
        self.user_id = user_id
        self.username = username
        self.role = role
        self.nome_completo = nome_completo
        self.listeners = []
        
        self.setup_window()
        self.create_layout()

    def register_listener(self, callback):
        self.listeners.append(callback)
        
    def notify_listeners(self, event_type):
        for callback in self.listeners:
            callback(event_type)
        
    def setup_window(self):
        self.root.title("CRM Compressores - Sistema de Gestão")
        self.root.geometry("1400x900")
        self.root.state('zoomed')  # Maximizar no Windows
        self.root.configure(bg='#f8fafc')
        
    def create_layout(self):
        # Frame principal
        self.main_frame = tk.Frame(self.root, bg='#f8fafc')
        self.main_frame.pack(fill="both", expand=True)
        
        # Sidebar
        self.create_sidebar()
        
        # Área de conteúdo
        self.content_frame = tk.Frame(self.main_frame, bg='#f8fafc')
        self.content_frame.pack(side="right", fill="both", expand=True, padx=(0, 20), pady=20)
        
        # Header
        self.create_header()
        
        # Área principal de conteúdo
        self.main_content = tk.Frame(self.content_frame, bg='#f8fafc')
        self.main_content.pack(fill="both", expand=True, pady=(20, 0))
        
        # Carregar módulos
        self.load_modules()
        
    def create_sidebar(self):
        # Sidebar frame
        self.sidebar = tk.Frame(self.main_frame, bg='#1e293b', width=280)
        self.sidebar.pack(side="left", fill="y", padx=(20, 20), pady=20)
        self.sidebar.pack_propagate(False)
        
        # Logo/Título
        logo_frame = tk.Frame(self.sidebar, bg='#1e293b', pady=20)
        logo_frame.pack(fill="x")
        
        title_label = tk.Label(logo_frame, text="CRM", 
                               font=('Arial', 18, 'bold'),
                               bg='#1e293b',
                               fg='#60a5fa')
        title_label.pack()
        
        subtitle_label = tk.Label(logo_frame, text="Compressores", 
                                  font=('Arial', 12),
                                  bg='#1e293b',
                                  fg='#94a3b8')
        subtitle_label.pack()
        
        # Menu items
        self.menu_frame = tk.Frame(self.sidebar, bg='#1e293b', pady=10)
        self.menu_frame.pack(fill="both", expand=True)
        
        # Definir itens do menu
        menu_items = [
            ("Dashboard", "📊", "dashboard"),
            ("Clientes", "🏢", "clientes"),
            ("Produtos", "📦", "produtos"),  # NOVA ABA
            ("Cotações", "📋", "cotacoes"),
            ("Relatórios", "📄", "relatorios"),
        ]
        
        # Adicionar itens administrativos se for admin
        if self.role == 'admin':
            menu_items.extend([
                ("Técnicos", "🔧", "tecnicos"),
                ("Usuários", "👥", "usuarios"),
            ])
        
        self.menu_buttons = {}
        self.current_module = None
        
        for text, icon, module_id in menu_items:
            btn_frame = tk.Frame(self.menu_frame, bg='#1e293b')
            btn_frame.pack(fill="x", pady=2)
            
            btn = tk.Button(btn_frame, 
                           text=f"{icon}  {text}",
                           font=('Arial', 11),
                           bg='#1e293b',
                           fg='#cbd5e1',
                           activebackground='#3b82f6',
                           activeforeground='white',
                           border=0,
                           cursor='hand2',
                           anchor='w',
                           padx=20,
                           pady=12,
                           command=lambda m=module_id: self.switch_module(m))
            btn.pack(fill="x")
            
            self.menu_buttons[module_id] = btn
            
        # Informações do usuário
        user_frame = tk.Frame(self.sidebar, bg='#1e293b', pady=20)
        user_frame.pack(side="bottom", fill="x")
        
        user_label = tk.Label(user_frame, text=f"👤 {self.nome_completo}", 
                              font=('Arial', 10),
                              bg='#1e293b',
                              fg='#cbd5e1')
        user_label.pack()
        
        role_label = tk.Label(user_frame, text=f"Perfil: {self.role.title()}", 
                              font=('Arial', 9),
                              bg='#1e293b',
                              fg='#94a3b8')
        role_label.pack()
        
    def create_header(self):
        self.header_frame = tk.Frame(self.content_frame, bg='white', relief='solid', bd=1)
        self.header_frame.pack(fill="x", pady=(0, 20))
        
        header_content = tk.Frame(self.header_frame, bg='white', padx=20, pady=15)
        header_content.pack(fill="x")
        
        # Título da página
        self.page_title = tk.Label(header_content, text="Dashboard", 
                                   font=('Arial', 24, 'bold'),
                                   bg='white',
                                   fg='#1e293b')
        self.page_title.pack(side="left")
        
        # Botões do header
        header_buttons = tk.Frame(header_content, bg='white')
        header_buttons.pack(side="right")
        
        # Botão de logout
        logout_btn = tk.Button(header_buttons, text="Sair", 
                               font=('Arial', 10),
                               bg='#e2e8f0',
                               fg='#475569',
                               relief='flat',
                               cursor='hand2',
                               padx=15,
                               pady=8,
                               command=self.logout)
        logout_btn.pack(side="right", padx=(10, 0))
        
    def load_modules(self):
        # Importar módulos
        from interface.modules.dashboard import DashboardModule
        from interface.modules.clientes import ClientesModule
        from interface.modules.produtos import ProdutosModule  # NOVO MÓDULO
        from interface.modules.cotacoes import CotacoesModule
        from interface.modules.relatorios import RelatoriosModule
        
        self.modules = {}
        
        # Carregar módulos
        self.modules['dashboard'] = DashboardModule(self.main_content, self.user_id, self.role)
        self.modules['clientes'] = ClientesModule(self.main_content, self.user_id, self.role)
        self.modules['produtos'] = ProdutosModule(self.main_content, self.user_id, self.role)  # NOVO
        self.modules['cotacoes'] = CotacoesModule(self.main_content, self.user_id, self.role)
        self.modules['relatorios'] = RelatoriosModule(self.main_content, self.user_id, self.role)
        
        if self.role == 'admin':
            from interface.modules.tecnicos import TecnicosModule
            from interface.modules.usuarios import UsuariosModule
            self.modules['tecnicos'] = TecnicosModule(self.main_content, self.user_id, self.role)
            self.modules['usuarios'] = UsuariosModule(self.main_content, self.user_id, self.role)
        
        # Mostrar dashboard inicialmente
        self.switch_module('dashboard')
        
    def switch_module(self, module_id):
        # Esconder módulo atual
        if self.current_module and self.current_module in self.modules:
            self.modules[self.current_module].hide()
            
        # Resetar cores dos botões
        for btn_id, btn in self.menu_buttons.items():
            if btn_id == module_id:
                btn.configure(bg='#3b82f6', fg='white')
            else:
                btn.configure(bg='#1e293b', fg='#cbd5e1')
        
        # Mostrar novo módulo
        if module_id in self.modules:
            self.modules[module_id].show()
            self.current_module = module_id
            
            # Atualizar título
            titles = {
                'dashboard': 'Dashboard',
                'clientes': 'Gestão de Clientes',
                'produtos': 'Gestão de Produtos/Serviços/Kits',  # NOVO
                'cotacoes': 'Gestão de Cotações',
                'relatorios': 'Relatórios Técnicos',
                'tecnicos': 'Gestão de Técnicos',
                'usuarios': 'Gestão de Usuários'
            }
            self.page_title.configure(text=titles.get(module_id, 'CRM'))
            
    def logout(self):
        if messagebox.askyesno("Logout", "Deseja realmente sair do sistema?"):
            self.root.quit()