import tkinter as tk
from tkinter import ttk
from .base_module import BaseModule

class RelatoriosGeraisModule(BaseModule):
    def setup_ui(self):
        container = tk.Frame(self.frame, bg='#f8fafc')
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Header
        header_frame = tk.Frame(container, bg='#f8fafc')
        header_frame.pack(fill="x", pady=(0, 20))
        title_label = tk.Label(header_frame, text="Relatórios Gerais", font=('Arial', 18, 'bold'), bg='#f8fafc', fg='#1e293b')
        title_label.pack(side="left")

        # Filtros e resultados
        main_frame = tk.Frame(container, bg='white')
        main_frame.pack(fill="both", expand=True)

        # Coluna esquerda - Filtros
        left_frame = tk.Frame(main_frame, bg='white')
        left_frame.pack(side="left", fill="y", padx=(0, 20), pady=10)
        self.create_filtros_section(left_frame)
        self.create_tipos_relatorio_section(left_frame)

        # Coluna direita - Resultados
        right_frame = tk.Frame(main_frame, bg='white')
        right_frame.pack(side="left", fill="both", expand=True, pady=10)
        self.resultados_tree = None
        self.create_resultados_section(right_frame)

    def create_filtros_section(self, parent):
        section_frame = tk.LabelFrame(parent, text="Filtros de Data", bg='white', font=('Arial', 12, 'bold'))
        section_frame.pack(fill="x", pady=(0, 15))
        # Adicione campos de filtro conforme necessário

    def create_tipos_relatorio_section(self, parent):
        section_frame = tk.LabelFrame(parent, text="Tipos de Relatório", bg='white', font=('Arial', 12, 'bold'))
        section_frame.pack(fill="x", pady=(0, 15))
        # Adicione opções de tipo de relatório

    def create_resultados_section(self, parent):
        import sqlite3
        if self.resultados_tree:
            self.resultados_tree.destroy()
        section_frame = tk.LabelFrame(parent, text="Resultados", bg='white', font=('Arial', 12, 'bold'))
        section_frame.pack(fill="both", expand=True)
        # Exemplo: relatório de cotações por status
        tree = ttk.Treeview(section_frame, columns=("col1", "col2"), show="headings")
        tree.heading("col1", text="Status")
        tree.heading("col2", text="Quantidade")
        tree.pack(fill="both", expand=True)
        conn = sqlite3.connect('crm_compressores.db')
        c = conn.cursor()
        c.execute("SELECT status, COUNT(*) FROM cotacoes GROUP BY status")
        for row in c.fetchall():
            tree.insert("", "end", values=row)
        conn.close()
        self.resultados_tree = tree