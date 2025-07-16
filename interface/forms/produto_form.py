import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from database import DB_NAME

class ProdutoForm:
    def __init__(self, parent, produto_id=None):
        self.parent = parent
        self.produto_id = produto_id
        self.on_save = None
        self.kit_itens = []
        self.produtos_disponiveis = []
        
        self.create_window()
        self.setup_ui()
        self.load_produtos_disponiveis()
        
        if produto_id:
            self.load_produto()
            
    def create_window(self):
        self.window = tk.Toplevel(self.parent)
        self.window.title("Produto/Serviço/Kit")
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
                               text="Novo Produto/Serviço/Kit" if not self.produto_id else "Editar Produto/Serviço/Kit",
                               font=('Arial', 16, 'bold'),
                               bg='white',
                               fg='#1e293b')
        title_label.pack(pady=(0, 20))
        
        # Seção: Dados Básicos
        self.create_dados_basicos_section()
        
        # Seção: Composição do Kit (só aparece se for Kit)
        self.create_kit_section()
        
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
        self.tipo_var = tk.StringVar()
        self.tipo_var.set("Produto")
        self.ncm_var = tk.StringVar()
        self.valor_var = tk.StringVar()
        self.valor_var.set("0.00")
        self.descricao_var = tk.StringVar()
        self.ativo_var = tk.BooleanVar()
        self.ativo_var.set(True)
        
        # Grid de campos
        fields_frame = tk.Frame(section_frame, bg='white')
        fields_frame.pack(fill="x")
        
        # Campos
        row = 0
        
        # Nome
        tk.Label(fields_frame, text="Nome *:", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.nome_var, font=('Arial', 10), width=50).grid(row=row, column=1, columnspan=2, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Tipo
        tk.Label(fields_frame, text="Tipo *:", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tipo_combo = ttk.Combobox(fields_frame, textvariable=self.tipo_var, 
                                 values=["Serviço", "Produto", "Kit"], 
                                 width=20, state="readonly")
        tipo_combo.grid(row=row, column=1, sticky="w", padx=(10, 0), pady=5)
        tipo_combo.bind("<<ComboboxSelected>>", self.on_tipo_change)
        row += 1
        
        # NCM
        tk.Label(fields_frame, text="NCM:", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        self.ncm_entry = tk.Entry(fields_frame, textvariable=self.ncm_var, font=('Arial', 10), width=20)
        self.ncm_entry.grid(row=row, column=1, sticky="w", padx=(10, 0), pady=5)
        row += 1
        
        # Valor Unitário
        tk.Label(fields_frame, text="Valor Unitário:", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.valor_var, font=('Arial', 10), width=20).grid(row=row, column=1, sticky="w", padx=(10, 0), pady=5)
        row += 1
        
        # Descrição
        tk.Label(fields_frame, text="Descrição:", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.descricao_var, font=('Arial', 10), width=50).grid(row=row, column=1, columnspan=2, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Ativo
        tk.Checkbutton(fields_frame, text="Ativo", variable=self.ativo_var, 
                       font=('Arial', 10), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        
        # Configurar colunas
        fields_frame.grid_columnconfigure(1, weight=1)
        
    def create_kit_section(self):
        # Frame da seção (inicialmente oculto)
        self.kit_section_frame = tk.LabelFrame(self.scrollable_frame, text="Composição do Kit", 
                                              font=('Arial', 12, 'bold'),
                                              bg='white',
                                              padx=15, pady=15)
        
        # Frame para adicionar item ao kit
        add_frame = tk.Frame(self.kit_section_frame, bg='white')
        add_frame.pack(fill="x", pady=(0, 10))
        
        # Variáveis para novo item do kit
        self.kit_produto_var = tk.StringVar()
        self.kit_quantidade_var = tk.StringVar()
        self.kit_quantidade_var.set("1")
        
        # Grid para adicionar item ao kit
        tk.Label(add_frame, text="Produto/Serviço:", font=('Arial', 10, 'bold'), bg='white').grid(row=0, column=0, sticky="w", padx=5)
        self.kit_produto_combo = ttk.Combobox(add_frame, textvariable=self.kit_produto_var, 
                                             width=40, state="readonly")
        self.kit_produto_combo.grid(row=0, column=1, padx=5)
        
        tk.Label(add_frame, text="Quantidade:", font=('Arial', 10, 'bold'), bg='white').grid(row=0, column=2, sticky="w", padx=5)
        tk.Entry(add_frame, textvariable=self.kit_quantidade_var, font=('Arial', 10), width=10).grid(row=0, column=3, padx=5)
        
        tk.Button(add_frame, text="Adicionar ao Kit",
                  font=('Arial', 10, 'bold'),
                  bg='#10b981',
                  fg='white',
                  relief='flat',
                  cursor='hand2',
                  padx=15,
                  command=self.adicionar_item_kit).grid(row=0, column=4, padx=10)
        
        # Lista de itens do kit
        self.kit_tree = ttk.Treeview(self.kit_section_frame, 
                                    columns=("tipo", "nome", "quantidade", "valor_unit", "valor_total"),
                                    show="headings",
                                    height=6)
        
        # Cabeçalhos
        self.kit_tree.heading("tipo", text="Tipo")
        self.kit_tree.heading("nome", text="Nome")
        self.kit_tree.heading("quantidade", text="Qtd")
        self.kit_tree.heading("valor_unit", text="Valor Unit.")
        self.kit_tree.heading("valor_total", text="Valor Total")
        
        # Larguras
        self.kit_tree.column("tipo", width=80)
        self.kit_tree.column("nome", width=250)
        self.kit_tree.column("quantidade", width=60)
        self.kit_tree.column("valor_unit", width=100)
        self.kit_tree.column("valor_total", width=100)
        
        self.kit_tree.pack(fill="x", pady=(10, 0))
        
        # Botões para itens do kit
        kit_buttons = tk.Frame(self.kit_section_frame, bg='white')
        kit_buttons.pack(fill="x", pady=(10, 0))
        
        tk.Button(kit_buttons, text="Remover Item",
                  font=('Arial', 10),
                  bg='#dc2626',
                  fg='white',
                  relief='flat',
                  cursor='hand2',
                  padx=15,
                  command=self.remover_item_kit).pack(side="left", padx=5)
        
        # Label do total do kit
        self.kit_total_label = tk.Label(kit_buttons, text="Total do Kit: R$ 0,00",
                                       font=('Arial', 12, 'bold'),
                                       bg='white',
                                       fg='#1e293b')
        self.kit_total_label.pack(side="right")
        
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
                             command=self.save_produto)
        save_btn.pack(side="right")
        
    def on_tipo_change(self, event=None):
        tipo = self.tipo_var.get()
        
        if tipo == "Kit":
            self.kit_section_frame.pack(fill="x", pady=(0, 15))
            self.ncm_entry.configure(state='disabled')
            self.ncm_var.set("")
        else:
            self.kit_section_frame.pack_forget()
            self.ncm_entry.configure(state='normal')
            
    def load_produtos_disponiveis(self):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            c.execute("SELECT id, nome, tipo, valor_unitario FROM produtos WHERE ativo = 1 AND tipo != 'Kit' ORDER BY tipo, nome")
            produtos = c.fetchall()
            
            self.produtos_disponiveis = produtos
            produtos_display = [f"{produto[2]} - {produto[1]} (R$ {produto[3]:.2f})" for produto in produtos]
            self.kit_produto_combo['values'] = produtos_display
            
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao carregar produtos: {e}")
        finally:
            conn.close()
            
    def adicionar_item_kit(self):
        if not self.kit_produto_var.get():
            messagebox.showwarning("Aviso", "Selecione um produto/serviço.")
            return
            
        try:
            quantidade = float(self.kit_quantidade_var.get())
        except ValueError:
            messagebox.showerror("Erro", "Quantidade deve ser um número válido.")
            return
            
        # Encontrar o produto selecionado
        selected_index = self.kit_produto_combo.current()
        if selected_index < 0:
            return
            
        produto = self.produtos_disponiveis[selected_index]
        produto_id, nome, tipo, valor_unitario = produto
        
        # Verificar se já foi adicionado
        for item in self.kit_itens:
            if item['produto_id'] == produto_id:
                messagebox.showwarning("Aviso", "Este item já foi adicionado ao kit.")
                return
        
        valor_total = quantidade * valor_unitario
        
        item = {
            'produto_id': produto_id,
            'nome': nome,
            'tipo': tipo,
            'quantidade': quantidade,
            'valor_unitario': valor_unitario,
            'valor_total': valor_total
        }
        
        self.kit_itens.append(item)
        self.atualizar_lista_kit()
        self.calcular_total_kit()
        
        # Limpar campos
        self.kit_produto_var.set("")
        self.kit_quantidade_var.set("1")
        
    def remover_item_kit(self):
        selected = self.kit_tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um item para remover.")
            return
            
        index = self.kit_tree.index(selected[0])
        del self.kit_itens[index]
        self.atualizar_lista_kit()
        self.calcular_total_kit()
        
    def atualizar_lista_kit(self):
        # Limpar lista
        for item in self.kit_tree.get_children():
            self.kit_tree.delete(item)
            
        # Adicionar itens
        for item in self.kit_itens:
            self.kit_tree.insert("", "end", values=(
                item['tipo'],
                item['nome'],
                item['quantidade'],
                f"R$ {item['valor_unitario']:.2f}",
                f"R$ {item['valor_total']:.2f}"
            ))
            
    def calcular_total_kit(self):
        total = sum(item['valor_total'] for item in self.kit_itens)
        self.kit_total_label.config(text=f"Total do Kit: R$ {total:.2f}")
        self.valor_var.set(f"{total:.2f}")
        
    def load_produto(self):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            # Carregar dados do produto
            c.execute("SELECT * FROM produtos WHERE id = ?", (self.produto_id,))
            produto = c.fetchone()
            
            if produto:
                self.nome_var.set(produto[1] or "")
                self.tipo_var.set(produto[2] or "Produto")
                self.ncm_var.set(produto[3] or "")
                self.valor_var.set(f"{produto[4]:.2f}" if produto[4] else "0.00")
                self.descricao_var.set(produto[5] or "")
                self.ativo_var.set(bool(produto[6]))
                
                # Atualizar interface baseado no tipo
                self.on_tipo_change()
                
                # Se for kit, carregar composição
                if produto[2] == "Kit":
                    c.execute("""
                        SELECT p.id, p.nome, p.tipo, p.valor_unitario, kc.quantidade
                        FROM kit_composicao kc
                        JOIN produtos p ON kc.produto_id = p.id
                        WHERE kc.kit_id = ?
                    """, (self.produto_id,))
                    
                    kit_items = c.fetchall()
                    self.kit_itens = []
                    
                    for item in kit_items:
                        produto_id, nome, tipo, valor_unitario, quantidade = item
                        self.kit_itens.append({
                            'produto_id': produto_id,
                            'nome': nome,
                            'tipo': tipo,
                            'quantidade': quantidade,
                            'valor_unitario': valor_unitario,
                            'valor_total': quantidade * valor_unitario
                        })
                    
                    self.atualizar_lista_kit()
                    self.calcular_total_kit()
                
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao carregar produto: {e}")
        finally:
            conn.close()
            
    def save_produto(self):
        # Validar campos obrigatórios
        if not self.nome_var.get():
            messagebox.showwarning("Aviso", "Nome é obrigatório.")
            return
            
        try:
            valor_unitario = float(self.valor_var.get().replace(',', '.'))
        except ValueError:
            messagebox.showerror("Erro", "Valor unitário deve ser um número válido.")
            return
            
        # Se for kit, deve ter pelo menos um item
        if self.tipo_var.get() == "Kit" and not self.kit_itens:
            messagebox.showwarning("Aviso", "Kit deve ter pelo menos um item.")
            return
            
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            if self.produto_id:
                # Atualizar produto
                c.execute("""
                    UPDATE produtos SET
                        nome=?, tipo=?, ncm=?, valor_unitario=?, descricao=?, ativo=?,
                        updated_at=CURRENT_TIMESTAMP
                    WHERE id=?
                """, (
                    self.nome_var.get(), self.tipo_var.get(), self.ncm_var.get(),
                    valor_unitario, self.descricao_var.get(), self.ativo_var.get(),
                    self.produto_id
                ))
                
                # Se for kit, remover composição antiga e inserir nova
                if self.tipo_var.get() == "Kit":
                    c.execute("DELETE FROM kit_composicao WHERE kit_id=?", (self.produto_id,))
                    for item in self.kit_itens:
                        c.execute("""
                            INSERT INTO kit_composicao (kit_id, produto_id, quantidade)
                            VALUES (?, ?, ?)
                        """, (self.produto_id, item['produto_id'], item['quantidade']))
                
                produto_id = self.produto_id
            else:
                # Inserir novo produto
                c.execute("""
                    INSERT INTO produtos (nome, tipo, ncm, valor_unitario, descricao, ativo)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    self.nome_var.get(), self.tipo_var.get(), self.ncm_var.get(),
                    valor_unitario, self.descricao_var.get(), self.ativo_var.get()
                ))
                produto_id = c.lastrowid
                
                # Se for kit, inserir composição
                if self.tipo_var.get() == "Kit":
                    for item in self.kit_itens:
                        c.execute("""
                            INSERT INTO kit_composicao (kit_id, produto_id, quantidade)
                            VALUES (?, ?, ?)
                        """, (produto_id, item['produto_id'], item['quantidade']))
            
            conn.commit()
            messagebox.showinfo("Sucesso", "Produto salvo com sucesso!")
            
            if self.on_save:
                self.on_save()
            else:
                if hasattr(self.master.master, "notify_listeners"):
                    self.master.master.notify_listeners("produtos_updated")
                
            self.window.destroy()
            
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao salvar produto: {e}")
        finally:
            conn.close()