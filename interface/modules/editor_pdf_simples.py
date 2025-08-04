import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import sqlite3
import os
import tempfile
from datetime import datetime
import subprocess
import json

# Importar módulo base
from .base_module import BaseModule

class EditorPDFSimplesModule(BaseModule):
    def __init__(self, parent, user_id, role, main_window):
        """Editor PDF Simples - Focado apenas na edição de conteúdo sem capa"""
        try:
            self.user_id = user_id
            self.role = role
            self.main_window = main_window
            
            # Configurar conexão com banco
            from database import DB_NAME
            self.db_name = DB_NAME
            
            # Inicializar variáveis básicas
            self.current_cotacao_id = None
            self.cotacao_data = {}
            self.pdf_fields = {}
            self.custom_texts = {}
            
            # Inicializar módulo base
            super().__init__(parent, user_id, role, main_window)
            
            # Carregar dados iniciais
            self.load_sample_cotacao()
            
        except Exception as e:
            print(f"Erro ao inicializar Editor PDF Simples: {e}")
            self.create_error_interface(parent, str(e))
    
    def setup_ui(self):
        """Criar interface simples e clara"""
        # Frame principal
        main_frame = tk.Frame(self.frame, bg='#f8fafc')
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title_label = tk.Label(main_frame, 
                              text="📝 Editor de Cotações PDF", 
                              font=('Arial', 18, 'bold'),
                              bg='#f8fafc', fg='#1e293b')
        title_label.pack(pady=(0, 20))
        
        # Status da cotação
        self.status_frame = tk.Frame(main_frame, bg='#e0f2fe', relief='solid', bd=1)
        self.status_frame.pack(fill="x", pady=(0, 20))
        
        self.status_label = tk.Label(self.status_frame, 
                                    text="📋 Selecione uma cotação para editar",
                                    font=('Arial', 12), bg='#e0f2fe', fg='#0277bd')
        self.status_label.pack(pady=10)
        
        # Seleção de cotação
        self.create_cotacao_selector(main_frame)
        
        # Painel de edição
        self.create_editing_panel(main_frame)
        
        # Botões de ação
        self.create_action_buttons(main_frame)
    
    def create_cotacao_selector(self, parent):
        """Criar seletor de cotação"""
        selector_frame = tk.LabelFrame(parent, text="🔍 Selecionar Cotação", 
                                      font=('Arial', 12, 'bold'),
                                      bg='#f8fafc', fg='#374151')
        selector_frame.pack(fill="x", pady=(0, 20))
        
        # Frame interno
        inner_frame = tk.Frame(selector_frame, bg='#f8fafc')
        inner_frame.pack(fill="x", padx=10, pady=10)
        
        # Combobox para cotações
        tk.Label(inner_frame, text="Cotação:", font=('Arial', 11), 
                bg='#f8fafc').pack(side="left", padx=(0, 10))
        
        self.cotacao_var = tk.StringVar()
        self.cotacao_combo = ttk.Combobox(inner_frame, textvariable=self.cotacao_var,
                                         width=50, state="readonly")
        self.cotacao_combo.pack(side="left", padx=(0, 10))
        self.cotacao_combo.bind('<<ComboboxSelected>>', self.on_cotacao_selected)
        
        # Botão carregar
        tk.Button(inner_frame, text="📂 Carregar", 
                 command=self.load_cotacoes,
                 bg='#3b82f6', fg='white', font=('Arial', 10, 'bold')).pack(side="left")
        
        # Carregar cotações automaticamente
        self.load_cotacoes()
    
    def create_editing_panel(self, parent):
        """Criar painel principal de edição"""
        edit_frame = tk.LabelFrame(parent, text="✏️ Edição de Campos", 
                                  font=('Arial', 12, 'bold'),
                                  bg='#f8fafc', fg='#374151')
        edit_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Criar notebook para organizar campos
        self.notebook = ttk.Notebook(edit_frame)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Aba 1: Dados do Cliente
        self.cliente_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.cliente_frame, text="👤 Cliente")
        self.create_cliente_fields(self.cliente_frame)
        
        # Aba 2: Dados da Cotação
        self.cotacao_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.cotacao_frame, text="💰 Cotação")
        self.create_cotacao_fields(self.cotacao_frame)
        
        # Aba 3: Textos Personalizados
        self.custom_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.custom_frame, text="📝 Textos Personalizados")
        self.create_custom_text_fields(self.custom_frame)
    
    def create_cliente_fields(self, parent):
        """Criar campos de dados do cliente"""
        # Container com scroll
        canvas = tk.Canvas(parent, bg='white')
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Campos do cliente
        self.cliente_fields = {}
        
        cliente_data = [
            ('nome', 'Nome da Empresa'),
            ('nome_fantasia', 'Nome Fantasia'),
            ('endereco', 'Endereço'),
            ('cidade', 'Cidade'),
            ('estado', 'Estado'),
            ('cep', 'CEP'),
            ('telefone', 'Telefone'),
            ('email', 'E-mail'),
            ('cnpj', 'CNPJ'),
            ('site', 'Website')
        ]
        
        for i, (field_name, field_label) in enumerate(cliente_data):
            row_frame = tk.Frame(scrollable_frame, bg='white')
            row_frame.pack(fill="x", padx=20, pady=5)
            
            tk.Label(row_frame, text=f"{field_label}:", 
                    font=('Arial', 10, 'bold'), bg='white', 
                    width=15, anchor='w').pack(side="left")
            
            entry = tk.Entry(row_frame, font=('Arial', 10), width=50)
            entry.pack(side="left", padx=(10, 0))
            self.cliente_fields[field_name] = entry
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_cotacao_fields(self, parent):
        """Criar campos de dados da cotação"""
        # Container com scroll
        canvas = tk.Canvas(parent, bg='white')
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Campos da cotação
        self.cotacao_fields = {}
        
        cotacao_data = [
            ('numero_proposta', 'Número da Proposta'),
            ('modelo_compressor', 'Modelo do Compressor'),
            ('numero_serie_compressor', 'Número de Série'),
            ('descricao_atividade', 'Descrição da Atividade'),
            ('valor_total', 'Valor Total (R$)'),
            ('tipo_frete', 'Tipo de Frete'),
            ('condicao_pagamento', 'Condição de Pagamento'),
            ('prazo_entrega', 'Prazo de Entrega'),
            ('observacoes', 'Observações')
        ]
        
        for i, (field_name, field_label) in enumerate(cotacao_data):
            row_frame = tk.Frame(scrollable_frame, bg='white')
            row_frame.pack(fill="x", padx=20, pady=5)
            
            tk.Label(row_frame, text=f"{field_label}:", 
                    font=('Arial', 10, 'bold'), bg='white', 
                    width=20, anchor='w').pack(side="left")
            
            if field_name in ['descricao_atividade', 'observacoes']:
                # Campo de texto multilinha
                text_widget = tk.Text(row_frame, font=('Arial', 10), 
                                    width=50, height=3)
                text_widget.pack(side="left", padx=(10, 0))
                self.cotacao_fields[field_name] = text_widget
            else:
                # Campo de texto simples
                entry = tk.Entry(row_frame, font=('Arial', 10), width=50)
                entry.pack(side="left", padx=(10, 0))
                self.cotacao_fields[field_name] = entry
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_custom_text_fields(self, parent):
        """Criar campos para textos personalizados"""
        # Container com scroll
        canvas = tk.Canvas(parent, bg='white')
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Campos personalizados
        self.custom_fields = {}
        
        custom_data = [
            ('cabecalho_personalizado', 'Cabeçalho Personalizado'),
            ('clausulas_especiais', 'Cláusulas Especiais'),
            ('termos_condicoes', 'Termos e Condições'),
            ('informacoes_adicionais', 'Informações Adicionais'),
            ('rodape_personalizado', 'Rodapé Personalizado')
        ]
        
        for i, (field_name, field_label) in enumerate(custom_data):
            row_frame = tk.Frame(scrollable_frame, bg='white')
            row_frame.pack(fill="x", padx=20, pady=10)
            
            tk.Label(row_frame, text=f"{field_label}:", 
                    font=('Arial', 11, 'bold'), bg='white').pack(anchor='w')
            
            text_widget = tk.Text(row_frame, font=('Arial', 10), 
                                width=70, height=4)
            text_widget.pack(fill="x", pady=(5, 0))
            self.custom_fields[field_name] = text_widget
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_action_buttons(self, parent):
        """Criar botões de ação"""
        button_frame = tk.Frame(parent, bg='#f8fafc')
        button_frame.pack(fill="x")
        
        # Botão Salvar
        tk.Button(button_frame, text="💾 Salvar Alterações", 
                 command=self.save_changes,
                 bg='#10b981', fg='white', 
                 font=('Arial', 12, 'bold'),
                 padx=20, pady=10).pack(side="left", padx=(0, 10))
        
        # Botão Gerar PDF
        tk.Button(button_frame, text="📄 Gerar PDF", 
                 command=self.generate_pdf,
                 bg='#3b82f6', fg='white', 
                 font=('Arial', 12, 'bold'),
                 padx=20, pady=10).pack(side="left", padx=(0, 10))
        
        # Botão Visualizar
        tk.Button(button_frame, text="👁️ Visualizar", 
                 command=self.preview_pdf,
                 bg='#f59e0b', fg='white', 
                 font=('Arial', 12, 'bold'),
                 padx=20, pady=10).pack(side="left", padx=(0, 10))
        
        # Botão Reset
        tk.Button(button_frame, text="🔄 Recarregar", 
                 command=self.reload_data,
                 bg='#6b7280', fg='white', 
                 font=('Arial', 12, 'bold'),
                 padx=20, pady=10).pack(side="right")
    
    def load_cotacoes(self):
        """Carregar lista de cotações disponíveis"""
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            
            c.execute("""
                SELECT c.id, c.numero_proposta, cl.nome as cliente_nome, c.data_criacao
                FROM cotacoes c
                LEFT JOIN clientes cl ON c.cliente_id = cl.id
                ORDER BY c.data_criacao DESC
            """)
            
            cotacoes = c.fetchall()
            
            if cotacoes:
                # Formatar lista para combobox
                cotacao_list = []
                for cot_id, numero, cliente, data in cotacoes:
                    display_text = f"ID:{cot_id} - {numero} - {cliente} ({data[:10]})"
                    cotacao_list.append(display_text)
                
                self.cotacao_combo['values'] = cotacao_list
                
                # Selecionar primeira cotação automaticamente
                if cotacao_list:
                    self.cotacao_combo.set(cotacao_list[0])
                    self.on_cotacao_selected(None)
                    
                self.status_label.config(text=f"✅ {len(cotacoes)} cotações carregadas")
            else:
                self.create_sample_cotacao()
                
        except Exception as e:
            print(f"Erro ao carregar cotações: {e}")
            messagebox.showerror("Erro", f"Erro ao carregar cotações: {e}")
        finally:
            if 'conn' in locals():
                conn.close()
    
    def on_cotacao_selected(self, event):
        """Quando uma cotação é selecionada"""
        try:
            selected = self.cotacao_var.get()
            if selected:
                # Extrair ID da cotação
                cotacao_id = int(selected.split(" - ")[0].replace("ID:", ""))
                self.current_cotacao_id = cotacao_id
                self.load_cotacao_data()
                
        except Exception as e:
            print(f"Erro ao selecionar cotação: {e}")
    
    def load_cotacao_data(self):
        """Carregar dados da cotação selecionada"""
        if not self.current_cotacao_id:
            return
            
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            
            # Buscar dados da cotação e cliente
            c.execute("""
                SELECT 
                    c.numero_proposta, c.modelo_compressor, c.numero_serie_compressor,
                    c.descricao_atividade, c.observacoes, c.valor_total,
                    c.tipo_frete, c.condicao_pagamento, c.prazo_entrega,
                    cl.nome, cl.nome_fantasia, cl.endereco, cl.cidade, cl.estado,
                    cl.cep, cl.telefone, cl.email, cl.cnpj, cl.site
                FROM cotacoes c
                LEFT JOIN clientes cl ON c.cliente_id = cl.id
                WHERE c.id = ?
            """, (self.current_cotacao_id,))
            
            result = c.fetchone()
            
            if result:
                # Preencher campos da cotação
                cot_data = result[:9]
                cot_fields = ['numero_proposta', 'modelo_compressor', 'numero_serie_compressor',
                             'descricao_atividade', 'observacoes', 'valor_total',
                             'tipo_frete', 'condicao_pagamento', 'prazo_entrega']
                
                for i, field_name in enumerate(cot_fields):
                    if field_name in self.cotacao_fields:
                        widget = self.cotacao_fields[field_name]
                        value = cot_data[i] or ""
                        
                        if isinstance(widget, tk.Text):
                            widget.delete(1.0, tk.END)
                            widget.insert(1.0, str(value))
                        else:
                            widget.delete(0, tk.END)
                            widget.insert(0, str(value))
                
                # Preencher campos do cliente
                cli_data = result[9:]
                cli_fields = ['nome', 'nome_fantasia', 'endereco', 'cidade', 'estado',
                             'cep', 'telefone', 'email', 'cnpj', 'site']
                
                for i, field_name in enumerate(cli_fields):
                    if field_name in self.cliente_fields:
                        widget = self.cliente_fields[field_name]
                        value = cli_data[i] or ""
                        widget.delete(0, tk.END)
                        widget.insert(0, str(value))
                
                self.status_label.config(
                    text=f"✅ Cotação ID:{self.current_cotacao_id} carregada com sucesso",
                    bg='#dcfce7', fg='#166534'
                )
                
                # Carregar textos personalizados salvos
                self.load_custom_texts()
                
        except Exception as e:
            print(f"Erro ao carregar dados da cotação: {e}")
            messagebox.showerror("Erro", f"Erro ao carregar dados: {e}")
        finally:
            if 'conn' in locals():
                conn.close()
    
    def load_custom_texts(self):
        """Carregar textos personalizados salvos"""
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            
            # Verificar se a tabela existe
            c.execute("""
                CREATE TABLE IF NOT EXISTS pdf_custom_texts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cotacao_id INTEGER,
                    field_name TEXT,
                    field_value TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (cotacao_id) REFERENCES cotacoes (id)
                )
            """)
            
            # Carregar textos salvos
            c.execute("""
                SELECT field_name, field_value 
                FROM pdf_custom_texts 
                WHERE cotacao_id = ?
            """, (self.current_cotacao_id,))
            
            results = c.fetchall()
            
            for field_name, field_value in results:
                if field_name in self.custom_fields:
                    widget = self.custom_fields[field_name]
                    widget.delete(1.0, tk.END)
                    widget.insert(1.0, field_value or "")
            
            conn.commit()
            
        except Exception as e:
            print(f"Erro ao carregar textos personalizados: {e}")
        finally:
            if 'conn' in locals():
                conn.close()
    
    def save_changes(self):
        """Salvar todas as alterações"""
        if not self.current_cotacao_id:
            messagebox.showwarning("Aviso", "Selecione uma cotação primeiro!")
            return
            
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            
            # Salvar dados da cotação
            cotacao_values = []
            cot_fields = ['numero_proposta', 'modelo_compressor', 'numero_serie_compressor',
                         'descricao_atividade', 'observacoes', 'valor_total',
                         'tipo_frete', 'condicao_pagamento', 'prazo_entrega']
            
            for field_name in cot_fields:
                if field_name in self.cotacao_fields:
                    widget = self.cotacao_fields[field_name]
                    if isinstance(widget, tk.Text):
                        value = widget.get(1.0, tk.END).strip()
                    else:
                        value = widget.get().strip()
                    cotacao_values.append(value)
            
            # Atualizar cotação
            c.execute("""
                UPDATE cotacoes SET
                numero_proposta=?, modelo_compressor=?, numero_serie_compressor=?,
                descricao_atividade=?, observacoes=?, valor_total=?,
                tipo_frete=?, condicao_pagamento=?, prazo_entrega=?
                WHERE id=?
            """, cotacao_values + [self.current_cotacao_id])
            
            # Buscar cliente_id
            c.execute("SELECT cliente_id FROM cotacoes WHERE id=?", (self.current_cotacao_id,))
            cliente_id = c.fetchone()[0]
            
            # Salvar dados do cliente
            cliente_values = []
            cli_fields = ['nome', 'nome_fantasia', 'endereco', 'cidade', 'estado',
                         'cep', 'telefone', 'email', 'cnpj', 'site']
            
            for field_name in cli_fields:
                if field_name in self.cliente_fields:
                    value = self.cliente_fields[field_name].get().strip()
                    cliente_values.append(value)
            
            # Atualizar cliente
            c.execute("""
                UPDATE clientes SET
                nome=?, nome_fantasia=?, endereco=?, cidade=?, estado=?,
                cep=?, telefone=?, email=?, cnpj=?, site=?
                WHERE id=?
            """, cliente_values + [cliente_id])
            
            # Salvar textos personalizados
            # Primeiro, remover textos antigos
            c.execute("DELETE FROM pdf_custom_texts WHERE cotacao_id=?", 
                     (self.current_cotacao_id,))
            
            # Inserir novos textos
            for field_name, widget in self.custom_fields.items():
                value = widget.get(1.0, tk.END).strip()
                if value:
                    c.execute("""
                        INSERT INTO pdf_custom_texts (cotacao_id, field_name, field_value)
                        VALUES (?, ?, ?)
                    """, (self.current_cotacao_id, field_name, value))
            
            conn.commit()
            
            self.status_label.config(
                text="💾 Alterações salvas com sucesso!",
                bg='#dcfce7', fg='#166534'
            )
            
            messagebox.showinfo("Sucesso", "Todas as alterações foram salvas!")
            
        except Exception as e:
            print(f"Erro ao salvar alterações: {e}")
            messagebox.showerror("Erro", f"Erro ao salvar: {e}")
        finally:
            if 'conn' in locals():
                conn.close()
    
    def generate_pdf(self):
        """Gerar PDF com as alterações"""
        if not self.current_cotacao_id:
            messagebox.showwarning("Aviso", "Selecione uma cotação primeiro!")
            return
        
        try:
            # Salvar alterações antes de gerar PDF
            self.save_changes()
            
            # Usar o gerador de PDF existente
            from pdf_generators.cotacao_nova import gerar_pdf_cotacao_nova
            
            success, result = gerar_pdf_cotacao_nova(
                self.current_cotacao_id, 
                self.db_name, 
                self.user_id
            )
            
            if success:
                self.status_label.config(
                    text=f"📄 PDF gerado com sucesso: {result}",
                    bg='#dcfce7', fg='#166534'
                )
                messagebox.showinfo("Sucesso", f"PDF gerado com sucesso!\n\nArquivo: {result}")
            else:
                messagebox.showerror("Erro", f"Erro ao gerar PDF: {result}")
                
        except Exception as e:
            print(f"Erro ao gerar PDF: {e}")
            messagebox.showerror("Erro", f"Erro ao gerar PDF: {e}")
    
    def preview_pdf(self):
        """Visualizar PDF gerado"""
        if not self.current_cotacao_id:
            messagebox.showwarning("Aviso", "Selecione uma cotação primeiro!")
            return
        
        try:
            # Gerar PDF temporário
            self.save_changes()
            
            from pdf_generators.cotacao_nova import gerar_pdf_cotacao_nova
            
            success, result = gerar_pdf_cotacao_nova(
                self.current_cotacao_id, 
                self.db_name, 
                self.user_id
            )
            
            if success and os.path.exists(result):
                # Tentar abrir PDF
                if os.name == 'nt':  # Windows
                    os.startfile(result)
                elif os.name == 'posix':  # Linux/Mac
                    subprocess.run(['xdg-open', result], check=False)
                
                self.status_label.config(
                    text="👁️ PDF aberto para visualização",
                    bg='#dbeafe', fg='#1d4ed8'
                )
            else:
                messagebox.showerror("Erro", f"Erro ao gerar PDF para visualização: {result}")
                
        except Exception as e:
            print(f"Erro ao visualizar PDF: {e}")
            messagebox.showerror("Erro", f"Erro ao visualizar PDF: {e}")
    
    def reload_data(self):
        """Recarregar dados da cotação atual"""
        if self.current_cotacao_id:
            self.load_cotacao_data()
            self.status_label.config(
                text="🔄 Dados recarregados",
                bg='#dbeafe', fg='#1d4ed8'
            )
        else:
            self.load_cotacoes()
    
    def create_sample_cotacao(self):
        """Criar cotação de exemplo se não existir nenhuma"""
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            
            # Verificar se já existe cliente de exemplo
            c.execute("SELECT id FROM clientes WHERE nome = 'Empresa Exemplo LTDA'")
            cliente_result = c.fetchone()
            
            if not cliente_result:
                # Criar cliente de exemplo
                c.execute("""
                    INSERT INTO clientes (nome, nome_fantasia, endereco, telefone, email, cnpj, cidade, estado, cep)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    'Empresa Exemplo LTDA', 'Exemplo Corp', 'Rua das Empresas, 123',
                    '(11) 3456-7890', 'contato@exemplo.com.br', '11.222.333/0001-44',
                    'São Paulo', 'SP', '01234-567'
                ))
                cliente_id = c.lastrowid
            else:
                cliente_id = cliente_result[0]
            
            # Criar cotação de exemplo
            c.execute("""
                INSERT INTO cotacoes (
                    numero_proposta, cliente_id, vendedor_id, modelo_compressor,
                    numero_serie_compressor, descricao_atividade, observacoes,
                    valor_total, tipo_frete, condicao_pagamento, prazo_entrega,
                    data_criacao
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                'PROP-EXEMPLO-2024-001', cliente_id, self.user_id, 'Compressor Schulz CSL20',
                'CSL2024001', 'Manutenção preventiva completa do sistema de ar comprimido',
                'Cotação de exemplo para demonstração do editor PDF',
                18500.00, 'FOB', '30 dias', '10 dias úteis',
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
            
            conn.commit()
            
            # Recarregar lista
            self.load_cotacoes()
            
            self.status_label.config(
                text="✅ Cotação de exemplo criada!",
                bg='#dcfce7', fg='#166534'
            )
            
        except Exception as e:
            print(f"Erro ao criar cotação de exemplo: {e}")
        finally:
            if 'conn' in locals():
                conn.close()
    
    def load_sample_cotacao(self):
        """Carregar uma cotação de exemplo no início"""
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            
            # Buscar primeira cotação disponível
            c.execute("SELECT id FROM cotacoes ORDER BY data_criacao DESC LIMIT 1")
            result = c.fetchone()
            
            if result:
                self.current_cotacao_id = result[0]
            else:
                # Se não há cotações, será criada uma no load_cotacoes
                pass
                
        except Exception as e:
            print(f"Erro ao carregar cotação inicial: {e}")
        finally:
            if 'conn' in locals():
                conn.close()
    
    def create_error_interface(self, parent, error_msg):
        """Criar interface de erro"""
        error_frame = tk.Frame(parent, bg='#fef2f2')
        error_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(error_frame, text="❌ Erro no Editor PDF", 
                font=('Arial', 16, 'bold'), 
                bg='#fef2f2', fg='#dc2626').pack(pady=20)
        
        tk.Label(error_frame, text=f"Detalhes do erro:\n{error_msg}", 
                font=('Arial', 11), 
                bg='#fef2f2', fg='#7f1d1d',
                wraplength=500, justify='left').pack(pady=10)