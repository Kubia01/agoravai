"""
Métodos de edição visual para o Editor PDF Avançado
"""
import tkinter as tk
from tkinter import simpledialog, messagebox
import sqlite3


def toggle_edit_mode(self):
    """Ativar/desativar modo de edição visual"""
    try:
        self.edit_mode = not self.edit_mode
        
        if self.edit_mode:
            if hasattr(self, 'fullscreen_status'):
                self.fullscreen_status.config(text="✏️ Modo de edição ATIVADO - Clique nos elementos")
            # Ativar clique no canvas
            if hasattr(self, 'fullscreen_canvas'):
                self.fullscreen_canvas.bind('<Button-1>', self.on_canvas_click_edit)
                self.fullscreen_canvas.bind('<Double-Button-1>', self.on_canvas_double_click_edit)
                # Mostrar áreas editáveis se estiver na capa
                if self.current_page == 1:
                    self.show_editable_areas()
        else:
            if hasattr(self, 'fullscreen_status'):
                self.fullscreen_status.config(text="👁️ Modo de visualização")
            # Desativar clique no canvas
            if hasattr(self, 'fullscreen_canvas'):
                self.fullscreen_canvas.unbind('<Button-1>')
                self.fullscreen_canvas.unbind('<Double-Button-1>')
                self.hide_editable_areas()
                
    except Exception as e:
        print(f"Erro ao alternar modo de edição: {e}")


def edit_element_properties(self, element):
    """Abrir diálogo para editar propriedades do elemento"""
    try:
        element_id = element['id']
        
        # Carregar valor atual do banco
        current_value = self.get_element_current_value(element_id)
        
        if element_id == 'cliente_nome':
            new_value = simpledialog.askstring(
                "Editar Nome do Cliente",
                "Nome do cliente:",
                initialvalue=current_value or "EMPRESA EXEMPLO LTDA"
            )
        elif element_id == 'vendedor_nome':
            new_value = simpledialog.askstring(
                "Editar Nome do Vendedor",
                "Nome do vendedor:",
                initialvalue=current_value or "Vendedor Responsável"
            )
        elif element_id == 'data_cotacao':
            new_value = simpledialog.askstring(
                "Editar Data",
                "Data da cotação (DD/MM/AAAA):",
                initialvalue=current_value or "01/01/2024"
            )
        else:
            new_value = simpledialog.askstring(
                f"Editar {element_id}",
                f"Novo valor para {element_id}:",
                initialvalue=current_value or ""
            )
        
        if new_value:
            self.update_element_value(element_id, new_value)
            if hasattr(self, 'fullscreen_status'):
                self.fullscreen_status.config(text=f"✅ {element_id} atualizado!")
            
    except Exception as e:
        print(f"Erro ao editar propriedades: {e}")


print("✅ Métodos de edição visual carregados!")
