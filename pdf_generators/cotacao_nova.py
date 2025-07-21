import sqlite3
import os
import datetime
import sys
from fpdf import FPDF
from database import DB_NAME
from utils.formatters import format_cep, format_phone, format_currency, format_date, format_cnpj

# Adicionar o diretório assets ao path para importar os templates
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from assets.filiais.filiais_config import obter_filial, obter_usuario_cotacao, obter_template_capa_jpeg

def clean_text(text):
    """Substitui tabs por espaços e remove caracteres problemáticos"""
    if text is None:
        return ""
    
    # Converter para string se não for
    text = str(text)
    
    # Substitui tabs por 4 espaços
    text = text.replace('\t', '    ')
    
    # Substituir caracteres especiais problemáticos
    replacements = {
        # Bullets e símbolos especiais
        '•': '- ',
        '●': '- ',
        '◦': '- ',
        '◆': '- ',
        '▪': '- ',
        '▫': '- ',
        '★': '* ',
        '☆': '* ',
        
        # Aspas especiais
        '"': '"',
        '"': '"',
        ''': "'",
        ''': "'",
        
        # Travessões
        '–': '-',
        '—': '-',
        
        # Outros símbolos
        '…': '...',
        '®': '(R)',
        '™': '(TM)',
        '©': '(C)',
        '°': ' graus',
        '€': 'EUR',
        '£': 'GBP',
        '¥': 'JPY',
        
        # Acentos problemáticos (fallback)
        'À': 'A', 'Á': 'A', 'Â': 'A', 'Ã': 'A', 'Ä': 'A',
        'È': 'E', 'É': 'E', 'Ê': 'E', 'Ë': 'E',
        'Ì': 'I', 'Í': 'I', 'Î': 'I', 'Ï': 'I',
        'Ò': 'O', 'Ó': 'O', 'Ô': 'O', 'Õ': 'O', 'Ö': 'O',
        'Ù': 'U', 'Ú': 'U', 'Û': 'U', 'Ü': 'U',
        'Ç': 'C', 'Ñ': 'N',
        'à': 'a', 'á': 'a', 'â': 'a', 'ã': 'a', 'ä': 'a',
        'è': 'e', 'é': 'e', 'ê': 'e', 'ë': 'e',
        'ì': 'i', 'í': 'i', 'î': 'i', 'ï': 'i',
        'ò': 'o', 'ó': 'o', 'ô': 'o', 'õ': 'o', 'ö': 'o',
        'ù': 'u', 'ú': 'u', 'û': 'u', 'ü': 'u',
        'ç': 'c', 'ñ': 'n',
    }
    
    # Aplicar substituições
    for old_char, new_char in replacements.items():
        text = text.replace(old_char, new_char)
    
    # Remover caracteres não ASCII restantes
    try:
        # Tentar encoding/decoding para limpar caracteres problemáticos
        text = text.encode('ascii', 'ignore').decode('ascii')
    except:
        # Se falhar, usar apenas caracteres básicos
        text = ''.join(char for char in text if ord(char) < 128)
    
    return text

class PDFCotacao(FPDF):
    def __init__(self, dados_filial, dados_usuario, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.first_page = True  
        self.baby_blue = (137, 207, 240)  # Azul bebê #89CFF0
        self.dados_filial = dados_filial
        self.dados_usuario = dados_usuario
        
        # Configurar encoding para suportar mais caracteres
        self.set_doc_option('core_fonts_encoding', 'latin-1')

    def header(self):
        # Pular header na primeira página (que será a capa JPEG)
        if self.first_page:
            self.first_page = False
            return
        
        # APENAS na segunda página (primeira com conteúdo): mostrar logo centralizado
        if getattr(self, 'page_no', 0) == 2 and not getattr(self, 'logo_adicionado', False):
            # Logo centralizado APENAS na primeira página de conteúdo
            logo_path = self.dados_filial.get("logo_path", "assets/logos/world_comp_brasil.jpg")
            if os.path.exists(logo_path):
                logo_height = 25
                logo_width = logo_height * 1.5
                # Centralizar logo
                x_centro = (210 - logo_width) / 2
                self.image(logo_path, x=x_centro, y=15, h=logo_height)
                self.logo_adicionado = True
            
        # Desenha a borda em todas as páginas de conteúdo
        self.set_line_width(0.5)
        self.rect(5, 5, 200, 287)  # A4: 210x297, então 5mm de margem

        # Header simples para páginas de conteúdo (sem logo repetido)
        self.set_font("Arial", 'B', 11)
        
        # Dados da proposta no canto superior direito
        self.set_xy(120, 10)
        self.cell(0, 5, clean_text(self.dados_filial.get('nome', '')), 0, 1, 'R')
        self.set_x(120)
        self.cell(0, 5, clean_text("PROPOSTA COMERCIAL:"), 0, 1, 'R')
        self.set_x(120)
        self.cell(0, 5, clean_text(f"NÚMERO: {self.numero_proposta}"), 0, 1, 'R')
        self.set_x(120)
        self.cell(0, 5, clean_text(f"DATA: {self.data_proposta}"), 0, 1, 'R')
        
        # Linha de separação
        self.line(10, 35, 200, 35)
        self.ln(10)

    def footer(self):
        # Posiciona o rodapé a 1.5 cm do fundo
        self.set_y(-20)
        
        # Linha divisória acima do rodapé
        self.line(10, self.get_y() - 5, 200, self.get_y() - 5)
        
        # Usar fonte padrão e cor azul bebê - RODAPÉ com dados da filial
        self.set_font("Arial", '', 10)  
        self.set_text_color(*self.baby_blue)  
        
        # Informações do rodapé baseadas na filial selecionada
        endereco_completo = f"{self.dados_filial.get('endereco', '')} - CEP: {self.dados_filial.get('cep', '')}"
        telefones_email = f"E-mail: {self.dados_filial.get('email', '')} | Fone: {self.dados_filial.get('telefones', '')}"
        cnpj_ie = f"CNPJ: {self.dados_filial.get('cnpj', '')} | I.E.: {self.dados_filial.get('inscricao_estadual', '')}"
        
        self.cell(0, 4, clean_text(endereco_completo), 0, 1, 'C')
        self.cell(0, 4, clean_text(telefones_email), 0, 1, 'C')
        self.cell(0, 4, clean_text(cnpj_ie), 0, 1, 'C')
        
        # Resetar cor para preto
        self.set_text_color(0, 0, 0)
    
    @staticmethod
    def obter_composicao_kit(kit_id):
        """Obtém a composição de um kit a partir do banco de dados"""
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        composicao = []
        
        try:
            c.execute("""
                SELECT p.nome, kc.quantidade 
                FROM kit_items kc
                JOIN produtos p ON kc.produto_id = p.id
                WHERE kc.kit_id = ?
            """, (kit_id,))
            
            for row in c.fetchall():
                nome, quantidade = row
                composicao.append(f"{quantidade} x {nome}")
                
        except sqlite3.Error:
            composicao = ["Erro ao carregar composição"]
        finally:
            conn.close()
        
        return composicao

def gerar_pdf_cotacao_nova(cotacao_id, db_name, current_user=None):
    """
    Versão melhorada do gerador de PDF de cotações
    - Corrige problemas de logo
    - Adiciona capa personalizada por usuário
    - Corrige problemas de descrição e valores
    - Inclui CNPJ da filial no rodapé
    """
    conn = None
    try:
        conn = sqlite3.connect(db_name)
        c = conn.cursor()   

        # Obter dados da cotação (incluindo filial_id)
        c.execute("""
            SELECT 
                cot.id, cot.numero_proposta, cot.modelo_compressor, cot.numero_serie_compressor, 
                cot.descricao_atividade, cot.observacoes, cot.data_criacao,
                cot.valor_total, cot.tipo_frete, cot.condicao_pagamento, cot.prazo_entrega,
                cli.id AS cliente_id, cli.nome AS cliente_nome, cli.nome_fantasia, cli.endereco, cli.email, 
                cli.telefone, cli.site, cli.cnpj, cli.cidade, cli.estado, cli.cep,
                usr.nome_completo, usr.email AS usr_email, usr.telefone AS usr_telefone, usr.username,
                cot.moeda, cot.relacao_pecas, cot.filial_id
            FROM cotacoes AS cot
            JOIN clientes AS cli ON cot.cliente_id = cli.id
            JOIN usuarios AS usr ON cot.responsavel_id = usr.id
            WHERE cot.id = ?
        """, (cotacao_id,))
        cotacao_data = c.fetchone()

        if not cotacao_data:
            return False, "Cotação não encontrada para gerar PDF."

        (
            cot_id, numero_proposta, modelo_compressor, numero_serie_compressor,
            descricao_atividade, observacoes, data_criacao,
            valor_total, tipo_frete, condicao_pagamento, prazo_entrega,
            cliente_id, cliente_nome, cliente_nome_fantasia, cliente_endereco, cliente_email, 
            cliente_telefone, cliente_site, cliente_cnpj, cliente_cidade, 
            cliente_estado, cliente_cep,
            responsavel_nome, responsavel_email, responsavel_telefone, responsavel_username,
            moeda, relacao_pecas, filial_id
        ) = cotacao_data

        # Obter dados da filial
        dados_filial = obter_filial(filial_id or 2)  # Default para filial 2
        if not dados_filial:
            return False, "Dados da filial não encontrados."

        # Obter configurações do usuário
        dados_usuario = obter_usuario_cotacao(responsavel_username)
        if not dados_usuario:
            dados_usuario = {
                'nome_completo': responsavel_nome,
                'assinatura': f"{responsavel_nome}\nVendas"
            }

        # Obter contato principal
        c.execute("""
            SELECT nome FROM contatos 
            WHERE cliente_id = ? 
            LIMIT 1
        """, (cliente_id,))
        contato_principal = c.fetchone()
        contato_nome = contato_principal[0] if contato_principal else "Não informado"

        # Obter itens da cotação - CORRIGIDO para garantir que dados não sejam nulos
        c.execute("""
            SELECT 
                ic.id, ic.tipo, ic.item_nome, ic.quantidade, 
                COALESCE(ic.descricao, p.descricao, '') as descricao, 
                COALESCE(ic.valor_unitario, 0) as valor_unitario, 
                COALESCE(ic.valor_total_item, 0) as valor_total_item,
                ic.mao_obra, ic.deslocamento, ic.estadia, ic.produto_id
            FROM itens_cotacao ic
            LEFT JOIN produtos p ON ic.produto_id = p.id
            WHERE ic.cotacao_id = ?
            ORDER BY ic.id
        """, (cotacao_id,))
        itens_cotacao = c.fetchall()

        # Criar o PDF
        pdf = PDFCotacao(dados_filial, dados_usuario, orientation='P', unit='mm', format='A4')
        pdf.set_auto_page_break(auto=True, margin=25)
        
        # Configurar dados para cabeçalho/footer
        pdf.numero_proposta = numero_proposta
        pdf.data_proposta = format_date(data_criacao)

        # PÁGINA 1: CAPA PERSONALIZADA JPEG
        # =================================
        
        # Verificar se existe template JPEG para o usuário
        template_jpeg_path = obter_template_capa_jpeg(responsavel_username)
        
        if template_jpeg_path and os.path.exists(template_jpeg_path):
            # Usar template JPEG personalizado
            pdf.add_page()
            # Adicionar template JPEG ocupando toda a página A4
            pdf.image(template_jpeg_path, x=0, y=0, w=210, h=297)
        else:
            # Fallback: capa simples sem template específico
            pdf.add_page()
            pdf.set_font("Arial", 'B', 24)
            pdf.set_y(100)
            pdf.cell(0, 15, clean_text("PROPOSTA COMERCIAL"), 0, 1, 'C')
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, clean_text(f"Nº {numero_proposta}"), 0, 1, 'C')
            pdf.set_font("Arial", '', 12)
            pdf.cell(0, 8, clean_text(f"Data: {format_date(data_criacao)}"), 0, 1, 'C')
            
            # Dados do cliente
            pdf.set_y(150)
            cliente_nome_display = cliente_nome_fantasia if cliente_nome_fantasia else cliente_nome
            pdf.cell(0, 8, clean_text(f"Cliente: {cliente_nome_display}"), 0, 1, 'C')
            
            # Dados da filial
            pdf.set_y(200)
            pdf.cell(0, 6, clean_text(dados_filial.get('nome', '')), 0, 1, 'C')
            pdf.cell(0, 5, clean_text(f"CNPJ: {dados_filial.get('cnpj', '')}"), 0, 1, 'C')

        # PÁGINA 2: CARTA DE APRESENTAÇÃO
        # ==============================
        pdf.add_page()
        pdf.set_font("Arial", size=11)
        
        # Texto de apresentação com nome personalizado
        modelo_text = f" {modelo_compressor}" if modelo_compressor else ""
        nome_vendedor = dados_usuario.get('nome_completo', responsavel_nome)
        
        texto_apresentacao = clean_text(f"""
Prezados Senhores,

Agradecemos a sua solicitação e apresentamos nossas condições comerciais para fornecimento de peças para o compressor{modelo_text}.

A World Comp coloca-se a disposição para analisar, corrigir, prestar esclarecimentos para adequação das especificações e necessidades dos clientes, para tanto basta informar o número da proposta e revisão.


Atenciosamente,
        """)
        pdf.multi_cell(0, 5, texto_apresentacao)
        
        # Assinatura personalizada
        pdf.set_y(230)
        pdf.set_font("Arial", 'B', 11)
        assinatura_linhas = dados_usuario.get('assinatura', f"{responsavel_nome}\nVendas").split('\n')
        for linha in assinatura_linhas:
            pdf.cell(0, 6, clean_text(linha), 0, 1, 'L')
        
        pdf.set_font("Arial", '', 11)
        pdf.cell(0, 5, clean_text(f"Fone: {dados_filial.get('telefones', '')}"), 0, 1, 'L')
        pdf.cell(0, 5, clean_text(dados_filial.get('nome', '')), 0, 1, 'L')

        # PÁGINA 3: SOBRE A EMPRESA (mantendo conteúdo original)
        # =====================================================
        pdf.add_page()
        pdf.set_y(45)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, clean_text("SOBRE A WORLD COMP"), 0, 1, 'L')
        pdf.set_font("Arial", '', 11)
        
        sobre_empresa = clean_text("Há mais de uma década no mercado de manutenção de compressores de ar de parafuso, de diversas marcas, atendemos clientes em todo território brasileiro.")
        pdf.multi_cell(0, 5, sobre_empresa)
        pdf.ln(5)
        
        # Seções sobre a empresa
        secoes = [
            ("FORNECIMENTO, SERVIÇO E LOCAÇÃO", """
A World Comp oferece os serviços de Manutenção Preventiva e Corretiva em Compressores e Unidades Compressoras, Venda de peças, Locação de compressores, Recuperação de Unidades Compressoras, Recuperação de Trocadores de Calor e Contrato de Manutenção em compressores de marcas como: Atlas Copco, Ingersoll Rand, Chicago Pneumatic entre outros.
            """),
            ("CONTE CONOSCO PARA UMA PARCERIA", """
Adaptamos nossa oferta para suas necessidades, objetivos e planejamento. Trabalhamos para que seu processo seja eficiente.
            """),
            ("MELHORIA CONTÍNUA", """
Continuamente investindo em comprometimento, competência e eficiência de nossos serviços, produtos e estrutura para garantirmos a máxima eficiência de sua produtividade.
            """),
            ("QUALIDADE DE SERVIÇOS", """
Com uma equipe de técnicos altamente qualificados e constantemente treinados para atendimentos em todos os modelos de compressores de ar, a World Comp oferece garantia de excelente atendimento e produtividade superior com rapidez e eficácia.
            """)
        ]
        
        for titulo, texto in secoes:
            pdf.set_text_color(*pdf.baby_blue)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 8, clean_text(titulo), 0, 1, 'L')
            
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", '', 11)
            pdf.multi_cell(0, 5, clean_text(texto))
            pdf.ln(3)
        
        texto_final = clean_text("Nossa missão é ser sua melhor parceria com sinônimo de qualidade, garantia e o melhor custo benefício.")
        pdf.multi_cell(0, 5, texto_final)
        pdf.ln(10)
        
        # PÁGINAS SEGUINTES: DETALHES DA PROPOSTA
        # ======================================
        pdf.add_page()
        
        # Ajustar posição inicial para dar espaço ao logo centralizado
        pdf.set_y(50)  # Começar mais abaixo para dar espaço ao logo
        
        # Dados da proposta
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, clean_text(f"PROPOSTA Nº {numero_proposta}"), 0, 1, 'L')
        pdf.set_font("Arial", '', 11)
        pdf.cell(0, 6, clean_text(f"Data: {format_date(data_criacao)}"), 0, 1, 'L')
        pdf.cell(0, 6, clean_text(f"Responsável: {responsavel_nome}"), 0, 1, 'L')
        pdf.cell(0, 6, clean_text(f"Telefone Responsável: {format_phone(responsavel_telefone)}"), 0, 1, 'L')
        pdf.ln(10)

        # Dados do cliente
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 6, clean_text("DADOS DO CLIENTE:"), 0, 1, 'L')
        pdf.set_font("Arial", '', 11)
        
        cliente_nome_display = cliente_nome_fantasia if cliente_nome_fantasia else cliente_nome
        pdf.cell(0, 5, clean_text(f"Empresa: {cliente_nome_display}"), 0, 1, 'L')
        if cliente_cnpj:
            pdf.cell(0, 5, clean_text(f"CNPJ: {format_cnpj(cliente_cnpj)}"), 0, 1, 'L')
        if contato_nome and contato_nome != "Não informado":
            pdf.cell(0, 5, clean_text(f"Contato: {contato_nome}"), 0, 1, 'L')
        pdf.ln(5)

        # Dados do compressor
        if modelo_compressor or numero_serie_compressor:
            pdf.set_font("Arial", 'B', 11)
            pdf.cell(0, 6, clean_text("DADOS DO COMPRESSOR:"), 0, 1, 'L')
            pdf.set_font("Arial", '', 11)
            if modelo_compressor:
                pdf.cell(0, 5, clean_text(f"Modelo: {modelo_compressor}"), 0, 1, 'L')
            if numero_serie_compressor:
                pdf.cell(0, 5, clean_text(f"Nº de Série: {numero_serie_compressor}"), 0, 1, 'L')
            pdf.ln(5)

        # Descrição - GARANTIR que não seja vazia
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 6, clean_text("DESCRIÇÃO DO SERVIÇO:"), 0, 1, 'L')
        pdf.set_font("Arial", '', 11)
        descricao_final = descricao_atividade if descricao_atividade and descricao_atividade.strip() else "Fornecimento de peças e serviços para compressor"
        pdf.multi_cell(0, 5, clean_text(descricao_final))
        pdf.ln(10)

        # Relação de Peças - GARANTIR que seja exibida corretamente
        if relacao_pecas and relacao_pecas.strip():
            relacao_sem_prefixo = relacao_pecas.replace("Serviço: ", "").replace("Produto: ", "").replace("Kit: ", "")
            pdf.set_font("Arial", 'B', 11)
            pdf.cell(0, 6, clean_text("RELAÇÃO DE PEÇAS A SEREM SUBSTITUÍDAS:"), 0, 1, 'L')
            pdf.set_font("Arial", '', 11)
            pdf.multi_cell(0, 5, clean_text(relacao_sem_prefixo))
            pdf.ln(5)

        # ITENS DA PROPOSTA - CORRIGIDO
        # =============================
        if itens_cotacao:
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 8, clean_text("ITENS DA PROPOSTA"), 0, 1, 'C')
            pdf.ln(5)

            # Configurar larguras das colunas
            col_widths = [15, 70, 20, 35, 30]
            
            # Cabeçalho da tabela
            pdf.set_x(10)
            pdf.set_fill_color(50, 100, 150)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Arial", 'B', 11)
            pdf.cell(col_widths[0], 8, clean_text("Item"), 1, 0, 'C', 1)
            pdf.cell(col_widths[1], 8, clean_text("Descrição"), 1, 0, 'L', 1)
            pdf.cell(col_widths[2], 8, clean_text("Qtd."), 1, 0, 'C', 1)
            pdf.cell(col_widths[3], 8, clean_text("Vl. Unit."), 1, 0, 'R', 1)
            pdf.cell(col_widths[4], 8, clean_text("Vl. Total"), 1, 1, 'R', 1)

            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", '', 11)
            item_counter = 1
            
            for item in itens_cotacao:
                (item_id, item_tipo, item_nome, quantidade, descricao, 
                 valor_unitario, valor_total_item, 
                 mao_obra, deslocamento, estadia, produto_id) = item
                
                # GARANTIR que descrição não seja vazia
                if not descricao or not descricao.strip():
                    descricao = item_nome or "Item sem descrição"
                
                # GARANTIR que valores não sejam zero quando deveriam ter valor
                # Converter valores para float para garantir cálculos corretos
                try:
                    valor_unitario = float(valor_unitario) if valor_unitario else 0.0
                    valor_total_item = float(valor_total_item) if valor_total_item else 0.0
                    quantidade = float(quantidade) if quantidade else 1.0
                except (ValueError, TypeError):
                    valor_unitario = 0.0
                    valor_total_item = 0.0
                    quantidade = 1.0
                
                # Recalcular valores se necessário
                if valor_unitario == 0 and valor_total_item > 0 and quantidade > 0:
                    valor_unitario = valor_total_item / quantidade
                elif valor_total_item == 0 and valor_unitario > 0 and quantidade > 0:
                    valor_total_item = valor_unitario * quantidade
                elif valor_unitario > 0 and valor_total_item == 0 and quantidade > 0:
                    valor_total_item = valor_unitario * quantidade

                # Tratamento para diferentes tipos de item
                descricao_final = descricao
                
                if item_tipo == "Kit" and produto_id:
                    composicao = PDFCotacao.obter_composicao_kit(produto_id)
                    if composicao and composicao != ["Erro ao carregar composição"]:
                        descricao_final = f"Kit: {item_nome}\nComposição:\n" + "\n".join(composicao)
                    else:
                        descricao_final = f"Kit: {item_nome}\nDescrição: {descricao}"
                
                elif item_tipo == "Serviço":
                    descricao_final = f"Serviço: {item_nome}"
                    if descricao and descricao.strip():
                        descricao_final += f"\nDetalhes: {descricao}"
                    if mao_obra or deslocamento or estadia:
                        descricao_final += "\nComposição:"
                        if mao_obra and mao_obra > 0:
                            descricao_final += f"\n- Mão de obra: R$ {mao_obra:.2f}"
                        if deslocamento and deslocamento > 0:
                            descricao_final += f"\n- Deslocamento: R$ {deslocamento:.2f}"
                        if estadia and estadia > 0:
                            descricao_final += f"\n- Estadia: R$ {estadia:.2f}"

                # Calcular altura necessária para o texto
                num_linhas = descricao_final.count('\n') + 1
                altura_linha = max(num_linhas * 5, 8)

                # Posições iniciais
                x_inicial = 10
                y_inicial = pdf.get_y()

                # Item
                pdf.set_xy(x_inicial, y_inicial)
                pdf.cell(col_widths[0], altura_linha, str(item_counter), 1, 0, 'C')

                # Descrição com quebra de linha
                pdf.set_xy(x_inicial + col_widths[0], y_inicial)
                pdf.multi_cell(col_widths[1], 5, clean_text(descricao_final), 1, 'L')
                
                # Calcular altura real após multi_cell
                altura_real = pdf.get_y() - y_inicial

                # Quantidade
                pdf.set_xy(x_inicial + col_widths[0] + col_widths[1], y_inicial)
                pdf.cell(col_widths[2], altura_real, str(int(quantidade)), 1, 0, 'C')

                # Valor Unitário - Melhorado com formatação e alinhamento
                pdf.set_xy(x_inicial + col_widths[0] + col_widths[1] + col_widths[2], y_inicial)
                if valor_unitario > 0:
                    valor_unit_text = f"R$ {valor_unitario:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                else:
                    valor_unit_text = "A COMBINAR"
                pdf.cell(col_widths[3], altura_real, clean_text(valor_unit_text), 1, 0, 'R')

                # Valor Total - Melhorado com formatação e alinhamento
                pdf.set_xy(x_inicial + sum(col_widths[0:4]), y_inicial)
                if valor_total_item > 0:
                    valor_total_text = f"R$ {valor_total_item:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                else:
                    valor_total_text = "A COMBINAR"
                pdf.cell(col_widths[4], altura_real, clean_text(valor_total_text), 1, 0, 'R')
                
                # Mover para próxima linha
                pdf.set_y(y_inicial + altura_real)
                item_counter += 1

            # Total da proposta - Melhorado
            pdf.set_x(10)
            pdf.set_font("Arial", 'B', 11)
            pdf.set_fill_color(200, 200, 200)
            pdf.cell(sum(col_widths[0:4]), 8, clean_text("VALOR TOTAL DA PROPOSTA:"), 1, 0, 'R', 1)
            
            # Formatar valor total corretamente
            if valor_total and valor_total > 0:
                valor_total_text = f"R$ {valor_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            else:
                valor_total_text = "A COMBINAR"
            
            pdf.cell(col_widths[4], 8, clean_text(valor_total_text), 1, 1, 'R', 1)
            pdf.ln(10)

        # Condições comerciais
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 6, clean_text("CONDIÇÕES COMERCIAIS:"), 0, 1, 'L')
        pdf.set_font("Arial", '', 11)
        pdf.cell(0, 5, clean_text(f"Tipo de Frete: {tipo_frete if tipo_frete else 'FOB'}"), 0, 1, 'L')
        pdf.cell(0, 5, clean_text(f"Condição de Pagamento: {condicao_pagamento if condicao_pagamento else 'A combinar'}"), 0, 1, 'L')
        pdf.cell(0, 5, clean_text(f"Prazo de Entrega: {prazo_entrega if prazo_entrega else 'A combinar'}"), 0, 1, 'L')
        pdf.cell(0, 5, clean_text(f"Moeda: {moeda if moeda else 'BRL (Real Brasileiro)'}"), 0, 1, 'L')
        pdf.ln(5)

        # Observações se houver
        if observacoes and observacoes.strip():
            pdf.set_font("Arial", 'B', 11)
            pdf.cell(0, 6, clean_text("OBSERVAÇÕES:"), 0, 1, 'L')
            pdf.set_font("Arial", '', 11)
            pdf.multi_cell(0, 5, clean_text(observacoes))

        # Salvar PDF
        output_dir = os.path.join("data", "cotacoes", "arquivos")
        os.makedirs(output_dir, exist_ok=True)
        file_name = f"Proposta_{numero_proposta.replace('/', '_').replace(' ', '')}.pdf"
        pdf_path = os.path.join(output_dir, file_name)
        pdf.output(pdf_path)

        # Atualizar caminho do PDF no banco de dados
        c.execute("UPDATE cotacoes SET caminho_arquivo_pdf=? WHERE id=?", (pdf_path, cot_id))
        conn.commit()

        return True, pdf_path

    except Exception as e:
        return False, f"Erro ao gerar PDF: {str(e)}"
    finally:
        if conn:
            conn.close()

# Manter compatibilidade com versão antiga
def gerar_pdf_cotacao(cotacao_id, db_name):
    """Função de compatibilidade que chama a nova versão"""
    return gerar_pdf_cotacao_nova(cotacao_id, db_name)