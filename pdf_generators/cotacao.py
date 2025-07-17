import sqlite3
import os
import datetime
from fpdf import FPDF
from database import DB_NAME
from utils.formatters import format_cep, format_phone, format_currency, format_date, format_cnpj

def clean_text(text):
    """Substitui tabs por espaços e remove caracteres problemáticos"""
    if text is None:
        return ""
    # Substitui tabs por 4 espaços
    text = text.replace('\t', '    ')
    return text

class PDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.first_page = True  # Controle para primeira página
        self.baby_blue = (137, 207, 240)  # Novo azul claro: #89CFF0 (azul bebê)

    def header(self):
        # Desenha a borda em todas as páginas
        self.set_line_width(0.5)
        self.rect(5, 5, 200, 287)  # A4: 210x297, então 5mm de margem

        # Usar fonte padrão em negrito
        self.set_font("Arial", 'B', 11)
        
        # Dados da proposta no canto superior esquerdo
        self.set_y(10)
        self.cell(0, 5, clean_text("WORLD COMP DO BRASIL COMPRESSORES EIRELI"), 0, 1)
        self.cell(0, 5, clean_text("PROPOSTA COMERCIAL:"), 0, 1)
        self.cell(0, 5, clean_text(f"NÚMERO: {self.numero_proposta}"), 0, 1)
        self.cell(0, 5, clean_text(f"DATA: {self.data_proposta}"), 0, 1)
        
        # Linha de separação
        self.line(10, 35, 200, 35)
        self.ln(5)
        
        # Apenas na primeira página: logo e dados do cliente/empresa
        if self.first_page:
            # Logo centralizado - AUMENTADO
            logo_path = "logo.jpg"
            logo_height = 30  # Aumentado de 25 para 30
            if os.path.exists(logo_path):
                # Centralizar horizontalmente: (largura_página - largura_logo)/2
                # Considerando que a logo tem proporção 1.5:1 (largura = altura * 1.5)
                logo_width = logo_height * 1.5
                self.image(logo_path, x=(210 - logo_width) / 2, y=40, w=logo_width)
            
            # Posição para dados do cliente e empresa
            self.set_y(80)  # Aumentado para 80 para dar espaço ao logo maior
            
            # Dados do cliente (lado esquerdo)
            self.set_font("Arial", 'B', 11)
            self.cell(95, 7, clean_text("APRESENTADO PARA:"), 0, 0, 'L')
            
            # Dados da empresa (lado direito) - MAIS À DIREITA
            self.set_x(135)  # Aumentado de 110 para 120
            self.cell(0, 7, clean_text("APRESENTADO POR:"), 0, 1, 'L')
            
            # Dados do cliente
            self.set_font("Arial", 'B', 11)
            self.cell(95, 6, clean_text(self.cliente_nome), 0, 0, 'L')
            
            # Dados da empresa
            self.set_x(135)
            self.set_font("Arial", 'B', 11)
            self.cell(0, 6, clean_text("WORLD COMP DO BRASIL"), 0, 1, 'L')
            
            # CNPJ
            self.set_font("Arial", '', 11)
            self.cell(95, 6, clean_text(f"CNPJ: {format_cnpj(self.cliente_cnpj)}"), 0, 0, 'L')
            self.set_x(135)
            self.cell(0, 6, clean_text("CNPJ: 10.644.944/0001-55"), 0, 1, 'L')
            
            # Telefone
            self.cell(95, 6, clean_text(f"FONE: {format_phone(self.cliente_telefone)}"), 0, 0, 'L')
            self.set_x(135)
            self.cell(0, 6, clean_text("FONE: (11) 4543-6893/4543-6857"), 0, 1, 'L')
            
            # Contato
            self.cell(95, 6, clean_text(f"Sr(a). {self.contato_nome}"), 0, 0, 'L')
            self.set_x(135)
            self.cell(0, 6, clean_text("rogerio@worldcompressores.com.br"), 0, 1, 'L')
            
            # Responsável
            self.cell(95, 6, "", 0, 0, 'L')
            self.set_x(135)
            self.cell(0, 6, clean_text("De: Vagner Cerqueira/Rogério"), 0, 1, 'L')
            
            self.ln(10)  # Espaço antes do conteúdo
        
        # Marca que as próximas páginas não são a primeira
        self.first_page = False

    def footer(self):
        # Posiciona o rodapé a 1.5 cm do fundo
        self.set_y(-20)
        
        # Linha divisória acima do rodapé
        self.line(10, self.get_y() - 5, 200, self.get_y() - 5)
        
        # Usar fonte padrão e cor azul bebê - RODAPÉ MINIMALISTA
        self.set_font("Arial", '', 10)  # Fonte menor
        self.set_text_color(*self.baby_blue)  # Cor azul bebê
        
        # Informações do rodapé centralizadas - apenas 2 linhas essenciais
        self.cell(0, 5, clean_text("Rua Fernando Pessoa, 17 - Batistini - São Bernardo do Campo/SP - CEP 09844-390"), 0, 1, 'C')
        self.cell(0, 5, clean_text("E-mail: rogerio@worldcompressores.com.br | Fone: (11) 4543-6896/4543-6857/4357-8062"), 0, 1, 'C')
        
        # Resetar cor para preto para o conteúdo principal
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

def gerar_pdf_cotacao(cotacao_id, db_name):
    conn = None
    try:
        conn = sqlite3.connect(db_name)
        c = conn.cursor()   

        # Obter dados da cotação
        c.execute("""
            SELECT 
                cot.id, cot.numero_proposta, cot.modelo_compressor, cot.numero_serie_compressor, 
                cot.descricao_atividade, cot.observacoes, cot.data_criacao,
                cot.valor_total, cot.tipo_frete, cot.condicao_pagamento, cot.prazo_entrega,
                cli.id AS cliente_id, cli.nome AS cliente_nome, cli.nome_fantasia, cli.endereco, cli.email, 
                cli.telefone, cli.site, cli.cnpj, cli.cidade, cli.estado, cli.cep,
                usr.nome_completo, usr.email AS usr_email, usr.telefone AS usr_telefone,
                cot.moeda, cot.relacao_pecas
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
            responsavel_nome, responsavel_email, responsavel_telefone,
            moeda, relacao_pecas
        ) = cotacao_data

        # Obter contato principal
        c.execute("""
            SELECT nome FROM contatos 
            WHERE cliente_id = ? 
            LIMIT 1
        """, (cliente_id,))
        contato_principal = c.fetchone()
        contato_nome = contato_principal[0] if contato_principal else "Não informado"

        # Obter itens da cotação MODIFICADO (incluindo produto_id)
        c.execute("""
            SELECT 
                id, tipo, item_nome, quantidade, descricao, 
                valor_unitario, valor_total_item, 
                mao_obra, deslocamento, estadia, produto_id
            FROM itens_cotacao 
            WHERE cotacao_id=?
        """, (cotacao_id,))
        itens_cotacao = c.fetchall()

        # PÁGINA 1: CARTA DE APRESENTAÇÃO (APENAS TEXTO)
        # =====================================================
        pdf = PDF(orientation='P', unit='mm', format='A4')
        pdf.set_auto_page_break(auto=True, margin=25)  # Aumenta margem inferior para evitar sobreposição
        
        # Configurar dados para cabeçalho/footer
        pdf.numero_proposta = numero_proposta
        pdf.data_proposta = format_date(data_criacao)
        pdf.cliente_nome = cliente_nome_fantasia if cliente_nome_fantasia else cliente_nome
        pdf.cliente_cnpj = cliente_cnpj
        pdf.cliente_telefone = cliente_telefone
        pdf.contato_nome = contato_nome
        
        pdf.add_page()
        pdf.set_font("Arial", size=11)
        
        # Texto de apresentação com espaçamento
        modelo_text = f" {modelo_compressor}" if modelo_compressor else ""
        texto_apresentacao = clean_text(f"""
Prezados Senhores,

Agradecemos a sua solicitação e apresentamos nossas condições comerciais para fornecimento de peças para o compressor{modelo_text}.

A World Comp coloca-se a disposição para analisar, corrigir, prestar esclarecimentos para adequação das especificações e necessidades dos clientes, para tanto basta informar o número da proposta e revisão.


Atenciosamente,
        """)
        pdf.multi_cell(0, 5, texto_apresentacao)
        
        # Assinatura mais baixa (perto do rodapé)
        pdf.set_y(230)  # Posiciona a 250mm do topo
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 6, clean_text("ROGÉRIO CERQUEIRA"), 0, 1, 'L')
        pdf.set_font("Arial", '', 11)
        pdf.cell(0, 5, clean_text("Vendas"), 0, 1, 'L')
        pdf.cell(0, 5, clean_text("Fone: (11) 4543-6893 / 4543-6857 / 4357-8062"), 0, 1, 'L')
        pdf.cell(0, 5, clean_text("WORLD COMP DO BRASIL COMPRESSORES EIRELI"), 0, 1, 'L')

        # =====================================================
        # PÁGINA 2: SOBRE A EMPRESA
        # =====================================================
        pdf.add_page()
        pdf.set_y(45)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, clean_text("SOBRE A WORLD COMP"), 0, 1, 'L')
        pdf.set_font("Arial", '', 11)
        
        sobre_empresa = clean_text("Há mais de uma década no mercado de manutenção de compressores de ar de parafuso, de diversas marcas, atendemos clientes em todo território brasileiro.")
        pdf.multi_cell(0, 5, sobre_empresa)
        pdf.ln(5)
        
        # Seções sobre a empresa com subtítulos em azul bebê
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
            # Título em azul bebê
            pdf.set_text_color(*pdf.baby_blue)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 8, clean_text(titulo), 0, 1, 'L')
            
            # Texto em preto
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", '', 11)
            pdf.multi_cell(0, 5, clean_text(texto))
            pdf.ln(3)
        
        # Texto final
        texto_final = clean_text("Nossa missão é ser sua melhor parceria com sinônimo de qualidade, garantia e o melhor custo benefício.")
        pdf.multi_cell(0, 5, texto_final)
        pdf.ln(10)
        
        # =====================================================
        # PÁGINAS SEGUINTES: DETALHES DA PROPOSTA
        # =====================================================
        pdf.add_page()
        
        # Dados da proposta
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, clean_text(f"PROPOSTA Nº {numero_proposta}"), 0, 1, 'L')
        pdf.set_font("Arial", '', 11)
        pdf.cell(0, 6, clean_text(f"Data: {format_date(data_criacao)}"), 0, 1, 'L')
        pdf.cell(0, 6, clean_text(f"Responsável: {responsavel_nome}"), 0, 1, 'L')
        pdf.cell(0, 6, clean_text(f"Telefone Responsável: {format_phone(responsavel_telefone)}"), 0, 1, 'L')
        pdf.ln(10)

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

        # Descrição
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 6, clean_text("DESCRIÇÃO DO SERVIÇO:"), 0, 1, 'L')
        pdf.set_font("Arial", '', 11)
        pdf.multi_cell(0, 5, clean_text(descricao_atividade if descricao_atividade else "Não especificado"))
        pdf.ln(10)

        # Relação de Peças a Serem Substituídas (removendo prefixos)
        if relacao_pecas:
            # Remover prefixos: "Serviço: ", "Peça: ", "Kit: "
            relacao_sem_prefixo = relacao_pecas.replace("Serviço: ", "").replace("Produto: ", "").replace("Kit: ", "")
            pdf.set_font("Arial", 'B', 11)
            pdf.cell(0, 6, clean_text("RELAÇÃO DE PEÇAS A SEREM SUBSTITUÍDAS:"), 0, 1, 'L')
            pdf.set_font("Arial", '', 11)
            pdf.multi_cell(0, 5, clean_text(relacao_sem_prefixo))
            pdf.ln(5)

        # Itens da proposta - mostrar apenas itens principais
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, clean_text("ITENS DA PROPOSTA"), 0, 1, 'C')
        pdf.ln(5)

        # Configurar larguras das colunas
        col_widths = [15, 70, 20, 35, 30]  # Item, Descrição, Qtd, Vl. Unit., Vl. Total
        
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
            
            # TRATAMENTO ESPECIAL PARA KITS E SERVIÇOS
            descricao_final = descricao
            
            if item_tipo == "Kit" and produto_id:
                # Obter composição do kit
                composicao = PDF.obter_composicao_kit(produto_id)
                descricao_final = f"Kit: {item_nome}\nComposição:\n" + "\n".join(composicao)
            
            elif item_tipo == "Serviço":
                descricao_final = f"Serviço: {item_nome}"
                if mao_obra or deslocamento or estadia:
                    descricao_final += "\nDetalhes:"
                    if mao_obra:
                        descricao_final += f"\n- Mão de obra: R${mao_obra:.2f}"
                    if deslocamento:
                        descricao_final += f"\n- Deslocamento: R${deslocamento:.2f}"
                    if estadia:
                        descricao_final += f"\n- Estadia: R${estadia:.2f}"
            
            # Calcular altura baseada no número de linhas
            num_linhas = descricao_final.count('\n') + 1
            altura_total = max(num_linhas * 6, 6)

            # Primeira linha - nome principal do item
            pdf.set_x(10)
            pdf.cell(col_widths[0], altura_total, str(item_counter), 1, 0, 'C')

            # Descrição principal - usar multi_cell para quebrar texto
            x_pos = pdf.get_x()
            y_pos = pdf.get_y()

            # Usar multi_cell para quebrar texto automaticamente
            pdf.multi_cell(col_widths[1], 6, clean_text(descricao_final), 1, 'L')

            # Calcular nova posição Y após o texto
            new_y = pdf.get_y()
            altura_real = new_y - y_pos

            # Voltar para posição original das outras colunas
            pdf.set_xy(x_pos + col_widths[1], y_pos)

            # Quantidade
            pdf.cell(col_widths[2], altura_real, str(int(quantidade)), 1, 0, 'C')

            # Valor Unitário
            pdf.cell(col_widths[3], altura_real, clean_text(f"R$ {valor_unitario:.2f}"), 1, 0, 'R')

            # Valor Total
            pdf.cell(col_widths[4], altura_real, clean_text(f"R$ {valor_total_item:.2f}"), 1, 1, 'R')
            
            item_counter += 1

        pdf.set_x(10)
        pdf.set_font("Arial", 'B', 11)
        pdf.set_fill_color(200, 200, 200)
        pdf.cell(sum(col_widths[0:4]), 8, clean_text("VALOR TOTAL DA PROPOSTA:"), 1, 0, 'R', 1)
        pdf.cell(col_widths[4], 8, clean_text(f"R$ {valor_total:.2f}"), 1, 1, 'R', 1)
        pdf.ln(10)

        # Condições comerciais
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 6, clean_text("CONDIÇÕES COMERCIAIS:"), 0, 1, 'L')
        pdf.set_font("Arial", '', 11)
        pdf.cell(0, 5, clean_text(f"Tipo de Frete: {tipo_frete if tipo_frete else 'Não especificado'}"), 0, 1, 'L')
        pdf.cell(0, 5, clean_text(f"Condição de Pagamento: {condicao_pagamento if condicao_pagamento else 'Não especificado'}"), 0, 1, 'L')
        pdf.cell(0, 5, clean_text(f"Prazo de Entrega: {prazo_entrega if prazo_entrega else 'Não especificado'}"), 0, 1, 'L')
        pdf.cell(0, 5, clean_text(f"Moeda: {moeda if moeda else 'BRL (Real Brasileiro)'}"), 0, 1, 'L')

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
        return False, str(e)
    finally:
        if conn:
            conn.close()