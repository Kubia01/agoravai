"""
Template base para capas personalizadas das cotações
"""

from fpdf import FPDF
import os

class CapaBase:
    def __init__(self, pdf, dados_cotacao, dados_filial, dados_usuario):
        self.pdf = pdf
        self.dados_cotacao = dados_cotacao
        self.dados_filial = dados_filial
        self.dados_usuario = dados_usuario
        
    def criar_capa(self):
        """Método base para criar a capa - deve ser sobrescrito pelas classes filhas"""
        self.pdf.add_page()
        
        # Configurar cores personalizadas
        self.baby_blue = (137, 207, 240)  # Azul bebê #89CFF0
        self.dark_blue = (50, 100, 150)   # Azul escuro
        
        # Logo da empresa centralizado no topo
        self._adicionar_logo()
        
        # Título principal
        self._adicionar_titulo_principal()
        
        # Informações da cotação
        self._adicionar_info_cotacao()
        
        # Cliente
        self._adicionar_info_cliente()
        
        # Dados da filial
        self._adicionar_info_filial()
        
        # Assinatura personalizada do usuário
        self._adicionar_assinatura()
        
    def _adicionar_logo(self):
        """Adiciona o logo da empresa centralizado"""
        logo_path = self.dados_filial.get("logo_path", "assets/logos/world_comp_brasil.jpg")
        if os.path.exists(logo_path):
            logo_height = 40
            logo_width = logo_height * 1.5
            self.pdf.image(logo_path, x=(210 - logo_width) / 2, y=20, w=logo_width)
            
    def _adicionar_titulo_principal(self):
        """Adiciona o título principal da capa"""
        self.pdf.set_y(80)
        self.pdf.set_font("Arial", 'B', 24)
        self.pdf.set_text_color(*self.dark_blue)
        self.pdf.cell(0, 15, "PROPOSTA COMERCIAL", 0, 1, 'C')
        
        self.pdf.set_font("Arial", 'B', 16)
        self.pdf.cell(0, 10, f"Nº {self.dados_cotacao.get('numero_proposta', '')}", 0, 1, 'C')
        
    def _adicionar_info_cotacao(self):
        """Adiciona informações básicas da cotação"""
        self.pdf.set_y(120)
        self.pdf.set_font("Arial", 'B', 14)
        self.pdf.set_text_color(0, 0, 0)
        
        # Data
        self.pdf.cell(0, 8, f"Data: {self.dados_cotacao.get('data_criacao', '')}", 0, 1, 'C')
        
        # Modelo do compressor se houver
        if self.dados_cotacao.get('modelo_compressor'):
            self.pdf.cell(0, 8, f"Equipamento: {self.dados_cotacao.get('modelo_compressor', '')}", 0, 1, 'C')
            
    def _adicionar_info_cliente(self):
        """Adiciona informações do cliente"""
        self.pdf.set_y(150)
        self.pdf.set_font("Arial", 'B', 12)
        self.pdf.set_text_color(*self.dark_blue)
        self.pdf.cell(0, 8, "APRESENTADO PARA:", 0, 1, 'C')
        
        self.pdf.set_font("Arial", 'B', 14)
        self.pdf.set_text_color(0, 0, 0)
        
        cliente_nome = self.dados_cotacao.get('cliente_nome_fantasia') or self.dados_cotacao.get('cliente_nome', '')
        self.pdf.cell(0, 8, cliente_nome, 0, 1, 'C')
        
        if self.dados_cotacao.get('cliente_cnpj'):
            self.pdf.set_font("Arial", '', 12)
            self.pdf.cell(0, 6, f"CNPJ: {self.dados_cotacao.get('cliente_cnpj', '')}", 0, 1, 'C')
            
    def _adicionar_info_filial(self):
        """Adiciona informações da filial"""
        self.pdf.set_y(190)
        self.pdf.set_font("Arial", 'B', 12)
        self.pdf.set_text_color(*self.dark_blue)
        self.pdf.cell(0, 8, "APRESENTADO POR:", 0, 1, 'C')
        
        self.pdf.set_font("Arial", 'B', 12)
        self.pdf.set_text_color(0, 0, 0)
        self.pdf.cell(0, 6, self.dados_filial.get('nome', ''), 0, 1, 'C')
        
        self.pdf.set_font("Arial", '', 10)
        self.pdf.cell(0, 5, f"CNPJ: {self.dados_filial.get('cnpj', '')}", 0, 1, 'C')
        self.pdf.cell(0, 5, self.dados_filial.get('endereco', ''), 0, 1, 'C')
        self.pdf.cell(0, 5, f"CEP: {self.dados_filial.get('cep', '')}", 0, 1, 'C')
        self.pdf.cell(0, 5, f"Telefones: {self.dados_filial.get('telefones', '')}", 0, 1, 'C')
        self.pdf.cell(0, 5, f"E-mail: {self.dados_filial.get('email', '')}", 0, 1, 'C')
        
    def _adicionar_assinatura(self):
        """Adiciona a assinatura personalizada do usuário - método a ser sobrescrito"""
        self.pdf.set_y(250)
        self.pdf.set_font("Arial", 'B', 12)
        self.pdf.set_text_color(*self.dark_blue)
        
        assinatura_linhas = self.dados_usuario.get('assinatura', '').split('\n')
        for linha in assinatura_linhas:
            self.pdf.cell(0, 6, linha, 0, 1, 'C')