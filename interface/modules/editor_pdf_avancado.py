import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
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

class EditorPDFAvancadoModule(BaseModule):
    def __init__(self, parent, user_id, role, main_window):
        try:
            self.user_info = {'role': role, 'user_id': user_id}
            
            # Configurar conexão com banco
            from database import DB_NAME
            self.db_name = DB_NAME
            
            # Inicializar propriedades
            self.cotacao_data = {}
            self.filial_data = {}
            self.usuario_data = {}
            self.texto_config = {}
            self.canvas_scale = 0.8
            self.page_width = 595  # A4 width in points
            self.page_height = 842  # A4 height in points
            
            super().__init__(parent, user_id, role, main_window)
            
            # Carregar dados
            self.load_sample_cotacao()
            self.load_filial_data()
            self.load_texto_config()
            
            # Gerar preview inicial
            self.generate_pdf_preview()
            
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
        
        tk.Label(title_frame, text="🚀 Editor PDF Completo - Preview Fiel + Correções", 
                font=('Arial', 16, 'bold'), bg='#f8fafc', fg='#1e293b').pack(side="left")
        
        # Frame principal horizontal
        main_frame = tk.Frame(self.frame, bg='#f8fafc')
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Coluna esquerda - Controles (35%)
        self.controls_frame = tk.Frame(main_frame, bg='white', relief='ridge', bd=1)
        self.controls_frame.pack(side="left", fill="both", expand=False, padx=(0, 10))
        self.controls_frame.config(width=350)
        
        # Coluna direita - Preview (65%)
        self.preview_frame = tk.Frame(main_frame, bg='white', relief='ridge', bd=1)
        self.preview_frame.pack(side="right", fill="both", expand=True)
        
        # Configurar painéis
        self.setup_controls_panel()
        self.setup_preview_panel()
    
    def setup_controls_panel(self):
        """Configurar painel de controles completo"""
        # Título do painel
        title_frame = tk.Frame(self.controls_frame, bg='#1e40af')
        title_frame.pack(fill="x")
        
        tk.Label(title_frame, text="✏️ Edição Completa", 
                font=('Arial', 12, 'bold'), bg='#1e40af', fg='white').pack(pady=10)
        
        # Notebook para organizar todas as funcionalidades
        self.controls_notebook = ttk.Notebook(self.controls_frame)
        self.controls_notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Aba 1: Dados da Cotação
        self.setup_cotacao_tab()
        
        # Aba 2: Dados do Cliente
        self.setup_cliente_tab()
        
        # Aba 3: Itens da Proposta
        self.setup_itens_tab()
        
        # Aba 4: Textos e Correções
        self.setup_textos_tab()
        
        # Aba 5: Templates e Estilo
        self.setup_templates_tab()
        
        # Botões de ação
        self.setup_action_buttons()
    
    def setup_cotacao_tab(self):
        """Configurar aba de dados da cotação"""
        cotacao_frame = tk.Frame(self.controls_notebook, bg='white')
        self.controls_notebook.add(cotacao_frame, text="📋 Cotação")
        
        # Scroll
        canvas = tk.Canvas(cotacao_frame, bg='white')
        scrollbar = ttk.Scrollbar(cotacao_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Campos da cotação
        self.cotacao_fields = {}
        
        fields = [
            ("Número da Proposta", "numero_proposta", "2025-001"),
            ("Data", "data_criacao", datetime.now().strftime("%d/%m/%Y")),
            ("Responsável", "responsavel_nome", "João Silva"),
            ("Telefone Responsável", "responsavel_telefone", "(11) 9999-9999"),
            ("Email Responsável", "responsavel_email", "joao@empresa.com"),
            ("Modelo Compressor", "modelo_compressor", "GA 30 VSD"),
            ("Nº Série Compressor", "numero_serie_compressor", "ABC123456"),
            ("Descrição da Atividade", "descricao_atividade", "Manutenção preventiva e troca de peças"),
            ("Tipo de Frete", "tipo_frete", "FOB"),
            ("Condição de Pagamento", "condicao_pagamento", "30 dias"),
            ("Prazo de Entrega", "prazo_entrega", "15 dias úteis"),
            ("Moeda", "moeda", "BRL (Real Brasileiro)"),
        ]
        
        for label, key, default in fields:
            self.create_field(scrollable_frame, label, key, default, self.cotacao_fields)
        
        # Observações (campo de texto)
        tk.Label(scrollable_frame, text="Observações", font=('Arial', 9, 'bold'), 
                bg='white', fg='#374151').pack(anchor="w", padx=10, pady=(10,2))
        
        self.observacoes_text = tk.Text(scrollable_frame, height=4, font=('Arial', 9), 
                                       bg='#f9fafb', relief='solid', bd=1)
        self.observacoes_text.pack(fill="x", padx=10, pady=(0,5))
        self.observacoes_text.insert("1.0", "Proposta válida por 30 dias. Garantia de 6 meses para peças novas.")
        self.observacoes_text.bind('<KeyRelease>', self.on_data_change)
    
    def setup_cliente_tab(self):
        """Configurar aba de dados do cliente"""
        cliente_frame = tk.Frame(self.controls_notebook, bg='white')
        self.controls_notebook.add(cliente_frame, text="👤 Cliente")
        
        # Scroll
        canvas = tk.Canvas(cliente_frame, bg='white')
        scrollbar = ttk.Scrollbar(cliente_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Campos do cliente
        self.cliente_fields = {}
        
        fields = [
            ("Nome/Razão Social", "cliente_nome", "EMPRESA EXEMPLO LTDA"),
            ("Nome Fantasia", "cliente_nome_fantasia", "Empresa Exemplo"),
            ("CNPJ", "cliente_cnpj", "12.345.678/0001-99"),
            ("Contato", "contato_nome", "Sr. João da Silva"),
            ("Email", "cliente_email", "contato@empresaexemplo.com.br"),
            ("Telefone", "cliente_telefone", "(11) 3456-7890"),
            ("Endereço", "cliente_endereco", "Rua Principal, 123"),
            ("Cidade", "cliente_cidade", "São Paulo"),
            ("Estado", "cliente_estado", "SP"),
            ("CEP", "cliente_cep", "01234-567"),
            ("Site", "cliente_site", "www.empresaexemplo.com.br"),
        ]
        
        for label, key, default in fields:
            self.create_field(scrollable_frame, label, key, default, self.cliente_fields)
    
    def setup_itens_tab(self):
        """Configurar aba de itens da proposta"""
        itens_frame = tk.Frame(self.controls_notebook, bg='white')
        self.controls_notebook.add(itens_frame, text="📦 Itens")
        
        # Título
        tk.Label(itens_frame, text="Itens da Proposta", font=('Arial', 12, 'bold'), 
                bg='white', fg='#1f2937').pack(pady=10)
        
        # Frame para lista de itens
        self.itens_frame = tk.Frame(itens_frame, bg='white')
        self.itens_frame.pack(fill="both", expand=True, padx=10)
        
        # Cabeçalho da tabela
        header_frame = tk.Frame(self.itens_frame, bg='#e5e7eb')
        header_frame.pack(fill="x", pady=(0,5))
        
        tk.Label(header_frame, text="Descrição", font=('Arial', 9, 'bold'), 
                bg='#e5e7eb', width=25).pack(side="left", padx=2)
        tk.Label(header_frame, text="Qtd", font=('Arial', 9, 'bold'), 
                bg='#e5e7eb', width=5).pack(side="left", padx=2)
        tk.Label(header_frame, text="Valor Unit.", font=('Arial', 9, 'bold'), 
                bg='#e5e7eb', width=10).pack(side="left", padx=2)
        tk.Label(header_frame, text="Total", font=('Arial', 9, 'bold'), 
                bg='#e5e7eb', width=10).pack(side="left", padx=2)
        
        # Scroll frame para itens
        canvas = tk.Canvas(self.itens_frame, bg='white', height=200)
        scrollbar = ttk.Scrollbar(self.itens_frame, orient="vertical", command=canvas.yview)
        self.itens_scrollable_frame = tk.Frame(canvas, bg='white')
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.itens_scrollable_frame, anchor="nw")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Lista de itens editáveis
        self.itens_list = []
        self.create_sample_items()
        
        # Botões de gerenciamento de itens
        btn_frame = tk.Frame(itens_frame, bg='white')
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Button(btn_frame, text="+ Adicionar Item", command=self.add_item,
                 font=('Arial', 9), bg='#10b981', fg='white').pack(side="left", padx=5)
        tk.Button(btn_frame, text="- Remover Último", command=self.remove_last_item,
                 font=('Arial', 9), bg='#ef4444', fg='white').pack(side="left", padx=5)
        
        # Valor total
        self.total_frame = tk.Frame(itens_frame, bg='#fef3c7')
        self.total_frame.pack(fill="x", padx=10, pady=5)
        
        self.total_label = tk.Label(self.total_frame, text="VALOR TOTAL: R$ 0,00", 
                                   font=('Arial', 12, 'bold'), bg='#fef3c7', fg='#92400e')
        self.total_label.pack(pady=10)
    
    def setup_textos_tab(self):
        """Configurar aba de textos e correções"""
        textos_frame = tk.Frame(self.controls_notebook, bg='white')
        self.controls_notebook.add(textos_frame, text="📝 Textos")
        
        # Scroll
        canvas = tk.Canvas(textos_frame, bg='white')
        scrollbar = ttk.Scrollbar(textos_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Textos editáveis
        self.texto_fields = {}
        
        # Texto de apresentação (Página 2)
        self.create_text_section(scrollable_frame, "Texto de Apresentação (Página 2)", 
                                "apresentacao", """Prezados Senhores,

Agradecemos a sua solicitação e apresentamos nossas condições comerciais para fornecimento de peças para o compressor.

A World Comp coloca-se a disposição para analisar, corrigir, prestar esclarecimentos para adequação das especificações e necessidades dos clientes, para tanto basta informar o número da proposta e revisão.


Atenciosamente,""")
        
        # Sobre a empresa (Página 3)
        self.create_text_section(scrollable_frame, "Sobre a Empresa (Página 3)", 
                                "sobre_empresa", """Há mais de uma década no mercado de manutenção de compressores de ar de parafuso, de diversas marcas, atendemos clientes em todo território brasileiro.""")
        
        # Seções da empresa
        secoes = [
            ("FORNECIMENTO, SERVIÇO E LOCAÇÃO", """A World Comp oferece os serviços de Manutenção Preventiva e Corretiva em Compressores e Unidades Compressoras, Venda de peças, Locação de compressores, Recuperação de Unidades Compressoras, Recuperação de Trocadores de Calor e Contrato de Manutenção em compressores de marcas como: Atlas Copco, Ingersoll Rand, Chicago Pneumatic entre outros."""),
            ("CONTE CONOSCO PARA UMA PARCERIA", """Adaptamos nossa oferta para suas necessidades, objetivos e planejamento. Trabalhamos para que seu processo seja eficiente."""),
            ("MELHORIA CONTÍNUA", """Continuamente investindo em comprometimento, competência e eficiência de nossos serviços, produtos e estrutura para garantirmos a máxima eficiência de sua produtividade."""),
            ("QUALIDADE DE SERVIÇOS", """Com uma equipe de técnicos altamente qualificados e constantemente treinados para atendimentos em todos os modelos de compressores de ar, a World Comp oferece garantia de excelente atendimento e produtividade superior com rapidez e eficácia.""")
        ]
        
        for titulo, texto in secoes:
            self.create_text_section(scrollable_frame, titulo, titulo.lower().replace(" ", "_"), texto)
    
    def setup_templates_tab(self):
        """Configurar aba de templates e estilo"""
        templates_frame = tk.Frame(self.controls_notebook, bg='white')
        self.controls_notebook.add(templates_frame, text="🎨 Templates")
        
        # Scroll
        canvas = tk.Canvas(templates_frame, bg='white')
        scrollbar = ttk.Scrollbar(templates_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Dados da filial/empresa
        tk.Label(scrollable_frame, text="Dados da Empresa", font=('Arial', 12, 'bold'), 
                bg='white', fg='#1f2937').pack(anchor="w", padx=10, pady=(10,5))
        
        self.filial_fields = {}
        
        filial_fields = [
            ("Nome da Empresa", "nome", "WORLD COMP COMPRESSORES LTDA"),
            ("Endereço", "endereco", "Rua Fernando Pessoa, nº 11 – Batistini"),
            ("CEP", "cep", "09844-390"),
            ("CNPJ", "cnpj", "10.644.944/0001-55"),
            ("Inscrição Estadual", "inscricao_estadual", "635.970.206.110"),
            ("Telefones", "telefones", "(11) 4543-6893 / 4543-6857"),
            ("Email", "email", "contato@worldcompressores.com.br"),
        ]
        
        for label, key, default in filial_fields:
            self.create_field(scrollable_frame, label, key, default, self.filial_fields)
        
        # Upload de templates de capa
        tk.Label(scrollable_frame, text="Template de Capa", font=('Arial', 12, 'bold'), 
                bg='white', fg='#1f2937').pack(anchor="w", padx=10, pady=(20,5))
        
        capa_frame = tk.Frame(scrollable_frame, bg='white')
        capa_frame.pack(fill="x", padx=10, pady=5)
        
        self.capa_path = tk.StringVar(value="assets/templates/capa_default.jpg")
        capa_entry = tk.Entry(capa_frame, textvariable=self.capa_path, 
                             font=('Arial', 9), width=30)
        capa_entry.pack(side="left", fill="x", expand=True)
        capa_entry.bind('<KeyRelease>', self.on_data_change)
        
        def choose_capa():
            filename = filedialog.askopenfilename(
                title="Selecionar Template de Capa",
                filetypes=[("Imagens", "*.png *.jpg *.jpeg")]
            )
            if filename:
                self.capa_path.set(filename)
                self.on_data_change()
        
        tk.Button(capa_frame, text="📁 Buscar", command=choose_capa,
                 font=('Arial', 8)).pack(side="right", padx=(5,0))
    
    def create_field(self, parent, label, key, default, fields_dict):
        """Criar campo de entrada padrão"""
        tk.Label(parent, text=label, font=('Arial', 9, 'bold'), 
                bg='white', fg='#374151').pack(anchor="w", padx=10, pady=(10,2))
        
        entry = tk.Entry(parent, font=('Arial', 9), bg='#f9fafb', 
                        relief='solid', bd=1, width=45)
        entry.pack(fill="x", padx=10, pady=(0,5))
        entry.insert(0, default)
        entry.bind('<KeyRelease>', self.on_data_change)
        
        fields_dict[key] = entry
    
    def create_text_section(self, parent, label, key, default):
        """Criar seção de texto editável"""
        tk.Label(parent, text=label, font=('Arial', 10, 'bold'), 
                bg='white', fg='#1f2937').pack(anchor="w", padx=10, pady=(15,5))
        
        text_widget = tk.Text(parent, height=6, font=('Arial', 9), 
                             bg='#f9fafb', relief='solid', bd=1, wrap=tk.WORD)
        text_widget.pack(fill="x", padx=10, pady=(0,5))
        text_widget.insert("1.0", default)
        text_widget.bind('<KeyRelease>', self.on_data_change)
        
        self.texto_fields[key] = text_widget
    
    def create_sample_items(self):
        """Criar itens de exemplo"""
        sample_items = [
            {"nome": "Filtro de Ar", "quantidade": 2, "valor_unitario": 150.00},
            {"nome": "Óleo Lubrificante 20L", "quantidade": 1, "valor_unitario": 380.00},
            {"nome": "Kit de Vedação", "quantidade": 1, "valor_unitario": 750.00},
        ]
        
        for item_data in sample_items:
            self.add_item(item_data)
    
    def add_item(self, item_data=None):
        """Adicionar novo item"""
        if item_data is None:
            item_data = {"nome": "Novo Item", "quantidade": 1, "valor_unitario": 0.00}
        
        item_frame = tk.Frame(self.itens_scrollable_frame, bg='white')
        item_frame.pack(fill="x", pady=1)
        
        # Descrição
        nome_entry = tk.Entry(item_frame, font=('Arial', 8), width=25)
        nome_entry.pack(side="left", padx=2)
        nome_entry.insert(0, item_data["nome"])
        nome_entry.bind('<KeyRelease>', self.on_item_change)
        
        # Quantidade
        qtd_entry = tk.Entry(item_frame, font=('Arial', 8), width=5)
        qtd_entry.pack(side="left", padx=2)
        qtd_entry.insert(0, str(item_data["quantidade"]))
        qtd_entry.bind('<KeyRelease>', self.on_item_change)
        
        # Valor unitário
        valor_entry = tk.Entry(item_frame, font=('Arial', 8), width=10)
        valor_entry.pack(side="left", padx=2)
        valor_entry.insert(0, f"{item_data['valor_unitario']:.2f}")
        valor_entry.bind('<KeyRelease>', self.on_item_change)
        
        # Total (calculado)
        total_label = tk.Label(item_frame, text="R$ 0,00", font=('Arial', 8), 
                              bg='white', width=10)
        total_label.pack(side="left", padx=2)
        
        self.itens_list.append({
            'frame': item_frame,
            'nome': nome_entry,
            'quantidade': qtd_entry,
            'valor_unitario': valor_entry,
            'total_label': total_label
        })
        
        self.calculate_totals()
    
    def remove_last_item(self):
        """Remover último item"""
        if self.itens_list:
            item = self.itens_list.pop()
            item['frame'].destroy()
            self.calculate_totals()
    
    def on_item_change(self, event=None):
        """Callback quando item é alterado"""
        self.calculate_totals()
        self.on_data_change(event)
    
    def calculate_totals(self):
        """Calcular totais dos itens"""
        total_geral = 0.0
        
        for item in self.itens_list:
            try:
                qtd = float(item['quantidade'].get() or 0)
                valor_unit = float(item['valor_unitario'].get() or 0)
                total_item = qtd * valor_unit
                
                item['total_label'].config(text=f"R$ {total_item:.2f}")
                total_geral += total_item
                
            except ValueError:
                item['total_label'].config(text="R$ 0,00")
        
        self.total_label.config(text=f"VALOR TOTAL: R$ {total_geral:.2f}")
    
    def setup_action_buttons(self):
        """Configurar botões de ação"""
        btn_frame = tk.Frame(self.controls_frame, bg='white')
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        # Botão de atualizar preview
        update_btn = tk.Button(btn_frame, text="🔄 Atualizar Preview", 
                              command=self.generate_pdf_preview,
                              font=('Arial', 10, 'bold'), bg='#10b981', fg='white',
                              relief='flat', cursor='hand2')
        update_btn.pack(fill="x", pady=2)
        
        # Botão de salvar configurações
        save_btn = tk.Button(btn_frame, text="💾 Salvar Configurações", 
                            command=self.save_configurations,
                            font=('Arial', 10, 'bold'), bg='#3b82f6', fg='white',
                            relief='flat', cursor='hand2')
        save_btn.pack(fill="x", pady=2)
        
        # Botão de gerar PDF final
        pdf_btn = tk.Button(btn_frame, text="📄 Gerar PDF Final", 
                           command=self.generate_final_pdf,
                           font=('Arial', 10, 'bold'), bg='#ef4444', fg='white',
                           relief='flat', cursor='hand2')
        pdf_btn.pack(fill="x", pady=2)
        
        # Botão de reset
        reset_btn = tk.Button(btn_frame, text="🔄 Resetar Tudo", 
                             command=self.reset_all_data,
                             font=('Arial', 9), bg='#6b7280', fg='white',
                             relief='flat', cursor='hand2')
        reset_btn.pack(fill="x", pady=2)
    
    def setup_preview_panel(self):
        """Configurar painel de preview"""
        # Título do painel
        title_frame = tk.Frame(self.preview_frame, bg='#dc2626')
        title_frame.pack(fill="x")
        
        tk.Label(title_frame, text="👁️ Preview Fiel do PDF", 
                font=('Arial', 12, 'bold'), bg='#dc2626', fg='white').pack(side="left", pady=10, padx=10)
        
        # Status
        self.preview_status = tk.Label(title_frame, text="Carregando...", 
                                      font=('Arial', 9), bg='#dc2626', fg='#fecaca')
        self.preview_status.pack(side="right", pady=10, padx=10)
        
        # Canvas para o preview
        canvas_frame = tk.Frame(self.preview_frame, bg='#f3f4f6')
        canvas_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical")
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient="horizontal")
        
        self.preview_canvas = tk.Canvas(canvas_frame, bg='white',
                                       yscrollcommand=v_scrollbar.set,
                                       xscrollcommand=h_scrollbar.set)
        
        v_scrollbar.config(command=self.preview_canvas.yview)
        h_scrollbar.config(command=self.preview_canvas.xview)
        
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        self.preview_canvas.pack(side="left", fill="both", expand=True)
        
        # Navegação de páginas
        nav_frame = tk.Frame(self.preview_frame, bg='white')
        nav_frame.pack(fill="x", padx=5, pady=5)
        
        tk.Button(nav_frame, text="◀ Anterior", command=lambda: self.change_page(-1),
                 font=('Arial', 9)).pack(side="left", padx=5)
        
        self.page_label = tk.Label(nav_frame, text="Página 1 de 4", 
                                  font=('Arial', 9, 'bold'), bg='white')
        self.page_label.pack(side="left", expand=True)
        
        tk.Button(nav_frame, text="Próxima ▶", command=lambda: self.change_page(1),
                 font=('Arial', 9)).pack(side="right", padx=5)
        
        # Página atual
        self.current_page = 1
        self.total_pages = 4
    
    def load_sample_cotacao(self):
        """Carregar dados de cotação de exemplo"""
        self.cotacao_data = {
            'numero_proposta': '2025-001',
            'data_criacao': datetime.now().strftime("%d/%m/%Y"),
            'responsavel_nome': 'João Silva',
            'responsavel_telefone': '(11) 9999-9999',
            'responsavel_email': 'joao@empresa.com',
            'modelo_compressor': 'GA 30 VSD',
            'numero_serie_compressor': 'ABC123456',
            'descricao_atividade': 'Manutenção preventiva e troca de peças',
            'tipo_frete': 'FOB',
            'condicao_pagamento': '30 dias',
            'prazo_entrega': '15 dias úteis',
            'moeda': 'BRL (Real Brasileiro)',
            'observacoes': 'Proposta válida por 30 dias. Garantia de 6 meses para peças novas.',
            'valor_total': 1280.00
        }
    
    def load_filial_data(self):
        """Carregar dados da filial"""
        self.filial_data = {
            'nome': 'WORLD COMP COMPRESSORES LTDA',
            'endereco': 'Rua Fernando Pessoa, nº 11 – Batistini – São Bernardo do Campo – SP',
            'cep': '09844-390',
            'cnpj': '10.644.944/0001-55',
            'inscricao_estadual': '635.970.206.110',
            'telefones': '(11) 4543-6893 / 4543-6857',
            'email': 'contato@worldcompressores.com.br'
        }
    
    def load_texto_config(self):
        """Carregar configurações de texto"""
        self.texto_config = {
            'apresentacao': """Prezados Senhores,

Agradecemos a sua solicitação e apresentamos nossas condições comerciais para fornecimento de peças para o compressor.

A World Comp coloca-se a disposição para analisar, corrigir, prestar esclarecimentos para adequação das especificações e necessidades dos clientes, para tanto basta informar o número da proposta e revisão.


Atenciosamente,""",
            'sobre_empresa': """Há mais de uma década no mercado de manutenção de compressores de ar de parafuso, de diversas marcas, atendemos clientes em todo território brasileiro."""
        }
    
    def on_data_change(self, event=None):
        """Callback quando dados são alterados"""
        # Debounce para evitar muitas atualizações
        if hasattr(self, '_update_timer'):
            self.frame.after_cancel(self._update_timer)
        
        self._update_timer = self.frame.after(1500, self.update_all_data)
    
    def update_all_data(self):
        """Atualizar todos os dados com valores dos campos"""
        try:
            # Atualizar dados da cotação
            if hasattr(self, 'cotacao_fields'):
                for key, entry in self.cotacao_fields.items():
                    self.cotacao_data[key] = entry.get()
            
            # Atualizar observações
            if hasattr(self, 'observacoes_text'):
                self.cotacao_data['observacoes'] = self.observacoes_text.get("1.0", tk.END).strip()
            
            # Atualizar dados do cliente
            if hasattr(self, 'cliente_fields'):
                for key, entry in self.cliente_fields.items():
                    self.cotacao_data[key] = entry.get()
            
            # Atualizar dados da filial
            if hasattr(self, 'filial_fields'):
                for key, entry in self.filial_fields.items():
                    self.filial_data[key] = entry.get()
            
            # Atualizar textos
            if hasattr(self, 'texto_fields'):
                for key, text_widget in self.texto_fields.items():
                    self.texto_config[key] = text_widget.get("1.0", tk.END).strip()
            
            # Recalcular totais
            self.calculate_totals()
            
            print("Dados atualizados automaticamente")
            
        except Exception as e:
            print(f"Erro ao atualizar dados: {e}")
    
    def generate_pdf_preview(self):
        """Gerar preview fiel do PDF"""
        try:
            self.preview_status.config(text="🔄 Gerando preview fiel...")
            self.frame.update()
            
            # Atualizar dados primeiro
            self.update_all_data()
            
            # Criar preview baseado na página atual
            if self.current_page == 1:
                self.create_capa_preview()
            elif self.current_page == 2:
                self.create_apresentacao_preview()
            elif self.current_page == 3:
                self.create_sobre_empresa_preview()
            elif self.current_page == 4:
                self.create_proposta_preview()
            
            self.preview_status.config(text="✅ Preview fiel atualizado")
            
        except Exception as e:
            self.preview_status.config(text="❌ Erro no preview")
            print(f"Erro ao gerar preview: {e}")
    
    def create_capa_preview(self):
        """Criar preview da capa (Página 1)"""
        # Limpar canvas
        self.preview_canvas.delete("all")
        
        # Dimensões da página
        page_width = int(self.page_width * self.canvas_scale)
        page_height = int(self.page_height * self.canvas_scale)
        
        # Criar retângulo da página
        self.preview_canvas.create_rectangle(10, 10, page_width + 10, page_height + 10,
                                           fill='white', outline='#d1d5db', width=2)
        
        # Simular template de capa JPEG
        # Fundo azul gradiente
        self.preview_canvas.create_rectangle(10, 10, page_width + 10, page_height + 10,
                                           fill='#1e40af', outline='')
        
        # Título principal
        self.preview_canvas.create_text(page_width//2 + 10, 150, 
                                      text="PROPOSTA COMERCIAL", 
                                      font=('Arial', 24, 'bold'),
                                      fill='white', anchor='center')
        
        # Nome da empresa
        self.preview_canvas.create_text(page_width//2 + 10, 200, 
                                      text=self.filial_data.get('nome', ''), 
                                      font=('Arial', 18, 'bold'),
                                      fill='white', anchor='center')
        
        # Número da proposta
        self.preview_canvas.create_text(page_width//2 + 10, 400, 
                                      text=f"PROPOSTA Nº {self.cotacao_data.get('numero_proposta', '')}", 
                                      font=('Arial', 16, 'bold'),
                                      fill='white', anchor='center')
        
        # Data
        self.preview_canvas.create_text(page_width//2 + 10, 430, 
                                      text=f"Data: {self.cotacao_data.get('data_criacao', '')}", 
                                      font=('Arial', 14),
                                      fill='white', anchor='center')
        
        # Cliente
        self.preview_canvas.create_text(page_width//2 + 10, 500, 
                                      text=f"A/C: {self.cotacao_data.get('contato_nome', '')}", 
                                      font=('Arial', 14),
                                      fill='white', anchor='center')
        
        self.preview_canvas.create_text(page_width//2 + 10, 530, 
                                      text=self.cotacao_data.get('cliente_nome', ''), 
                                      font=('Arial', 14),
                                      fill='white', anchor='center')
        
        # Configurar scroll region
        self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all"))
        self.page_label.config(text=f"Página {self.current_page} de {self.total_pages}")
    
    def create_apresentacao_preview(self):
        """Criar preview da apresentação (Página 2)"""
        # Limpar canvas
        self.preview_canvas.delete("all")
        
        # Dimensões da página
        page_width = int(self.page_width * self.canvas_scale)
        page_height = int(self.page_height * self.canvas_scale)
        
        # Criar retângulo da página com borda
        self.preview_canvas.create_rectangle(10, 10, page_width + 10, page_height + 10,
                                           fill='white', outline='#000000', width=1)
        
        # Header (exatamente como no PDF)
        y_pos = 20
        
        # Dados da proposta no header
        self.preview_canvas.create_text(20, y_pos, text=self.filial_data.get('nome', ''), 
                                      font=('Arial', 11, 'bold'), fill='black', anchor='nw')
        y_pos += 15
        
        self.preview_canvas.create_text(20, y_pos, text="PROPOSTA COMERCIAL:", 
                                      font=('Arial', 11, 'bold'), fill='black', anchor='nw')
        y_pos += 15
        
        self.preview_canvas.create_text(20, y_pos, text=f"NÚMERO: {self.cotacao_data.get('numero_proposta', '')}", 
                                      font=('Arial', 11, 'bold'), fill='black', anchor='nw')
        y_pos += 15
        
        self.preview_canvas.create_text(20, y_pos, text=f"DATA: {self.cotacao_data.get('data_criacao', '')}", 
                                      font=('Arial', 11, 'bold'), fill='black', anchor='nw')
        y_pos += 20
        
        # Linha de separação
        self.preview_canvas.create_line(20, y_pos, page_width - 10, y_pos, fill='black', width=1)
        y_pos += 30
        
        # Dados do cliente
        self.preview_canvas.create_text(20, y_pos, text=f"A/C: {self.cotacao_data.get('contato_nome', '')}", 
                                      font=('Arial', 11), fill='black', anchor='nw')
        y_pos += 15
        
        self.preview_canvas.create_text(20, y_pos, text=self.cotacao_data.get('cliente_nome', ''), 
                                      font=('Arial', 11), fill='black', anchor='nw')
        y_pos += 30
        
        # Email do responsável
        self.preview_canvas.create_text(20, y_pos, text=f"E-mail: {self.cotacao_data.get('responsavel_email', '')}", 
                                      font=('Arial', 11), fill='black', anchor='nw')
        y_pos += 15
        
        # Responsável
        self.preview_canvas.create_text(page_width//2 + 20, y_pos, text=f"Responsável: {self.cotacao_data.get('responsavel_nome', '')}", 
                                      font=('Arial', 11), fill='black', anchor='nw')
        y_pos += 30
        
        # Texto de apresentação
        texto_apresentacao = self.texto_config.get('apresentacao', '')
        lines = texto_apresentacao.split('\n')
        
        for line in lines:
            if line.strip():
                self.preview_canvas.create_text(20, y_pos, text=line.strip(), 
                                              font=('Arial', 11), fill='black', anchor='nw')
            y_pos += 15
        
        # Assinatura na parte inferior
        y_pos = page_height - 100
        
        self.preview_canvas.create_text(20, y_pos, text=self.cotacao_data.get('responsavel_nome', '').upper(), 
                                      font=('Arial', 11, 'bold'), fill='black', anchor='nw')
        y_pos += 15
        
        self.preview_canvas.create_text(20, y_pos, text="Vendas", 
                                      font=('Arial', 11), fill='black', anchor='nw')
        y_pos += 15
        
        self.preview_canvas.create_text(20, y_pos, text=f"Fone: {self.filial_data.get('telefones', '')}", 
                                      font=('Arial', 11), fill='black', anchor='nw')
        y_pos += 15
        
        self.preview_canvas.create_text(20, y_pos, text=self.filial_data.get('nome', ''), 
                                      font=('Arial', 11), fill='black', anchor='nw')
        
        # Rodapé (azul bebê)
        self.create_footer_preview(page_height)
        
        # Configurar scroll region
        self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all"))
        self.page_label.config(text=f"Página {self.current_page} de {self.total_pages}")
    
    def create_sobre_empresa_preview(self):
        """Criar preview sobre a empresa (Página 3)"""
        # Limpar canvas
        self.preview_canvas.delete("all")
        
        # Dimensões da página
        page_width = int(self.page_width * self.canvas_scale)
        page_height = int(self.page_height * self.canvas_scale)
        
        # Criar retângulo da página com borda
        self.preview_canvas.create_rectangle(10, 10, page_width + 10, page_height + 10,
                                           fill='white', outline='#000000', width=1)
        
        # Header
        self.create_header_preview()
        
        # Conteúdo
        y_pos = 80
        
        # Título principal
        self.preview_canvas.create_text(20, y_pos, text="SOBRE A WORLD COMP", 
                                      font=('Arial', 12, 'bold'), fill='black', anchor='nw')
        y_pos += 25
        
        # Texto introdutório
        sobre_texto = self.texto_config.get('sobre_empresa', '')
        self.create_wrapped_text(20, y_pos, sobre_texto, page_width - 40, 11)
        y_pos += 40
        
        # Seções
        secoes = [
            ("FORNECIMENTO, SERVIÇO E LOCAÇÃO", "fornecimento_servico_e_locacao"),
            ("CONTE CONOSCO PARA UMA PARCERIA", "conte_conosco_para_uma_parceria"),
            ("MELHORIA CONTÍNUA", "melhoria_continua"),
            ("QUALIDADE DE SERVIÇOS", "qualidade_de_servicos")
        ]
        
        for titulo, key in secoes:
            # Título da seção (azul bebê)
            self.preview_canvas.create_text(20, y_pos, text=titulo, 
                                          font=('Arial', 12, 'bold'), fill='#89CFF0', anchor='nw')
            y_pos += 20
            
            # Texto da seção
            texto = self.texto_config.get(key, '')
            if texto:
                y_pos = self.create_wrapped_text(20, y_pos, texto, page_width - 40, 11)
            y_pos += 15
        
        # Texto final
        texto_final = "Nossa missão é ser sua melhor parceria com sinônimo de qualidade, garantia e o melhor custo benefício."
        self.create_wrapped_text(20, y_pos, texto_final, page_width - 40, 11)
        
        # Rodapé
        self.create_footer_preview(page_height)
        
        # Configurar scroll region
        self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all"))
        self.page_label.config(text=f"Página {self.current_page} de {self.total_pages}")
    
    def create_proposta_preview(self):
        """Criar preview da proposta (Página 4)"""
        # Limpar canvas
        self.preview_canvas.delete("all")
        
        # Dimensões da página
        page_width = int(self.page_width * self.canvas_scale)
        page_height = int(self.page_height * self.canvas_scale)
        
        # Criar retângulo da página com borda
        self.preview_canvas.create_rectangle(10, 10, page_width + 10, page_height + 10,
                                           fill='white', outline='#000000', width=1)
        
        # Header
        self.create_header_preview()
        
        # Conteúdo
        y_pos = 80
        
        # Título da proposta
        self.preview_canvas.create_text(20, y_pos, text=f"PROPOSTA Nº {self.cotacao_data.get('numero_proposta', '')}", 
                                      font=('Arial', 12, 'bold'), fill='black', anchor='nw')
        y_pos += 20
        
        self.preview_canvas.create_text(20, y_pos, text=f"Data: {self.cotacao_data.get('data_criacao', '')}", 
                                      font=('Arial', 11), fill='black', anchor='nw')
        y_pos += 15
        
        self.preview_canvas.create_text(20, y_pos, text=f"Responsável: {self.cotacao_data.get('responsavel_nome', '')}", 
                                      font=('Arial', 11), fill='black', anchor='nw')
        y_pos += 15
        
        self.preview_canvas.create_text(20, y_pos, text=f"Telefone Responsável: {self.cotacao_data.get('responsavel_telefone', '')}", 
                                      font=('Arial', 11), fill='black', anchor='nw')
        y_pos += 25
        
        # Dados do cliente
        self.preview_canvas.create_text(20, y_pos, text="DADOS DO CLIENTE:", 
                                      font=('Arial', 11, 'bold'), fill='black', anchor='nw')
        y_pos += 15
        
        cliente_nome = self.cotacao_data.get('cliente_nome_fantasia', '') or self.cotacao_data.get('cliente_nome', '')
        self.preview_canvas.create_text(20, y_pos, text=f"Empresa: {cliente_nome}", 
                                      font=('Arial', 11), fill='black', anchor='nw')
        y_pos += 15
        
        if self.cotacao_data.get('cliente_cnpj'):
            self.preview_canvas.create_text(20, y_pos, text=f"CNPJ: {self.cotacao_data.get('cliente_cnpj', '')}", 
                                          font=('Arial', 11), fill='black', anchor='nw')
            y_pos += 15
        
        if self.cotacao_data.get('contato_nome'):
            self.preview_canvas.create_text(20, y_pos, text=f"Contato: {self.cotacao_data.get('contato_nome', '')}", 
                                          font=('Arial', 11), fill='black', anchor='nw')
            y_pos += 20
        
        # Dados do compressor
        if self.cotacao_data.get('modelo_compressor') or self.cotacao_data.get('numero_serie_compressor'):
            self.preview_canvas.create_text(20, y_pos, text="DADOS DO COMPRESSOR:", 
                                          font=('Arial', 11, 'bold'), fill='black', anchor='nw')
            y_pos += 15
            
            if self.cotacao_data.get('modelo_compressor'):
                self.preview_canvas.create_text(20, y_pos, text=f"Modelo: {self.cotacao_data.get('modelo_compressor', '')}", 
                                              font=('Arial', 11), fill='black', anchor='nw')
                y_pos += 15
            
            if self.cotacao_data.get('numero_serie_compressor'):
                self.preview_canvas.create_text(20, y_pos, text=f"Nº de Série: {self.cotacao_data.get('numero_serie_compressor', '')}", 
                                              font=('Arial', 11), fill='black', anchor='nw')
                y_pos += 20
        
        # Descrição do serviço
        self.preview_canvas.create_text(20, y_pos, text="DESCRIÇÃO DO SERVIÇO:", 
                                      font=('Arial', 11, 'bold'), fill='black', anchor='nw')
        y_pos += 15
        
        descricao = self.cotacao_data.get('descricao_atividade', 'Fornecimento de peças e serviços para compressor')
        y_pos = self.create_wrapped_text(20, y_pos, descricao, page_width - 40, 11)
        y_pos += 20
        
        # Tabela de itens
        self.preview_canvas.create_text(page_width//2 + 10, y_pos, text="ITENS DA PROPOSTA", 
                                      font=('Arial', 12, 'bold'), fill='black', anchor='center')
        y_pos += 25
        
        # Criar tabela
        y_pos = self.create_items_table(y_pos, page_width)
        
        # Condições comerciais
        y_pos += 25
        self.preview_canvas.create_text(20, y_pos, text="CONDIÇÕES COMERCIAIS:", 
                                      font=('Arial', 11, 'bold'), fill='black', anchor='nw')
        y_pos += 15
        
        self.preview_canvas.create_text(20, y_pos, text=f"Tipo de Frete: {self.cotacao_data.get('tipo_frete', 'FOB')}", 
                                      font=('Arial', 11), fill='black', anchor='nw')
        y_pos += 15
        
        self.preview_canvas.create_text(20, y_pos, text=f"Condição de Pagamento: {self.cotacao_data.get('condicao_pagamento', 'A combinar')}", 
                                      font=('Arial', 11), fill='black', anchor='nw')
        y_pos += 15
        
        self.preview_canvas.create_text(20, y_pos, text=f"Prazo de Entrega: {self.cotacao_data.get('prazo_entrega', 'A combinar')}", 
                                      font=('Arial', 11), fill='black', anchor='nw')
        y_pos += 15
        
        self.preview_canvas.create_text(20, y_pos, text=f"Moeda: {self.cotacao_data.get('moeda', 'BRL (Real Brasileiro)')}", 
                                      font=('Arial', 11), fill='black', anchor='nw')
        y_pos += 20
        
        # Observações
        if self.cotacao_data.get('observacoes'):
            self.preview_canvas.create_text(20, y_pos, text="OBSERVAÇÕES:", 
                                          font=('Arial', 11, 'bold'), fill='black', anchor='nw')
            y_pos += 15
            
            self.create_wrapped_text(20, y_pos, self.cotacao_data.get('observacoes', ''), page_width - 40, 11)
        
        # Rodapé
        self.create_footer_preview(page_height)
        
        # Configurar scroll region
        self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all"))
        self.page_label.config(text=f"Página {self.current_page} de {self.total_pages}")
    
    def create_header_preview(self):
        """Criar header padrão"""
        y_pos = 20
        
        # Dados da proposta no header
        self.preview_canvas.create_text(20, y_pos, text=self.filial_data.get('nome', ''), 
                                      font=('Arial', 11, 'bold'), fill='black', anchor='nw')
        y_pos += 15
        
        self.preview_canvas.create_text(20, y_pos, text="PROPOSTA COMERCIAL:", 
                                      font=('Arial', 11, 'bold'), fill='black', anchor='nw')
        y_pos += 15
        
        self.preview_canvas.create_text(20, y_pos, text=f"NÚMERO: {self.cotacao_data.get('numero_proposta', '')}", 
                                      font=('Arial', 11, 'bold'), fill='black', anchor='nw')
        y_pos += 15
        
        self.preview_canvas.create_text(20, y_pos, text=f"DATA: {self.cotacao_data.get('data_criacao', '')}", 
                                      font=('Arial', 11, 'bold'), fill='black', anchor='nw')
        y_pos += 15
        
        # Linha de separação
        page_width = int(self.page_width * self.canvas_scale)
        self.preview_canvas.create_line(20, y_pos, page_width - 10, y_pos, fill='black', width=1)
    
    def create_footer_preview(self, page_height):
        """Criar rodapé padrão"""
        y_pos = page_height - 60
        page_width = int(self.page_width * self.canvas_scale)
        
        # Linha divisória
        self.preview_canvas.create_line(20, y_pos - 10, page_width - 10, y_pos - 10, fill='black', width=1)
        
        # Informações do rodapé (azul bebê #89CFF0)
        endereco_completo = f"{self.filial_data.get('endereco', '')} - CEP: {self.filial_data.get('cep', '')}"
        cnpj_completo = f"CNPJ: {self.filial_data.get('cnpj', '')}"
        contato_completo = f"E-mail: {self.filial_data.get('email', '')} | Fone: {self.filial_data.get('telefones', '')}"
        
        self.preview_canvas.create_text(page_width//2 + 10, y_pos, text=endereco_completo, 
                                      font=('Arial', 10), fill='#89CFF0', anchor='center')
        y_pos += 15
        
        self.preview_canvas.create_text(page_width//2 + 10, y_pos, text=cnpj_completo, 
                                      font=('Arial', 10), fill='#89CFF0', anchor='center')
        y_pos += 15
        
        self.preview_canvas.create_text(page_width//2 + 10, y_pos, text=contato_completo, 
                                      font=('Arial', 10), fill='#89CFF0', anchor='center')
    
    def create_wrapped_text(self, x, y, text, max_width, font_size):
        """Criar texto com quebra de linha"""
        lines = text.split('\n')
        current_y = y
        
        for line in lines:
            if line.strip():
                # Simular quebra de linha (simplificado)
                words = line.split()
                current_line = ""
                
                for word in words:
                    test_line = current_line + word + " "
                    # Simplificado: assumir largura média de caractere
                    if len(test_line) * (font_size * 0.6) < max_width:
                        current_line = test_line
                    else:
                        if current_line:
                            self.preview_canvas.create_text(x, current_y, text=current_line.strip(), 
                                                          font=('Arial', font_size), fill='black', anchor='nw')
                            current_y += font_size + 5
                        current_line = word + " "
                
                if current_line:
                    self.preview_canvas.create_text(x, current_y, text=current_line.strip(), 
                                                  font=('Arial', font_size), fill='black', anchor='nw')
                    current_y += font_size + 5
            else:
                current_y += font_size + 5
        
        return current_y
    
    def create_items_table(self, y_start, page_width):
        """Criar tabela de itens"""
        # Larguras das colunas
        col_widths = [40, 200, 60, 80, 70]  # Item, Descrição, Qtd, Valor Unit., Total
        x_positions = [20]
        for width in col_widths[:-1]:
            x_positions.append(x_positions[-1] + width)
        
        y_pos = y_start
        
        # Cabeçalho da tabela
        header_height = 20
        
        # Fundo do cabeçalho
        self.preview_canvas.create_rectangle(20, y_pos, 20 + sum(col_widths), y_pos + header_height,
                                           fill='#326496', outline='black', width=1)
        
        # Textos do cabeçalho
        headers = ["Item", "Descrição", "Qtd.", "Valor Unitário", "Valor Total"]
        for i, (header, x_pos) in enumerate(zip(headers, x_positions)):
            self.preview_canvas.create_text(x_pos + col_widths[i]//2, y_pos + header_height//2, 
                                          text=header, font=('Arial', 11, 'bold'), 
                                          fill='white', anchor='center')
        
        y_pos += header_height
        
        # Linhas dos itens
        item_counter = 1
        for item in self.itens_list:
            try:
                nome = item['nome'].get()
                qtd = item['quantidade'].get()
                valor_unit = float(item['valor_unitario'].get() or 0)
                total = float(qtd) * valor_unit
                
                # Altura da linha
                row_height = 25
                
                # Fundo da linha
                self.preview_canvas.create_rectangle(20, y_pos, 20 + sum(col_widths), y_pos + row_height,
                                                   fill='white', outline='black', width=1)
                
                # Conteúdo das células
                self.preview_canvas.create_text(x_positions[0] + col_widths[0]//2, y_pos + row_height//2, 
                                              text=str(item_counter), font=('Arial', 11), 
                                              fill='black', anchor='center')
                
                # Descrição (alinhada à esquerda)
                desc_text = nome[:30] + "..." if len(nome) > 30 else nome
                self.preview_canvas.create_text(x_positions[1] + 5, y_pos + row_height//2, 
                                              text=desc_text, font=('Arial', 11), 
                                              fill='black', anchor='w')
                
                self.preview_canvas.create_text(x_positions[2] + col_widths[2]//2, y_pos + row_height//2, 
                                              text=qtd, font=('Arial', 11), 
                                              fill='black', anchor='center')
                
                self.preview_canvas.create_text(x_positions[3] + col_widths[3] - 5, y_pos + row_height//2, 
                                              text=f"R$ {valor_unit:.2f}", font=('Arial', 11), 
                                              fill='black', anchor='e')
                
                self.preview_canvas.create_text(x_positions[4] + col_widths[4] - 5, y_pos + row_height//2, 
                                              text=f"R$ {total:.2f}", font=('Arial', 11), 
                                              fill='black', anchor='e')
                
                y_pos += row_height
                item_counter += 1
                
            except (ValueError, AttributeError):
                continue
        
        # Linha do total
        total_height = 25
        total_geral = sum([float(item['quantidade'].get() or 0) * float(item['valor_unitario'].get() or 0) 
                          for item in self.itens_list])
        
        # Fundo do total
        self.preview_canvas.create_rectangle(20, y_pos, 20 + sum(col_widths), y_pos + total_height,
                                           fill='#c8c8c8', outline='black', width=1)
        
        # Texto do total
        self.preview_canvas.create_text(x_positions[3] + col_widths[3] - 5, y_pos + total_height//2, 
                                      text="VALOR TOTAL DA PROPOSTA:", font=('Arial', 12, 'bold'), 
                                      fill='black', anchor='e')
        
        self.preview_canvas.create_text(x_positions[4] + col_widths[4] - 5, y_pos + total_height//2, 
                                      text=f"R$ {total_geral:.2f}", font=('Arial', 12, 'bold'), 
                                      fill='black', anchor='e')
        
        return y_pos + total_height
    
    def change_page(self, direction):
        """Mudar página do preview"""
        new_page = self.current_page + direction
        
        if 1 <= new_page <= self.total_pages:
            self.current_page = new_page
            self.generate_pdf_preview()
    
    def save_configurations(self):
        """Salvar todas as configurações"""
        try:
            # Criar diretório se não existir
            os.makedirs('data/editor_config', exist_ok=True)
            
            # Dados para salvar
            config_data = {
                'cotacao_data': self.cotacao_data,
                'filial_data': self.filial_data,
                'texto_config': self.texto_config,
                'data_criacao': datetime.now().isoformat()
            }
            
            # Salvar arquivo
            filename = f"data/editor_config/config_usuario_{self.user_id}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)
            
            messagebox.showinfo("Sucesso", "Configurações salvas com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar configurações: {e}")
    
    def generate_final_pdf(self):
        """Gerar PDF final usando o gerador real"""
        try:
            # Atualizar dados
            self.update_all_data()
            
            # Simular criação de cotação no banco para usar o gerador real
            messagebox.showinfo("PDF Final", 
                               f"""PDF seria gerado com os dados atuais:

Proposta: {self.cotacao_data.get('numero_proposta', '')}
Cliente: {self.cotacao_data.get('cliente_nome', '')}
Valor Total: R$ {sum([float(item['quantidade'].get() or 0) * float(item['valor_unitario'].get() or 0) for item in self.itens_list]):.2f}

Para gerar o PDF real, use o módulo de Cotações após salvar os dados.""")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar PDF: {e}")
    
    def reset_all_data(self):
        """Resetar todos os dados"""
        if messagebox.askyesno("Confirmar", "Resetar todos os dados para os valores padrão?"):
            # Recarregar dados
            self.load_sample_cotacao()
            self.load_filial_data()
            self.load_texto_config()
            
            # Atualizar campos
            for key, entry in self.cotacao_fields.items():
                entry.delete(0, tk.END)
                entry.insert(0, self.cotacao_data.get(key, ''))
            
            for key, entry in self.cliente_fields.items():
                entry.delete(0, tk.END)
                entry.insert(0, self.cotacao_data.get(key, ''))
            
            for key, entry in self.filial_fields.items():
                entry.delete(0, tk.END)
                entry.insert(0, self.filial_data.get(key, ''))
            
            for key, text_widget in self.texto_fields.items():
                text_widget.delete("1.0", tk.END)
                text_widget.insert("1.0", self.texto_config.get(key, ''))
            
            # Resetar observações
            self.observacoes_text.delete("1.0", tk.END)
            self.observacoes_text.insert("1.0", self.cotacao_data.get('observacoes', ''))
            
            # Limpar itens e recriar exemplos
            for item in self.itens_list:
                item['frame'].destroy()
            self.itens_list = []
            self.create_sample_items()
            
            # Gerar novo preview
            self.generate_pdf_preview()
            
            messagebox.showinfo("Sucesso", "Todos os dados foram resetados!")
    
    def show_success(self, message):
        """Mostrar mensagem de sucesso"""
        print(f"✅ {message}")
    
    def show_error(self, message):
        """Mostrar mensagem de erro"""
        print(f"❌ {message}")