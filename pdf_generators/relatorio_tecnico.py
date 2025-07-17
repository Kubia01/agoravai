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
    
    def chapter_title(self, title):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, title, 0, 1)
        self.ln(2)
    
    def chapter_body(self, body):
        self.set_font("Arial", "", 10)
        self.multi_cell(0, 5, body)
        self.ln()

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
            "data_recebimento": "r.data_recebimento"
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
            
        # Log para debug
        print(f"Dados do relatório: {relatorio_data}")
        print(f"Colunas esperadas: {len(base_columns) + len(report_columns)}")
        print(f"Colunas recebidas: {len(relatorio_data) if relatorio_data else 0}")
        
        # Criar um dicionário para acessar valores por nome ao invés de índices
        column_indices = {}
        
        # Mapear colunas base para índices
        for i, col_name in enumerate(base_columns):
            col_key = col_name.split('.')[-1]  # Remove table prefix
            column_indices[col_name] = i
            column_indices[col_key] = i
            
        # Mapear colunas de relatório para índices
        for i, col_full in enumerate(report_columns):
            idx = i + len(base_columns)
            if " as " in col_full:
                col_name = col_full.split(" as ")[1]
                column_indices[col_name] = idx
            else:
                col_name = col_full.split('.')[-1]  # Remove table prefix
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
        
        # Obter fotos/anexos
        fotos = []
        if 'fotos' in column_names:
            c.execute("SELECT fotos FROM relatorios_tecnicos WHERE id = ?", (relatorio_id,))
            fotos_str = c.fetchone()[0]
            if fotos_str and isinstance(fotos_str, str):
                fotos = [path for path in fotos_str.split(';') if path.strip()]
        
        # Criar PDF
        pdf = RelatorioPDF()
        pdf.add_page()
        
        # Identificação do Cliente
        pdf.chapter_title("IDENTIFICAÇÃO DO CLIENTE")
        pdf.set_font("Arial", "B", 10)
        pdf.cell(40, 6, "NOME DO SITE:")
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 6, get_value("nome"), 0, 1)
        
        pdf.set_font("Arial", "B", 10)
        pdf.cell(40, 6, "CNPJ:")
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 6, format_cnpj(get_value("cnpj")), 0, 1)
        
        endereco = get_value("endereco")
        if endereco:  # endereco
            pdf.set_font("Arial", "B", 10)
            pdf.cell(40, 6, "ENDEREÇO:")
            pdf.set_font("Arial", "", 10)
            pdf.cell(0, 6, endereco, 0, 1)
        
        cidade = get_value("cidade") 
        estado = get_value("estado")
        if cidade and estado:  # cidade, estado
            pdf.set_font("Arial", "B", 10)
            pdf.cell(40, 6, "CIDADE/UF:")
            pdf.set_font("Arial", "", 10)
            pdf.cell(0, 6, f"{cidade}/{estado}", 0, 1)
        
        pdf.ln(5)
        
        # Dados do Serviço
        pdf.chapter_title("DETALHAMENTO DO SERVIÇO")
        
        formulario = get_value("formulario_servico")
        if formulario:  # formulario_servico
            pdf.set_font("Arial", "B", 10)
            pdf.cell(40, 6, "FORMULÁRIO:")
            pdf.set_font("Arial", "", 10)
            pdf.cell(0, 6, formulario, 0, 1)
        
        tipo = get_value("tipo_servico")
        if tipo:  # tipo_servico
            pdf.set_font("Arial", "B", 10)
            pdf.cell(40, 6, "TIPO SERVIÇO:")
            pdf.set_font("Arial", "", 10)
            pdf.cell(0, 6, tipo, 0, 1)
        
        data_receb = get_value("data_recebimento")
        if data_receb:  # data_recebimento
            pdf.set_font("Arial", "B", 10)
            pdf.cell(40, 6, "DATA RECEB.:")
            pdf.set_font("Arial", "", 10)
            pdf.cell(0, 6, format_date(data_receb), 0, 1)
        
        descricao = get_value("descricao_servico")
        if descricao:  # descricao_servico
            pdf.set_font("Arial", "B", 10)
            pdf.cell(0, 6, "DESCRIÇÃO DA ATIVIDADE:", 0, 1)
            pdf.set_font("Arial", "", 10)
            pdf.multi_cell(0, 5, descricao)
        
        pdf.ln(5)
        
        # Eventos em Campo
        if eventos:
            pdf.chapter_title("EVENTOS EM CAMPO")
            pdf.set_font("Arial", "B", 10)
            pdf.cell(40, 6, "HORA", border=1)
            pdf.cell(60, 6, "EVENTO", border=1)
            pdf.cell(40, 6, "TIPO", border=1)
            pdf.cell(40, 6, "TÉCNICO", border=1)
            pdf.ln()
            
            pdf.set_font("Arial", "", 10)
            for evento in eventos:
                pdf.cell(40, 6, evento[1], border=1)
                pdf.cell(60, 6, evento[2], border=1)
                pdf.cell(40, 6, evento[3], border=1)
                pdf.cell(40, 6, evento[0], border=1)
                pdf.ln()
            
            pdf.ln(5)
        
        # Condição do Equipamento
        pdf.chapter_title("CONDIÇÃO DO EQUIPAMENTO")
        
        condicao_inicial = get_value("condicao_inicial")
        if condicao_inicial:
            pdf.set_font("Arial", "B", 10)
            pdf.cell(0, 6, "CONDIÇÃO INICIAL:", 0, 1)
            pdf.set_font("Arial", "", 10)
            pdf.multi_cell(0, 5, condicao_inicial)
            pdf.ln(2)
        
        condicao_atual = get_value("condicao_atual")
        if condicao_atual:
            pdf.set_font("Arial", "B", 10)
            pdf.cell(0, 6, "CONDIÇÃO ATUAL:", 0, 1)
            pdf.set_font("Arial", "", 10)
            pdf.multi_cell(0, 5, condicao_atual)
            pdf.ln(2)
        
        condicao_encontrada = get_value("condicao_encontrada")
        if condicao_encontrada:
            pdf.set_font("Arial", "B", 10)
            pdf.cell(0, 6, "CONDIÇÃO ENCONTRADA:", 0, 1)
            pdf.set_font("Arial", "", 10)
            pdf.multi_cell(0, 5, condicao_encontrada)
            pdf.ln(2)
        
        placa_id = get_value("placa_identificacao")
        if placa_id:
            pdf.set_font("Arial", "B", 10)
            pdf.cell(70, 6, "PLACA DE IDENTIFICAÇÃO:", 0, 0)
            pdf.set_font("Arial", "", 10)
            pdf.cell(0, 6, placa_id, 0, 1)
        
        acoplamento = get_value("acoplamento")
        if acoplamento:
            pdf.set_font("Arial", "B", 10)
            pdf.cell(70, 6, "ACOPLAMENTO:", 0, 0)
            pdf.set_font("Arial", "", 10)
            pdf.cell(0, 6, acoplamento, 0, 1)
        
        aspectos_rotores = get_value("aspectos_rotores")
        if aspectos_rotores:
            pdf.set_font("Arial", "B", 10)
            pdf.cell(70, 6, "ASPECTOS DOS ROTORES:", 0, 0)
            pdf.set_font("Arial", "", 10)
            pdf.cell(0, 6, aspectos_rotores, 0, 1)
        
        valvulas = get_value("valvulas_acopladas")
        if valvulas:
            pdf.set_font("Arial", "B", 10)
            pdf.cell(70, 6, "VÁLVULAS ACOPLADAS:", 0, 0)
            pdf.set_font("Arial", "", 10)
            pdf.cell(0, 6, valvulas, 0, 1)
        
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