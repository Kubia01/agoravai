import tkinter as tk
from tkinter import ttk
import sqlite3
from datetime import datetime, timedelta
from .base_module import BaseModule
from database import DB_NAME
from utils.formatters import format_currency

class DashboardModule(BaseModule):
    def setup_ui(self):
        # Container principal com melhor aproveitamento de espaço
        container = tk.Frame(self.frame, bg='#f8fafc')
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header com informações do usuário
        self.create_header(container)
        
        # Frame principal dividido em duas colunas
        main_frame = tk.Frame(container, bg='#f8fafc')
        main_frame.pack(fill="both", expand=True, pady=(20, 0))
        
        # Coluna esquerda (70% da largura)
        left_frame = tk.Frame(main_frame, bg='#f8fafc')
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Coluna direita (30% da largura)
        right_frame = tk.Frame(main_frame, bg='#f8fafc')
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Criar seções
        self.create_stats_cards(left_frame)
        self.create_recent_activities(left_frame)
        self.create_quick_actions(right_frame)
        self.create_performance_charts(right_frame)
        
        # Carregar dados
        self.load_dashboard_data()
        
    def create_header(self, parent):
        """Header com informações do usuário e período"""
        header_frame = tk.Frame(parent, bg='white', relief='solid', bd=1)
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Informações do usuário
        user_info_frame = tk.Frame(header_frame, bg='white')
        user_info_frame.pack(side="left", padx=20, pady=15)
        
        # Nome do usuário
        self.user_name_label = tk.Label(user_info_frame, 
                                       text="Carregando...", 
                                       font=('Arial', 16, 'bold'),
                                       bg='white', fg='#1e293b')
        self.user_name_label.pack(anchor="w")
        
        # Perfil do usuário
        self.user_role_label = tk.Label(user_info_frame, 
                                       text="", 
                                       font=('Arial', 12),
                                       bg='white', fg='#64748b')
        self.user_role_label.pack(anchor="w")
        
        # Período atual
        period_frame = tk.Frame(header_frame, bg='white')
        period_frame.pack(side="right", padx=20, pady=15)
        
        period_label = tk.Label(period_frame, 
                               text=f"Período: {datetime.now().strftime('%B/%Y')}", 
                               font=('Arial', 12, 'bold'),
                               bg='white', fg='#64748b')
        period_label.pack(anchor="e")
        
    def create_stats_cards(self, parent):
        """Cards de estatísticas com melhor layout"""
        # Frame para os cards
        cards_frame = tk.Frame(parent, bg='#f8fafc')
        cards_frame.pack(fill="x", pady=(0, 20))
        
        # Grid 2x2 para os cards principais
        # Card 1: Cotações
        self.quotes_card = self.create_stat_card(cards_frame, "💰 Cotações", "0", "#3b82f6", "Em Aberto: 0")
        self.quotes_card.grid(row=0, column=0, padx=(0, 10), pady=(0, 10), sticky="ew")
        
        # Card 2: Valor Total
        self.value_card = self.create_stat_card(cards_frame, "💵 Valor Total", "R$ 0,00", "#10b981", "Média: R$ 0,00")
        self.value_card.grid(row=0, column=1, padx=(10, 0), pady=(0, 10), sticky="ew")
        
        # Card 3: Relatórios
        self.reports_card = self.create_stat_card(cards_frame, "📋 Relatórios", "0", "#f59e0b", "Este mês: 0")
        self.reports_card.grid(row=1, column=0, padx=(0, 10), pady=(10, 0), sticky="ew")
        
        # Card 4: Performance
        self.performance_card = self.create_stat_card(cards_frame, "📈 Performance", "0%", "#ef4444", "Taxa de Aprovação")
        self.performance_card.grid(row=1, column=1, padx=(10, 0), pady=(10, 0), sticky="ew")
        
        # Configurar grid
        cards_frame.grid_columnconfigure(0, weight=1)
        cards_frame.grid_columnconfigure(1, weight=1)
        
    def create_stat_card(self, parent, title, value, color, subtitle=""):
        """Criar um card de estatística melhorado"""
        card = tk.Frame(parent, bg='white', relief='solid', bd=1)
        
        # Container interno
        inner_frame = tk.Frame(card, bg='white', padx=20, pady=15)
        inner_frame.pack(fill="both", expand=True)
        
        # Título
        title_label = tk.Label(inner_frame, text=title, 
                              font=('Arial', 14, 'bold'),
                              bg='white', fg=color)
        title_label.pack(anchor="w")
        
        # Valor principal
        value_label = tk.Label(inner_frame, text=value,
                              font=('Arial', 28, 'bold'),
                              bg='white', fg='#1e293b')
        value_label.pack(anchor="w", pady=(5, 0))
        
        # Subtítulo
        if subtitle:
            subtitle_label = tk.Label(inner_frame, text=subtitle,
                                    font=('Arial', 10),
                                    bg='white', fg='#64748b')
            subtitle_label.pack(anchor="w", pady=(2, 0))
        
        # Armazenar referências
        card.value_label = value_label
        card.subtitle_label = subtitle_label if subtitle else None
        
        return card
        
    def create_recent_activities(self, parent):
        """Seção de atividades recentes otimizada"""
        # Frame principal
        activities_frame = self.create_section_frame(parent, "Atividades Recentes")
        activities_frame.pack(fill="both", expand=True)
        
        # Notebook para diferentes tipos de atividades
        self.activities_notebook = ttk.Notebook(activities_frame)
        self.activities_notebook.pack(fill="both", expand=True, pady=10)
        
        # Aba Cotações Recentes
        quotes_frame = tk.Frame(self.activities_notebook, bg='white')
        self.activities_notebook.add(quotes_frame, text="Cotações")
        self.create_recent_quotes_list(quotes_frame)
        
        # Aba Relatórios Recentes
        reports_frame = tk.Frame(self.activities_notebook, bg='white')
        self.activities_notebook.add(reports_frame, text="Relatórios")
        self.create_recent_reports_list(reports_frame)
        
    def create_quick_actions(self, parent):
        """Ações rápidas na coluna direita"""
        actions_frame = self.create_section_frame(parent, "Ações Rápidas")
        actions_frame.pack(fill="x", pady=(0, 20))
        
        # Botões de ação rápida
        actions = [
            ("➕ Nova Cotação", "#3b82f6"),
            ("📋 Novo Relatório", "#10b981"),
            ("👥 Novo Cliente", "#f59e0b"),
            ("📦 Novo Produto", "#ef4444")
        ]
        
        for text, color in actions:
            btn = tk.Button(actions_frame, text=text, 
                           font=('Arial', 12, 'bold'),
                           bg=color, fg='white',
                           relief='flat', padx=20, pady=10,
                           cursor='hand2')
            btn.pack(fill="x", pady=5)
            
            # Hover effect
            btn.bind('<Enter>', lambda e, b=btn: b.configure(bg=self.lighten_color(color)))
            btn.bind('<Leave>', lambda e, b=btn, c=color: b.configure(bg=c))
    
    def create_performance_charts(self, parent):
        """Gráficos de performance na coluna direita"""
        charts_frame = self.create_section_frame(parent, "Performance")
        charts_frame.pack(fill="both", expand=True)
        
        # Status das cotações
        status_frame = tk.Frame(charts_frame, bg='white')
        status_frame.pack(fill="x", pady=10)
        
        status_label = tk.Label(status_frame, text="Status das Cotações", 
                               font=('Arial', 12, 'bold'),
                               bg='white', fg='#1e293b')
        status_label.pack(anchor="w", pady=(0, 10))
        
        # Lista de status
        self.status_list = tk.Frame(status_frame, bg='white')
        self.status_list.pack(fill="x")
        
        # Top produtos
        products_frame = tk.Frame(charts_frame, bg='white')
        products_frame.pack(fill="x", pady=10)
        
        products_label = tk.Label(products_frame, text="Top Produtos", 
                                 font=('Arial', 12, 'bold'),
                                 bg='white', fg='#1e293b')
        products_label.pack(anchor="w", pady=(0, 10))
        
        # Lista de produtos
        self.products_list = tk.Frame(products_frame, bg='white')
        self.products_list.pack(fill="x")
        
    def create_recent_quotes_list(self, parent):
        """Lista de cotações recentes otimizada"""
        # Frame com scroll
        list_frame = tk.Frame(parent, bg='white')
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Treeview para cotações
        columns = ('Data', 'Cliente', 'Valor', 'Status')
        self.quotes_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        
        # Configurar colunas
        self.quotes_tree.heading('Data', text='Data')
        self.quotes_tree.heading('Cliente', text='Cliente')
        self.quotes_tree.heading('Valor', text='Valor')
        self.quotes_tree.heading('Status', text='Status')
        
        self.quotes_tree.column('Data', width=100)
        self.quotes_tree.column('Cliente', width=200)
        self.quotes_tree.column('Valor', width=100)
        self.quotes_tree.column('Status', width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.quotes_tree.yview)
        self.quotes_tree.configure(yscrollcommand=scrollbar.set)
        
        self.quotes_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def create_recent_reports_list(self, parent):
        """Lista de relatórios recentes otimizada"""
        # Frame com scroll
        list_frame = tk.Frame(parent, bg='white')
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Treeview para relatórios
        columns = ('Data', 'Cliente', 'Técnico', 'Status')
        self.reports_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        
        # Configurar colunas
        self.reports_tree.heading('Data', text='Data')
        self.reports_tree.heading('Cliente', text='Cliente')
        self.reports_tree.heading('Técnico', text='Técnico')
        self.reports_tree.heading('Status', text='Status')
        
        self.reports_tree.column('Data', width=100)
        self.reports_tree.column('Cliente', width=200)
        self.reports_tree.column('Técnico', width=150)
        self.reports_tree.column('Status', width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.reports_tree.yview)
        self.reports_tree.configure(yscrollcommand=scrollbar.set)
        
        self.reports_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def load_dashboard_data(self):
        """Carregar dados do dashboard baseado no usuário"""
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            
            # Obter informações do usuário atual
            current_user = self._get_current_username()
            user_role = self._get_user_role(current_user)
            
            # Atualizar header
            self.user_name_label.config(text=f"Bem-vindo, {current_user}")
            self.user_role_label.config(text=f"Perfil: {user_role}")
            
            # Carregar estatísticas baseadas no perfil
            if user_role == 'master':
                self.load_master_stats(cursor)
            else:
                self.load_user_stats(cursor, current_user)
            
            # Carregar atividades recentes
            self.load_recent_quotes(cursor, current_user, user_role)
            self.load_recent_reports(cursor, current_user, user_role)
            
            # Carregar performance
            self.load_performance_data(cursor, current_user, user_role)
            
            conn.close()
            
        except Exception as e:
            print(f"Erro ao carregar dashboard: {e}")
    
    def load_master_stats(self, cursor):
        """Carregar estatísticas para usuário master"""
        # Total de cotações
        cursor.execute("SELECT COUNT(*) FROM cotacoes")
        total_quotes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM cotacoes WHERE status = 'Em Aberto'")
        open_quotes = cursor.fetchone()[0]
        
        # Valor total
        cursor.execute("SELECT COALESCE(SUM(valor_total), 0) FROM cotacoes")
        total_value = cursor.fetchone()[0]
        
        cursor.execute("SELECT COALESCE(AVG(valor_total), 0) FROM cotacoes WHERE valor_total > 0")
        avg_value = cursor.fetchone()[0]
        
        # Relatórios
        cursor.execute("SELECT COUNT(*) FROM relatorios")
        total_reports = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM relatorios WHERE created_at >= date('now', 'start of month')")
        month_reports = cursor.fetchone()[0]
        
        # Performance
        cursor.execute("SELECT COUNT(*) FROM cotacoes WHERE status = 'Aprovada'")
        approved_quotes = cursor.fetchone()[0]
        
        approval_rate = (approved_quotes / total_quotes * 100) if total_quotes > 0 else 0
        
        # Atualizar cards
        self.quotes_card.value_label.config(text=str(total_quotes))
        self.quotes_card.subtitle_label.config(text=f"Em Aberto: {open_quotes}")
        
        self.value_card.value_label.config(text=format_currency(total_value))
        self.value_card.subtitle_label.config(text=f"Média: {format_currency(avg_value)}")
        
        self.reports_card.value_label.config(text=str(total_reports))
        self.reports_card.subtitle_label.config(text=f"Este mês: {month_reports}")
        
        self.performance_card.value_label.config(text=f"{approval_rate:.1f}%")
        
    def load_user_stats(self, cursor, username):
        """Carregar estatísticas para usuário específico"""
        # Total de cotações do usuário
        cursor.execute("SELECT COUNT(*) FROM cotacoes WHERE usuario = ?", (username,))
        total_quotes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM cotacoes WHERE usuario = ? AND status = 'Em Aberto'", (username,))
        open_quotes = cursor.fetchone()[0]
        
        # Valor total do usuário
        cursor.execute("SELECT COALESCE(SUM(valor_total), 0) FROM cotacoes WHERE usuario = ?", (username,))
        total_value = cursor.fetchone()[0]
        
        cursor.execute("SELECT COALESCE(AVG(valor_total), 0) FROM cotacoes WHERE usuario = ? AND valor_total > 0", (username,))
        avg_value = cursor.fetchone()[0]
        
        # Relatórios do usuário
        cursor.execute("SELECT COUNT(*) FROM relatorios WHERE usuario = ?", (username,))
        total_reports = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM relatorios WHERE usuario = ? AND created_at >= date('now', 'start of month')", (username,))
        month_reports = cursor.fetchone()[0]
        
        # Performance do usuário
        cursor.execute("SELECT COUNT(*) FROM cotacoes WHERE usuario = ? AND status = 'Aprovada'", (username,))
        approved_quotes = cursor.fetchone()[0]
        
        approval_rate = (approved_quotes / total_quotes * 100) if total_quotes > 0 else 0
        
        # Atualizar cards
        self.quotes_card.value_label.config(text=str(total_quotes))
        self.quotes_card.subtitle_label.config(text=f"Em Aberto: {open_quotes}")
        
        self.value_card.value_label.config(text=format_currency(total_value))
        self.value_card.subtitle_label.config(text=f"Média: {format_currency(avg_value)}")
        
        self.reports_card.value_label.config(text=str(total_reports))
        self.reports_card.subtitle_label.config(text=f"Este mês: {month_reports}")
        
        self.performance_card.value_label.config(text=f"{approval_rate:.1f}%")
    
    def load_recent_quotes(self, cursor, username, role):
        """Carregar cotações recentes"""
        # Limpar lista
        for item in self.quotes_tree.get_children():
            self.quotes_tree.delete(item)
        
        # Query baseada no perfil
        if role == 'master':
            query = """
                SELECT c.data_criacao, cl.nome, c.valor_total, c.status
                FROM cotacoes c
                LEFT JOIN clientes cl ON c.cliente_id = cl.id
                ORDER BY c.data_criacao DESC
                LIMIT 10
            """
            cursor.execute(query)
        else:
            query = """
                SELECT c.data_criacao, cl.nome, c.valor_total, c.status
                FROM cotacoes c
                LEFT JOIN clientes cl ON c.cliente_id = cl.id
                WHERE c.usuario = ?
                ORDER BY c.data_criacao DESC
                LIMIT 10
            """
            cursor.execute(query, (username,))
        
        for row in cursor.fetchall():
            data, cliente, valor, status = row
            data_str = data.split()[0] if data else ""
            valor_str = format_currency(valor) if valor else "R$ 0,00"
            
            self.quotes_tree.insert('', 'end', values=(data_str, cliente, valor_str, status))
    
    def load_recent_reports(self, cursor, username, role):
        """Carregar relatórios recentes"""
        # Limpar lista
        for item in self.reports_tree.get_children():
            self.reports_tree.delete(item)
        
        # Query baseada no perfil
        if role == 'master':
            query = """
                SELECT r.created_at, cl.nome, t.nome, r.status
                FROM relatorios r
                LEFT JOIN clientes cl ON r.cliente_id = cl.id
                LEFT JOIN tecnicos t ON r.tecnico_id = t.id
                ORDER BY r.created_at DESC
                LIMIT 10
            """
            cursor.execute(query)
        else:
            query = """
                SELECT r.created_at, cl.nome, t.nome, r.status
                FROM relatorios r
                LEFT JOIN clientes cl ON r.cliente_id = cl.id
                LEFT JOIN tecnicos t ON r.tecnico_id = t.id
                WHERE r.usuario = ?
                ORDER BY r.created_at DESC
                LIMIT 10
            """
            cursor.execute(query, (username,))
        
        for row in cursor.fetchall():
            data, cliente, tecnico, status = row
            data_str = data.split()[0] if data else ""
            
            self.reports_tree.insert('', 'end', values=(data_str, cliente, tecnico, status))
    
    def load_performance_data(self, cursor, username, role):
        """Carregar dados de performance"""
        # Limpar listas
        for widget in self.status_list.winfo_children():
            widget.destroy()
        
        for widget in self.products_list.winfo_children():
            widget.destroy()
        
        # Status das cotações
        if role == 'master':
            cursor.execute("""
                SELECT status, COUNT(*) 
                FROM cotacoes 
                GROUP BY status 
                ORDER BY COUNT(*) DESC
            """)
        else:
            cursor.execute("""
                SELECT status, COUNT(*) 
                FROM cotacoes 
                WHERE usuario = ?
                GROUP BY status 
                ORDER BY COUNT(*) DESC
            """, (username,))
        
        for status, count in cursor.fetchall():
            status_frame = tk.Frame(self.status_list, bg='white')
            status_frame.pack(fill="x", pady=2)
            
            tk.Label(status_frame, text=status, font=('Arial', 10), bg='white').pack(side="left")
            tk.Label(status_frame, text=str(count), font=('Arial', 10, 'bold'), bg='white').pack(side="right")
        
        # Top produtos
        if role == 'master':
            cursor.execute("""
                SELECT p.nome, COUNT(*) 
                FROM cotacao_itens ci
                JOIN produtos p ON ci.produto_id = p.id
                GROUP BY p.id, p.nome
                ORDER BY COUNT(*) DESC
                LIMIT 5
            """)
        else:
            cursor.execute("""
                SELECT p.nome, COUNT(*) 
                FROM cotacao_itens ci
                JOIN produtos p ON ci.produto_id = p.id
                JOIN cotacoes c ON ci.cotacao_id = c.id
                WHERE c.usuario = ?
                GROUP BY p.id, p.nome
                ORDER BY COUNT(*) DESC
                LIMIT 5
            """, (username,))
        
        for produto, count in cursor.fetchall():
            prod_frame = tk.Frame(self.products_list, bg='white')
            prod_frame.pack(fill="x", pady=2)
            
            tk.Label(prod_frame, text=produto, font=('Arial', 10), bg='white').pack(side="left")
            tk.Label(prod_frame, text=str(count), font=('Arial', 10, 'bold'), bg='white').pack(side="right")
    
    def _get_current_username(self):
        """Obter nome do usuário atual"""
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT username FROM usuarios WHERE id = (SELECT MAX(id) FROM usuarios)")
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else "Usuário"
        except:
            return "Usuário"
    
    def _get_user_role(self, username):
        """Obter perfil do usuário"""
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT role FROM usuarios WHERE username = ?", (username,))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else "operador"
        except:
            return "operador"
    
    def lighten_color(self, color):
        """Clarear cor para efeito hover"""
        # Implementação simples - você pode melhorar isso
        return color
    
    def handle_event(self, event_type, data=None):
        """Manipular eventos do sistema"""
        if event_type == "refresh_dashboard":
            self.load_dashboard_data()