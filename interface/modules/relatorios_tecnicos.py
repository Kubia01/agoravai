import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import sqlite3
import json
from datetime import datetime
from .base_module import BaseModule
from database import DB_NAME
from utils.formatters import format_date
from collections import Counter

class RelatoriosTecnicosModule(BaseModule):
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
        
        # Inicializar variáveis
        self.current_relatorio_id = None
        self.tecnicos_eventos = {}
        self.anexos_aba = {1: [], 2: [], 3: [], 4: []}
        
        # Carregar dados iniciais
        self.refresh_all_data()
        
        self.ensure_responsavel_id_column()
        
    def ensure_responsavel_id_column(self):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("PRAGMA table_info(relatorios_tecnicos)")
        columns = [row[1] for row in c.fetchall()]
        if 'responsavel_id' not in columns:
            try:
                c.execute("ALTER TABLE relatorios_tecnicos ADD COLUMN responsavel_id INTEGER")
                conn.commit()
            except Exception as e:
                print(f"Erro ao adicionar coluna responsavel_id em relatorios_tecnicos: {e}")
        conn.close()
        
    def create_header(self, parent):
        header_frame = tk.Frame(parent, bg='#f8fafc')
        header_frame.pack(fill="x", pady=(0, 20))
        
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
        # Frame principal dividido em duas colunas: conteúdo e indicadores
        main_content_frame = tk.Frame(parent, bg='white')
        main_content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Coluna esquerda (conteúdo principal - 60%)
        left_frame = tk.Frame(main_content_frame, bg='white')
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Coluna direita (indicadores - 40%)
        right_frame = tk.Frame(main_content_frame, bg='#f8fafc', width=320)
        right_frame.pack(side="right", fill="y", padx=(10, 0))
        right_frame.pack_propagate(False)  # Manter largura fixa
        
        # Criar indicadores baseados no nível de acesso
        if self.role == 'Admin':
            self.create_admin_indicadores(right_frame)
        else:
            self.create_user_indicadores(right_frame)
        
        # Conteúdo principal
        self.create_cliente_section(left_frame)
        self.create_servico_section(left_frame)
        self.create_tecnicos_section(left_frame)
        self.create_equipamento_section(left_frame)
        self.create_vinculacao_section(left_frame)
        self.create_relatorio_buttons(left_frame)
        
    def create_admin_indicadores(self, parent):
        """Indicadores para administradores - dados gerais"""
        # Total de relatórios
        total_frame = tk.LabelFrame(parent, text="Total de Relatórios", bg='#f8fafc', font=('Arial', 12, 'bold'))
        total_frame.pack(fill="x", padx=10, pady=5)
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM relatorios_tecnicos")
        total = c.fetchone()[0]
        conn.close()
        
        tk.Label(total_frame, text=f"{total}", font=('Arial', 24, 'bold'), 
                bg='#f8fafc', fg='#1e40af').pack(pady=10)
        
        # Relatórios por mês
        mes_frame = tk.LabelFrame(parent, text="Relatórios por Mês", bg='#f8fafc', font=('Arial', 12, 'bold'))
        mes_frame.pack(fill="x", padx=10, pady=5)
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""
            SELECT strftime('%m/%Y', data_criacao) as mes, COUNT(*) 
            FROM relatorios_tecnicos 
            GROUP BY strftime('%m/%Y', data_criacao) 
            ORDER BY data_criacao DESC 
            LIMIT 6
        """)
        meses = c.fetchall()
        conn.close()
        
        for mes, qtd in meses:
            tk.Label(mes_frame, text=f"{mes}: {qtd}", font=('Arial', 10), 
                    bg='#f8fafc').pack(anchor="w", padx=10, pady=2)
        
        # Top técnicos
        tecnicos_frame = tk.LabelFrame(parent, text="Top Técnicos", bg='#f8fafc', font=('Arial', 12, 'bold'))
        tecnicos_frame.pack(fill="x", padx=10, pady=5)
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""
            SELECT u.nome_completo, COUNT(*) as total
            FROM relatorios_tecnicos r
            JOIN usuarios u ON r.responsavel_id = u.id
            GROUP BY r.responsavel_id
            ORDER BY total DESC
            LIMIT 5
        """)
        tecnicos = c.fetchall()
        conn.close()
        
        for nome, total in tecnicos:
            tk.Label(tecnicos_frame, text=f"{nome}: {total}", font=('Arial', 10), 
                    bg='#f8fafc').pack(anchor="w", padx=10, pady=2)
        
        # Relatórios por cliente
        clientes_frame = tk.LabelFrame(parent, text="Top Clientes", bg='#f8fafc', font=('Arial', 12, 'bold'))
        clientes_frame.pack(fill="x", padx=10, pady=5)
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""
            SELECT c.nome, COUNT(*) as total
            FROM relatorios_tecnicos r
            JOIN clientes c ON r.cliente_id = c.id
            GROUP BY r.cliente_id
            ORDER BY total DESC
            LIMIT 5
        """)
        clientes = c.fetchall()
        conn.close()
        
        for nome, total in clientes:
            tk.Label(clientes_frame, text=f"{nome}: {total}", font=('Arial', 10), 
                    bg='#f8fafc').pack(anchor="w", padx=10, pady=2)
    
    def create_user_indicadores(self, parent):
        """Indicadores para usuários comuns - dados individuais"""
        # Meus relatórios
        meus_frame = tk.LabelFrame(parent, text="Meus Relatórios", bg='#f8fafc', font=('Arial', 12, 'bold'))
        meus_frame.pack(fill="x", padx=10, pady=5)
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM relatorios_tecnicos WHERE responsavel_id = ?", (self.user_id,))
        total = c.fetchone()[0]
        conn.close()
        
        tk.Label(meus_frame, text=f"{total}", font=('Arial', 24, 'bold'), 
                bg='#f8fafc', fg='#059669').pack(pady=10)
        
        # Meus relatórios por mês
        mes_frame = tk.LabelFrame(parent, text="Meus Relatórios por Mês", bg='#f8fafc', font=('Arial', 12, 'bold'))
        mes_frame.pack(fill="x", padx=10, pady=5)
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""
            SELECT strftime('%m/%Y', data_criacao) as mes, COUNT(*) 
            FROM relatorios_tecnicos 
            WHERE responsavel_id = ?
            GROUP BY strftime('%m/%Y', data_criacao) 
            ORDER BY data_criacao DESC 
            LIMIT 6
        """, (self.user_id,))
        meses = c.fetchall()
        conn.close()
        
        for mes, qtd in meses:
            tk.Label(mes_frame, text=f"{mes}: {qtd}", font=('Arial', 10), 
                    bg='#f8fafc').pack(anchor="w", padx=10, pady=2)
        
        # Meus clientes mais frequentes
        clientes_frame = tk.LabelFrame(parent, text="Meus Clientes Mais Frequentes", bg='#f8fafc', font=('Arial', 12, 'bold'))
        clientes_frame.pack(fill="x", padx=10, pady=5)
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""
            SELECT c.nome, COUNT(*) as total
            FROM relatorios_tecnicos r
            JOIN clientes c ON r.cliente_id = c.id
            WHERE r.responsavel_id = ?
            GROUP BY r.cliente_id
            ORDER BY total DESC
            LIMIT 5
        """, (self.user_id,))
        clientes = c.fetchall()
        conn.close()
        
        for nome, total in clientes:
            tk.Label(clientes_frame, text=f"{nome}: {total}", font=('Arial', 10), 
                    bg='#f8fafc').pack(anchor="w", padx=10, pady=2)
    
    def create_cliente_section(self, parent):
        section_frame = self.create_section_frame(parent, "Identificação do Cliente")
        section_frame.pack(fill="x", pady=(0, 15))
        
        # Grid de campos
        fields_frame = tk.Frame(section_frame, bg='white')
        fields_frame.pack(fill="x")
        
        # Variáveis
        self.cliente_var = tk.StringVar()
        
        # Cliente com busca reativa
        tk.Label(fields_frame, text="Cliente *:", 
                 font=('Arial', 10, 'bold'), bg='white').grid(row=0, column=0, sticky="w", pady=5)
        
        cliente_frame = tk.Frame(fields_frame, bg='white')
        cliente_frame.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        self.cliente_combo = ttk.Combobox(cliente_frame, textvariable=self.cliente_var, width=40)
        self.cliente_combo.pack(side="left", fill="x", expand=True)
        
        # Botão para buscar/atualizar clientes
        refresh_clientes_btn = self.create_button(cliente_frame, "🔄", self.refresh_clientes, bg='#10b981')
        refresh_clientes_btn.pack(side="right", padx=(5, 0))
        
        # Configurar colunas
        fields_frame.grid_columnconfigure(1, weight=1)
        
    def create_servico_section(self, parent):
        section_frame = self.create_section_frame(parent, "Dados do Serviço")
        section_frame.pack(fill="x", pady=(0, 15))
        
        # Grid de campos
        fields_frame = tk.Frame(section_frame, bg='white')
        fields_frame.pack(fill="x")
        
        # Variáveis
        self.numero_relatorio_var = tk.StringVar()
        self.data_criacao_var = tk.StringVar(value=datetime.now().strftime('%d/%m/%Y'))
        self.formulario_servico_var = tk.StringVar()
        self.tipo_servico_var = tk.StringVar()
        self.data_recebimento_var = tk.StringVar()
        
        row = 0
        
        # Número do Relatório
        tk.Label(fields_frame, text="Número do Relatório:", 
                 font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.numero_relatorio_var, 
                 font=('Arial', 10), width=30).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Data de Criação
        tk.Label(fields_frame, text="Data de Criação:", 
                 font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=2, sticky="w", pady=5, padx=(20, 0))
        tk.Entry(fields_frame, textvariable=self.data_criacao_var, 
                 font=('Arial', 10), width=15).grid(row=row, column=3, sticky="w", padx=(10, 0), pady=5)
        row += 1
        
        # Formulário de Serviço
        tk.Label(fields_frame, text="Formulário de Serviço:", 
                 font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.formulario_servico_var, 
                 font=('Arial', 10), width=30).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Tipo de Serviço
        tk.Label(fields_frame, text="Tipo de Serviço:", 
                 font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tipo_servico_combo = ttk.Combobox(fields_frame, textvariable=self.tipo_servico_var, 
                                         values=["Manutenção", "Instalação", "Reparo", "Inspeção", "Outro"], width=27)
        tipo_servico_combo.grid(row=row, column=1, sticky="w", padx=(10, 0), pady=5)
        row += 1
        
        # Data de Recebimento
        tk.Label(fields_frame, text="Data de Recebimento:", 
                 font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.data_recebimento_var, 
                 font=('Arial', 10), width=15).grid(row=row, column=1, sticky="w", padx=(10, 0), pady=5)
        
        # Configurar colunas
        fields_frame.grid_columnconfigure(1, weight=1)
        
    def create_tecnicos_section(self, parent):
        section_frame = self.create_section_frame(parent, "Técnicos Responsáveis")
        section_frame.pack(fill="x", pady=(0, 15))
        
        # Grid de campos
        fields_frame = tk.Frame(section_frame, bg='white')
        fields_frame.pack(fill="x")
        
        # Variáveis
        self.responsavel_var = tk.StringVar()
        
        # Responsável
        tk.Label(fields_frame, text="Responsável *:", 
                 font=('Arial', 10, 'bold'), bg='white').grid(row=0, column=0, sticky="w", pady=5)
        
        responsavel_frame = tk.Frame(fields_frame, bg='white')
        responsavel_frame.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        self.responsavel_combo = ttk.Combobox(responsavel_frame, textvariable=self.responsavel_var, width=40)
        self.responsavel_combo.pack(side="left", fill="x", expand=True)
        
        # Botão para buscar/atualizar técnicos
        refresh_tecnicos_btn = self.create_button(responsavel_frame, "🔄", self.refresh_tecnicos, bg='#10b981')
        refresh_tecnicos_btn.pack(side="right", padx=(5, 0))
        
        # Configurar colunas
        fields_frame.grid_columnconfigure(1, weight=1)
        
    def create_equipamento_section(self, parent):
        section_frame = self.create_section_frame(parent, "Dados do Equipamento")
        section_frame.pack(fill="x", pady=(0, 15))
        
        # Grid de campos
        fields_frame = tk.Frame(section_frame, bg='white')
        fields_frame.pack(fill="x")
        
        # Variáveis
        self.condicao_encontrada_var = tk.StringVar()
        self.placa_identificacao_var = tk.StringVar()
        self.acoplamento_var = tk.StringVar()
        self.aspectos_rotores_var = tk.StringVar()
        self.valvulas_acopladas_var = tk.StringVar()
        self.data_recebimento_equip_var = tk.StringVar()
        
        row = 0
        
        # Condição Encontrada
        tk.Label(fields_frame, text="Condição Encontrada:", 
                 font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.condicao_encontrada_var, 
                 font=('Arial', 10), width=30).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Placa de Identificação
        tk.Label(fields_frame, text="Placa de Identificação:", 
                 font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.placa_identificacao_var, 
                 font=('Arial', 10), width=30).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Acoplamento
        tk.Label(fields_frame, text="Acoplamento:", 
                 font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.acoplamento_var, 
                 font=('Arial', 10), width=30).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Aspectos dos Rotores
        tk.Label(fields_frame, text="Aspectos dos Rotores:", 
                 font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.aspectos_rotores_var, 
                 font=('Arial', 10), width=30).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Válvulas Acopladas
        tk.Label(fields_frame, text="Válvulas Acopladas:", 
                 font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.valvulas_acopladas_var, 
                 font=('Arial', 10), width=30).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Data de Recebimento do Equipamento
        tk.Label(fields_frame, text="Data Recebimento Equip.:", 
                 font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.data_recebimento_equip_var, 
                 font=('Arial', 10), width=15).grid(row=row, column=1, sticky="w", padx=(10, 0), pady=5)
        
        # Configurar colunas
        fields_frame.grid_columnconfigure(1, weight=1)
        
    def create_vinculacao_section(self, parent):
        section_frame = self.create_section_frame(parent, "Vinculação com Cotação")
        section_frame.pack(fill="x", pady=(0, 15))
        
        # Grid de campos
        fields_frame = tk.Frame(section_frame, bg='white')
        fields_frame.pack(fill="x")
        
        # Variáveis
        self.cotacao_var = tk.StringVar()
        
        # Cotação
        tk.Label(fields_frame, text="Cotação (opcional):", 
                 font=('Arial', 10, 'bold'), bg='white').grid(row=0, column=0, sticky="w", pady=5)
        
        cotacao_frame = tk.Frame(fields_frame, bg='white')
        cotacao_frame.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        self.cotacao_combo = ttk.Combobox(cotacao_frame, textvariable=self.cotacao_var, width=40)
        self.cotacao_combo.pack(side="left", fill="x", expand=True)
        
        # Botão para buscar/atualizar cotações
        refresh_cotacoes_btn = self.create_button(cotacao_frame, "🔄", self.refresh_cotacoes, bg='#10b981')
        refresh_cotacoes_btn.pack(side="right", padx=(5, 0))
        
        # Configurar colunas
        fields_frame.grid_columnconfigure(1, weight=1)
        
    def create_relatorio_buttons(self, parent):
        buttons_frame = tk.Frame(parent, bg='white')
        buttons_frame.pack(fill="x", pady=20)
        
        # Botões
        salvar_btn = self.create_button(buttons_frame, "💾 Salvar Relatório", self.salvar_relatorio, bg='#10b981')
        salvar_btn.pack(side="left", padx=(0, 10))
        
        limpar_btn = self.create_button(buttons_frame, "🗑️ Limpar", self.limpar_formulario, bg='#6b7280')
        limpar_btn.pack(side="left", padx=(0, 10))
        
        gerar_pdf_btn = self.create_button(buttons_frame, "📄 Gerar PDF", self.gerar_pdf, bg='#3b82f6')
        gerar_pdf_btn.pack(side="left")
        
    def create_lista_relatorios_tab(self):
        # Frame da aba
        lista_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(lista_frame, text="Lista de Relatórios")
        
        # Frame principal dividido em duas colunas
        main_frame = tk.Frame(lista_frame, bg='white')
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Coluna esquerda (lista - 60%)
        left_frame = tk.Frame(main_frame, bg='white')
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Coluna direita (indicadores - 40%)
        right_frame = tk.Frame(main_frame, bg='#f8fafc', width=320)
        right_frame.pack(side="right", fill="y", padx=(10, 0))
        right_frame.pack_propagate(False)
        
        # Criar indicadores baseados no nível de acesso
        if self.role == 'Admin':
            self.create_admin_indicadores(right_frame)
        else:
            self.create_user_indicadores(right_frame)
        
        # Lista de relatórios
        self.create_relatorios_list(left_frame)
        
    def create_relatorios_list(self, parent):
        # Header da lista
        header_frame = tk.Frame(parent, bg='white')
        header_frame.pack(fill="x", pady=(0, 10))
        
        title_label = tk.Label(header_frame, text="Relatórios Técnicos", 
                               font=('Arial', 14, 'bold'), bg='white')
        title_label.pack(side="left")
        
        refresh_btn = self.create_button(header_frame, "🔄 Atualizar", self.refresh_relatorios, bg='#10b981')
        refresh_btn.pack(side="right")
        
        # Treeview
        tree_frame = tk.Frame(parent, bg='white')
        tree_frame.pack(fill="both", expand=True)
        
        columns = ("ID", "Número", "Cliente", "Data Criação", "Responsável")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        # Configurar colunas
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind de seleção
        self.tree.bind('<<TreeviewSelect>>', self.on_relatorio_select)
        
        # Carregar dados
        self.refresh_relatorios()
        
    def create_section_frame(self, parent, title):
        return tk.LabelFrame(parent, text=title, bg='white', font=('Arial', 12, 'bold'))
        
    def create_button(self, parent, text, command, bg='#3b82f6'):
        return tk.Button(parent, text=text, command=command, 
                        font=('Arial', 10), bg=bg, fg='white', 
                        relief="flat", padx=15, pady=5, cursor="hand2")
        
    def refresh_all_data(self):
        self.carregar_clientes()
        self.carregar_tecnicos()
        self.carregar_cotacoes()
        
    def carregar_clientes(self):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT id, nome FROM clientes ORDER BY nome")
        clientes = c.fetchall()
        conn.close()
        
        self.clientes_dict = {f"{nome} (ID: {id})": id for id, nome in clientes}
        self.cliente_combo['values'] = list(self.clientes_dict.keys())
        
    def carregar_tecnicos(self):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT id, nome_completo FROM usuarios WHERE role = 'Técnico' ORDER BY nome_completo")
        tecnicos = c.fetchall()
        conn.close()
        
        self.tecnicos_dict = {f"{nome} (ID: {id})": id for id, nome in tecnicos}
        self.responsavel_combo['values'] = list(self.tecnicos_dict.keys())
        
    def carregar_cotacoes(self):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT id, numero FROM cotacoes ORDER BY numero DESC")
        cotacoes = c.fetchall()
        conn.close()
        
        self.cotacoes_dict = {f"{numero} (ID: {id})": id for id, numero in cotacoes}
        self.cotacao_combo['values'] = list(self.cotacoes_dict.keys())
        
    def refresh_clientes(self):
        self.carregar_clientes()
        messagebox.showinfo("Sucesso", "Lista de clientes atualizada!")
        
    def refresh_tecnicos(self):
        self.carregar_tecnicos()
        messagebox.showinfo("Sucesso", "Lista de técnicos atualizada!")
        
    def refresh_cotacoes(self):
        self.carregar_cotacoes()
        messagebox.showinfo("Sucesso", "Lista de cotações atualizada!")
        
    def refresh_relatorios(self):
        # Limpar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        if self.role == 'Admin':
            c.execute("""
                SELECT r.id, r.numero_relatorio, c.nome, r.data_criacao, u.nome_completo
                FROM relatorios_tecnicos r
                LEFT JOIN clientes c ON r.cliente_id = c.id
                LEFT JOIN usuarios u ON r.responsavel_id = u.id
                ORDER BY r.data_criacao DESC
            """)
        else:
            c.execute("""
                SELECT r.id, r.numero_relatorio, c.nome, r.data_criacao, u.nome_completo
                FROM relatorios_tecnicos r
                LEFT JOIN clientes c ON r.cliente_id = c.id
                LEFT JOIN usuarios u ON r.responsavel_id = u.id
                WHERE r.responsavel_id = ?
                ORDER BY r.data_criacao DESC
            """, (self.user_id,))
            
        relatorios = c.fetchall()
        conn.close()
        
        for relatorio in relatorios:
            self.tree.insert('', 'end', values=relatorio)
            
    def salvar_relatorio(self):
        try:
            # Validar campos obrigatórios
            if not self.numero_relatorio_var.get().strip():
                messagebox.showerror("Erro", "Número do relatório é obrigatório")
                return
            
            # Obter IDs
            cliente_text = self.cliente_var.get()
            responsavel_text = self.responsavel_var.get()
            cotacao_text = self.cotacao_var.get()
            
            cliente_id = self.clientes_dict.get(cliente_text)
            responsavel_id = self.tecnicos_dict.get(responsavel_text)
            cotacao_id = self.cotacoes_dict.get(cotacao_text) if cotacao_text else None
            
            if not cliente_id:
                messagebox.showerror("Erro", "Cliente é obrigatório")
                return
            
            if not responsavel_id:
                messagebox.showerror("Erro", "Responsável é obrigatório")
                return
            
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            
            if self.current_relatorio_id:
                # Atualizar
                c.execute("""
                    UPDATE relatorios_tecnicos 
                    SET numero_relatorio = ?, cliente_id = ?, responsavel_id = ?, data_criacao = ?,
                        formulario_servico = ?, tipo_servico = ?, data_recebimento = ?,
                        condicao_encontrada = ?, placa_identificacao = ?, acoplamento = ?,
                        aspectos_rotores = ?, valvulas_acopladas = ?, data_recebimento_equip = ?,
                        cotacao_id = ?
                    WHERE id = ?
                """, (
                    self.numero_relatorio_var.get(), cliente_id, responsavel_id, 
                    self.data_criacao_var.get(), self.formulario_servico_var.get(),
                    self.tipo_servico_var.get(), self.data_recebimento_var.get(),
                    self.condicao_encontrada_var.get(), self.placa_identificacao_var.get(),
                    self.acoplamento_var.get(), self.aspectos_rotores_var.get(),
                    self.valvulas_acopladas_var.get(), self.data_recebimento_equip_var.get(),
                    cotacao_id, self.current_relatorio_id
                ))
            else:
                # Inserir novo
                c.execute("""
                    INSERT INTO relatorios_tecnicos (
                        numero_relatorio, cliente_id, responsavel_id, data_criacao,
                        formulario_servico, tipo_servico, data_recebimento,
                        condicao_encontrada, placa_identificacao, acoplamento,
                        aspectos_rotores, valvulas_acopladas, data_recebimento_equip,
                        cotacao_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.numero_relatorio_var.get(), cliente_id, responsavel_id, 
                    self.data_criacao_var.get(), self.formulario_servico_var.get(),
                    self.tipo_servico_var.get(), self.data_recebimento_var.get(),
                    self.condicao_encontrada_var.get(), self.placa_identificacao_var.get(),
                    self.acoplamento_var.get(), self.aspectos_rotores_var.get(),
                    self.valvulas_acopladas_var.get(), self.data_recebimento_equip_var.get(),
                    cotacao_id
                ))
                
                self.current_relatorio_id = c.lastrowid
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Sucesso", "Relatório salvo com sucesso!")
            self.refresh_relatorios()
            self.limpar_formulario()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar relatório: {str(e)}")

    def limpar_formulario(self):
        self.numero_relatorio_var.set('')
        self.cliente_var.set('')
        self.responsavel_var.set('')
        self.data_criacao_var.set(datetime.now().strftime('%d/%m/%Y'))
        self.formulario_servico_var.set('')
        self.tipo_servico_var.set('')
        self.data_recebimento_var.set('')
        self.condicao_encontrada_var.set('')
        self.placa_identificacao_var.set('')
        self.acoplamento_var.set('')
        self.aspectos_rotores_var.set('')
        self.valvulas_acopladas_var.set('')
        self.data_recebimento_equip_var.set('')
        self.cotacao_var.set('')
        self.current_relatorio_id = None

    def on_relatorio_select(self, event):
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            relatorio_id = item['values'][0]
            self.carregar_relatorio(relatorio_id)

    def carregar_relatorio(self, relatorio_id):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""
            SELECT r.*, c.nome as cliente_nome, u.nome_completo as responsavel_nome
            FROM relatorios_tecnicos r
            LEFT JOIN clientes c ON r.cliente_id = c.id
            LEFT JOIN usuarios u ON r.responsavel_id = u.id
            WHERE r.id = ?
        """, (relatorio_id,))
        relatorio = c.fetchone()
        conn.close()
        
        if relatorio:
            self.current_relatorio_id = relatorio_id
            self.numero_relatorio_var.set(relatorio[1] or '')
            
            # Encontrar cliente no combo
            for key, value in self.clientes_dict.items():
                if value == relatorio[2]:
                    self.cliente_var.set(key)
                    break
            
            # Encontrar responsável no combo
            for key, value in self.tecnicos_dict.items():
                if value == relatorio[3]:
                    self.responsavel_var.set(key)
                    break
            
            self.data_criacao_var.set(relatorio[4] or '')
            self.formulario_servico_var.set(relatorio[5] or '')
            self.tipo_servico_var.set(relatorio[6] or '')
            self.data_recebimento_var.set(relatorio[7] or '')
            self.condicao_encontrada_var.set(relatorio[10] or '')
            self.placa_identificacao_var.set(relatorio[11] or '')
            self.acoplamento_var.set(relatorio[12] or '')
            self.aspectos_rotores_var.set(relatorio[13] or '')
            self.valvulas_acopladas_var.set(relatorio[14] or '')
            self.data_recebimento_equip_var.set(relatorio[15] or '')
            
            # Encontrar cotação no combo
            if relatorio[29]:  # cotacao_id
                for key, value in self.cotacoes_dict.items():
                    if value == relatorio[29]:
                        self.cotacao_var.set(key)
                        break

    def gerar_pdf(self):
        if not self.current_relatorio_id:
            messagebox.showerror("Erro", "Selecione um relatório para gerar o PDF")
            return
        
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="Salvar PDF"
            )
            
            if filename:
                # Aqui você implementaria a geração do PDF
                messagebox.showinfo("Sucesso", f"PDF gerado com sucesso: {filename}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar PDF: {str(e)}")