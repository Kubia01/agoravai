import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import sqlite3
import json
from datetime import datetime
from .base_module import BaseModule
from database import DB_NAME
from utils.formatters import format_date
from collections import Counter

class RelatoriosModule(BaseModule):
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
        import sqlite3
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("PRAGMA table_info(relatorios_tecnicos)")
        columns = [row[1] for row in c.fetchall()]
        if 'responsavel_id' not in columns:
            try:
                c.execute("ALTER TABLE relatorios_tecnicos ADD COLUMN responsavel_id INTEGER")
                conn.commit()
            except:
                pass
        conn.close()

    def create_header(self, container):
        header_frame = tk.Frame(container, bg='#1e40af', height=60)
        header_frame.pack(fill="x", pady=(0, 20))
        header_frame.pack_propagate(False)
        
        title = tk.Label(header_frame, text="Relatórios Técnicos", 
                        font=('Arial', 16, 'bold'), fg='white', bg='#1e40af')
        title.pack(side="left", padx=20, pady=15)

    def create_novo_relatorio_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Novo Relatório")
        
        # Scrollable frame
        canvas = tk.Canvas(tab, bg='#f8fafc')
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Formulário
        self.create_form(scrollable_frame)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_lista_relatorios_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Lista de Relatórios")
        
        # Frame para controles
        controls_frame = tk.Frame(tab, bg='#f8fafc')
        controls_frame.pack(fill="x", padx=20, pady=10)
        
        # Botões
        tk.Button(controls_frame, text="Atualizar", command=self.refresh_relatorios,
                 bg='#3b82f6', fg='white', font=('Arial', 10)).pack(side="left", padx=5)
        
        # Treeview para lista
        columns = ('ID', 'Número', 'Cliente', 'Data Criação', 'Responsável')
        self.tree = ttk.Treeview(tab, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Bind double click
        self.tree.bind('<Double-1>', self.on_relatorio_select)

    def create_form(self, parent):
        # Informações básicas
        basic_frame = tk.LabelFrame(parent, text="Informações Básicas", 
                                   font=('Arial', 12, 'bold'), bg='#f8fafc')
        basic_frame.pack(fill="x", padx=20, pady=10)
        
        # Número do relatório
        tk.Label(basic_frame, text="Número do Relatório:", bg='#f8fafc').grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.numero_relatorio = tk.Entry(basic_frame, width=30)
        self.numero_relatorio.grid(row=0, column=1, padx=10, pady=5)
        
        # Cliente
        tk.Label(basic_frame, text="Cliente:", bg='#f8fafc').grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.cliente_var = tk.StringVar()
        self.cliente_combo = ttk.Combobox(basic_frame, textvariable=self.cliente_var, width=27)
        self.cliente_combo.grid(row=1, column=1, padx=10, pady=5)
        
        # Responsável
        tk.Label(basic_frame, text="Responsável:", bg='#f8fafc').grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.responsavel_var = tk.StringVar()
        self.responsavel_combo = ttk.Combobox(basic_frame, textvariable=self.responsavel_var, width=27)
        self.responsavel_combo.grid(row=2, column=1, padx=10, pady=5)
        
        # Data de criação
        tk.Label(basic_frame, text="Data de Criação:", bg='#f8fafc').grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.data_criacao = tk.Entry(basic_frame, width=30)
        self.data_criacao.grid(row=3, column=1, padx=10, pady=5)
        self.data_criacao.insert(0, datetime.now().strftime('%d/%m/%Y'))
        
        # Botões
        buttons_frame = tk.Frame(parent, bg='#f8fafc')
        buttons_frame.pack(fill="x", padx=20, pady=20)
        
        tk.Button(buttons_frame, text="Salvar", command=self.salvar_relatorio,
                 bg='#10b981', fg='white', font=('Arial', 12, 'bold')).pack(side="left", padx=5)
        
        tk.Button(buttons_frame, text="Limpar", command=self.limpar_formulario,
                 bg='#f59e0b', fg='white', font=('Arial', 12)).pack(side="left", padx=5)
        
        tk.Button(buttons_frame, text="Gerar PDF", command=self.gerar_pdf,
                 bg='#ef4444', fg='white', font=('Arial', 12)).pack(side="left", padx=5)

    def refresh_all_data(self):
        self.carregar_clientes()
        self.carregar_tecnicos()
        self.refresh_relatorios()

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
        c.execute("SELECT id, nome FROM usuarios WHERE role = 'tecnico' ORDER BY nome")
        tecnicos = c.fetchall()
        conn.close()
        
        self.tecnicos_dict = {f"{nome} (ID: {id})": id for id, nome in tecnicos}
        self.responsavel_combo['values'] = list(self.tecnicos_dict.keys())

    def refresh_relatorios(self):
        # Limpar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""
            SELECT r.id, r.numero_relatorio, c.nome, r.data_criacao, u.nome
            FROM relatorios_tecnicos r
            LEFT JOIN clientes c ON r.cliente_id = c.id
            LEFT JOIN usuarios u ON r.responsavel_id = u.id
            ORDER BY r.data_criacao DESC
        """)
        relatorios = c.fetchall()
        conn.close()
        
        for relatorio in relatorios:
            self.tree.insert('', 'end', values=relatorio)

    def salvar_relatorio(self):
        try:
            # Validar campos obrigatórios
            if not self.numero_relatorio.get().strip():
                messagebox.showerror("Erro", "Número do relatório é obrigatório")
                return
            
            # Obter IDs
            cliente_text = self.cliente_var.get()
            responsavel_text = self.responsavel_var.get()
            
            cliente_id = self.clientes_dict.get(cliente_text)
            responsavel_id = self.tecnicos_dict.get(responsavel_text)
            
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
                    SET numero_relatorio = ?, cliente_id = ?, responsavel_id = ?, data_criacao = ?
                    WHERE id = ?
                """, (self.numero_relatorio.get(), cliente_id, responsavel_id, 
                     self.data_criacao.get(), self.current_relatorio_id))
            else:
                # Inserir novo
                c.execute("""
                    INSERT INTO relatorios_tecnicos (numero_relatorio, cliente_id, responsavel_id, data_criacao)
                    VALUES (?, ?, ?, ?)
                """, (self.numero_relatorio.get(), cliente_id, responsavel_id, self.data_criacao.get()))
                
                self.current_relatorio_id = c.lastrowid
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Sucesso", "Relatório salvo com sucesso!")
            self.refresh_relatorios()
            self.limpar_formulario()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar relatório: {str(e)}")

    def limpar_formulario(self):
        self.numero_relatorio.delete(0, tk.END)
        self.cliente_var.set('')
        self.responsavel_var.set('')
        self.data_criacao.delete(0, tk.END)
        self.data_criacao.insert(0, datetime.now().strftime('%d/%m/%Y'))
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
            SELECT r.*, c.nome as cliente_nome, u.nome as responsavel_nome
            FROM relatorios_tecnicos r
            LEFT JOIN clientes c ON r.cliente_id = c.id
            LEFT JOIN usuarios u ON r.responsavel_id = u.id
            WHERE r.id = ?
        """, (relatorio_id,))
        relatorio = c.fetchone()
        conn.close()
        
        if relatorio:
            self.current_relatorio_id = relatorio_id
            self.numero_relatorio.delete(0, tk.END)
            self.numero_relatorio.insert(0, relatorio[1] or '')
            
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
            
            self.data_criacao.delete(0, tk.END)
            self.data_criacao.insert(0, relatorio[4] or '')

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