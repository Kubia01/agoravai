"""
Template personalizado de capa para Valdir
"""

try:
    from .base_capa import CapaBase
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from base_capa import CapaBase

class CapaValdir(CapaBase):
    def _adicionar_assinatura(self):
        """Assinatura personalizada do Valdir"""
        self.pdf.set_y(250)
        
        # Mensagem personalizada
        self.pdf.set_font("Arial", 'I', 11)
        self.pdf.set_text_color(80, 80, 80)
        self.pdf.cell(0, 6, "Atendimento especializado em compressores", 0, 1, 'C')
        self.pdf.ln(5)
        
        # Assinatura
        self.pdf.set_font("Arial", 'B', 14)
        self.pdf.set_text_color(*self.dark_blue)
        self.pdf.cell(0, 8, "VALDIR", 0, 1, 'C')
        
        self.pdf.set_font("Arial", '', 12)
        self.pdf.set_text_color(0, 0, 0)
        self.pdf.cell(0, 6, "Consultor Técnico Comercial", 0, 1, 'C')
        self.pdf.cell(0, 5, "World Comp Compressores", 0, 1, 'C')
        
    def _adicionar_titulo_principal(self):
        """Título personalizado para Valdir"""
        self.pdf.set_y(80)
        self.pdf.set_font("Arial", 'B', 24)
        self.pdf.set_text_color(*self.dark_blue)
        self.pdf.cell(0, 15, "PROPOSTA TÉCNICA COMERCIAL", 0, 1, 'C')
        
        self.pdf.set_font("Arial", 'B', 16)
        self.pdf.cell(0, 10, f"Nº {self.dados_cotacao.get('numero_proposta', '')}", 0, 1, 'C')
        
        # Subtítulo personalizado
        self.pdf.set_font("Arial", 'I', 12)
        self.pdf.set_text_color(100, 100, 100)
        self.pdf.cell(0, 8, "Soluções Profissionais em Ar Comprimido", 0, 1, 'C')