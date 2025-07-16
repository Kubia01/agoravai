import sqlite3
import os
from fpdf import FPDF
from datetime import datetime
from utils.formatters import format_currency, format_date, format_cnpj

class CotacaoPDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_auto_page_break(auto=True, margin=15)
    
    def header(self):
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "PROPOSTA COMERCIAL", 0, 1, "C")
        self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Página {self.page_no()}", 0, 0, "C")
    
    def add_section_title(self, title):
        """Adicionar título de seção"""
        self.set_font("Arial", "B", 12)
        self.ln(5)
        self.cell(0, 8, title, 0, 1, "L")
        self.ln(2)
    
    def add_field(self, label, value, width=None):
        """Adicionar campo com label e valor"""
        self.set_font("Arial", "B", 10)
        label_width = width if width else len(label) * 2 + 10
        self.cell(label_width, 6, label, 0, 0, "L")
        
        self.set_font("Arial", "", 10)
        self.cell(0, 6, str(value) if value else "", 0, 1, "L")

def gerar_pdf_cotacao(cotacao_id, db_name):
    """Gerar PDF da cotação"""
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    
    try:
        # Buscar dados da cotação
        c.execute("""
            SELECT c.*, cl.nome as cliente_nome, cl.cnpj, cl.endereco, cl.cidade, cl.estado,
                   u.nome_completo as responsavel_nome
            FROM cotacoes c
            JOIN clientes cl ON c.cliente_id = cl.id
            JOIN usuarios u ON c.responsavel_id = u.id
            WHERE c.id = ?
        """, (cotacao_id,))
        
        cotacao = c.fetchone()
        if not cotacao:
            return False, "Cotação não encontrada"
        
        # Buscar itens da cotação
        c.execute("""
            SELECT tipo, item_nome, quantidade, valor_unitario, valor_total_item, 
                   descricao, mao_obra, deslocamento, estadia
            FROM itens_cotacao
            WHERE cotacao_id = ?
            ORDER BY id
        """, (cotacao_id,))
        itens = c.fetchall()
        
        # Criar PDF
        pdf = CotacaoPDF()
        pdf.add_page()
        
        # Cabeçalho da cotação
        pdf.add_section_title("DADOS DA PROPOSTA")
        pdf.add_field("Número da Proposta:", cotacao[1])  # numero_proposta
        pdf.add_field("Data de Criação:", format_date(cotacao[4]))
        pdf.add_field("Data de Validade:", format_date(cotacao[5]))
        pdf.add_field("Responsável:", cotacao[20])  # responsavel_nome
        
        # Dados do cliente
        pdf.add_section_title("DADOS DO CLIENTE")
        pdf.add_field("Cliente:", cotacao[17])  # cliente_nome
        pdf.add_field("CNPJ:", format_cnpj(cotacao[18]))
        pdf.add_field("Endereço:", f"{cotacao[19]} - {cotacao[20]}/{cotacao[21]}")
        
        # Dados do equipamento
        if cotacao[6] or cotacao[7]:  # modelo_compressor, numero_serie_compressor
            pdf.add_section_title("DADOS DO EQUIPAMENTO")
            if cotacao[6]:
                pdf.add_field("Modelo do Compressor:", cotacao[6])
            if cotacao[7]:
                pdf.add_field("Número de Série:", cotacao[7])
        
        # Descrição da atividade
        if cotacao[8]:  # descricao_atividade
            pdf.add_section_title("DESCRIÇÃO DA ATIVIDADE")
            pdf.set_font("Arial", "", 10)
            pdf.multi_cell(0, 5, cotacao[8])
            pdf.ln(2)
        
        # Itens da cotação
        if itens:
            pdf.add_section_title("ITENS DA PROPOSTA")
            
            # Cabeçalho da tabela
            pdf.set_font("Arial", "B", 9)
            pdf.cell(20, 8, "Tipo", 1, 0, "C")
            pdf.cell(50, 8, "Item", 1, 0, "C")
            pdf.cell(15, 8, "Qtd", 1, 0, "C")
            pdf.cell(25, 8, "Valor Unit.", 1, 0, "C")
            pdf.cell(25, 8, "Mão Obra", 1, 0, "C")
            pdf.cell(25, 8, "Desloc.", 1, 0, "C")
            pdf.cell(20, 8, "Estadia", 1, 0, "C")
            pdf.cell(25, 8, "Total", 1, 1, "C")
            
            # Itens
            pdf.set_font("Arial", "", 8)
            total_geral = 0
            
            for item in itens:
                tipo, nome, qtd, valor_unit, total_item, desc, mao_obra, desloc, estadia = item
                
                pdf.cell(20, 6, tipo, 1, 0, "C")
                pdf.cell(50, 6, nome[:20] + "..." if len(nome) > 20 else nome, 1, 0, "L")
                pdf.cell(15, 6, str(int(qtd)), 1, 0, "C")
                pdf.cell(25, 6, format_currency(valor_unit), 1, 0, "R")
                pdf.cell(25, 6, format_currency(mao_obra), 1, 0, "R")
                pdf.cell(25, 6, format_currency(desloc), 1, 0, "R")
                pdf.cell(20, 6, format_currency(estadia), 1, 0, "R")
                pdf.cell(25, 6, format_currency(total_item), 1, 1, "R")
                
                total_geral += total_item
                
                # Descrição (se houver)
                if desc and desc.strip():
                    pdf.cell(10, 4, "", 0, 0)  # Indent
                    pdf.set_font("Arial", "I", 7)
                    pdf.multi_cell(180, 3, f"Descrição: {desc}")
                    pdf.set_font("Arial", "", 8)
            
            # Total geral
            pdf.set_font("Arial", "B", 10)
            pdf.cell(185, 8, "TOTAL GERAL:", 1, 0, "R")
            pdf.cell(25, 8, format_currency(total_geral), 1, 1, "R")
        
        # Condições comerciais
        pdf.add_section_title("CONDIÇÕES COMERCIAIS")
        pdf.add_field("Tipo de Frete:", cotacao[11])  # tipo_frete
        pdf.add_field("Condição de Pagamento:", cotacao[12])  # condicao_pagamento
        pdf.add_field("Prazo de Entrega:", cotacao[13])  # prazo_entrega
        pdf.add_field("Moeda:", cotacao[14])  # moeda
        pdf.add_field("Status:", cotacao[15])  # status
        
        # Observações
        if cotacao[9]:  # observacoes
            pdf.add_section_title("OBSERVAÇÕES")
            pdf.set_font("Arial", "", 10)
            pdf.multi_cell(0, 5, cotacao[9])
        
        # Salvar PDF
        output_dir = "data/pdfs"
        os.makedirs(output_dir, exist_ok=True)
        filename = f"cotacao_{cotacao_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(output_dir, filename)
        
        pdf.output(filepath)
        
        return True, filepath
        
    except Exception as e:
        print(f"Erro ao gerar PDF: {e}")
        import traceback
        traceback.print_exc()
        return False, str(e)
    finally:
        conn.close()