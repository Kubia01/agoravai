import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from database import DB_NAME

class ClienteForm:
    def __init__(self, parent, cliente_id=None):
        self.parent = parent
        self.cliente_id = cliente_id
        self.on_save = None
        self.contatos = []
        
        self.create_window()
        self.setup_ui()
        
        if cliente_id:
            self.load_cliente()
            
    def create_window(self):
        self.window = tk.Toplevel(self.parent)
        self.window.title("Cliente")
        self.window.geometry("800x700")
        self.window.transient(self.parent)
        self.window.grab_set()
        self.window.configure(bg='white')
        
        # Centralizar
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (400)
        y = (self.window.winfo_screenheight() // 2) - (350)
        self.window.geometry(f"800x700+{x}+{y}")
        
    def setup_ui(self):
        # Frame principal com scroll
        main_frame = tk.Frame(self.window, bg='white')
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Canvas e scrollbar
        canvas = tk.Canvas(main_frame, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg='white')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Título
        title_label = tk.Label(self.scrollable_frame, 
                               text="Novo Cliente" if not self.cliente_id else "Editar Cliente",
                               font=('Arial', 16, 'bold'),
                               bg='white',
                               fg='#1e293b')
        title_label.pack(pady=(0, 20))
        
        # Seção: Dados Básicos
        self.create_dados_basicos_section()
        
        # Seção: Endereço
        self.create_endereco_section()
        
        # Seção: Contatos
        self.create_contatos_section()
        
        # Botões
        self.create_buttons()
        
    def create_dados_basicos_section(self):
        # Frame da seção
        section_frame = tk.LabelFrame(self.scrollable_frame, text="Dados Básicos", 
                                      font=('Arial', 12, 'bold'),
                                      bg='white',
                                      padx=15, pady=15)
        section_frame.pack(fill="x", pady=(0, 15))
        
        # Variáveis
        self.nome_var = tk.StringVar()
        self.nome_fantasia_var = tk.StringVar()
        self.cnpj_var = tk.StringVar()
        self.telefone_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.site_var = tk.StringVar()
        self.prazo_pagamento_var = tk.StringVar()
        
        # Grid de campos
        fields_frame = tk.Frame(section_frame, bg='white')
        fields_frame.pack(fill="x")
        
        # Campos
        row = 0
        
        # Nome
        tk.Label(fields_frame, text="Nome *:", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.nome_var, font=('Arial', 10), width=40).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Nome Fantasia
        tk.Label(fields_frame, text="Nome Fantasia:", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.nome_fantasia_var, font=('Arial', 10), width=40).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # CNPJ
        tk.Label(fields_frame, text="CNPJ *:", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.cnpj_var, font=('Arial', 10), width=40).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Telefone
        tk.Label(fields_frame, text="Telefone Principal:", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.telefone_var, font=('Arial', 10), width=40).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Email
        tk.Label(fields_frame, text="Email Principal:", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.email_var, font=('Arial', 10), width=40).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Site
        tk.Label(fields_frame, text="Site:", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.site_var, font=('Arial', 10), width=40).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Prazo de Pagamento
        tk.Label(fields_frame, text="Prazo de Pagamento:", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.prazo_pagamento_var, font=('Arial', 10), width=40).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Configurar colunas
        fields_frame.grid_columnconfigure(1, weight=1)
        
    def create_endereco_section(self):
        # Frame da seção
        section_frame = tk.LabelFrame(self.scrollable_frame, text="Endereço", 
                                      font=('Arial', 12, 'bold'),
                                      bg='white',
                                      padx=15, pady=15)
        section_frame.pack(fill="x", pady=(0, 15))
        
        # Variáveis
        self.endereco_var = tk.StringVar()
        self.cidade_var = tk.StringVar()
        self.estado_var = tk.StringVar()
        self.cep_var = tk.StringVar()
        self.pais_var = tk.StringVar()
        self.pais_var.set("Brasil")
        
        # Grid de campos
        fields_frame = tk.Frame(section_frame, bg='white')
        fields_frame.pack(fill="x")
        
        # Endereço
        tk.Label(fields_frame, text="Endereço:", font=('Arial', 10, 'bold'), bg='white').grid(row=0, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.endereco_var, font=('Arial', 10), width=60).grid(row=0, column=1, columnspan=3, sticky="ew", padx=(10, 0), pady=5)
        
        # Cidade
        tk.Label(fields_frame, text="Cidade:", font=('Arial', 10, 'bold'), bg='white').grid(row=1, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.cidade_var, font=('Arial', 10), width=25).grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Estado
        tk.Label(fields_frame, text="Estado:", font=('Arial', 10, 'bold'), bg='white').grid(row=1, column=2, sticky="w", padx=(20, 0), pady=5)
        estados = ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"]
        estado_combo = ttk.Combobox(fields_frame, textvariable=self.estado_var, values=estados, width=10)
        estado_combo.grid(row=1, column=3, sticky="ew", padx=(10, 0), pady=5)
        
        # CEP
        tk.Label(fields_frame, text="CEP:", font=('Arial', 10, 'bold'), bg='white').grid(row=2, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.cep_var, font=('Arial', 10), width=15).grid(row=2, column=1, sticky="w", padx=(10, 0), pady=5)
        
        # País
        tk.Label(fields_frame, text="País:", font=('Arial', 10, 'bold'), bg='white').grid(row=2, column=2, sticky="w", padx=(20, 0), pady=5)
        tk.Entry(fields_frame, textvariable=self.pais_var, font=('Arial', 10), width=15).grid(row=2, column=3, sticky="ew", padx=(10, 0), pady=5)
        
        # Configurar colunas
        fields_frame.grid_columnconfigure(1, weight=1)
        fields_frame.grid_columnconfigure(3, weight=1)
        
    def create_contatos_section(self):
        # Frame da seção
        section_frame = tk.LabelFrame(self.scrollable_frame, text="Contatos", 
                                      font=('Arial', 12, 'bold'),
                                      bg='white',
                                      padx=15, pady=15)
        section_frame.pack(fill="x", pady=(0, 15))
        
        # Frame para adicionar contato
        add_frame = tk.Frame(section_frame, bg='white')
        add_frame.pack(fill="x", pady=(0, 10))
        
        # Variáveis para novo contato
        self.contato_nome_var = tk.StringVar()
        self.contato_cargo_var = tk.StringVar()
        self.contato_email_var = tk.StringVar()
        self.contato_telefone_var = tk.StringVar()
        self.contato_principal_var = tk.BooleanVar()
        
        # Grid para adicionar contato
        tk.Label(add_frame, text="Nome:", font=('Arial', 10, 'bold'), bg='white').grid(row=0, column=0, sticky="w", padx=5)
        tk.Entry(add_frame, textvariable=self.contato_nome_var, font=('Arial', 10), width=20).grid(row=0, column=1, padx=5)
        
        tk.Label(add_frame, text="Cargo:", font=('Arial', 10, 'bold'), bg='white').grid(row=0, column=2, sticky="w", padx=5)
        tk.Entry(add_frame, textvariable=self.contato_cargo_var, font=('Arial', 10), width=20).grid(row=0, column=3, padx=5)
        
        tk.Label(add_frame, text="Email:", font=('Arial', 10, 'bold'), bg='white').grid(row=1, column=0, sticky="w", padx=5, pady=5)
        tk.Entry(add_frame, textvariable=self.contato_email_var, font=('Arial', 10), width=20).grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(add_frame, text="Telefone:", font=('Arial', 10, 'bold'), bg='white').grid(row=1, column=2, sticky="w", padx=5, pady=5)
        tk.Entry(add_frame, textvariable=self.contato_telefone_var, font=('Arial', 10), width=20).grid(row=1, column=3, padx=5, pady=5)
        
        tk.Checkbutton(add_frame, text="Principal", variable=self.contato_principal_var, 
                       font=('Arial', 10), bg='white').grid(row=1, column=4, padx=10, pady=5)
        
        tk.Button(add_frame, text="Adicionar Contato",
                  font=('Arial', 10, 'bold'),
                  bg='#10b981',
                  fg='white',
                  relief='flat',
                  cursor='hand2',
                  padx=15,
                  command=self.adicionar_contato).grid(row=1, column=5, padx=10, pady=5)
        
        # Lista de contatos
        self.contatos_tree = ttk.Treeview(section_frame, 
                                         columns=("nome", "cargo", "email", "telefone", "principal"),
                                         show="headings",
                                         height=6)
        
        # Cabeçalhos
        self.contatos_tree.heading("nome", text="Nome")
        self.contatos_tree.heading("cargo", text="Cargo")
        self.contatos_tree.heading("email", text="Email")
        self.contatos_tree.heading("telefone", text="Telefone")
        self.contatos_tree.heading("principal", text="Principal")
        
        # Larguras
        self.contatos_tree.column("nome", width=150)
        self.contatos_tree.column("cargo", width=150)
        self.contatos_tree.column("email", width=200)
        self.contatos_tree.column("telefone", width=120)
        self.contatos_tree.column("principal", width=80)
        
        self.contatos_tree.pack(fill="x", pady=(10, 0))
        
        # Botões para contatos
        contato_buttons = tk.Frame(section_frame, bg='white')
        contato_buttons.pack(fill="x", pady=(10, 0))
        
        tk.Button(contato_buttons, text="Definir como Principal",
                  font=('Arial', 10),
                  bg='#f59e0b',
                  fg='white',
                  relief='flat',
                  cursor='hand2',
                  padx=15,
                  command=self.definir_principal).pack(side="left", padx=5)
        
        tk.Button(contato_buttons, text="Remover Contato",
                  font=('Arial', 10),
                  bg='#dc2626',
                  fg='white',
                  relief='flat',
                  cursor='hand2',
                  padx=15,
                  command=self.remover_contato).pack(side="left", padx=5)
        
    def create_buttons(self):
        # Frame dos botões
        buttons_frame = tk.Frame(self.scrollable_frame, bg='white')
        buttons_frame.pack(fill="x", pady=(20, 0))
        
        # Botões
        cancel_btn = tk.Button(buttons_frame, text="Cancelar", 
                               font=('Arial', 10),
                               bg='#e2e8f0',
                               fg='#475569',
                               relief='flat',
                               cursor='hand2',
                               padx=15,
                               pady=8,
                               command=self.window.destroy)
        cancel_btn.pack(side="right", padx=(10, 0))
        
        save_btn = tk.Button(buttons_frame, text="Salvar", 
                             font=('Arial', 10, 'bold'),
                             bg='#3b82f6',
                             fg='white',
                             relief='flat',
                             cursor='hand2',
                             padx=15,
                             pady=8,
                             command=self.save_cliente)
        save_btn.pack(side="right")
        
    def adicionar_contato(self):
        nome = self.contato_nome_var.get()
        if not nome:
            messagebox.showwarning("Aviso", "Nome do contato é obrigatório.")
            return
            
        contato = {
            'nome': nome,
            'cargo': self.contato_cargo_var.get(),
            'email': self.contato_email_var.get(),
            'telefone': self.contato_telefone_var.get(),
            'principal': self.contato_principal_var.get()
        }
        
        # Se este contato for principal, remover principal dos outros
        if contato['principal']:
            for c in self.contatos:
                c['principal'] = False
        
        self.contatos.append(contato)
        self.atualizar_lista_contatos()
        
        # Limpar campos
        self.contato_nome_var.set("")
        self.contato_cargo_var.set("")
        self.contato_email_var.set("")
        self.contato_telefone_var.set("")
        self.contato_principal_var.set(False)
        
    def remover_contato(self):
        selected = self.contatos_tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um contato para remover.")
            return
            
        index = self.contatos_tree.index(selected[0])
        del self.contatos[index]
        self.atualizar_lista_contatos()
        
    def definir_principal(self):
        selected = self.contatos_tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um contato para definir como principal.")
            return
            
        index = self.contatos_tree.index(selected[0])
        
        # Remover principal de todos
        for c in self.contatos:
            c['principal'] = False
            
        # Definir o selecionado como principal
        self.contatos[index]['principal'] = True
        self.atualizar_lista_contatos()
        
    def atualizar_lista_contatos(self):
        # Limpar lista
        for item in self.contatos_tree.get_children():
            self.contatos_tree.delete(item)
            
        # Adicionar contatos
        for contato in self.contatos:
            self.contatos_tree.insert("", "end", values=(
                contato['nome'],
                contato['cargo'],
                contato['email'],
                contato['telefone'],
                "Sim" if contato['principal'] else "Não"
            ))
            
    def load_cliente(self):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            # Carregar dados do cliente
            c.execute("SELECT * FROM clientes WHERE id = ?", (self.cliente_id,))
            cliente = c.fetchone()
            
            if cliente:
                self.nome_var.set(cliente[1] or "")
                self.nome_fantasia_var.set(cliente[3] or "")
                self.cnpj_var.set(cliente[4] or "")
                self.endereco_var.set(cliente[5] or "")
                self.cidade_var.set(cliente[6] or "")
                self.estado_var.set(cliente[7] or "")
                self.cep_var.set(cliente[8] or "")
                self.pais_var.set(cliente[9] or "Brasil")
                self.telefone_var.set(cliente[10] or "")
                self.email_var.set(cliente[11] or "")
                self.site_var.set(cliente[12] or "")
                self.prazo_pagamento_var.set(cliente[13] or "")
            
            # Carregar contatos
            c.execute("SELECT * FROM contatos_cliente WHERE cliente_id = ?", (self.cliente_id,))
            contatos_db = c.fetchall()
            
            self.contatos = []
            for contato_db in contatos_db:
                contato = {
                    'id': contato_db[0],
                    'nome': contato_db[2],
                    'cargo': contato_db[3] or "",
                    'email': contato_db[4] or "",
                    'telefone': contato_db[5] or "",
                    'principal': bool(contato_db[6])
                }
                self.contatos.append(contato)
            
            self.atualizar_lista_contatos()
                
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao carregar cliente: {e}")
        finally:
            conn.close()
            
    def save_cliente(self):
        # Validar campos obrigatórios
        if not self.nome_var.get() or not self.cnpj_var.get():
            messagebox.showwarning("Aviso", "Nome e CNPJ são obrigatórios.")
            return
            
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            if self.cliente_id:
                # Atualizar cliente
                c.execute("""
                    UPDATE clientes SET
                        nome=?, nome_fantasia=?, cnpj=?, endereco=?, cidade=?, estado=?, 
                        cep=?, pais=?, telefone=?, email=?, site=?, prazo_pagamento=?,
                        updated_at=CURRENT_TIMESTAMP
                    WHERE id=?
                """, (
                    self.nome_var.get(), self.nome_fantasia_var.get(), self.cnpj_var.get(),
                    self.endereco_var.get(), self.cidade_var.get(), self.estado_var.get(),
                    self.cep_var.get(), self.pais_var.get(), self.telefone_var.get(),
                    self.email_var.get(), self.site_var.get(), self.prazo_pagamento_var.get(),
                    self.cliente_id
                ))
                
                # Remover contatos antigos
                c.execute("DELETE FROM contatos_cliente WHERE cliente_id=?", (self.cliente_id,))
                cliente_id = self.cliente_id
            else:
                # Inserir novo cliente
                c.execute("""
                    INSERT INTO clientes (
                        nome, nome_fantasia, cnpj, endereco, cidade, estado, cep, pais,
                        telefone, email, site, prazo_pagamento
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.nome_var.get(), self.nome_fantasia_var.get(), self.cnpj_var.get(),
                    self.endereco_var.get(), self.cidade_var.get(), self.estado_var.get(),
                    self.cep_var.get(), self.pais_var.get(), self.telefone_var.get(),
                    self.email_var.get(), self.site_var.get(), self.prazo_pagamento_var.get()
                ))
                cliente_id = c.lastrowid
            
            # Inserir contatos
            for contato in self.contatos:
                c.execute("""
                    INSERT INTO contatos_cliente (cliente_id, nome, cargo, email, telefone, principal)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    cliente_id, contato['nome'], contato['cargo'],
                    contato['email'], contato['telefone'], contato['principal']
                ))
            
            conn.commit()
            messagebox.showinfo("Sucesso", "Cliente salvo com sucesso!")
            
            if self.on_save:
                self.on_save()
                
            self.window.destroy()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "CNPJ já cadastrado.")
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao salvar cliente: {e}")
        finally:
            conn.close()