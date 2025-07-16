import sqlite3
import os
from fpdf import FPDF
from datetime import datetime
from utils.formatters import format_date, format_cnpj, format_phone

class RelatorioPDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_auto_page_break(auto=True, margin=15)
    
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "ORDEM DE SERVIÇO DE CAMPO SIMPLIFICADA", 0, 1, "C")
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
    
    def add_multiline_field(self, label, value):
        """Adicionar campo com múltiplas linhas"""
        self.set_font("Arial", "B", 10)
        self.cell(0, 6, label, 0, 1, "L")
        
        self.set_font("Arial", "", 10)
        if value:
            self.multi_cell(0, 5, str(value))
        self.ln(2)

def gerar_pdf_relatorio(relatorio_id, db_name):
    """Gerar PDF do relatório técnico com todas as 4 abas"""
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    
    try:
        # Buscar dados do relatório
        c.execute("""
            SELECT r.*, c.nome as cliente_nome, c.cnpj, c.endereco, c.cidade, c.estado,
                   u.nome_completo as responsavel_nome
            FROM relatorios_tecnicos r
            JOIN clientes c ON r.cliente_id = c.id
            JOIN usuarios u ON r.responsavel_id = u.id
            WHERE r.id = ?
        """, (relatorio_id,))
        
        relatorio = c.fetchone()
        if not relatorio:
            return False, "Relatório não encontrado"
        
        # Buscar técnicos e eventos
        c.execute("""
            SELECT t.nome, ec.data_hora, ec.evento, ec.tipo
            FROM eventos_campo ec
            JOIN tecnicos t ON ec.tecnico_id = t.id
            WHERE ec.relatorio_id = ?
            ORDER BY ec.data_hora
        """, (relatorio_id,))
        eventos = c.fetchall()
        
        # Criar PDF
        pdf = RelatorioPDF()
        pdf.add_page()
        
        # Cabeçalho do relatório
        pdf.add_section_title("IDENTIFICAÇÃO DO CLIENTE")
        pdf.add_field("Cliente:", relatorio[25])  # cliente_nome
        pdf.add_field("CNPJ:", format_cnpj(relatorio[26]))
        pdf.add_field("Endereço:", f"{relatorio[27]} - {relatorio[28]}/{relatorio[29]}")
        
        # Dados do serviço
        pdf.add_section_title("DADOS DO SERVIÇO")
        pdf.add_field("Número do Relatório:", relatorio[1])  # numero_relatorio
        pdf.add_field("Data de Criação:", format_date(relatorio[4]))
        pdf.add_field("Responsável:", relatorio[31])  # responsavel_nome
        pdf.add_field("Formulário de Serviço:", relatorio[5])
        pdf.add_field("Tipo de Serviço:", relatorio[6])
        pdf.add_multiline_field("Descrição do Serviço:", relatorio[7])
        
        # Técnicos e Eventos
        if eventos:
            pdf.add_section_title("TÉCNICOS E EVENTOS")
            for evento in eventos:
                tecnico, data_hora, descricao, tipo = evento
                pdf.add_field(f"{tecnico} ({tipo}):", f"{data_hora} - {descricao}")
        
        # ABA 1: CONDIÇÃO INICIAL
        pdf.add_section_title("CONDIÇÃO ATUAL DO EQUIPAMENTO")
        pdf.add_field("Condição Encontrada:", relatorio[9])  # condicao_encontrada
        pdf.add_field("Placa/N.Série:", relatorio[10])       # placa_identificacao
        pdf.add_field("Acoplamento:", relatorio[11])          # acoplamento
        pdf.add_field("Aspectos Rotores:", relatorio[12])     # aspectos_rotores
        pdf.add_field("Válvulas Acopladas:", relatorio[13])   # valvulas_acopladas
        pdf.add_field("Data Recebimento:", relatorio[14])     # data_recebimento_equip
        
        # ABA 2: PERITAGEM DO SUBCONJUNTO
        pdf.add_section_title("DESACOPLANDO ELEMENTO COMPRESSOR DA CAIXA DE ACIONAMENTO")
        pdf.add_field("Parafusos/Pinos:", relatorio[15])      # parafusos_pinos
        pdf.add_field("Superfície Vedação:", relatorio[16])   # superficie_vedacao
        pdf.add_field("Engrenagens:", relatorio[17])          # engrenagens
        pdf.add_field("Bico Injertor:", relatorio[18])        # bico_injertor
        pdf.add_field("Rolamentos:", relatorio[19])           # rolamentos
        pdf.add_field("Aspecto Óleo:", relatorio[20])         # aspecto_oleo
        pdf.add_field("Data:", relatorio[21])                 # data_peritagem
        
        # ABA 3: DESMEMBRANDO UNIDADE COMPRESSORA
        pdf.add_section_title("GRAU DE INTERFERÊNCIA NA DESMONTAGEM")
        pdf.add_field("Interferência Desmontagem:", relatorio[22])  # interf_desmontagem
        pdf.add_field("Aspecto Rotores:", relatorio[23])            # aspecto_rotores_aba3
        pdf.add_field("Aspecto Carcaça:", relatorio[24])            # aspecto_carcaca
        pdf.add_field("Interferência Mancais:", relatorio[25])      # interf_mancais
        pdf.add_field("Galeria Hidráulica:", relatorio[26])         # galeria_hidraulica
        pdf.add_field("Data Desmembração:", relatorio[27])          # data_desmembracao
        
        # ABA 4: RELAÇÃO DE PEÇAS E SERVIÇOS
        pdf.add_section_title("SERVIÇOS E PEÇAS")
        pdf.add_multiline_field("SERVIÇOS PROPOSTO PARA REFORMA DO SUBCONJUNTO:", relatorio[28])  # servicos_propostos
        pdf.add_multiline_field("PEÇAS RECOMENDADAS PARA REFORMA:", relatorio[29])                # pecas_recomendadas
        pdf.add_field("DATA:", relatorio[30])                                                      # data_pecas
        
        # Salvar PDF
        output_dir = "data/pdfs"
        os.makedirs(output_dir, exist_ok=True)
        filename = f"relatorio_tecnico_{relatorio_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
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