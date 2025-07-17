import sqlite3
import os
from fpdf import FPDF
from datetime import datetime
import json
from utils.formatters import format_date, format_cnpj, format_phone

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
        self.rect(5, 5, 200, 287)  # A4: 210x297, então 5mm de margem
        
        # Cabeçalho corporativo
        self.set_pdf_font('B', 11)
        self.set_y(10)
        self.cell(0, 5, self.clean_pdf_text("WORLD COMP DO BRASIL COMPRESSORES EIRELI"), 0, 1)
        self.cell(0, 5, self.clean_pdf_text("ORDEM DE SERVIÇO DE CAMPO SIMPLIFICADA"), 0, 1)
        self.cell(0, 5, self.clean_pdf_text(f"RELATÓRIO Nº: {getattr(self, 'numero_relatorio', 'N/A')}"), 0, 1)
        self.cell(0, 5, self.clean_pdf_text(f"DATA: {getattr(self, 'data_relatorio', 'N/A')}"), 0, 1)
        
        # Linha de separação
        self.line(10, 35, 200, 35)
        self.ln(5)
        
        # Logo centralizado apenas na primeira página
        if self.first_page:
            logo_path = "logo.jpg"
            if os.path.exists(logo_path):
                logo_height = 25
                logo_width = logo_height * 1.5
                self.image(logo_path, x=(210 - logo_width) / 2, y=40, w=logo_width)
            self.set_y(75)
        
        self.first_page = False
    
    def footer(self):
        self.set_y(-20)
        self.line(10, self.get_y() - 5, 200, self.get_y() - 5)
        
        self.set_pdf_font('', 10)
        self.set_text_color(*self.baby_blue)
        self.cell(0, 5, self.clean_pdf_text("Rua Fernando Pessoa, 17 - Batistini - São Bernardo do Campo/SP - CEP 09844-390"), 0, 1, 'C')
        self.cell(0, 5, self.clean_pdf_text("E-mail: rogerio@worldcompressores.com.br | Fone: (11) 4543-6896/4543-6857/4357-8062"), 0, 1, 'C')
        
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
        self.set_text_color(*self.baby_blue)
        self.set_pdf_font('B', 12)
        self.cell(0, 8, self.clean_pdf_text(title), 0, 1, 'L')
        self.set_text_color(0, 0, 0)
        self.ln(2)

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
        pdf.set_pdf_font("", 11)
        
        nome_cliente = get_value("nome")
        if nome_cliente:
            pdf.cell(0, 6, f"RAZÃO SOCIAL: {nome_cliente}", 0, 1)
            
        cnpj_cliente = get_value("cnpj")
        if cnpj_cliente:
            pdf.cell(0, 6, f"CNPJ: {format_cnpj(cnpj_cliente)}", 0, 1)
            
        endereco_cliente = get_value("endereco")
        if endereco_cliente:
            pdf.cell(0, 6, f"ENDEREÇO: {endereco_cliente}", 0, 1)
            
        cidade = get_value("cidade")
        estado = get_value("estado")
        if cidade and estado:
            pdf.cell(0, 6, f"CIDADE/UF: {cidade}/{estado}", 0, 1)
        
        pdf.ln(5)
        
        # === DADOS DO SERVIÇO ===
        pdf.section_title("DADOS DO SERVIÇO")
        
        numero_rel = get_value("numero_relatorio")
        if numero_rel:
            pdf.cell(0, 6, f"Nº RELATÓRIO: {numero_rel}", 0, 1)
            
        data_criacao = get_value("data_criacao")
        if data_criacao:
            pdf.cell(0, 6, f"DATA: {format_date(data_criacao)}", 0, 1)
            
        formulario = get_value("formulario_servico")
        if formulario:
            pdf.cell(0, 6, f"FORMULÁRIO DE SERVIÇO: {formulario}", 0, 1)
            
        tipo_servico = get_value("tipo_servico")
        if tipo_servico:
            pdf.cell(0, 6, f"TIPO DE SERVIÇO: {tipo_servico}", 0, 1)
            
        descricao_servico = get_value("descricao_servico")
        if descricao_servico:
            pdf.cell(0, 6, "DESCRIÇÃO DO SERVIÇO:", 0, 1)
            pdf.multi_cell(0, 5, pdf.clean_pdf_text(descricao_servico))
        
        pdf.ln(5)
        
        # === TÉCNICOS E EVENTOS ===
        if eventos:
            pdf.section_title("REGISTRO DE EVENTOS DE CAMPO")
            for evento in eventos:
                tecnico, data_hora, desc_evento, tipo_evento = evento
                pdf.cell(0, 6, f"TÉCNICO: {tecnico}", 0, 1)
                pdf.cell(0, 6, f"DATA/HORA: {str(data_hora)}", 0, 1)
                pdf.cell(0, 6, f"TIPO: {tipo_evento}", 0, 1)
                pdf.cell(0, 6, "EVENTO:", 0, 1)
                pdf.multi_cell(0, 5, pdf.clean_pdf_text(str(desc_evento)))
                pdf.ln(2)
        
        # === ABA 1: CONDIÇÃO ATUAL DO EQUIPAMENTO ===
        pdf.section_title("CONDIÇÃO ATUAL DO EQUIPAMENTO")
        
        condicao_encontrada = get_value("condicao_encontrada")
        if condicao_encontrada:
            pdf.cell(0, 6, "CONDIÇÃO ENCONTRADA:", 0, 1)
            pdf.multi_cell(0, 5, pdf.clean_pdf_text(condicao_encontrada))
            pdf.ln(2)
            
        placa_id = get_value("placa_identificacao")
        if placa_id:
            pdf.cell(0, 6, f"PLACA DE IDENTIFICAÇÃO/Nº SÉRIE: {placa_id}", 0, 1)
        
        acoplamento = get_value("acoplamento")
        if acoplamento:
            pdf.cell(0, 6, "ACOPLAMENTO:", 0, 1)
            pdf.multi_cell(0, 5, pdf.clean_pdf_text(acoplamento))
            pdf.ln(2)
        
        aspectos_rotores = get_value("aspectos_rotores")
        if aspectos_rotores:
            pdf.cell(0, 6, "ASPECTOS DOS ROTORES:", 0, 1)
            pdf.multi_cell(0, 5, pdf.clean_pdf_text(aspectos_rotores))
            pdf.ln(2)
        
        valvulas = get_value("valvulas_acopladas")
        if valvulas:
            pdf.cell(0, 6, "VÁLVULAS ACOPLADAS:", 0, 1)
            pdf.multi_cell(0, 5, pdf.clean_pdf_text(valvulas))
            pdf.ln(2)
            
        data_receb_equip = get_value("data_recebimento_equip")
        if data_receb_equip:
            pdf.cell(0, 6, f"DATA DE RECEBIMENTO DO EQUIPAMENTO: {data_receb_equip}", 0, 1)
        
        # Anexos da Aba 1
        if 1 in anexos_abas and anexos_abas[1]:
            pdf.ln(3)
            pdf.cell(0, 6, "ANEXOS - CONDIÇÃO ATUAL DO EQUIPAMENTO:", 0, 1)
            for i, anexo in enumerate(anexos_abas[1], 1):
                if isinstance(anexo, dict):
                    nome = anexo.get('nome', f'Anexo {i}')
                    descricao = anexo.get('descricao', '')
                    pdf.cell(0, 5, pdf.clean_pdf_text(f"  • {nome}"), 0, 1)
                    if descricao:
                        pdf.multi_cell(0, 4, pdf.clean_pdf_text(f"    {descricao}"))
        
        # === ABA 2: PERITAGEM DO SUBCONJUNTO ===
        pdf.section_title("DESACOPLANDO ELEMENTO COMPRESSOR DA CAIXA DE ACIONAMENTO")
        
        parafusos_pinos = get_value("parafusos_pinos")
        if parafusos_pinos:
            pdf.cell(0, 6, "PARAFUSOS/PINOS:", 0, 1)
            pdf.multi_cell(0, 5, pdf.clean_pdf_text(parafusos_pinos))
            pdf.ln(2)
            
        superficie_vedacao = get_value("superficie_vedacao")
        if superficie_vedacao:
            pdf.cell(0, 6, "SUPERFÍCIE DE VEDAÇÃO:", 0, 1)
            pdf.multi_cell(0, 5, pdf.clean_pdf_text(superficie_vedacao))
            pdf.ln(2)
            
        engrenagens = get_value("engrenagens")
        if engrenagens:
            pdf.cell(0, 6, "ENGRENAGENS:", 0, 1)
            pdf.multi_cell(0, 5, pdf.clean_pdf_text(engrenagens))
            pdf.ln(2)
            
        bico_injetor = get_value("bico_injetor")
        if bico_injetor:
            pdf.cell(0, 6, "BICO INJETOR:", 0, 1)
            pdf.multi_cell(0, 5, pdf.clean_pdf_text(bico_injetor))
            pdf.ln(2)
            
        rolamentos = get_value("rolamentos")
        if rolamentos:
            pdf.cell(0, 6, "ROLAMENTOS:", 0, 1)
            pdf.multi_cell(0, 5, pdf.clean_pdf_text(rolamentos))
            pdf.ln(2)
            
        aspecto_oleo = get_value("aspecto_oleo")
        if aspecto_oleo:
            pdf.cell(0, 6, "ASPECTO DO ÓLEO:", 0, 1)
            pdf.multi_cell(0, 5, pdf.clean_pdf_text(aspecto_oleo))
            pdf.ln(2)
            
        data_peritagem = get_value("data_peritagem")
        if data_peritagem:
            pdf.cell(0, 6, f"DATA DA PERITAGEM: {data_peritagem}", 0, 1)
        
        # Anexos da Aba 2
        if 2 in anexos_abas and anexos_abas[2]:
            pdf.ln(3)
            pdf.cell(0, 6, "ANEXOS - PERITAGEM DO SUBCONJUNTO:", 0, 1)
            for i, anexo in enumerate(anexos_abas[2], 1):
                if isinstance(anexo, dict):
                    nome = anexo.get('nome', f'Anexo {i}')
                    descricao = anexo.get('descricao', '')
                    pdf.cell(0, 5, pdf.clean_pdf_text(f"  • {nome}"), 0, 1)
                    if descricao:
                        pdf.multi_cell(0, 4, pdf.clean_pdf_text(f"    {descricao}"))
        
        # === ABA 3: DESMEMBRANDO UNIDADE COMPRESSORA ===
        pdf.section_title("GRAU DE INTERFERÊNCIA NA DESMONTAGEM")
        
        interf_desmontagem = get_value("interf_desmontagem")
        if interf_desmontagem:
            pdf.cell(0, 6, "INTERFERÊNCIA PARA DESMONTAGEM:", 0, 1)
            pdf.multi_cell(0, 5, pdf.clean_pdf_text(interf_desmontagem))
            pdf.ln(2)
            
        aspecto_rotores_aba3 = get_value("aspecto_rotores_aba3")
        if aspecto_rotores_aba3:
            pdf.cell(0, 6, "ASPECTO DOS ROTORES:", 0, 1)
            pdf.multi_cell(0, 5, pdf.clean_pdf_text(aspecto_rotores_aba3))
            pdf.ln(2)
            
        aspecto_carcaca = get_value("aspecto_carcaca")
        if aspecto_carcaca:
            pdf.cell(0, 6, "ASPECTO DA CARCAÇA:", 0, 1)
            pdf.multi_cell(0, 5, pdf.clean_pdf_text(aspecto_carcaca))
            pdf.ln(2)
            
        interf_mancais = get_value("interf_mancais")
        if interf_mancais:
            pdf.cell(0, 6, "INTERFERÊNCIA DOS MANCAIS:", 0, 1)
            pdf.multi_cell(0, 5, pdf.clean_pdf_text(interf_mancais))
            pdf.ln(2)
            
        galeria_hidraulica = get_value("galeria_hidraulica")
        if galeria_hidraulica:
            pdf.cell(0, 6, "GALERIA HIDRÁULICA:", 0, 1)
            pdf.multi_cell(0, 5, pdf.clean_pdf_text(galeria_hidraulica))
            pdf.ln(2)
            
        data_desmembracao = get_value("data_desmembracao")
        if data_desmembracao:
            pdf.cell(0, 6, f"DATA DE DESMEMBRAÇÃO: {data_desmembracao}", 0, 1)
        
        # Anexos da Aba 3
        if 3 in anexos_abas and anexos_abas[3]:
            pdf.ln(3)
            pdf.cell(0, 6, "ANEXOS - DESMEMBRAÇÃO DA UNIDADE:", 0, 1)
            for i, anexo in enumerate(anexos_abas[3], 1):
                if isinstance(anexo, dict):
                    nome = anexo.get('nome', f'Anexo {i}')
                    descricao = anexo.get('descricao', '')
                    pdf.cell(0, 5, pdf.clean_pdf_text(f"  • {nome}"), 0, 1)
                    if descricao:
                        pdf.multi_cell(0, 4, pdf.clean_pdf_text(f"    {descricao}"))
        
        # === ABA 4: RELAÇÃO DE PEÇAS E SERVIÇOS ===
        pdf.section_title("RELAÇÃO DE PEÇAS E SERVIÇOS")
        
        servicos_propostos = get_value("servicos_propostos")
        if servicos_propostos:
            pdf.cell(0, 6, "SERVIÇOS PROPOSTOS PARA REFORMA DO SUBCONJUNTO:", 0, 1)
            pdf.multi_cell(0, 5, pdf.clean_pdf_text(servicos_propostos))
            pdf.ln(2)
            
        pecas_recomendadas = get_value("pecas_recomendadas")
        if pecas_recomendadas:
            pdf.cell(0, 6, "PEÇAS RECOMENDADAS PARA REFORMA:", 0, 1)
            pdf.multi_cell(0, 5, pdf.clean_pdf_text(pecas_recomendadas))
            pdf.ln(2)
            
        data_pecas = get_value("data_pecas")
        if data_pecas:
            pdf.cell(0, 6, f"DATA: {data_pecas}", 0, 1)
        
        # Anexos da Aba 4
        if 4 in anexos_abas and anexos_abas[4]:
            pdf.ln(3)
            pdf.cell(0, 6, "ANEXOS - PEÇAS E SERVIÇOS:", 0, 1)
            for i, anexo in enumerate(anexos_abas[4], 1):
                if isinstance(anexo, dict):
                    nome = anexo.get('nome', f'Anexo {i}')
                    descricao = anexo.get('descricao', '')
                    pdf.cell(0, 5, pdf.clean_pdf_text(f"  • {nome}"), 0, 1)
                    if descricao:
                        pdf.multi_cell(0, 4, pdf.clean_pdf_text(f"    {descricao}"))
        
        # === INFORMAÇÕES ADICIONAIS ===
        tempo_trabalho = get_value("tempo_trabalho_total")
        if tempo_trabalho:
            pdf.cell(0, 6, f"TEMPO DE TRABALHO TOTAL: {tempo_trabalho}", 0, 1)
            
        tempo_deslocamento = get_value("tempo_deslocamento_total")
        if tempo_deslocamento:
            pdf.cell(0, 6, f"TEMPO DE DESLOCAMENTO TOTAL: {tempo_deslocamento}", 0, 1)
        
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