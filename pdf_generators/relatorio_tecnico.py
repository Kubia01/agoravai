import sqlite3
import os
from fpdf import FPDF
from datetime import datetime
import json
from utils.formatters import format_date, format_cnpj, format_phone

def clean_text(text):
    """Substitui tabs por espaços e remove caracteres problemáticos"""
    if text is None:
        return ""
    text = text.replace('\t', '    ')
    return text

class RelatorioPDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_auto_page_break(auto=True, margin=25)
        self.baby_blue = (137, 207, 240)  # Azul bebê corporativo
        self.first_page = True
    
    def header(self):
        # Desenha a borda em todas as páginas
        self.set_line_width(0.5)
        self.rect(5, 5, 200, 287)  # A4: 210x297, então 5mm de margem
        
        # Cabeçalho corporativo
        self.set_font("Arial", 'B', 11)
        self.set_y(10)
        self.cell(0, 5, clean_text("WORLD COMP DO BRASIL COMPRESSORES EIRELI"), 0, 1)
        self.cell(0, 5, clean_text("ORDEM DE SERVIÇO DE CAMPO SIMPLIFICADA"), 0, 1)
        self.cell(0, 5, clean_text(f"RELATÓRIO Nº: {getattr(self, 'numero_relatorio', 'N/A')}"), 0, 1)
        self.cell(0, 5, clean_text(f"DATA: {getattr(self, 'data_relatorio', 'N/A')}"), 0, 1)
        
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
        
        self.set_font("Arial", '', 10)
        self.set_text_color(*self.baby_blue)
        self.cell(0, 5, clean_text("Rua Fernando Pessoa, 17 - Batistini - São Bernardo do Campo/SP - CEP 09844-390"), 0, 1, 'C')
        self.cell(0, 5, clean_text("E-mail: rogerio@worldcompressores.com.br | Fone: (11) 4543-6896/4543-6857/4357-8062"), 0, 1, 'C')
        
        self.set_text_color(0, 0, 0)

    def section_title(self, title):
        self.set_text_color(*self.baby_blue)
        self.set_font("Arial", 'B', 12)
        self.cell(0, 8, clean_text(title), 0, 1, 'L')
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
        
        # Construir a query dinamicamente com base nas colunas existentes
        base_columns = ["r.numero_relatorio", "r.data_criacao", "c.nome", "c.cnpj", "c.endereco", "c.cidade", "c.estado"]
        
        # Verificar quais colunas existem na tabela
        report_columns = []
        column_map = {
            "formulario_servico": "r.formulario_servico",
            "tipo_servico": "r.tipo_servico",
            "descricao_servico": "r.descricao_servico",
            "condicao_encontrada": "r.condicao_encontrada",
            "placa_identificacao": "r.placa_identificacao",
            "acoplamento": "r.acoplamento",
            "aspectos_rotores": "r.aspectos_rotores",
            "valvulas_acopladas": "r.valvulas_acopladas",
            "data_recebimento": "r.data_recebimento",
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
        
        # Obter anexos - verificar se a coluna existe
        anexos = []
        if 'anexos' in column_names:
            c.execute("SELECT anexos FROM relatorios_tecnicos WHERE id = ?", (relatorio_id,))
            anexos_result = c.fetchone()
            if anexos_result and anexos_result[0]:
                try:
                    anexos_data = anexos_result[0]
                    if isinstance(anexos_data, str):
                        anexos = json.loads(anexos_data)
                    elif isinstance(anexos_data, list):
                        anexos = anexos_data
                except (json.JSONDecodeError, TypeError):
                    anexos = []
        
        # Criar PDF
        pdf = RelatorioPDF()
        
        # Configurar dados para cabeçalho
        pdf.numero_relatorio = get_value("numero_relatorio")
        pdf.data_relatorio = format_date(get_value("data_criacao"))
        
        pdf.add_page()
        
        # Identificação do Cliente
        pdf.section_title("IDENTIFICAÇÃO DO CLIENTE")
        pdf.set_font("Arial", "", 11)
        
        nome_cliente = get_value("nome")
        if nome_cliente:
            pdf.cell(0, 6, f"CLIENTE: {nome_cliente}", 0, 1)
            
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
        
        # Dados do Serviço
        pdf.section_title("DADOS DO SERVIÇO")
        
        numero_rel = get_value("numero_relatorio")
        if numero_rel:
            pdf.cell(0, 6, f"Nº RELATÓRIO: {numero_rel}", 0, 1)
            
        data_criacao = get_value("data_criacao")
        if data_criacao:
            pdf.cell(0, 6, f"DATA: {format_date(data_criacao)}", 0, 1)
            
        formulario = get_value("formulario_servico")
        if formulario:
            pdf.cell(0, 6, f"FORMULÁRIO: {formulario}", 0, 1)
            
        tipo_servico = get_value("tipo_servico")
        if tipo_servico:
            pdf.cell(0, 6, f"TIPO SERVIÇO: {tipo_servico}", 0, 1)
            
        data_recebimento = get_value("data_recebimento")
        if data_recebimento:
            pdf.cell(0, 6, f"DATA RECEBIMENTO: {format_date(data_recebimento)}", 0, 1)
            
        descricao_servico = get_value("descricao_servico")
        if descricao_servico:
            pdf.cell(0, 6, "DESCRIÇÃO DA ATIVIDADE:", 0, 1)
            pdf.multi_cell(0, 5, clean_text(descricao_servico))
        
        pdf.ln(5)
        
        # Eventos em Campo
        if eventos:
            pdf.section_title("EVENTOS EM CAMPO")
            pdf.set_font("Arial", "B", 10)
            pdf.cell(40, 6, "HORA", 1, 0, 'C')
            pdf.cell(60, 6, "EVENTO", 1, 0, 'C')
            pdf.cell(40, 6, "TIPO", 1, 0, 'C')
            pdf.cell(40, 6, "TÉCNICO", 1, 1, 'C')
            
            pdf.set_font("Arial", "", 10)
            for evento in eventos:
                tecnico, data_hora, desc_evento, tipo_evento = evento
                pdf.cell(40, 6, str(data_hora)[:16] if data_hora else "", 1)
                pdf.cell(60, 6, str(desc_evento)[:25] if desc_evento else "", 1)
                pdf.cell(40, 6, str(tipo_evento) if tipo_evento else "", 1)
                pdf.cell(40, 6, str(tecnico) if tecnico else "", 1)
                pdf.ln()
            pdf.ln(5)
        
        # Condição do Equipamento
        pdf.section_title("CONDIÇÃO DO EQUIPAMENTO")
        
        condicao_inicial = get_value("condicao_inicial")
        if condicao_inicial:
            pdf.set_font("Arial", "B", 10)
            pdf.cell(0, 6, "CONDIÇÃO INICIAL:", 0, 1)
            pdf.set_font("Arial", "", 10)
            pdf.multi_cell(0, 5, clean_text(condicao_inicial))
            pdf.ln(2)
        
        condicao_atual = get_value("condicao_atual")
        if condicao_atual:
            pdf.set_font("Arial", "B", 10)
            pdf.cell(0, 6, "CONDIÇÃO ATUAL:", 0, 1)
            pdf.set_font("Arial", "", 10)
            pdf.multi_cell(0, 5, clean_text(condicao_atual))
            pdf.ln(2)
        
        condicao_encontrada = get_value("condicao_encontrada")
        if condicao_encontrada:
            pdf.set_font("Arial", "B", 10)
            pdf.cell(0, 6, "CONDIÇÃO ENCONTRADA:", 0, 1)
            pdf.set_font("Arial", "", 10)
            pdf.multi_cell(0, 5, clean_text(condicao_encontrada))
            pdf.ln(2)
        
        placa_id = get_value("placa_identificacao")
        if placa_id:
            pdf.set_font("Arial", "", 11)
            pdf.cell(0, 6, f"PLACA DE IDENTIFICAÇÃO: {placa_id}", 0, 1)
        
        acoplamento = get_value("acoplamento")
        if acoplamento:
            pdf.cell(0, 6, f"ACOPLAMENTO: {acoplamento}", 0, 1)
        
        aspectos_rotores = get_value("aspectos_rotores")
        if aspectos_rotores:
            pdf.cell(0, 6, f"ASPECTOS DOS ROTORES: {aspectos_rotores}", 0, 1)
        
        valvulas = get_value("valvulas_acopladas")
        if valvulas:
            pdf.cell(0, 6, f"VÁLVULAS ACOPLADAS: {valvulas}", 0, 1)
        
        # Anexos
        if anexos:
            pdf.ln(5)
            pdf.section_title("ANEXOS")
            for i, anexo in enumerate(anexos, 1):
                if isinstance(anexo, dict):
                    nome = anexo.get('nome', f'Anexo {i}')
                    descricao = anexo.get('descricao', '')
                    caminho = anexo.get('caminho', '')
                    
                    pdf.set_font("Arial", "B", 10)
                    pdf.cell(0, 6, f"Anexo {i}: {nome}", 0, 1)
                    
                    if descricao:
                        pdf.set_font("Arial", "", 10)
                        pdf.multi_cell(0, 5, f"Descrição: {descricao}")
                        
                    if caminho:
                        pdf.set_font("Arial", "I", 9)
                        pdf.cell(0, 5, f"Arquivo: {caminho}", 0, 1)
                        
                    pdf.ln(2)
                else:
                    pdf.set_font("Arial", "", 10)
                    pdf.cell(0, 6, f"Anexo {i}: {str(anexo)}", 0, 1)
                    pdf.ln(2)
        
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