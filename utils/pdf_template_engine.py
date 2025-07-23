import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import tempfile

try:
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib.units import mm, cm, inch, point
    from reportlab.lib.colors import Color, black, white, blue, red, green
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("⚠️ ReportLab não disponível - funcionalidade de PDF limitada")

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

class PDFTemplateEngine:
    """
    Engine completo para geração de PDFs baseado em templates visuais.
    Converte elementos do editor visual em PDFs profissionais.
    """
    
    def __init__(self, template_data: Dict[str, Any], field_resolver=None):
        self.template_data = template_data
        self.field_resolver = field_resolver
        self.output_path = None
        
        # Configurações padrão
        self.page_size = A4
        self.page_width, self.page_height = A4
        self.margin_left = 72  # 1 inch
        self.margin_right = 72
        self.margin_top = 72
        self.margin_bottom = 72
        
        # Fontes disponíveis
        self.fonts = {
            'Arial': 'Helvetica',
            'Times': 'Times-Roman',
            'Helvetica': 'Helvetica',
            'Courier': 'Courier'
        }
        
        # Cache de imagens e elementos
        self.image_cache = {}
        self.element_cache = {}
        
        # Configurações avançadas
        self.quality_dpi = 300
        self.compress_images = True
        self.embed_fonts = True
        
    def generate_pdf(self, output_path: str, metadata: Optional[Dict] = None) -> bool:
        """
        Gerar PDF completo baseado no template
        
        Args:
            output_path: Caminho do arquivo PDF de saída
            metadata: Metadados do PDF (título, autor, etc.)
        
        Returns:
            True se geração foi bem-sucedida
        """
        try:
            if not REPORTLAB_AVAILABLE:
                print("❌ ReportLab não disponível - não é possível gerar PDF")
                return False
            
            self.output_path = output_path
            
            # Criar documento PDF
            doc = SimpleDocTemplate(
                output_path,
                pagesize=self.page_size,
                leftMargin=self.margin_left,
                rightMargin=self.margin_right,
                topMargin=self.margin_top,
                bottomMargin=self.margin_bottom,
                title=metadata.get('title', 'Documento Gerado') if metadata else 'Documento Gerado',
                author=metadata.get('author', 'Sistema CRM') if metadata else 'Sistema CRM',
                subject=metadata.get('subject', 'Proposta Comercial') if metadata else 'Proposta Comercial'
            )
            
            # Preparar conteúdo de todas as páginas
            story = []
            
            pages = self.template_data.get('pages', [])
            total_pages = len(pages)
            
            for page_index, page_data in enumerate(pages):
                print(f"🔄 Processando página {page_index + 1} de {total_pages}")
                
                # Processar elementos da página
                page_elements = self.process_page_elements(page_data, page_index + 1, total_pages)
                
                # Adicionar elementos ao story
                story.extend(page_elements)
                
                # Quebra de página (exceto última página)
                if page_index < total_pages - 1:
                    from reportlab.platypus import PageBreak
                    story.append(PageBreak())
            
            # Construir PDF
            doc.build(story, onFirstPage=self.create_page_template, onLaterPages=self.create_page_template)
            
            print(f"✅ PDF gerado com sucesso: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao gerar PDF: {e}")
            return False
    
    def process_page_elements(self, page_data: Dict[str, Any], page_num: int, total_pages: int) -> List[Any]:
        """
        Processar elementos de uma página específica
        
        Args:
            page_data: Dados da página do template
            page_num: Número da página atual
            total_pages: Total de páginas
        
        Returns:
            Lista de elementos para o ReportLab
        """
        elements = []
        page_elements = page_data.get('elements', [])
        
        # Ordenar elementos por posição Y (top to bottom)
        sorted_elements = sorted(page_elements, key=lambda x: x.get('y', 0))
        
        # Processar cada elemento
        for element in sorted_elements:
            try:
                element_type = element.get('type', '')
                
                if element_type == 'text':
                    processed = self.process_text_element(element)
                elif element_type == 'dynamic_field':
                    processed = self.process_dynamic_field_element(element)
                elif element_type == 'image':
                    processed = self.process_image_element(element)
                elif element_type == 'table':
                    processed = self.process_table_element(element)
                elif element_type == 'line':
                    processed = self.process_line_element(element)
                elif element_type == 'rectangle':
                    processed = self.process_rectangle_element(element)
                else:
                    continue  # Tipo não suportado
                
                if processed:
                    if isinstance(processed, list):
                        elements.extend(processed)
                    else:
                        elements.append(processed)
                        
            except Exception as e:
                print(f"⚠️ Erro ao processar elemento {element.get('id', 'unknown')}: {e}")
                continue
        
        return elements
    
    def process_text_element(self, element: Dict[str, Any]) -> Optional[Any]:
        """Processar elemento de texto"""
        try:
            text = element.get('text', '')
            if not text:
                return None
            
            # Resolver campos dinâmicos no texto
            if self.field_resolver:
                text = self.field_resolver.resolve_template_text(text)
            
            # Configurações de estilo
            font_family = self.fonts.get(element.get('font_family', 'Arial'), 'Helvetica')
            font_size = element.get('font_size', 12)
            color = self.parse_color(element.get('color', '#000000'))
            bold = element.get('bold', False)
            italic = element.get('italic', False)
            
            # Criar estilo
            style_name = f"custom_{element.get('id', 'text')}"
            style = ParagraphStyle(
                style_name,
                parent=getSampleStyleSheet()['Normal'],
                fontName=self.get_font_name(font_family, bold, italic),
                fontSize=font_size,
                textColor=color,
                alignment=TA_LEFT,  # Pode ser configurável
                spaceAfter=6
            )
            
            # Criar parágrafo
            paragraph = Paragraph(text, style)
            
            return paragraph
            
        except Exception as e:
            print(f"Erro ao processar texto: {e}")
            return None
    
    def process_dynamic_field_element(self, element: Dict[str, Any]) -> Optional[Any]:
        """Processar elemento de campo dinâmico"""
        try:
            field_ref = element.get('field_ref', '')
            if not field_ref:
                return None
            
            # Resolver campo dinâmico
            if self.field_resolver:
                text = self.field_resolver.resolve_field(field_ref)
            else:
                text = f"[{field_ref}]"
            
            # Criar elemento de texto com o valor resolvido
            text_element = element.copy()
            text_element['text'] = text
            text_element['type'] = 'text'
            
            return self.process_text_element(text_element)
            
        except Exception as e:
            print(f"Erro ao processar campo dinâmico: {e}")
            return None
    
    def process_image_element(self, element: Dict[str, Any]) -> Optional[Any]:
        """Processar elemento de imagem"""
        try:
            image_path = element.get('image_path', '')
            if not image_path or not os.path.exists(image_path):
                return None
            
            width = element.get('width', 100) * point
            height = element.get('height', 100) * point
            
            # Criar imagem do ReportLab
            img = RLImage(image_path, width=width, height=height)
            
            return img
            
        except Exception as e:
            print(f"Erro ao processar imagem: {e}")
            return None
    
    def process_table_element(self, element: Dict[str, Any]) -> Optional[Any]:
        """Processar elemento de tabela"""
        try:
            # Dados da tabela
            table_data = element.get('data', [])
            if not table_data:
                # Criar tabela de exemplo se não houver dados
                rows = element.get('rows', 3)
                cols = element.get('cols', 3)
                table_data = [[f"Célula {r+1},{c+1}" for c in range(cols)] for r in range(rows)]
            
            # Criar tabela
            table = Table(table_data)
            
            # Estilo da tabela
            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ])
            
            table.setStyle(table_style)
            
            return table
            
        except Exception as e:
            print(f"Erro ao processar tabela: {e}")
            return None
    
    def process_line_element(self, element: Dict[str, Any]) -> Optional[Any]:
        """Processar elemento de linha"""
        try:
            # Para linhas, usamos Spacer com linha customizada
            # Implementação simplificada - pode ser expandida
            return Spacer(1, 12)
            
        except Exception as e:
            print(f"Erro ao processar linha: {e}")
            return None
    
    def process_rectangle_element(self, element: Dict[str, Any]) -> Optional[Any]:
        """Processar elemento de retângulo"""
        try:
            # Para retângulos, criar usando canvas customizado
            # Implementação simplificada
            return Spacer(1, element.get('height', 50))
            
        except Exception as e:
            print(f"Erro ao processar retângulo: {e}")
            return None
    
    def create_page_template(self, canvas_obj, doc):
        """
        Criar template de página (cabeçalho/rodapé)
        """
        try:
            # Configurações da página
            page_width = self.page_width
            page_height = self.page_height
            
            # Cabeçalho (se configurado)
            if self.has_header():
                self.draw_header(canvas_obj, page_width, page_height)
            
            # Rodapé (se configurado)
            if self.has_footer():
                self.draw_footer(canvas_obj, page_width, page_height)
            
            # Numeração de página
            self.draw_page_number(canvas_obj, page_width, page_height)
            
        except Exception as e:
            print(f"Erro ao criar template de página: {e}")
    
    def has_header(self) -> bool:
        """Verificar se template tem cabeçalho"""
        # Implementar lógica para detectar elementos de cabeçalho
        return False
    
    def has_footer(self) -> bool:
        """Verificar se template tem rodapé"""
        # Implementar lógica para detectar elementos de rodapé
        return True  # Por enquanto sempre true
    
    def draw_header(self, canvas_obj, page_width: float, page_height: float):
        """Desenhar cabeçalho da página"""
        try:
            canvas_obj.setFont("Helvetica-Bold", 12)
            canvas_obj.drawString(72, page_height - 50, "Cabeçalho do Documento")
        except Exception as e:
            print(f"Erro ao desenhar cabeçalho: {e}")
    
    def draw_footer(self, canvas_obj, page_width: float, page_height: float):
        """Desenhar rodapé da página"""
        try:
            # Rodapé padrão com informações da empresa
            footer_y = 30
            
            canvas_obj.setFont("Helvetica", 8)
            canvas_obj.setFillColor(colors.Color(0.54, 0.81, 0.94))  # Azul bebê #89CFF0
            
            # Informações da empresa (centralizadas)
            empresa_info = [
                "WORLD COMP COMPRESSORES LTDA",
                "Rua Fernando Pessoa, nº 11 – Batistini – São Bernardo do Campo – SP – CEP: 09844-390",
                "CNPJ: 10.644.944/0001-55 | Fone: (11) 4543-6893 / 4543-6857",
                "E-mail: contato@worldcompressores.com.br"
            ]
            
            for i, info in enumerate(empresa_info):
                y_pos = footer_y + (len(empresa_info) - i - 1) * 10
                text_width = canvas_obj.stringWidth(info, "Helvetica", 8)
                x_pos = (page_width - text_width) / 2
                canvas_obj.drawString(x_pos, y_pos, info)
                
        except Exception as e:
            print(f"Erro ao desenhar rodapé: {e}")
    
    def draw_page_number(self, canvas_obj, page_width: float, page_height: float):
        """Desenhar numeração da página"""
        try:
            page_num = canvas_obj.getPageNumber()
            canvas_obj.setFont("Helvetica", 8)
            canvas_obj.setFillColor(colors.black)
            canvas_obj.drawRightString(page_width - 72, 20, f"Página {page_num}")
        except Exception as e:
            print(f"Erro ao desenhar número da página: {e}")
    
    def parse_color(self, color_str: str) -> Color:
        """
        Converter string de cor em objeto Color do ReportLab
        
        Args:
            color_str: Cor em formato hex (#RRGGBB) ou nome
        
        Returns:
            Objeto Color do ReportLab
        """
        try:
            if color_str.startswith('#'):
                # Formato hex
                hex_color = color_str.lstrip('#')
                if len(hex_color) == 6:
                    r = int(hex_color[0:2], 16) / 255.0
                    g = int(hex_color[2:4], 16) / 255.0
                    b = int(hex_color[4:6], 16) / 255.0
                    return Color(r, g, b)
            
            # Cores nomeadas
            color_map = {
                'black': colors.black,
                'white': colors.white,
                'red': colors.red,
                'green': colors.green,
                'blue': colors.blue,
                'yellow': colors.yellow,
                'orange': colors.orange,
                'purple': colors.purple,
                'grey': colors.grey,
                'gray': colors.grey
            }
            
            return color_map.get(color_str.lower(), colors.black)
            
        except Exception:
            return colors.black
    
    def get_font_name(self, base_font: str, bold: bool = False, italic: bool = False) -> str:
        """
        Obter nome da fonte considerando estilos
        
        Args:
            base_font: Fonte base
            bold: Se deve ser negrito
            italic: Se deve ser itálico
        
        Returns:
            Nome da fonte para ReportLab
        """
        font_map = {
            'Helvetica': {
                (False, False): 'Helvetica',
                (True, False): 'Helvetica-Bold',
                (False, True): 'Helvetica-Oblique',
                (True, True): 'Helvetica-BoldOblique'
            },
            'Times-Roman': {
                (False, False): 'Times-Roman',
                (True, False): 'Times-Bold',
                (False, True): 'Times-Italic',
                (True, True): 'Times-BoldItalic'
            },
            'Courier': {
                (False, False): 'Courier',
                (True, False): 'Courier-Bold',
                (False, True): 'Courier-Oblique',
                (True, True): 'Courier-BoldOblique'
            }
        }
        
        font_variants = font_map.get(base_font, font_map['Helvetica'])
        return font_variants.get((bold, italic), base_font)
    
    def generate_preview_image(self, page_index: int = 0, scale: float = 1.0) -> Optional[str]:
        """
        Gerar imagem de preview de uma página
        
        Args:
            page_index: Índice da página (0-based)
            scale: Escala da imagem (1.0 = tamanho real)
        
        Returns:
            Caminho da imagem gerada ou None se erro
        """
        try:
            if not PIL_AVAILABLE:
                return None
            
            # Dimensões da página em pixels
            dpi = 150 * scale
            width_px = int(self.page_width * dpi / 72)
            height_px = int(self.page_height * dpi / 72)
            
            # Criar imagem
            img = Image.new('RGB', (width_px, height_px), 'white')
            draw = ImageDraw.Draw(img)
            
            # Desenhar elementos da página
            pages = self.template_data.get('pages', [])
            if page_index < len(pages):
                page_data = pages[page_index]
                self.draw_page_preview(draw, page_data, width_px, height_px, scale)
            
            # Salvar imagem temporária
            temp_path = os.path.join(tempfile.gettempdir(), f"preview_page_{page_index}_{datetime.now().timestamp()}.png")
            img.save(temp_path, 'PNG', dpi=(dpi, dpi))
            
            return temp_path
            
        except Exception as e:
            print(f"Erro ao gerar preview: {e}")
            return None
    
    def draw_page_preview(self, draw: ImageDraw.Draw, page_data: Dict[str, Any], 
                         width_px: int, height_px: int, scale: float):
        """
        Desenhar elementos da página no preview
        
        Args:
            draw: Objeto ImageDraw
            page_data: Dados da página
            width_px: Largura em pixels
            height_px: Altura em pixels
            scale: Escala de conversão
        """
        try:
            elements = page_data.get('elements', [])
            
            for element in elements:
                element_type = element.get('type', '')
                x = int(element.get('x', 0) * scale)
                y = int(element.get('y', 0) * scale)
                
                if element_type in ['text', 'dynamic_field']:
                    self.draw_text_preview(draw, element, x, y, scale)
                elif element_type == 'rectangle':
                    self.draw_rectangle_preview(draw, element, x, y, scale)
                elif element_type == 'line':
                    self.draw_line_preview(draw, element, x, y, scale)
                    
        except Exception as e:
            print(f"Erro ao desenhar preview da página: {e}")
    
    def draw_text_preview(self, draw: ImageDraw.Draw, element: Dict[str, Any], 
                         x: int, y: int, scale: float):
        """Desenhar texto no preview"""
        try:
            if element.get('type') == 'dynamic_field':
                field_ref = element.get('field_ref', '')
                text = self.field_resolver.resolve_field(field_ref) if self.field_resolver else f"[{field_ref}]"
            else:
                text = element.get('text', '')
            
            if not text:
                return
            
            font_size = int(element.get('font_size', 12) * scale)
            color = element.get('color', '#000000')
            
            # Tentar carregar fonte (simplificado)
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            draw.text((x, y), text, fill=color, font=font)
            
        except Exception as e:
            print(f"Erro ao desenhar texto no preview: {e}")
    
    def draw_rectangle_preview(self, draw: ImageDraw.Draw, element: Dict[str, Any], 
                              x: int, y: int, scale: float):
        """Desenhar retângulo no preview"""
        try:
            width = int(element.get('width', 100) * scale)
            height = int(element.get('height', 50) * scale)
            fill_color = element.get('fill_color', '')
            border_color = element.get('border_color', '#000000')
            
            # Desenhar retângulo
            coords = [x, y, x + width, y + height]
            
            if fill_color:
                draw.rectangle(coords, fill=fill_color)
            
            draw.rectangle(coords, outline=border_color)
            
        except Exception as e:
            print(f"Erro ao desenhar retângulo no preview: {e}")
    
    def draw_line_preview(self, draw: ImageDraw.Draw, element: Dict[str, Any], 
                         x: int, y: int, scale: float):
        """Desenhar linha no preview"""
        try:
            length = int(element.get('length', 100) * scale)
            color = element.get('color', '#000000')
            thickness = int(element.get('thickness', 1))
            
            end_x = x + length
            end_y = y + element.get('angle_offset', 0) * scale
            
            draw.line([x, y, end_x, end_y], fill=color, width=thickness)
            
        except Exception as e:
            print(f"Erro ao desenhar linha no preview: {e}")
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Obter metadados do template
        
        Returns:
            Dicionário com metadados
        """
        return {
            'template_version': self.template_data.get('version', '1.0'),
            'created_at': self.template_data.get('created_at', datetime.now().isoformat()),
            'total_pages': len(self.template_data.get('pages', [])),
            'has_dynamic_fields': self.has_dynamic_fields(),
            'generator': 'PDFTemplateEngine v1.0'
        }
    
    def has_dynamic_fields(self) -> bool:
        """Verificar se template tem campos dinâmicos"""
        pages = self.template_data.get('pages', [])
        for page in pages:
            elements = page.get('elements', [])
            for element in elements:
                if element.get('type') == 'dynamic_field':
                    return True
        return False
    
    def validate_template(self) -> Tuple[bool, List[str]]:
        """
        Validar template antes da geração
        
        Returns:
            Tuple (is_valid, list_of_errors)
        """
        errors = []
        
        try:
            # Validar estrutura básica
            if not isinstance(self.template_data, dict):
                errors.append("Template deve ser um dicionário")
                return False, errors
            
            pages = self.template_data.get('pages', [])
            if not pages:
                errors.append("Template deve ter pelo menos uma página")
            
            # Validar cada página
            for i, page in enumerate(pages):
                if not isinstance(page, dict):
                    errors.append(f"Página {i+1} deve ser um dicionário")
                    continue
                
                elements = page.get('elements', [])
                for j, element in enumerate(elements):
                    if not isinstance(element, dict):
                        errors.append(f"Elemento {j+1} da página {i+1} deve ser um dicionário")
                        continue
                    
                    # Validar tipo de elemento
                    element_type = element.get('type', '')
                    if not element_type:
                        errors.append(f"Elemento {j+1} da página {i+1} deve ter um tipo")
                    
                    # Validar posição
                    if 'x' not in element or 'y' not in element:
                        errors.append(f"Elemento {j+1} da página {i+1} deve ter posição (x, y)")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            errors.append(f"Erro na validação: {e}")
            return False, errors