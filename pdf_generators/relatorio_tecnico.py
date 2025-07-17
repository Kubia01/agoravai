import sqlite3
import os
from fpdf import FPDF
from datetime import datetime
from utils.formatters import format_date, format_cnpj, format_phone
import json

class RelatorioPDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_auto_page_break(auto=True, margin=15)
    
    def header(self):
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "ORDEM DE SERVIÇO DE CAMPO SIMPLIFICADA", 0, 1, "C")
        self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Página {self.page_no()}", 0, 0, "C")
    
    def add_section_title(self, title):
        """Adicionar título de seção com estilo do formato original"""
        self.set_font("Arial", "B", 14)
        self.ln(5)
        self.cell(0, 10, title, 1, 1, "C", True)
        self.ln(3)
    
    def add_field(self, label, value, width=None):
        """Adicionar campo com label e valor"""
        self.set_font("Arial", "B", 10)
        label_width = width if width else 50
        self.cell(label_width, 6, label, 1, 0, "L")
        
        self.set_font("Arial", "", 10)
        self.cell(0, 6, str(value) if value else "", 1, 1, "L")
    
    def add_multiline_field(self, label, value):
        """Adicionar campo com múltiplas linhas"""
        self.set_font("Arial", "B", 10)
        self.cell(0, 6, label, 1, 1, "L", True)
        
        self.set_font("Arial", "", 10)
        if value:
            lines = str(value).split('\n')
            for line in lines:
                self.cell(0, 5, line, 1, 1, "L")
        else:
            self.cell(0, 5, "", 1, 1, "L")
        self.ln(2)
    
    def add_anexos_section(self, anexos_json, aba_nome):
        """Adicionar seção de anexos para uma aba específica"""
        if not anexos_json:
            return
            
        try:
            anexos = json.loads(anexos_json) if isinstance(anexos_json, str) else anexos_json
            if not anexos:
                return
                
            self.add_section_title(f"ANEXOS - {aba_nome}")
            
            for i, anexo in enumerate(anexos, 1):
                if isinstance(anexo, dict):
                    nome = anexo.get('nome', f'Anexo {i}')
                    descricao = anexo.get('descricao', '')
                    caminho = anexo.get('caminho', '')
                else:
                    nome = f'Anexo {i}'
                    descricao = str(anexo)
                    caminho = ''
                
                self.add_field(f"Anexo {i}:", nome)
                if descricao:
                    self.add_field("Descrição:", descricao)
                if caminho:
                    self.add_field("Arquivo:", caminho)
                self.ln(2)
                
        except (json.JSONDecodeError, TypeError) as e:
            self.add_field(f"Erro ao carregar anexos de {aba_nome}:", str(e))

def gerar_pdf_relatorio(relatorio_id, db_name):
    """Gerar PDF do relatório técnico com todas as 4 abas e anexos"""
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    
    try:
        # Buscar dados do relatório
        c.execute("""
            SELECT r.*, c.nome as cliente_nome, c.cnpj, c.endereco, c.numero, c.complemento, 
                   c.bairro, c.cidade, c.estado, c.cep, c.telefone, c.email,
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
        
        # === CABEÇALHO DO RELATÓRIO ===
        pdf.add_section_title("IDENTIFICAÇÃO DO CLIENTE")
        
        # Dados do cliente (formato original)
        pdf.add_field("RAZÃO SOCIAL:", relatorio[35])  # cliente_nome
        if relatorio[36]:  # cnpj
            pdf.add_field("CNPJ:", format_cnpj(relatorio[36]))
        
        # Endereço completo
        endereco_completo = relatorio[37] or ""  # endereco
        if relatorio[38]:  # numero
            endereco_completo += f", {relatorio[38]}"
        if relatorio[39]:  # complemento
            endereco_completo += f", {relatorio[39]}"
        if relatorio[40]:  # bairro
            endereco_completo += f" - {relatorio[40]}"
        
        pdf.add_field("ENDEREÇO:", endereco_completo)
        
        cidade_estado = relatorio[41] or ""  # cidade
        if relatorio[42]:  # estado
            cidade_estado += f"/{relatorio[42]}"
        if relatorio[43]:  # cep
            cidade_estado += f" - CEP: {relatorio[43]}"
            
        pdf.add_field("CIDADE/UF:", cidade_estado)
        
        if relatorio[44]:  # telefone
            pdf.add_field("TELEFONE:", format_phone(relatorio[44]))
        if relatorio[45]:  # email
            pdf.add_field("E-MAIL:", relatorio[45])
        
        # === DADOS DO SERVIÇO ===
        pdf.add_section_title("DADOS DO SERVIÇO")
        pdf.add_field("Nº RELATÓRIO:", relatorio[1])  # numero_relatorio
        pdf.add_field("DATA:", format_date(relatorio[4]))  # data_criacao
        pdf.add_field("RESPONSÁVEL:", relatorio[46])  # responsavel_nome
        
        if relatorio[5]:  # formulario_servico
            pdf.add_field("FORMULÁRIO DE SERVIÇO:", relatorio[5])
        if relatorio[6]:  # tipo_servico
            pdf.add_field("TIPO DE SERVIÇO:", relatorio[6])
        if relatorio[7]:  # descricao_servico
            pdf.add_multiline_field("DESCRIÇÃO DO SERVIÇO:", relatorio[7])
        
        # === TÉCNICOS E EVENTOS ===
        if eventos:
            pdf.add_section_title("REGISTRO DE EVENTOS DE CAMPO")
            for evento in eventos:
                tecnico, data_hora, descricao, tipo = evento
                pdf.add_field("TÉCNICO:", tecnico)
                pdf.add_field("DATA/HORA:", str(data_hora))
                pdf.add_field("TIPO:", tipo)
                pdf.add_multiline_field("EVENTO:", descricao)
                pdf.ln(2)
        
        # === ABA 1: CONDIÇÃO INICIAL DO EQUIPAMENTO ===
        pdf.add_section_title("CONDIÇÃO ATUAL DO EQUIPAMENTO")
        
        if relatorio[9]:  # condicao_encontrada
            pdf.add_multiline_field("CONDIÇÃO ENCONTRADA:", relatorio[9])
        if relatorio[10]:  # placa_identificacao
            pdf.add_field("PLACA DE IDENTIFICAÇÃO/Nº SÉRIE:", relatorio[10])
        if relatorio[11]:  # acoplamento
            pdf.add_multiline_field("ACOPLAMENTO:", relatorio[11])
        if relatorio[12]:  # aspectos_rotores
            pdf.add_multiline_field("ASPECTOS DOS ROTORES:", relatorio[12])
        if relatorio[13]:  # valvulas_acopladas
            pdf.add_multiline_field("VÁLVULAS ACOPLADAS:", relatorio[13])
        if relatorio[14]:  # data_recebimento_equip
            pdf.add_field("DATA DE RECEBIMENTO DO EQUIPAMENTO:", relatorio[14])
        
        # Anexos da Aba 1
        if relatorio[33]:  # anexos_aba1
            pdf.add_anexos_section(relatorio[33], "CONDIÇÃO ATUAL DO EQUIPAMENTO")
        
        # === ABA 2: PERITAGEM DO SUBCONJUNTO ===
        pdf.add_section_title("DESACOPLANDO ELEMENTO COMPRESSOR DA CAIXA DE ACIONAMENTO")
        
        if relatorio[15]:  # parafusos_pinos
            pdf.add_multiline_field("PARAFUSOS/PINOS:", relatorio[15])
        if relatorio[16]:  # superficie_vedacao
            pdf.add_multiline_field("SUPERFÍCIE DE VEDAÇÃO:", relatorio[16])
        if relatorio[17]:  # engrenagens
            pdf.add_multiline_field("ENGRENAGENS:", relatorio[17])
        if relatorio[18]:  # bico_injertor
            pdf.add_multiline_field("BICO INJETOR:", relatorio[18])
        if relatorio[19]:  # rolamentos
            pdf.add_multiline_field("ROLAMENTOS:", relatorio[19])
        if relatorio[20]:  # aspecto_oleo
            pdf.add_multiline_field("ASPECTO DO ÓLEO:", relatorio[20])
        if relatorio[21]:  # data_peritagem
            pdf.add_field("DATA DA PERITAGEM:", relatorio[21])
        
        # Anexos da Aba 2
        if relatorio[34]:  # anexos_aba2
            pdf.add_anexos_section(relatorio[34], "PERITAGEM DO SUBCONJUNTO")
        
        # === ABA 3: DESMEMBRANDO UNIDADE COMPRESSORA ===
        pdf.add_section_title("GRAU DE INTERFERÊNCIA NA DESMONTAGEM")
        
        if relatorio[22]:  # interf_desmontagem
            pdf.add_multiline_field("INTERFERÊNCIA PARA DESMONTAGEM:", relatorio[22])
        if relatorio[23]:  # aspecto_rotores_aba3
            pdf.add_multiline_field("ASPECTO DOS ROTORES:", relatorio[23])
        if relatorio[24]:  # aspecto_carcaca
            pdf.add_multiline_field("ASPECTO DA CARCAÇA:", relatorio[24])
        if relatorio[25]:  # interf_mancais
            pdf.add_multiline_field("INTERFERÊNCIA DOS MANCAIS:", relatorio[25])
        if relatorio[26]:  # galeria_hidraulica
            pdf.add_multiline_field("GALERIA HIDRÁULICA:", relatorio[26])
        if relatorio[27]:  # data_desmembracao
            pdf.add_field("DATA DE DESMEMBRAÇÃO:", relatorio[27])
        
        # Anexos da Aba 3
        if relatorio[35]:  # anexos_aba3 (índice corrigido)
            pdf.add_anexos_section(relatorio[35], "DESMEMBRAÇÃO DA UNIDADE")
        
        # === ABA 4: RELAÇÃO DE PEÇAS E SERVIÇOS ===
        pdf.add_section_title("RELAÇÃO DE PEÇAS E SERVIÇOS")
        
        if relatorio[28]:  # servicos_propostos
            pdf.add_multiline_field("SERVIÇOS PROPOSTOS PARA REFORMA DO SUBCONJUNTO:", relatorio[28])
        if relatorio[29]:  # pecas_recomendadas
            pdf.add_multiline_field("PEÇAS RECOMENDADAS PARA REFORMA:", relatorio[29])
        if relatorio[30]:  # data_pecas
            pdf.add_field("DATA:", relatorio[30])
        
        # Anexos da Aba 4
        if len(relatorio) > 36 and relatorio[36]:  # anexos_aba4 (índice corrigido)
            pdf.add_anexos_section(relatorio[36], "PEÇAS E SERVIÇOS")
        
        # === INFORMAÇÕES ADICIONAIS ===
        if relatorio[31]:  # tempo_trabalho_total
            pdf.add_field("TEMPO DE TRABALHO TOTAL:", relatorio[31])
        if relatorio[32]:  # tempo_deslocamento_total
            pdf.add_field("TEMPO DE DESLOCAMENTO TOTAL:", relatorio[32])
        
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