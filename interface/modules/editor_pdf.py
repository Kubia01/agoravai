import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import json
import os
from PIL import Image, ImageTk
from .base_module import BaseModule

class EditorPDFModule(BaseModule):
    def __init__(self, parent, user_id, role, main_window):
        self.user_info = {'role': role, 'user_id': user_id}
        super().__init__(parent, user_id, role, main_window)
        
        self.pdf_layout = self.load_pdf_layout()
        self.background_image = None
        self.overlay_image = None
        self.selected_element = None
        self.canvas_scale = 0.5  # Escala para visualização
        self.page_width = 595  # A4 width in points
        self.page_height = 842  # A4 height in points
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configurar interface do editor de PDF"""
        # Título
        title_frame = tk.Frame(self.frame, bg='white')
        title_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        tk.Label(title_frame, text="Editor de PDF Visual", 
                font=('Arial', 16, 'bold'), bg='white', fg='#1e293b').pack(side="left")
        
        # Frame principal
        main_content = tk.Frame(self.frame, bg='white')
        main_content.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Barra de ferramentas
        self.setup_toolbar(main_content)
        
        # Frame do editor
        editor_frame = tk.Frame(main_content, bg='white')
        editor_frame.pack(fill="both", expand=True, pady=10)
        
        # Painel lateral de propriedades
        self.setup_properties_panel(editor_frame)
        
        # Canvas do editor
        self.setup_canvas(editor_frame)
        
        # Carregar layout inicial
        self.refresh_canvas()
        
    def setup_toolbar(self, parent):
        """Configurar barra de ferramentas"""
        toolbar_frame = tk.Frame(parent, bg='#f8fafc', relief="raised", bd=1)
        toolbar_frame.pack(fill="x", pady=(0, 10))
        
        # Grupo de arquivos
        file_group = tk.LabelFrame(toolbar_frame, text="Arquivo", bg='#f8fafc', font=('Arial', 9))
        file_group.pack(side="left", padx=5, pady=5)
        
        new_btn = self.create_button(file_group, "Novo", self.new_layout, bg='#10b981', width=8)
        new_btn.pack(side="left", padx=2, pady=2)
        
        save_btn = self.create_button(file_group, "Salvar", self.save_layout, bg='#3b82f6', width=8)
        save_btn.pack(side="left", padx=2, pady=2)
        
        load_btn = self.create_button(file_group, "Carregar", self.load_layout_dialog, bg='#f59e0b', width=8)
        load_btn.pack(side="left", padx=2, pady=2)
        
        # Grupo de capas
        capa_group = tk.LabelFrame(toolbar_frame, text="Capas", bg='#f8fafc', font=('Arial', 9))
        capa_group.pack(side="left", padx=5, pady=5)
        
        bg_btn = self.create_button(capa_group, "Fundo", self.add_background, bg='#6366f1', width=8)
        bg_btn.pack(side="left", padx=2, pady=2)
        
        overlay_btn = self.create_button(capa_group, "Sobrepos.", self.add_overlay, bg='#8b5cf6', width=8)
        overlay_btn.pack(side="left", padx=2, pady=2)
        
        # Grupo de elementos
        element_group = tk.LabelFrame(toolbar_frame, text="Elementos", bg='#f8fafc', font=('Arial', 9))
        element_group.pack(side="left", padx=5, pady=5)
        
        text_btn = self.create_button(element_group, "Texto", self.add_text_element, bg='#059669', width=8)
        text_btn.pack(side="left", padx=2, pady=2)
        
        field_btn = self.create_button(element_group, "Campo", self.add_field_element, bg='#dc2626', width=8)
        field_btn.pack(side="left", padx=2, pady=2)
        
        # Grupo de visualização
        view_group = tk.LabelFrame(toolbar_frame, text="Visualização", bg='#f8fafc', font=('Arial', 9))
        view_group.pack(side="left", padx=5, pady=5)
        
        zoom_in_btn = self.create_button(view_group, "Zoom +", self.zoom_in, bg='#64748b', width=8)
        zoom_in_btn.pack(side="left", padx=2, pady=2)
        
        zoom_out_btn = self.create_button(view_group, "Zoom -", self.zoom_out, bg='#64748b', width=8)
        zoom_out_btn.pack(side="left", padx=2, pady=2)
        
        preview_btn = self.create_button(view_group, "Preview", self.preview_pdf, bg='#7c3aed', width=8)
        preview_btn.pack(side="left", padx=2, pady=2)
        
    def setup_properties_panel(self, parent):
        """Configurar painel de propriedades"""
        self.properties_frame = tk.LabelFrame(parent, text="Propriedades", 
                                            font=('Arial', 12, 'bold'), bg='white', fg='#1e293b')
        self.properties_frame.pack(side="right", fill="y", padx=(10, 0))
        
        # Propriedades do elemento selecionado
        self.props_notebook = ttk.Notebook(self.properties_frame)
        self.props_notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Aba de posição
        pos_frame = tk.Frame(self.props_notebook, bg='white')
        self.props_notebook.add(pos_frame, text="Posição")
        
        # X
        tk.Label(pos_frame, text="X:", bg='white', font=('Arial', 10)).pack(anchor="w", padx=5, pady=2)
        self.x_var = tk.StringVar()
        self.x_entry = tk.Entry(pos_frame, textvariable=self.x_var, width=15)
        self.x_entry.pack(fill="x", padx=5, pady=2)
        self.x_entry.bind('<Return>', self.update_element_position)
        
        # Y
        tk.Label(pos_frame, text="Y:", bg='white', font=('Arial', 10)).pack(anchor="w", padx=5, pady=2)
        self.y_var = tk.StringVar()
        self.y_entry = tk.Entry(pos_frame, textvariable=self.y_var, width=15)
        self.y_entry.pack(fill="x", padx=5, pady=2)
        self.y_entry.bind('<Return>', self.update_element_position)
        
        # Largura
        tk.Label(pos_frame, text="Largura:", bg='white', font=('Arial', 10)).pack(anchor="w", padx=5, pady=2)
        self.width_var = tk.StringVar()
        self.width_entry = tk.Entry(pos_frame, textvariable=self.width_var, width=15)
        self.width_entry.pack(fill="x", padx=5, pady=2)
        self.width_entry.bind('<Return>', self.update_element_size)
        
        # Altura
        tk.Label(pos_frame, text="Altura:", bg='white', font=('Arial', 10)).pack(anchor="w", padx=5, pady=2)
        self.height_var = tk.StringVar()
        self.height_entry = tk.Entry(pos_frame, textvariable=self.height_var, width=15)
        self.height_entry.pack(fill="x", padx=5, pady=2)
        self.height_entry.bind('<Return>', self.update_element_size)
        
        # Aba de formato
        format_frame = tk.Frame(self.props_notebook, bg='white')
        self.props_notebook.add(format_frame, text="Formato")
        
        # Fonte
        tk.Label(format_frame, text="Fonte:", bg='white', font=('Arial', 10)).pack(anchor="w", padx=5, pady=2)
        self.font_var = tk.StringVar(value="Arial")
        font_combo = ttk.Combobox(format_frame, textvariable=self.font_var, 
                                 values=["Arial", "Helvetica", "Times", "Courier"], state="readonly")
        font_combo.pack(fill="x", padx=5, pady=2)
        
        # Tamanho da fonte
        tk.Label(format_frame, text="Tamanho:", bg='white', font=('Arial', 10)).pack(anchor="w", padx=5, pady=2)
        self.font_size_var = tk.StringVar(value="12")
        font_size_entry = tk.Entry(format_frame, textvariable=self.font_size_var, width=15)
        font_size_entry.pack(fill="x", padx=5, pady=2)
        
        # Cor
        tk.Label(format_frame, text="Cor:", bg='white', font=('Arial', 10)).pack(anchor="w", padx=5, pady=2)
        self.color_var = tk.StringVar(value="#000000")
        color_entry = tk.Entry(format_frame, textvariable=self.color_var, width=15)
        color_entry.pack(fill="x", padx=5, pady=2)
        
        # Botões de ação
        action_frame = tk.Frame(self.properties_frame, bg='white')
        action_frame.pack(fill="x", padx=10, pady=10)
        
        delete_btn = self.create_button(action_frame, "Excluir", self.delete_element, bg='#ef4444')
        delete_btn.pack(fill="x", pady=2)
        
        duplicate_btn = self.create_button(action_frame, "Duplicar", self.duplicate_element, bg='#6366f1')
        duplicate_btn.pack(fill="x", pady=2)
        
    def setup_canvas(self, parent):
        """Configurar canvas do editor"""
        canvas_frame = tk.Frame(parent, bg='white', relief="sunken", bd=2)
        canvas_frame.pack(side="left", fill="both", expand=True)
        
        # Canvas com scrollbars
        self.canvas = tk.Canvas(canvas_frame, bg='white', 
                               width=int(self.page_width * self.canvas_scale),
                               height=int(self.page_height * self.canvas_scale))
        
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient="horizontal", command=self.canvas.xview)
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        
        self.canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        h_scrollbar.pack(side="bottom", fill="x")
        v_scrollbar.pack(side="right", fill="y")
        
        # Eventos do canvas
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        
        # Configurar scroll region
        self.canvas.configure(scrollregion=(0, 0, 
                                          int(self.page_width * self.canvas_scale),
                                          int(self.page_height * self.canvas_scale)))
        
    def load_pdf_layout(self):
        """Carregar layout do PDF"""
        default_layout = {
            "elements": [
                {
                    "id": "title",
                    "type": "text",
                    "text": "PROPOSTA COMERCIAL",
                    "x": 50,
                    "y": 50,
                    "width": 200,
                    "height": 30,
                    "font": "Arial",
                    "font_size": 16,
                    "color": "#000000",
                    "bold": True
                },
                {
                    "id": "client_name",
                    "type": "field",
                    "field": "cliente.nome",
                    "label": "Cliente:",
                    "x": 50,
                    "y": 100,
                    "width": 300,
                    "height": 20,
                    "font": "Arial",
                    "font_size": 12,
                    "color": "#000000"
                }
            ],
            "background_image": None,
            "overlay_image": None
        }
        
        try:
            layout_file = "data/pdf_layout.json"
            if os.path.exists(layout_file):
                with open(layout_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return default_layout
        except Exception as e:
            print(f"Erro ao carregar layout: {e}")
            return default_layout
            
    def save_layout(self):
        """Salvar layout atual"""
        try:
            os.makedirs("data", exist_ok=True)
            with open("data/pdf_layout.json", 'w', encoding='utf-8') as f:
                json.dump(self.pdf_layout, f, ensure_ascii=False, indent=2)
            self.show_success("Layout salvo com sucesso!")
        except Exception as e:
            self.show_error("Erro", f"Erro ao salvar layout: {str(e)}")
            
    def new_layout(self):
        """Criar novo layout"""
        if messagebox.askyesno("Novo Layout", "Deseja criar um novo layout? O atual será perdido."):
            self.pdf_layout = {
                "elements": [],
                "background_image": None,
                "overlay_image": None
            }
            self.refresh_canvas()
            
    def load_layout_dialog(self):
        """Dialog para carregar layout"""
        file_path = filedialog.askopenfilename(
            title="Carregar Layout",
            filetypes=[("JSON", "*.json"), ("Todos os arquivos", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.pdf_layout = json.load(f)
                self.refresh_canvas()
                self.show_success("Layout carregado com sucesso!")
            except Exception as e:
                self.show_error("Erro", f"Erro ao carregar layout: {str(e)}")
                
    def add_background(self):
        """Adicionar imagem de fundo"""
        file_path = filedialog.askopenfilename(
            title="Selecionar imagem de fundo",
            filetypes=[("Imagens", "*.jpg *.jpeg *.png"), ("Todos os arquivos", "*.*")]
        )
        
        if file_path:
            self.pdf_layout["background_image"] = file_path
            self.refresh_canvas()
            
    def add_overlay(self):
        """Adicionar imagem sobreposta"""
        file_path = filedialog.askopenfilename(
            title="Selecionar imagem sobreposta",
            filetypes=[("Imagens", "*.jpg *.jpeg *.png"), ("Todos os arquivos", "*.*")]
        )
        
        if file_path:
            self.pdf_layout["overlay_image"] = file_path
            self.refresh_canvas()
            
    def add_text_element(self):
        """Adicionar elemento de texto"""
        text = simpledialog.askstring("Texto", "Digite o texto:")
        if text:
            element = {
                "id": f"text_{len(self.pdf_layout['elements']) + 1}",
                "type": "text",
                "text": text,
                "x": 50,
                "y": 50 + len(self.pdf_layout['elements']) * 30,
                "width": 200,
                "height": 20,
                "font": "Arial",
                "font_size": 12,
                "color": "#000000"
            }
            self.pdf_layout["elements"].append(element)
            self.refresh_canvas()
            
    def add_field_element(self):
        """Adicionar campo dinâmico"""
        field_options = [
            "cliente.nome", "cliente.cnpj", "cliente.endereco",
            "proposta.numero", "proposta.data", "proposta.valor_total",
            "usuario.nome", "empresa.nome"
        ]
        
        # Dialog para selecionar campo
        field_window = tk.Toplevel(self.frame)
        field_window.title("Selecionar Campo")
        field_window.geometry("300x400")
        field_window.transient(self.frame)
        
        tk.Label(field_window, text="Selecione o campo:", font=('Arial', 12, 'bold')).pack(pady=10)
        
        listbox = tk.Listbox(field_window, font=('Arial', 10))
        for option in field_options:
            listbox.insert(tk.END, option)
        listbox.pack(fill="both", expand=True, padx=20, pady=10)
        
        def add_selected_field():
            selection = listbox.curselection()
            if selection:
                field = field_options[selection[0]]
                element = {
                    "id": f"field_{len(self.pdf_layout['elements']) + 1}",
                    "type": "field",
                    "field": field,
                    "label": field.replace(".", " ").title() + ":",
                    "x": 50,
                    "y": 50 + len(self.pdf_layout['elements']) * 30,
                    "width": 300,
                    "height": 20,
                    "font": "Arial",
                    "font_size": 12,
                    "color": "#000000"
                }
                self.pdf_layout["elements"].append(element)
                self.refresh_canvas()
                field_window.destroy()
        
        btn_frame = tk.Frame(field_window)
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Button(btn_frame, text="Adicionar", command=add_selected_field, 
                 bg='#10b981', fg='white', font=('Arial', 10, 'bold')).pack(side="right", padx=(5, 0))
        tk.Button(btn_frame, text="Cancelar", command=field_window.destroy, 
                 bg='#ef4444', fg='white', font=('Arial', 10, 'bold')).pack(side="right")
        
    def refresh_canvas(self):
        """Atualizar canvas"""
        self.canvas.delete("all")
        
        # Desenhar imagem de fundo
        if self.pdf_layout.get("background_image") and os.path.exists(self.pdf_layout["background_image"]):
            try:
                img = Image.open(self.pdf_layout["background_image"])
                img = img.resize((int(self.page_width * self.canvas_scale), 
                                int(self.page_height * self.canvas_scale)), Image.Resampling.LANCZOS)
                self.background_image = ImageTk.PhotoImage(img)
                self.canvas.create_image(0, 0, anchor="nw", image=self.background_image)
            except Exception as e:
                print(f"Erro ao carregar imagem de fundo: {e}")
        
        # Desenhar elementos
        for element in self.pdf_layout["elements"]:
            self.draw_element(element)
            
        # Desenhar imagem sobreposta
        if self.pdf_layout.get("overlay_image") and os.path.exists(self.pdf_layout["overlay_image"]):
            try:
                img = Image.open(self.pdf_layout["overlay_image"])
                img = img.resize((int(self.page_width * self.canvas_scale), 
                                int(self.page_height * self.canvas_scale)), Image.Resampling.LANCZOS)
                self.overlay_image = ImageTk.PhotoImage(img)
                self.canvas.create_image(0, 0, anchor="nw", image=self.overlay_image, tags="overlay")
            except Exception as e:
                print(f"Erro ao carregar imagem sobreposta: {e}")
                
    def draw_element(self, element):
        """Desenhar elemento no canvas"""
        x = element["x"] * self.canvas_scale
        y = element["y"] * self.canvas_scale
        width = element["width"] * self.canvas_scale
        height = element["height"] * self.canvas_scale
        
        # Retângulo do elemento
        rect_id = self.canvas.create_rectangle(x, y, x + width, y + height, 
                                             outline="#666", fill="#f0f0f0", tags=element["id"])
        
        # Texto do elemento
        display_text = element.get("text", element.get("label", element.get("field", "Campo")))
        text_id = self.canvas.create_text(x + 5, y + height/2, anchor="w", 
                                        text=display_text, font=("Arial", 8), tags=element["id"])
        
    def on_canvas_click(self, event):
        """Clique no canvas"""
        clicked_item = self.canvas.find_closest(event.x, event.y)[0]
        tags = self.canvas.gettags(clicked_item)
        
        if tags and tags[0] != "current":
            self.select_element(tags[0])
        else:
            self.select_element(None)
            
    def on_canvas_drag(self, event):
        """Arrastar no canvas"""
        if self.selected_element:
            # Calcular nova posição
            new_x = event.x / self.canvas_scale
            new_y = event.y / self.canvas_scale
            
            # Atualizar elemento
            for element in self.pdf_layout["elements"]:
                if element["id"] == self.selected_element:
                    element["x"] = max(0, new_x)
                    element["y"] = max(0, new_y)
                    break
                    
            self.refresh_canvas()
            self.update_properties_panel()
            
    def on_canvas_release(self, event):
        """Soltar no canvas"""
        pass
        
    def select_element(self, element_id):
        """Selecionar elemento"""
        self.selected_element = element_id
        self.update_properties_panel()
        
        # Destacar elemento selecionado
        self.refresh_canvas()
        if element_id:
            items = self.canvas.find_withtag(element_id)
            for item in items:
                if self.canvas.type(item) == "rectangle":
                    self.canvas.itemconfig(item, outline="red", width=2)
                    
    def update_properties_panel(self):
        """Atualizar painel de propriedades"""
        if self.selected_element:
            # Encontrar elemento
            element = None
            for elem in self.pdf_layout["elements"]:
                if elem["id"] == self.selected_element:
                    element = elem
                    break
                    
            if element:
                self.x_var.set(str(element["x"]))
                self.y_var.set(str(element["y"]))
                self.width_var.set(str(element["width"]))
                self.height_var.set(str(element["height"]))
                self.font_var.set(element.get("font", "Arial"))
                self.font_size_var.set(str(element.get("font_size", 12)))
                self.color_var.set(element.get("color", "#000000"))
        else:
            # Limpar campos
            for var in [self.x_var, self.y_var, self.width_var, self.height_var]:
                var.set("")
                
    def update_element_position(self, event=None):
        """Atualizar posição do elemento"""
        if self.selected_element:
            try:
                x = float(self.x_var.get())
                y = float(self.y_var.get())
                
                for element in self.pdf_layout["elements"]:
                    if element["id"] == self.selected_element:
                        element["x"] = x
                        element["y"] = y
                        break
                        
                self.refresh_canvas()
                self.select_element(self.selected_element)
                
            except ValueError:
                self.show_warning("Valor inválido", "Digite valores numéricos válidos.")
                
    def update_element_size(self, event=None):
        """Atualizar tamanho do elemento"""
        if self.selected_element:
            try:
                width = float(self.width_var.get())
                height = float(self.height_var.get())
                
                for element in self.pdf_layout["elements"]:
                    if element["id"] == self.selected_element:
                        element["width"] = width
                        element["height"] = height
                        break
                        
                self.refresh_canvas()
                self.select_element(self.selected_element)
                
            except ValueError:
                self.show_warning("Valor inválido", "Digite valores numéricos válidos.")
                
    def delete_element(self):
        """Excluir elemento selecionado"""
        if self.selected_element:
            if messagebox.askyesno("Confirmar", "Deseja excluir o elemento selecionado?"):
                self.pdf_layout["elements"] = [e for e in self.pdf_layout["elements"] 
                                             if e["id"] != self.selected_element]
                self.selected_element = None
                self.refresh_canvas()
                self.update_properties_panel()
                
    def duplicate_element(self):
        """Duplicar elemento selecionado"""
        if self.selected_element:
            for element in self.pdf_layout["elements"]:
                if element["id"] == self.selected_element:
                    new_element = element.copy()
                    new_element["id"] = f"{element['id']}_copy_{len(self.pdf_layout['elements'])}"
                    new_element["x"] += 20
                    new_element["y"] += 20
                    self.pdf_layout["elements"].append(new_element)
                    self.refresh_canvas()
                    break
                    
    def zoom_in(self):
        """Aumentar zoom"""
        self.canvas_scale = min(2.0, self.canvas_scale * 1.2)
        self.refresh_canvas()
        
    def zoom_out(self):
        """Diminuir zoom"""
        self.canvas_scale = max(0.2, self.canvas_scale / 1.2)
        self.refresh_canvas()
        
    def preview_pdf(self):
        """Visualizar PDF"""
        self.show_info("Preview", "Funcionalidade de preview será implementada em versão futura.")