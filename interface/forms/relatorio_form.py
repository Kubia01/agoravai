import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from database import DB_NAME

class RelatorioForm:
    def __init__(self, parent, relatorio_id=None, user_id=None):
        self.parent = parent
        self.relatorio_id = relatorio_id
        self.user_id = user_id
        self.on_save = None
        
        self.create_window()
        self.setup_ui()
        
        if relatorio_id:
            self.load_relatorio()
            
    def create_window(self):
        self.window = tk.Toplevel(self.parent)
        self.window.title("Relatório Técnico")
        self.window.geometry("900x700")
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Centralizar
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (450)
        y = (self.window.winfo_screenheight() // 2) - (350)
        self.window.geometry(f"900x700+{x}+{y}")
        
    def setup_ui(self):
        # Frame principal com scroll
        main_frame = ttk.Frame(self.window, style='Modern.TFrame')
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Canvas e scrollbar
        canvas = tk.Canvas(main_frame, bg='#f8fafc', highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas, style='Modern.TFrame')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Título
        title_label = ttk.Label(self.scrollable_frame, 
                               text="Novo Relatório Técnico" if not self.relatorio_id else "Editar Relatório Técnico",
                               font=('Segoe UI', 16, 'bold'),
                               background='#f8fafc',
                               foreground='#1e293b')
        title_label.pack(pady=(0, 20))
        
        # Seção: Cliente
        self.create_cliente_section()
        
        # Seção: Dados do Serviço
        self.create_servico_section()
        
        # Seção: Condição do Equipamento
        self.create_equipamento_section()
        
        # Botões
        self.create_buttons()
        
    def create_cliente_section(self):
        # Frame da seção
        section_frame = ttk.LabelFrame(self.scrollable_frame, text="Identificação do Cliente", 
                                      style='Card.TFrame', padding="15")
        section_frame.pack(fill="x", pady=(0, 15))
        
        # Cliente
        cliente_frame = ttk.Frame(section_frame, style='Card.TFrame')
        cliente_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(cliente_frame, text="Cliente:", style='Card.TLabel').pack(side="left")
        
        self.cliente_var = tk.StringVar()
        self.cliente_combo = ttk.Combobox(cliente_frame, textvariable=self.cliente_var,
                                         style='Modern.TEntry', width=50, state="readonly")
        self.cliente_combo.pack(side="right", fill="x", expand=True, padx=(10, 0))
        
        # Carregar clientes
        self.load_clientes()
        
    def create_servico_section(self):
        # Frame da seção
        section_frame = ttk.LabelFrame(self.scrollable_frame, text="Dados do Serviço", 
                                      style='Card.TFrame', padding="15")
        section_frame.pack(fill="x", pady=(0, 15))
        
        # Grid de campos
        fields_frame = ttk.Frame(section_frame, style='Card.TFrame')
        fields_frame.pack(fill="x")
        
        # Formulário de Serviço
        ttk.Label(fields_frame, text="Formulário de Serviço:", style='Card.TLabel').grid(row=0, column=0, sticky="w", pady=5)
        self.form_servico_var = tk.StringVar()
        ttk.Entry(fields_frame, textvariable=self.form_servico_var, style='Modern.TEntry', width=30).grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Tipo de Serviço
        ttk.Label(fields_frame, text="Tipo de Serviço:", style='Card.TLabel').grid(row=1, column=0, sticky="w", pady=5)
        self.tipo_servico_var = tk.StringVar()
        tipo_combo = ttk.Combobox(fields_frame, textvariable=self.tipo_servico_var,
                                 values=["Manutenção Preventiva", "Manutenção Corretiva", "Instalação", "Vistoria", "Outro"],
                                 style='Modern.TEntry', width=30)
        tipo_combo.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Data de Recebimento
        ttk.Label(fields_frame, text="Data de Recebimento:", style='Card.TLabel').grid(row=2, column=0, sticky="w", pady=5)
        self.data_recebimento_var = tk.StringVar()
        ttk.Entry(fields_frame, textvariable=self.data_recebimento_var, style='Modern.TEntry', width=30).grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Configurar colunas
        fields_frame.grid_columnconfigure(1, weight=1)
        
        # Descrição do Serviço
        desc_frame = ttk.Frame(section_frame, style='Card.TFrame')
        desc_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Label(desc_frame, text="Descrição da Atividade:", style='Card.TLabel').pack(anchor="w")
        self.descricao_text = tk.Text(desc_frame, height=4, wrap=tk.WORD, font=('Segoe UI', 10))
        self.descricao_text.pack(fill="x", pady=(5, 0))
        
    def create_equipamento_section(self):
        # Frame da seção
        section_frame = ttk.LabelFrame(self.scrollable_frame, text="Condição do Equipamento", 
                                      style='Card.TFrame', padding="15")
        section_frame.pack(fill="x", pady=(0, 15))
        
        # Campos do equipamento
        self.equipamento_vars = {}
        campos = [
            "Condição Inicial",
            "Condição Atual", 
            "Condição Encontrada",
            "Placa de Identificação",
            "Acoplamento",
            "Aspectos dos Rotores",
            "Válvulas Acopladas"
        ]
        
        for i, campo in enumerate(campos):
            row = i // 2
            col = (i % 2) * 2
            
            ttk.Label(section_frame, text=f"{campo}:", style='Card.TLabel').grid(row=row, column=col, sticky="w", pady=5, padx=(0, 10))
            
            var = tk.StringVar()
            self.equipamento_vars[campo] = var
            ttk.Entry(section_frame, textvariable=var, style='Modern.TEntry', width=30).grid(row=row, column=col+1, sticky="ew", pady=5, padx=(0, 20))
        
        # Configurar colunas
        section_frame.grid_columnconfigure(1, weight=1)
        section_frame.grid_columnconfigure(3, weight=1)
        
    def create_buttons(self):
        # Frame dos botões
        buttons_frame = ttk.Frame(self.scrollable_frame, style='Modern.TFrame')
        buttons_frame.pack(fill="x", pady=(20, 0))
        
        # Botões
        cancel_btn = ttk.Button(buttons_frame, text="Cancelar", 
                               style='Secondary.TButton',
                               command=self.window.destroy)
        cancel_btn.pack(side="right", padx=(10, 0))
        
        save_btn = ttk.Button(buttons_frame, text="Salvar", 
                             style='Modern.TButton',
                             command=self.save_relatorio)
        save_btn.pack(side="right")
        
    def load_clientes(self):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            c.execute("SELECT id, nome FROM clientes ORDER BY nome")
            clientes = c.fetchall()
            
            self.clientes_dict = {f"{nome} (ID: {id})": id for id, nome in clientes}
            self.cliente_combo['values'] = list(self.clientes_dict.keys())
            
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao carregar clientes: {e}")
        finally:
            conn.close()
            
    def load_relatorio(self):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            # First get all column names to understand the structure
            c.execute("PRAGMA table_info(relatorios_tecnicos)")
            columns_info = c.fetchall()
            column_names = [column[1] for column in columns_info]
            
            # Create a query that explicitly selects each column by name
            columns_sql = []
            for col in column_names:
                columns_sql.append(f"r.{col}")
            
            query = f"""
                SELECT {', '.join(columns_sql)}, c.nome as cliente_nome
                FROM relatorios_tecnicos r
                JOIN clientes c ON r.cliente_id = c.id
                WHERE r.id = ?
            """
            
            c.execute(query, (self.relatorio_id,))
            
            relatorio = c.fetchone()
            if relatorio:
                # Create a dictionary mapping column names to values
                relatorio_dict = {}
                for i, col in enumerate(column_names):
                    if i < len(relatorio):
                        relatorio_dict[col] = relatorio[i]
                
                # Add the cliente_nome column
                cliente_nome_index = len(column_names)
                if cliente_nome_index < len(relatorio):
                    cliente_nome = relatorio[cliente_nome_index]
                    relatorio_dict['cliente_nome'] = cliente_nome
                
                # Preencher campos
                if 'cliente_id' in relatorio_dict and 'cliente_nome' in relatorio_dict:
                    cliente_key = f"{relatorio_dict['cliente_nome']} (ID: {relatorio_dict['cliente_id']})"
                    if cliente_key in self.clientes_dict:
                        self.cliente_var.set(cliente_key)
                
                # Set form fields using the dictionary
                if 'formulario_servico' in relatorio_dict:
                    self.form_servico_var.set(relatorio_dict['formulario_servico'] or "")
                    
                if 'tipo_servico' in relatorio_dict:
                    self.tipo_servico_var.set(relatorio_dict['tipo_servico'] or "")
                    
                if 'data_recebimento' in relatorio_dict:
                    self.data_recebimento_var.set(relatorio_dict['data_recebimento'] or "")
                
                if 'descricao_servico' in relatorio_dict and relatorio_dict['descricao_servico']:
                    self.descricao_text.delete("1.0", tk.END)  # Clear existing content
                    self.descricao_text.insert("1.0", relatorio_dict['descricao_servico'])
                
                # Map database column names to form field names
                field_mapping = {
                    'condicao_inicial': "Condição Inicial",
                    'condicao_atual': "Condição Atual", 
                    'condicao_encontrada': "Condição Encontrada",
                    'placa_identificacao': "Placa de Identificação",
                    'acoplamento': "Acoplamento",
                    'aspectos_rotores': "Aspectos dos Rotores",
                    'valvulas_acopladas': "Válvulas Acopladas"
                }
                
                # Set equipment fields from the dictionary
                for db_field, form_field in field_mapping.items():
                    if db_field in relatorio_dict and form_field in self.equipamento_vars:
                        self.equipamento_vars[form_field].set(relatorio_dict.get(db_field) or "")
                        
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao carregar relatório: {e}")
        finally:
            conn.close()
            
    def save_relatorio(self):
        # Validar campos obrigatórios
        if not self.cliente_var.get():
            messagebox.showwarning("Aviso", "Selecione um cliente.")
            return
            
        cliente_id = self.clientes_dict[self.cliente_var.get()]
        
        # Dados do relatório
        data = {
            'cliente_id': cliente_id,
            'responsavel_id': self.user_id,
            'formulario_servico': self.form_servico_var.get(),
            'tipo_servico': self.tipo_servico_var.get(),
            'descricao_servico': self.descricao_text.get("1.0", tk.END).strip(),
            'data_recebimento': self.data_recebimento_var.get()
        }
        
        # Verificar quais campos de equipamento existem
        for campo in ["Condição Inicial", "Condição Atual", "Condição Encontrada",
                      "Placa de Identificação", "Acoplamento", "Aspectos dos Rotores", 
                      "Válvulas Acopladas"]:
            if campo in self.equipamento_vars:
                campo_db = campo.lower().replace(' ', '_').replace('ção', 'cao')
                data[campo_db] = self.equipamento_vars[campo].get()
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            # Verificar quais colunas existem na tabela
            c.execute("PRAGMA table_info(relatorios_tecnicos)")
            columns_info = c.fetchall()
            column_names = [column[1] for column in columns_info]
            
            if self.relatorio_id:
                # Atualizar - Construir query dinamicamente
                update_parts = []
                update_values = []
                
                for key, value in data.items():
                    if key in column_names:
                        update_parts.append(f"{key}=?")
                        update_values.append(value)
                
                if update_parts:
                    query = f"UPDATE relatorios_tecnicos SET {', '.join(update_parts)} WHERE id=?"
                    update_values.append(self.relatorio_id)
                    c.execute(query, update_values)
            else:
                # Inserir - Construir query dinamicamente
                numero_relatorio = f"REL-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                data_criacao = datetime.now().strftime('%Y-%m-%d')
                
                # Adicionar campos obrigatórios
                data['numero_relatorio'] = numero_relatorio
                data['data_criacao'] = data_criacao
                
                # Filtrar para incluir apenas colunas existentes
                columns = []
                values = []
                placeholders = []
                
                for key, value in data.items():
                    if key in column_names:
                        columns.append(key)
                        values.append(value)
                        placeholders.append('?')
                
                query = f"INSERT INTO relatorios_tecnicos ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
                c.execute(query, values)
            
            conn.commit()
            messagebox.showinfo("Sucesso", "Relatório salvo com sucesso!")
            
            if self.on_save:
                self.on_save()
                
            self.window.destroy()
            
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao salvar relatório: {e}")
        finally:
            conn.close()