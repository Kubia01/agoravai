import sqlite3
import os
from fpdf import FPDF
from datetime import datetime
import json
from utils.formatters import format_date, format_cnpj, format_phone
from PIL import Image
import tempfile

def clean_text(text, aggressive=False):
    """Substitui tabs por espaços e remove caracteres problemáticos"""
    if text is None:
        return ""
    
    # Converter para string se não for
    text = str(text)
    
    # Substituir tabs por espaços
    text = text.replace('\t', '    ')
    
    # Remover ou substituir caracteres problemáticos
    replacements = {
        '"': '"',  # Smart quotes
        '"': '"',
        ''': "'",
        ''': "'",
        '…': '...',
        '–': '-',
        '—': '-',
        '°': 'o',
        '®': '(R)',
        '©': '(C)',
        '™': '(TM)',
        'ª': 'a',
        'º': 'o',
        'ç': 'c',
        'Ç': 'C'
    }
    
    for old_char, new_char in replacements.items():
        text = text.replace(old_char, new_char)
    
    # Se aggressive=True, remover todos os acentos também
    if aggressive:
        accents = {
            'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a', 'ä': 'a',
            'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
            'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
            'ó': 'o', 'ò': 'o', 'õ': 'o', 'ô': 'o', 'ö': 'o',
            'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',
            'Á': 'A', 'À': 'A', 'Ã': 'A', 'Â': 'A', 'Ä': 'A',
            'É': 'E', 'È': 'E', 'Ê': 'E', 'Ë': 'E',
            'Í': 'I', 'Ì': 'I', 'Î': 'I', 'Ï': 'I',
            'Ó': 'O', 'Ò': 'O', 'Õ': 'O', 'Ô': 'O', 'Ö': 'O',
            'Ú': 'U', 'Ù': 'U', 'Û': 'U', 'Ü': 'U'
        }
        for old_char, new_char in accents.items():
            text = text.replace(old_char, new_char)
    
    # Remover caracteres não-ASCII restantes
    text = ''.join(char if ord(char) < 128 else '?' for char in text)
    
    return text

class RelatorioPDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_auto_page_break(auto=True, margin=25)
        self.baby_blue = (137, 207, 240)  # Azul bebê corporativo
        self.dark_blue = (41, 128, 185)   # Azul escuro para títulos
        self.light_gray = (245, 245, 245) # Cinza claro para backgrounds
        self.first_page = True
        
        # Adicionar fonte Unicode para suportar caracteres especiais
        try:
            # Tentar adicionar DejaVu Sans (comum no sistema)
            self.add_font('DejaVu', '', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', uni=True)
            self.add_font('DejaVu', 'B', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', uni=True)
            self.unicode_font = True
            print("Fonte Unicode DejaVu carregada com sucesso!")
        except:
            try:
                # Fallback para Arial se disponível
                self.add_font('Arial', '', 'arial.ttf', uni=True)
                self.add_font('Arial', 'B', 'arialbd.ttf', uni=True)
                self.unicode_font = True
                print("Fonte Unicode Arial carregada com sucesso!")
            except:
                # Usar fonte padrão e clean_text mais agressivo
                self.unicode_font = False
                print("Usando fonte padrão sem Unicode - texto será limpo agressivamente")
    
    def header(self):
        # Desenha a borda em todas as páginas
        self.set_line_width(0.5)
        self.set_draw_color(70, 70, 70)  # Cor cinza escura para bordas
        self.rect(5, 5, 200, 287)  # A4: 210x297, então 5mm de margem
        
        # Background do cabeçalho
        self.set_fill_color(*self.light_gray)
        self.rect(8, 8, 194, 25, 'F')
        
        # Cabeçalho corporativo
        self.set_text_color(*self.dark_blue)
        self.set_pdf_font('B', 12)
        self.set_y(12)
        self.cell(0, 6, self.clean_pdf_text("WORLD COMP DO BRASIL COMPRESSORES EIRELI"), 0, 1, 'C')
        
        self.set_pdf_font('B', 10)
        self.cell(0, 5, self.clean_pdf_text("ORDEM DE SERVIÇO DE CAMPO SIMPLIFICADA"), 0, 1, 'C')
        
        self.set_pdf_font('', 9)
        self.cell(0, 4, self.clean_pdf_text(f"RELATÓRIO Nº: {getattr(self, 'numero_relatorio', 'N/A')} | DATA: {getattr(self, 'data_relatorio', 'N/A')}"), 0, 1, 'C')
        
        # Linha de separação
        self.set_draw_color(*self.dark_blue)
        self.set_line_width(0.8)
        self.line(10, 35, 200, 35)
        
        # Logo centralizado apenas na primeira página
        if self.first_page:
            logo_path = "logo.jpg"
            if os.path.exists(logo_path):
                logo_height = 20
                logo_width = logo_height * 1.5
                self.image(logo_path, x=(210 - logo_width) / 2, y=40, w=logo_width)
            self.set_y(70)
        else:
            self.set_y(45)
        
        self.first_page = False
        self.set_text_color(0, 0, 0)  # Resetar cor do texto
    
    def footer(self):
        self.set_y(-20)
        self.set_draw_color(*self.dark_blue)
        self.line(10, self.get_y() - 5, 200, self.get_y() - 5)
        
        self.set_pdf_font('', 8)
        self.set_text_color(*self.dark_blue)
        self.cell(0, 4, self.clean_pdf_text("Rua Fernando Pessoa, 17 - Batistini - São Bernardo do Campo/SP - CEP 09844-390"), 0, 1, 'C')
        self.cell(0, 4, self.clean_pdf_text("E-mail: rogerio@worldcompressores.com.br | Fone: (11) 4543-6896/4543-6857/4357-8062"), 0, 1, 'C')
        
        # Número da página
        self.set_text_color(100, 100, 100)
        self.cell(0, 4, f"Página {self.page_no()}", 0, 0, 'R')
        
        self.set_text_color(0, 0, 0)

    def set_pdf_font(self, style='', size=10):
        """Define fonte apropriada (Unicode se disponível)"""
        if self.unicode_font:
            self.set_font("DejaVu", style, size)
        else:
            self.set_font("Arial", style, size)
    
    def clean_pdf_text(self, text):
        """Limpa texto conforme a capacidade da fonte"""
        return clean_text(text, aggressive=not self.unicode_font)
    
    def section_title(self, title):
        """Título de seção com background e formatação profissional"""
        self.ln(3)
        
        # Background da seção
        self.set_fill_color(*self.light_gray)
        self.rect(10, self.get_y(), 190, 8, 'F')
        
        # Título
        self.set_text_color(*self.dark_blue)
        self.set_pdf_font('B', 11)
        self.cell(0, 8, self.clean_pdf_text(title), 0, 1, 'L')
        self.set_text_color(0, 0, 0)
        self.ln(2)
    
    def field_label_value(self, label, value, new_line=True):
        """Formatar campo com label e valor de forma profissional"""
        if not value:
            return
            
        self.set_pdf_font('B', 9)
        self.set_text_color(*self.dark_blue)
        label_width = self.get_string_width(label + ": ") + 5
        self.cell(label_width, 5, self.clean_pdf_text(label + ":"), 0, 0)
        
        self.set_pdf_font('', 9)
        self.set_text_color(0, 0, 0)
        if new_line:
            self.cell(0, 5, self.clean_pdf_text(str(value)), 0, 1)
        else:
            self.cell(0, 5, self.clean_pdf_text(str(value)), 0, 0)
    
    def multi_line_field(self, label, value):
        """Campo de múltiplas linhas com formatação profissional"""
        if not value:
            return
            
        self.set_pdf_font('B', 9)
        self.set_text_color(*self.dark_blue)
        self.cell(0, 5, self.clean_pdf_text(label + ":"), 0, 1)
        
        self.set_pdf_font('', 9)
        self.set_text_color(0, 0, 0)
        self.set_left_margin(15)  # Indentar o conteúdo
        self.multi_cell(0, 4, self.clean_pdf_text(str(value)))
        self.set_left_margin(10)  # Voltar margem normal
        self.ln(2)
    
    def add_image_to_pdf(self, image_path, max_width=80, max_height=60):
        """Adiciona imagem ao PDF com redimensionamento automático"""
        try:
            if not os.path.exists(image_path):
                return False
                
            # Verificar se é uma imagem suportada
            supported_formats = ['.jpg', '.jpeg', '.png']
            file_ext = os.path.splitext(image_path)[1].lower()
            
            if file_ext not in supported_formats:
                return False
            
            # Obter dimensões da imagem
            with Image.open(image_path) as img:
                img_width, img_height = img.size
                
                # Calcular proporção para redimensionamento
                width_ratio = max_width / img_width
                height_ratio = max_height / img_height
                ratio = min(width_ratio, height_ratio)
                
                new_width = img_width * ratio
                new_height = img_height * ratio
                
                # Verificar se há espaço suficiente na página
                if self.get_y() + new_height > 270:  # 270 é próximo ao fim da página
                    self.add_page()
                
                # Adicionar imagem centralizada
                x_pos = (210 - new_width) / 2
                self.image(image_path, x=x_pos, y=self.get_y(), w=new_width, h=new_height)
                self.ln(new_height + 3)
                
                return True
                
        except Exception as e:
            print(f"Erro ao adicionar imagem {image_path}: {str(e)}")
            return False
    
    def add_attachments_section(self, anexos, section_title):
        """Adiciona seção de anexos com imagens e informações"""
        if not anexos:
            return
            
        self.ln(3)
        self.set_pdf_font('B', 10)
        self.set_text_color(*self.dark_blue)
        self.cell(0, 6, self.clean_pdf_text(section_title), 0, 1)
        self.set_text_color(0, 0, 0)
        
        for i, anexo in enumerate(anexos, 1):
            if isinstance(anexo, dict):
                nome = anexo.get('nome', f'Anexo {i}')
                caminho = anexo.get('caminho', '')
                descricao = anexo.get('descricao', '')
                
                # Exibir nome do arquivo
                self.set_pdf_font('B', 9)
                self.cell(0, 5, self.clean_pdf_text(f"{i}. {nome}"), 0, 1)
                
                # Exibir descrição se existir
                if descricao:
                    self.set_pdf_font('', 8)
                    self.set_text_color(80, 80, 80)
                    self.set_left_margin(15)
                    self.multi_cell(0, 4, self.clean_pdf_text(descricao))
                    self.set_left_margin(10)
                    self.set_text_color(0, 0, 0)
                
                # Tentar exibir a imagem se for um arquivo de imagem
                if caminho and os.path.exists(caminho):
                    file_ext = os.path.splitext(caminho)[1].lower()
                    if file_ext in ['.jpg', '.jpeg', '.png']:
                        self.ln(2)
                        if self.add_image_to_pdf(caminho):
                            # Adicionar legenda
                            self.set_pdf_font('I', 8)
                            self.set_text_color(100, 100, 100)
                            self.cell(0, 4, self.clean_pdf_text(f"Figura {i}: {nome}"), 0, 1, 'C')
                            self.set_text_color(0, 0, 0)
                
                self.ln(3)

def gerar_pdf_relatorio(relatorio_id, db_name):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    
    try:
        # Primeiro obter os nomes das colunas existentes na tabela
        c.execute("PRAGMA table_info(relatorios_tecnicos)")
        columns_info = c.fetchall()
        column_names = [column[1] for column in columns_info]
        
        # Construir a query dinamicamente com base nas colunas existentes - EXPANDIDA PARA 4 ABAS
        base_columns = ["r.numero_relatorio", "r.data_criacao", "c.nome", "c.cnpj", "c.endereco", "c.cidade", "c.estado"]
        
        # Verificar quais colunas existem na tabela para as 4 abas
        report_columns = []
        column_map = {
            # Dados básicos do serviço
            "formulario_servico": "r.formulario_servico",
            "tipo_servico": "r.tipo_servico",
            "descricao_servico": "r.descricao_servico",
            "data_recebimento": "r.data_recebimento",
            
            # ABA 1: Condição Atual do Equipamento
            "condicao_encontrada": "r.condicao_encontrada",
            "placa_identificacao": "r.placa_identificacao",
            "acoplamento": "r.acoplamento",
            "aspectos_rotores": "r.aspectos_rotores",
            "valvulas_acopladas": "r.valvulas_acopladas",
            "data_recebimento_equip": "r.data_recebimento_equip",
            
            # ABA 2: Peritagem do Subconjunto
            "parafusos_pinos": "r.parafusos_pinos",
            "superficie_vedacao": "r.superficie_vedacao",
            "engrenagens": "r.engrenagens",
            "bico_injetor": "r.bico_injetor",
            "rolamentos": "r.rolamentos",
            "aspecto_oleo": "r.aspecto_oleo",
            "data_peritagem": "r.data_peritagem",
            
            # ABA 3: Desmembrando Unidade Compressora
            "interf_desmontagem": "r.interf_desmontagem",
            "aspecto_rotores_aba3": "r.aspecto_rotores_aba3",
            "aspecto_carcaca": "r.aspecto_carcaca",
            "interf_mancais": "r.interf_mancais",
            "galeria_hidraulica": "r.galeria_hidraulica",
            "data_desmembracao": "r.data_desmembracao",
            
            # ABA 4: Relação de Peças e Serviços
            "servicos_propostos": "r.servicos_propostos",
            "pecas_recomendadas": "r.pecas_recomendadas",
            "data_pecas": "r.data_pecas",
            "tempo_trabalho_total": "r.tempo_trabalho_total",
            "tempo_deslocamento_total": "r.tempo_deslocamento_total",
            
            # Campos adicionais
            "condicao_inicial": "r.condicao_inicial",
            "condicao_atual": "r.condicao_atual"
        }
        
        for col_name, sql_col in column_map.items():
            if col_name in column_names:
                report_columns.append(sql_col)
            else:
                report_columns.append("NULL as " + col_name)
        
        # Construir a query completa
        query = f"""
            SELECT {', '.join(base_columns)}, {', '.join(report_columns)}
            FROM relatorios_tecnicos r
            JOIN clientes c ON r.cliente_id = c.id
            WHERE r.id = ?
        """
        
        c.execute(query, (relatorio_id,))
        relatorio_data = c.fetchone()
        
        if not relatorio_data:
            return False, "Relatório não encontrado"
        
        # Criar um dicionário para acessar valores por nome
        column_indices = {}
        
        # Mapear colunas base para índices
        for i, col_name in enumerate(base_columns):
            col_key = col_name.split('.')[-1]
            column_indices[col_name] = i
            column_indices[col_key] = i
            
        # Mapear colunas de relatório para índices
        for i, col_full in enumerate(report_columns):
            idx = i + len(base_columns)
            if " as " in col_full:
                col_name = col_full.split(" as ")[1]
                column_indices[col_name] = idx
            else:
                col_name = col_full.split('.')[-1]
                column_indices[col_full] = idx
                column_indices[col_name] = idx
        
        # Função auxiliar para acessar dados de forma segura
        def get_value(key, default=""):
            idx = -1
            if key in column_indices:
                idx = column_indices[key]
            elif f"r.{key}" in column_indices:
                idx = column_indices[f"r.{key}"]
            elif f"c.{key}" in column_indices:
                idx = column_indices[f"c.{key}"]
                
            if idx >= 0 and idx < len(relatorio_data):
                return relatorio_data[idx] or default
            return default
        
        # Obter eventos
        c.execute("""
            SELECT t.nome, e.data_hora, e.evento, e.tipo
            FROM eventos_campo e
            JOIN tecnicos t ON e.tecnico_id = t.id
            WHERE e.relatorio_id = ?
            ORDER BY e.data_hora
        """, (relatorio_id,))
        eventos = c.fetchall()
        
        # Obter anexos das 4 abas
        anexos_abas = {}
        for aba_num in range(1, 5):
            aba_col = f'anexos_aba{aba_num}'
            if aba_col in column_names:
                c.execute(f"SELECT {aba_col} FROM relatorios_tecnicos WHERE id = ?", (relatorio_id,))
                anexos_result = c.fetchone()
                if anexos_result and anexos_result[0]:
                    try:
                        anexos_data = anexos_result[0]
                        if isinstance(anexos_data, str):
                            anexos_abas[aba_num] = json.loads(anexos_data)
                        elif isinstance(anexos_data, list):
                            anexos_abas[aba_num] = anexos_data
                    except (json.JSONDecodeError, TypeError):
                        anexos_abas[aba_num] = []
        
        # Criar PDF
        pdf = RelatorioPDF()
        
        # Configurar dados para cabeçalho
        pdf.numero_relatorio = get_value("numero_relatorio")
        pdf.data_relatorio = format_date(get_value("data_criacao"))
        
        pdf.add_page()
        
        # === CABEÇALHO DO RELATÓRIO ===
        pdf.section_title("IDENTIFICAÇÃO DO CLIENTE")
        
        nome_cliente = get_value("nome")
        pdf.field_label_value("RAZÃO SOCIAL", nome_cliente)
            
        cnpj_cliente = get_value("cnpj")
        if cnpj_cliente:
            pdf.field_label_value("CNPJ", format_cnpj(cnpj_cliente))
            
        endereco_cliente = get_value("endereco")
        pdf.field_label_value("ENDEREÇO", endereco_cliente)
            
        cidade = get_value("cidade")
        estado = get_value("estado")
        if cidade and estado:
            pdf.field_label_value("CIDADE/UF", f"{cidade}/{estado}")
        
        pdf.ln(3)
        
        # === DADOS DO SERVIÇO ===
        pdf.section_title("DADOS DO SERVIÇO")
        
        numero_rel = get_value("numero_relatorio")
        pdf.field_label_value("Nº RELATÓRIO", numero_rel)
            
        data_criacao = get_value("data_criacao")
        if data_criacao:
            pdf.field_label_value("DATA", format_date(data_criacao))
            
        formulario = get_value("formulario_servico")
        pdf.field_label_value("FORMULÁRIO DE SERVIÇO", formulario)
            
        tipo_servico = get_value("tipo_servico")
        pdf.field_label_value("TIPO DE SERVIÇO", tipo_servico)
            
        descricao_servico = get_value("descricao_servico")
        pdf.multi_line_field("DESCRIÇÃO DO SERVIÇO", descricao_servico)
        
        pdf.ln(3)
        
        # === TÉCNICOS E EVENTOS ===
        if eventos:
            pdf.section_title("REGISTRO DE EVENTOS DE CAMPO")
            for evento in eventos:
                tecnico, data_hora, desc_evento, tipo_evento = evento
                pdf.field_label_value("TÉCNICO", tecnico)
                pdf.field_label_value("DATA/HORA", str(data_hora))
                pdf.field_label_value("TIPO", tipo_evento)
                pdf.multi_line_field("EVENTO", desc_evento)
                pdf.ln(1)
        
        # === ABA 1: CONDIÇÃO ATUAL DO EQUIPAMENTO ===
        pdf.section_title("CONDIÇÃO ATUAL DO EQUIPAMENTO")
        
        condicao_encontrada = get_value("condicao_encontrada")
        pdf.multi_line_field("CONDIÇÃO ENCONTRADA", condicao_encontrada)
            
        placa_id = get_value("placa_identificacao")
        pdf.field_label_value("PLACA DE IDENTIFICAÇÃO/Nº SÉRIE", placa_id)
        
        acoplamento = get_value("acoplamento")
        pdf.multi_line_field("ACOPLAMENTO", acoplamento)
        
        aspectos_rotores = get_value("aspectos_rotores")
        pdf.multi_line_field("ASPECTOS DOS ROTORES", aspectos_rotores)
        
        valvulas = get_value("valvulas_acopladas")
        pdf.multi_line_field("VÁLVULAS ACOPLADAS", valvulas)
            
        data_receb_equip = get_value("data_recebimento_equip")
        pdf.field_label_value("DATA DE RECEBIMENTO DO EQUIPAMENTO", data_receb_equip)
        
        # Anexos da Aba 1 com imagens
        if 1 in anexos_abas and anexos_abas[1]:
            pdf.add_attachments_section(anexos_abas[1], "ANEXOS - CONDIÇÃO ATUAL DO EQUIPAMENTO")
        
        # === ABA 2: PERITAGEM DO SUBCONJUNTO ===
        pdf.section_title("DESACOPLANDO ELEMENTO COMPRESSOR DA CAIXA DE ACIONAMENTO")
        
        parafusos_pinos = get_value("parafusos_pinos")
        pdf.multi_line_field("PARAFUSOS/PINOS", parafusos_pinos)
            
        superficie_vedacao = get_value("superficie_vedacao")
        pdf.multi_line_field("SUPERFÍCIE DE VEDAÇÃO", superficie_vedacao)
            
        engrenagens = get_value("engrenagens")
        pdf.multi_line_field("ENGRENAGENS", engrenagens)
            
        bico_injetor = get_value("bico_injetor")
        pdf.multi_line_field("BICO INJETOR", bico_injetor)
            
        rolamentos = get_value("rolamentos")
        pdf.multi_line_field("ROLAMENTOS", rolamentos)
            
        aspecto_oleo = get_value("aspecto_oleo")
        pdf.multi_line_field("ASPECTO DO ÓLEO", aspecto_oleo)
            
        data_peritagem = get_value("data_peritagem")
        pdf.field_label_value("DATA DA PERITAGEM", data_peritagem)
        
        # Anexos da Aba 2 com imagens
        if 2 in anexos_abas and anexos_abas[2]:
            pdf.add_attachments_section(anexos_abas[2], "ANEXOS - PERITAGEM DO SUBCONJUNTO")
        
        # === ABA 3: DESMEMBRANDO UNIDADE COMPRESSORA ===
        pdf.section_title("GRAU DE INTERFERÊNCIA NA DESMONTAGEM")
        
        interf_desmontagem = get_value("interf_desmontagem")
        pdf.multi_line_field("INTERFERÊNCIA PARA DESMONTAGEM", interf_desmontagem)
            
        aspecto_rotores_aba3 = get_value("aspecto_rotores_aba3")
        pdf.multi_line_field("ASPECTO DOS ROTORES", aspecto_rotores_aba3)
            
        aspecto_carcaca = get_value("aspecto_carcaca")
        pdf.multi_line_field("ASPECTO DA CARCAÇA", aspecto_carcaca)
            
        interf_mancais = get_value("interf_mancais")
        pdf.multi_line_field("INTERFERÊNCIA DOS MANCAIS", interf_mancais)
            
        galeria_hidraulica = get_value("galeria_hidraulica")
        pdf.multi_line_field("GALERIA HIDRÁULICA", galeria_hidraulica)
            
        data_desmembracao = get_value("data_desmembracao")
        pdf.field_label_value("DATA DE DESMEMBRAÇÃO", data_desmembracao)
        
        # Anexos da Aba 3 com imagens
        if 3 in anexos_abas and anexos_abas[3]:
            pdf.add_attachments_section(anexos_abas[3], "ANEXOS - DESMEMBRAÇÃO DA UNIDADE")
        
        # === ABA 4: RELAÇÃO DE PEÇAS E SERVIÇOS ===
        pdf.section_title("RELAÇÃO DE PEÇAS E SERVIÇOS")
        
        servicos_propostos = get_value("servicos_propostos")
        pdf.multi_line_field("SERVIÇOS PROPOSTOS PARA REFORMA DO SUBCONJUNTO", servicos_propostos)
            
        pecas_recomendadas = get_value("pecas_recomendadas")
        pdf.multi_line_field("PEÇAS RECOMENDADAS PARA REFORMA", pecas_recomendadas)
            
        data_pecas = get_value("data_pecas")
        pdf.field_label_value("DATA", data_pecas)
        
        # Anexos da Aba 4 com imagens
        if 4 in anexos_abas and anexos_abas[4]:
            pdf.add_attachments_section(anexos_abas[4], "ANEXOS - PEÇAS E SERVIÇOS")
        
        # === INFORMAÇÕES ADICIONAIS ===
        pdf.section_title("INFORMAÇÕES COMPLEMENTARES")
        
        tempo_trabalho = get_value("tempo_trabalho_total")
        pdf.field_label_value("TEMPO DE TRABALHO TOTAL", tempo_trabalho)
            
        tempo_deslocamento = get_value("tempo_deslocamento_total")
        pdf.field_label_value("TEMPO DE DESLOCAMENTO TOTAL", tempo_deslocamento)
        
        # Salvar arquivo
        output_dir = os.path.join("data", "relatorios")
        os.makedirs(output_dir, exist_ok=True)
        filename = f"relatorio_{relatorio_id}.pdf"
        filepath = os.path.join(output_dir, filename)
        pdf.output(filepath)
        
        return True, filepath
        
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()