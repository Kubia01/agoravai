import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import shutil
from .base_module import BaseModule

class CorrecoesModule(BaseModule):
    def __init__(self, parent, user_id, role, main_window):
        self.user_info = {'role': role, 'user_id': user_id}
        
        # Configurar conexão com banco ANTES de chamar super().__init__
        from database import DB_NAME
        import sqlite3
        self.db_name = DB_NAME
        
        # Verificar se o usuário é administrador ANTES de criar a UI
        if self.user_info.get('role') != 'admin':
            # Criar um frame vazio com mensagem de erro
            self.frame = tk.Frame(parent, bg='#f8fafc')
            self.frame.pack(fill="both", expand=True)
            
            error_frame = tk.Frame(self.frame, bg='white')
            error_frame.pack(expand=True, fill="both", padx=50, pady=50)
            
            tk.Label(error_frame, text="🚫 Acesso Negado", 
                    font=('Arial', 18, 'bold'), bg='white', fg='#ef4444').pack(pady=20)
            tk.Label(error_frame, text="Esta funcionalidade é exclusiva para administradores.", 
                    font=('Arial', 12), bg='white', fg='#64748b').pack()
            return
        
        super().__init__(parent, user_id, role, main_window)
        
    def setup_ui(self):
        """Configurar interface do módulo de correções"""
        # Título
        title_frame = tk.Frame(self.frame, bg='white')
        title_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        tk.Label(title_frame, text="Correções e Alterações", 
                font=('Arial', 16, 'bold'), bg='white', fg='#1e293b').pack(side="left")
                
        # Notebook para organizar as funcionalidades
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Aba 1: Configurações de Texto do PDF
        self.setup_pdf_text_tab()
        
        # Aba 2: Gerenciamento de Templates
        self.setup_templates_tab()
        
        # Aba 3: Upload de Novos Templates
        self.setup_upload_tab()
        
    def setup_pdf_text_tab(self):
        """Configurar aba de configurações de texto do PDF"""
        pdf_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(pdf_frame, text="Textos do PDF")
        
        # Frame principal com scroll
        canvas = tk.Canvas(pdf_frame, bg='white')
        scrollbar = ttk.Scrollbar(pdf_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configurações de texto
        self.create_text_config_section(scrollable_frame, "Cabeçalho", "header")
        self.create_text_config_section(scrollable_frame, "Corpo do PDF", "body")
        self.create_text_config_section(scrollable_frame, "Rodapé", "footer")
        self.create_text_config_section(scrollable_frame, "Observações", "observations")
        
        # Botões de ação
        buttons_frame = tk.Frame(scrollable_frame, bg='white')
        buttons_frame.pack(fill="x", padx=20, pady=20)
        
        save_btn = self.create_button(buttons_frame, "Salvar Alterações", 
                                     self.save_pdf_texts, bg='#10b981')
        save_btn.pack(side="left", padx=(0, 10))
        
        reset_btn = self.create_button(buttons_frame, "Restaurar Padrão", 
                                      self.reset_pdf_texts, bg='#f59e0b')
        reset_btn.pack(side="left")
        
    def create_text_config_section(self, parent, title, key):
        """Criar seção de configuração de texto"""
        section_frame = tk.LabelFrame(parent, text=title, font=('Arial', 12, 'bold'), 
                                     bg='white', fg='#1e293b', pady=10)
        section_frame.pack(fill="x", padx=20, pady=10)
        
        # Text widget para edição
        text_widget = tk.Text(section_frame, height=6, width=80, font=('Arial', 10))
        text_widget.pack(padx=10, pady=5, fill="x")
        
        # Carregar texto atual
        current_text = self.load_pdf_text_config(key)
        text_widget.insert("1.0", current_text)
        
        # Armazenar referência
        setattr(self, f"text_{key}", text_widget)
        
    def setup_templates_tab(self):
        """Configurar aba de gerenciamento de templates"""
        templates_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(templates_frame, text="Gerenciar Templates")
        
        # Lista de usuários com templates
        list_frame = tk.LabelFrame(templates_frame, text="Usuários com Templates Personalizados", 
                                  font=('Arial', 12, 'bold'), bg='white', fg='#1e293b')
        list_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Treeview para mostrar usuários
        columns = ('Usuario', 'Nome Completo', 'Template', 'Status')
        self.templates_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.templates_tree.heading(col, text=col)
            self.templates_tree.column(col, width=150)
            
        self.templates_tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Botões de ação
        buttons_frame = tk.Frame(list_frame, bg='white')
        buttons_frame.pack(fill="x", padx=10, pady=5)
        
        refresh_btn = self.create_button(buttons_frame, "Atualizar Lista", 
                                        self.refresh_templates_list, bg='#3b82f6')
        refresh_btn.pack(side="left", padx=(0, 10))
        
        edit_btn = self.create_button(buttons_frame, "Editar Template", 
                                     self.edit_template, bg='#f59e0b')
        edit_btn.pack(side="left", padx=(0, 10))
        
        delete_btn = self.create_button(buttons_frame, "Remover Template", 
                                       self.delete_template, bg='#ef4444')
        delete_btn.pack(side="left")
        
        # Carregar lista inicial
        self.refresh_templates_list()
        
    def setup_upload_tab(self):
        """Configurar aba de upload de novos templates"""
        upload_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(upload_frame, text="Upload Templates")
        
        # Instruções
        instructions_frame = tk.LabelFrame(upload_frame, text="Instruções", 
                                         font=('Arial', 12, 'bold'), bg='white', fg='#1e293b')
        instructions_frame.pack(fill="x", padx=20, pady=20)
        
        instructions_text = """
        1. Selecione um usuário para adicionar um template personalizado
        2. Escolha o arquivo de imagem (JPG, PNG) para a capa
        3. O sistema irá redimensionar automaticamente a imagem
        4. Templates são aplicados automaticamente na geração de PDFs
        """
        
        tk.Label(instructions_frame, text=instructions_text, font=('Arial', 10), 
                bg='white', fg='#64748b', justify="left").pack(padx=10, pady=10)
        
        # Formulário de upload
        form_frame = tk.LabelFrame(upload_frame, text="Novo Template", 
                                  font=('Arial', 12, 'bold'), bg='white', fg='#1e293b')
        form_frame.pack(fill="x", padx=20, pady=10)
        
        # Seleção de usuário
        user_frame = tk.Frame(form_frame, bg='white')
        user_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(user_frame, text="Usuário:", font=('Arial', 10, 'bold'), 
                bg='white').pack(side="left")
        
        self.user_var = tk.StringVar()
        self.user_combo = ttk.Combobox(user_frame, textvariable=self.user_var, 
                                      values=self.get_all_users(), width=30, state="readonly")
        self.user_combo.pack(side="left", padx=(10, 0))
        
        # Seleção de arquivo
        file_frame = tk.Frame(form_frame, bg='white')
        file_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(file_frame, text="Arquivo:", font=('Arial', 10, 'bold'), 
                bg='white').pack(side="left")
        
        self.file_path_var = tk.StringVar()
        self.file_entry = tk.Entry(file_frame, textvariable=self.file_path_var, 
                                  width=40, state="readonly")
        self.file_entry.pack(side="left", padx=(10, 5))
        
        browse_btn = self.create_button(file_frame, "Procurar", 
                                       self.browse_template_file, bg='#64748b')
        browse_btn.pack(side="left")
        
        # Botões de ação
        action_frame = tk.Frame(form_frame, bg='white')
        action_frame.pack(fill="x", padx=10, pady=20)
        
        upload_btn = self.create_button(action_frame, "Fazer Upload", 
                                       self.upload_template, bg='#10b981')
        upload_btn.pack(side="left", padx=(0, 10))
        
        clear_btn = self.create_button(action_frame, "Limpar", 
                                      self.clear_upload_form, bg='#f59e0b')
        clear_btn.pack(side="left")
        
    def load_pdf_text_config(self, key):
        """Carregar configuração de texto do PDF"""
        config_file = "data/pdf_texts.json"
        
        default_texts = {
            "header": "PROPOSTA COMERCIAL\nCompressores de Ar",
            "body": "Prezados Senhores,\n\nSegue nossa proposta comercial conforme solicitado:",
            "footer": "Atenciosamente,\nEquipe Comercial",
            "observations": "- Valores válidos por 30 dias\n- Entrega em até 15 dias úteis\n- Garantia de 12 meses"
        }
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                return config.get(key, default_texts.get(key, ""))
            else:
                return default_texts.get(key, "")
        except Exception as e:
            print(f"Erro ao carregar configuração: {e}")
            return default_texts.get(key, "")
            
    def save_pdf_texts(self):
        """Salvar configurações de texto do PDF"""
        try:
            config = {}
            for key in ["header", "body", "footer", "observations"]:
                text_widget = getattr(self, f"text_{key}")
                config[key] = text_widget.get("1.0", tk.END).strip()
            
            os.makedirs("data", exist_ok=True)
            with open("data/pdf_texts.json", 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
                
            self.show_success("Configurações salvas com sucesso!")
            
        except Exception as e:
            self.show_error("Erro", f"Erro ao salvar configurações: {str(e)}")
            
    def reset_pdf_texts(self):
        """Restaurar textos padrão"""
        if messagebox.askyesno("Confirmar", "Deseja restaurar os textos padrão? Esta ação não pode ser desfeita."):
            try:
                if os.path.exists("data/pdf_texts.json"):
                    os.remove("data/pdf_texts.json")
                
                # Recarregar textos padrão
                for key in ["header", "body", "footer", "observations"]:
                    text_widget = getattr(self, f"text_{key}")
                    text_widget.delete("1.0", tk.END)
                    text_widget.insert("1.0", self.load_pdf_text_config(key))
                
                self.show_success("Textos restaurados para o padrão!")
                
            except Exception as e:
                self.show_error("Erro", f"Erro ao restaurar textos: {str(e)}")
                
    def refresh_templates_list(self):
        """Atualizar lista de templates"""
        # Limpar árvore
        for item in self.templates_tree.get_children():
            self.templates_tree.delete(item)
            
        # Carregar usuários com templates
        from assets.filiais.filiais_config import USUARIOS_COTACAO
        
        for username, config in USUARIOS_COTACAO.items():
            template_path = config.get('template_capa_jpeg', '')
            status = "✓ Ativo" if os.path.exists(template_path) else "✗ Arquivo não encontrado"
            
            self.templates_tree.insert('', 'end', values=(
                username.title(),
                config.get('nome_completo', username),
                os.path.basename(template_path) if template_path else "Não definido",
                status
            ))
            
    def edit_template(self):
        """Editar template selecionado"""
        selection = self.templates_tree.selection()
        if not selection:
            self.show_warning("Seleção", "Selecione um usuário para editar o template.")
            return
            
        item = self.templates_tree.item(selection[0])
        username = item['values'][0].lower()
        
        # Abrir dialog para selecionar novo arquivo
        file_path = filedialog.askopenfilename(
            title="Selecionar novo template",
            filetypes=[("Imagens", "*.jpg *.jpeg *.png"), ("Todos os arquivos", "*.*")]
        )
        
        if file_path:
            try:
                # Copiar arquivo para pasta de templates
                template_dir = "assets/templates/capas"
                os.makedirs(template_dir, exist_ok=True)
                
                # Nome do arquivo de destino
                _, ext = os.path.splitext(file_path)
                dest_file = os.path.join(template_dir, f"capa_{username}{ext}")
                
                # Copiar arquivo
                shutil.copy2(file_path, dest_file)
                
                self.show_success(f"Template do usuário {username} atualizado com sucesso!")
                self.refresh_templates_list()
                
            except Exception as e:
                self.show_error("Erro", f"Erro ao atualizar template: {str(e)}")
                
    def delete_template(self):
        """Remover template selecionado"""
        selection = self.templates_tree.selection()
        if not selection:
            self.show_warning("Seleção", "Selecione um usuário para remover o template.")
            return
            
        item = self.templates_tree.item(selection[0])
        username = item['values'][0].lower()
        
        if messagebox.askyesno("Confirmar", f"Deseja remover o template do usuário {username}?"):
            try:
                from assets.filiais.filiais_config import USUARIOS_COTACAO
                
                if username in USUARIOS_COTACAO:
                    template_path = USUARIOS_COTACAO[username].get('template_capa_jpeg', '')
                    if template_path and os.path.exists(template_path):
                        os.remove(template_path)
                        
                self.show_success(f"Template do usuário {username} removido com sucesso!")
                self.refresh_templates_list()
                
            except Exception as e:
                self.show_error("Erro", f"Erro ao remover template: {str(e)}")
                
    def get_all_users(self):
        """Obter lista de todos os usuários"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT username FROM usuarios ORDER BY username")
            users = [row[0] for row in cursor.fetchall()]
            conn.close()
            return users
        except Exception as e:
            print(f"Erro ao buscar usuários: {e}")
            return []
            
    def browse_template_file(self):
        """Procurar arquivo de template"""
        file_path = filedialog.askopenfilename(
            title="Selecionar template",
            filetypes=[("Imagens", "*.jpg *.jpeg *.png"), ("Todos os arquivos", "*.*")]
        )
        
        if file_path:
            self.file_path_var.set(file_path)
            
    def upload_template(self):
        """Fazer upload de novo template"""
        username = self.user_var.get()
        file_path = self.file_path_var.get()
        
        if not username:
            self.show_warning("Validação", "Selecione um usuário.")
            return
            
        if not file_path:
            self.show_warning("Validação", "Selecione um arquivo.")
            return
            
        try:
            # Criar diretório se não existir
            template_dir = "assets/templates/capas"
            os.makedirs(template_dir, exist_ok=True)
            
            # Nome do arquivo de destino
            _, ext = os.path.splitext(file_path)
            dest_file = os.path.join(template_dir, f"capa_{username.lower()}{ext}")
            
            # Copiar arquivo
            shutil.copy2(file_path, dest_file)
            
            self.show_success(f"Template para o usuário {username} carregado com sucesso!")
            self.clear_upload_form()
            self.refresh_templates_list()
            
        except Exception as e:
            self.show_error("Erro", f"Erro ao fazer upload: {str(e)}")
            
    def clear_upload_form(self):
        """Limpar formulário de upload"""
        self.user_var.set("")
        self.file_path_var.set("")