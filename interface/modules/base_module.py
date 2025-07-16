import tkinter as tk

class BaseModule:
    def __init__(self, parent, user_id, role):
        self.master = parent
        self.frame = tk.Frame(parent)
        self.user_id = user_id
        self.role = role
        self.is_visible = False  # Atributo adicionado
        self.setup_ui()
    
    def setup_ui(self):
        # Método a ser implementado pelas subclasses
        pass
    
    def show(self):
        if not self.is_visible:
            self.frame.pack(fill="both", expand=True)
            self.is_visible = True
    
    def hide(self):
        if self.is_visible:
            self.frame.pack_forget()
            self.is_visible = False
            
    def on_show(self):
        # Chamado quando o módulo é mostrado
        pass
        
    def on_hide(self):
        # Chamado quando o módulo é escondido
        pass
        
    def refresh(self):
        # Atualizar dados do módulo
        pass