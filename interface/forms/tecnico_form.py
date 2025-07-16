import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from database import DB_NAME

class TecnicoForm:
    def __init__(self, parent, tecnico_id=None):
        self.parent = parent
        self.tecnico_id = tecnico_id
        self.on_save = None
        
        self.create_window()
        self.setup_ui()
        
        if tecnico_id:
            self.load_tecnico()
            
    def create_window(self):
        self.window = tk.Toplevel(self.parent)
        self.window.title("Técnico")
        self.window.geometry("500x400")
        self.window.transient(self.parent)
        self.window.grab_set()
        self.window.configure(bg='white')
        
        # Centralizar
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (250)
        y = (self.window.winfo_screenheight() // 2) - (200)
        self.window.geometry(f"500x400+{x}+{y}")
        
    def setup_ui(self):
        # Frame principal
        main_frame = tk.Frame(self.window, bg='white', padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Título
        title_label = tk.Label(main_frame, 
                               text="Novo Técnico" if not self.tecnico_id else "Editar Técnico",
                               font=('Arial', 16, 'bold'),
                               bg='white',
                               fg='#1e293b')
        title_label.pack(pady=(0, 20))
        
        # Campos
        self.create_fields(main_frame)
        
        # Botões
        self.create_buttons(main_frame)
        
    def create_fields(self, parent):
        # Frame dos campos
        fields_frame = tk.Frame(parent, bg='white')
        fields_frame.pack(fill="both", expand=True)
        
        # Variáveis
        self.nome_var = tk.StringVar()
        self.especialidade_var = tk.StringVar()
        self.telefone_var = tk.StringVar()
        self.email_var = tk.StringVar()
        
        # Campos
        row = 0
        
        # Nome
        tk.Label(fields_frame, text="Nome *:", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.nome_var, font=('Arial', 10), width=40).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Especialidade
        tk.Label(fields_frame, text="Especialidade:", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.especialidade_var, font=('Arial', 10), width=40).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Telefone
        tk.Label(fields_frame, text="Telefone:", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.telefone_var, font=('Arial', 10), width=40).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Email
        tk.Label(fields_frame, text="Email:", font=('Arial', 10, 'bold'), bg='white').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(fields_frame, textvariable=self.email_var, font=('Arial', 10), width=40).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Configurar colunas
        fields_frame.grid_columnconfigure(1, weight=1)
        
    def create_buttons(self, parent):
        # Frame dos botões
        buttons_frame = tk.Frame(parent, bg='white')
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
                             command=self.save_tecnico)
        save_btn.pack(side="right")
        
    def load_tecnico(self):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            c.execute("SELECT * FROM tecnicos WHERE id = ?", (self.tecnico_id,))
            tecnico = c.fetchone()
            
            if tecnico:
                self.nome_var.set(tecnico[1] or "")
                self.especialidade_var.set(tecnico[2] or "")
                self.telefone_var.set(tecnico[3] or "")
                self.email_var.set(tecnico[4] or "")
                
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao carregar técnico: {e}")
        finally:
            conn.close()
            
    def save_tecnico(self):
        # Validar campos obrigatórios
        if not self.nome_var.get():
            messagebox.showwarning("Aviso", "Nome é obrigatório.")
            return
            
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        try:
            if self.tecnico_id:
                # Atualizar
                c.execute("""
                    UPDATE tecnicos SET
                        nome=?, especialidade=?, telefone=?, email=?
                    WHERE id=?
                """, (
                    self.nome_var.get(), self.especialidade_var.get(),
                    self.telefone_var.get(), self.email_var.get(), self.tecnico_id
                ))
            else:
                # Inserir
                c.execute("""
                    INSERT INTO tecnicos (nome, especialidade, telefone, email)
                    VALUES (?, ?, ?, ?)
                """, (
                    self.nome_var.get(), self.especialidade_var.get(),
                    self.telefone_var.get(), self.email_var.get()
                ))
            
            conn.commit()
            messagebox.showinfo("Sucesso", "Técnico salvo com sucesso!")
            
            if self.on_save:
                self.on_save()
                
            self.window.destroy()
            
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao salvar técnico: {e}")
        finally:
            conn.close()