import tkinter as tk
from tkinter import ttk
import sqlite3
from database import DB_NAME
from .base_module import BaseModule

class DashboardModule(BaseModule):
    def setup_ui(self):
        # Container principal
        container = tk.Frame(self.frame, bg='#f8fafc')
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Cards de estatísticas
        self.create_stats_cards(container)
        
        # Gráficos e listas
        content_frame = tk.Frame(container, bg='#f8fafc')
        content_frame.pack(fill="both", expand=True, pady=(20, 0))
        
        # Atividades recentes
        self.create_recent_activities(content_frame)
        
        # Itens pendentes
        self.create_pending_items(content_frame)
        
    def create_stats_cards(self, parent):
        stats_frame = tk.Frame(parent, bg='#f8fafc')
        stats_frame.pack(fill="x")
        
        # Obter estatísticas do banco
        stats = self.get_statistics()
        
        cards_data = [
            ("Total de Clientes", stats['clientes'], "🏢", "#3b82f6"),
            ("Cotações Ativas", stats['cotacoes'], "📋", "#10b981"),
            ("Relatórios Técnicos", stats['relatorios'], "📄", "#f59e0b"),
            ("Valor Total", f"R$ {stats['valor_total']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'), "💰", "#8b5cf6")
        ]
        
        for i, (title, value, icon, color) in enumerate(cards_data):
            card = self.create_stat_card(stats_frame, title, value, icon, color)
            card.grid(row=0, column=i, padx=10, sticky="ew")
            
        # Configurar colunas para expandir igualmente
        for i in range(4):
            stats_frame.grid_columnconfigure(i, weight=1)
            
    def create_stat_card(self, parent, title, value, icon, color):
        card = tk.Frame(parent, bg='white', relief='solid', bd=1, padx=20, pady=20)
        
        # Header do card
        header_frame = tk.Frame(card, bg='white')
        header_frame.pack(fill="x")
        
        icon_label = tk.Label(header_frame, text=icon, 
                              font=('Arial', 24),
                              bg='white')
        icon_label.pack(side="left")
        
        # Valor
        value_label = tk.Label(card, text=str(value), 
                               font=('Arial', 20, 'bold'),
                               bg='white',
                               fg=color)
        value_label.pack(anchor="w", pady=(10, 0))
        
        # Título
        title_label = tk.Label(card, text=title, 
                               font=('Arial', 12),
                               bg='white',
                               fg='#64748b')
        title_label.pack(anchor="w")
        
        return card
        
    def create_recent_activities(self, parent):
        # Frame para atividades recentes
        activities_frame = tk.LabelFrame(parent, text="Atividades Recentes", 
                                         bg='white', font=('Arial', 12, 'bold'))
        activities_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Lista de atividades
        activities_list = ttk.Treeview(activities_frame, 
                                      columns=("data", "atividade", "usuario"),
                                      show="headings",
                                      height=8)
        
        activities_list.heading("data", text="Data")
        activities_list.heading("atividade", text="Atividade")
        activities_list.heading("usuario", text="Usuário")
        
        activities_list.column("data", width=100)
        activities_list.column("atividade", width=300)
        activities_list.column("usuario", width=150)
        
        activities_list.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Carregar atividades
        self.load_recent_activities(activities_list)
        
    def create_pending_items(self, parent):
        # Frame para itens pendentes
        pending_frame = tk.LabelFrame(parent, text="Itens Pendentes", 
                                      bg='white', font=('Arial', 12, 'bold'))
        pending_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Relatórios sem cotação
        relatorios_frame = tk.Frame(pending_frame, bg='white')
        relatorios_frame.pack(fill="x", pady=(10, 10), padx=10)
        
        rel_label = tk.Label(relatorios_frame, text="⚠️ Relatórios sem Cotação", 
                             font=('Arial', 12, 'bold'),
                             bg='white',
                             fg='#f59e0b')
        rel_label.pack(anchor="w")
        
        rel_count = self.get_pending_reports_count()
        rel_count_label = tk.Label(relatorios_frame, text=f"{rel_count} relatórios", 
                                   font=('Arial', 10),
                                   bg='white',
                                   fg='#64748b')
        rel_count_label.pack(anchor="w")
        
        # Cotações em aberto
        cotacoes_frame = tk.Frame(pending_frame, bg='white')
        cotacoes_frame.pack(fill="x", pady=(0, 10), padx=10)
        
        cot_label = tk.Label(cotacoes_frame, text="📋 Cotações em Aberto", 
                             font=('Arial', 12, 'bold'),
                             bg='white',
                             fg='#3b82f6')
        cot_label.pack(anchor="w")
        
        cot_count = self.get_open_quotes_count()
        cot_count_label = tk.Label(cotacoes_frame, text=f"{cot_count} cotações", 
                                   font=('Arial', 10),
                                   bg='white',
                                   fg='#64748b')
        cot_count_label.pack(anchor="w")
        
    def get_statistics(self):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            # Total de clientes
            c.execute("SELECT COUNT(*) FROM clientes")
            clientes = c.fetchone()[0]
            
            # Total de cotações
            c.execute("SELECT COUNT(*) FROM cotacoes")
            cotacoes = c.fetchone()[0]
            
            # Total de relatórios
            c.execute("SELECT COUNT(*) FROM relatorios_tecnicos")
            relatorios = c.fetchone()[0]
            
            # Valor total das cotações
            c.execute("SELECT COALESCE(SUM(valor_total), 0) FROM cotacoes")
            valor_total = c.fetchone()[0]
            
            return {
                'clientes': clientes,
                'cotacoes': cotacoes,
                'relatorios': relatorios,
                'valor_total': valor_total
            }
        except sqlite3.Error:
            return {
                'clientes': 0,
                'cotacoes': 0,
                'relatorios': 0,
                'valor_total': 0
            }
        finally:
            conn.close()
            
    def load_recent_activities(self, tree):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            # Buscar atividades recentes (cotações e relatórios)
            c.execute("""
                SELECT data_criacao, 'Cotação criada: ' || numero_proposta, 
                       (SELECT nome_completo FROM usuarios WHERE id = responsavel_id)
                FROM cotacoes 
                ORDER BY data_criacao DESC 
                LIMIT 5
            """)
            
            for row in c.fetchall():
                tree.insert("", "end", values=row)
                
        except sqlite3.Error:
            pass
        finally:
            conn.close()
            
    def get_pending_reports_count(self):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            c.execute("SELECT COUNT(*) FROM relatorios_tecnicos WHERE cotacao_id IS NULL")
            return c.fetchone()[0]
        except sqlite3.Error:
            return 0
        finally:
            conn.close()
            
    def get_open_quotes_count(self):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            c.execute("SELECT COUNT(*) FROM cotacoes WHERE status = 'Em Aberto'")
            return c.fetchone()[0]
        except sqlite3.Error:
            return 0
        finally:
            conn.close()
            
    def on_show(self):
        # Atualizar dados quando mostrar o dashboard
        if hasattr(self, 'frame') and self.frame:
            # Limpar e recriar
            for widget in self.frame.winfo_children():
                widget.destroy()
            self.setup_ui()