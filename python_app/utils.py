# utils.py
import re
import locale
from datetime import datetime

def format_cnpj(cnpj):
    """Formatar CNPJ no padrão XX.XXX.XXX/XXXX-XX"""
    if not cnpj:
        return "Não informado"
    
    # Remove caracteres não numéricos
    cnpj_clean = re.sub(r'\D', '', str(cnpj))
    
    # Verifica se tem 14 dígitos
    if len(cnpj_clean) != 14:
        return cnpj  # Retorna original se não tiver 14 dígitos
    
    # Formata
    return f"{cnpj_clean[:2]}.{cnpj_clean[2:5]}.{cnpj_clean[5:8]}/{cnpj_clean[8:12]}-{cnpj_clean[12:]}"

def format_cep(cep):
    """Formatar CEP no padrão XXXXX-XXX"""
    if not cep:
        return "Não informado"
    
    # Remove caracteres não numéricos
    cep_clean = re.sub(r'\D', '', str(cep))
    
    # Verifica se tem 8 dígitos
    if len(cep_clean) != 8:
        return cep  # Retorna original se não tiver 8 dígitos
    
    # Formata
    return f"{cep_clean[:5]}-{cep_clean[5:]}"

def format_phone(phone):
    """Formatar telefone no padrão (XX) XXXXX-XXXX ou (XX) XXXX-XXXX"""
    if not phone:
        return "Não informado"
    
    # Remove caracteres não numéricos
    phone_clean = re.sub(r'\D', '', str(phone))
    
    # Formata baseado no número de dígitos
    if len(phone_clean) == 11:  # Celular
        return f"({phone_clean[:2]}) {phone_clean[2:7]}-{phone_clean[7:]}"
    elif len(phone_clean) == 10:  # Fixo
        return f"({phone_clean[:2]}) {phone_clean[2:6]}-{phone_clean[6:]}"
    else:
        return phone  # Retorna original se não tiver formato esperado

def format_currency(value, currency_symbol="R$"):
    """Formatar valor monetário no padrão brasileiro"""
    if value is None:
        return f"{currency_symbol} 0,00"
    
    try:
        # Converte para float se for string
        if isinstance(value, str):
            value = float(value.replace(',', '.'))
        
        # Formata com separador de milhares e duas casas decimais
        formatted = f"{currency_symbol} {value:,.2f}"
        
        # Substitui separadores para padrão brasileiro
        formatted = formatted.replace(',', 'X').replace('.', ',').replace('X', '.')
        
        return formatted
    except (ValueError, TypeError):
        return f"{currency_symbol} 0,00"

def format_date(date_input, input_format="%Y-%m-%d", output_format="%d/%m/%Y"):
    """Formatar data no padrão brasileiro"""
    if not date_input:
        return "Não informado"
    
    try:
        # Se já é um objeto datetime
        if isinstance(date_input, datetime):
            return date_input.strftime(output_format)
        
        # Se é string, converte
        if isinstance(date_input, str):
            # Tenta diferentes formatos de entrada
            formats = ["%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"]
            for fmt in formats:
                try:
                    date_obj = datetime.strptime(date_input, fmt)
                    return date_obj.strftime(output_format)
                except ValueError:
                    continue
        
        return str(date_input)
    except (ValueError, TypeError):
        return str(date_input)

def format_percentage(value, decimals=2):
    """Formatar porcentagem"""
    if value is None:
        return "0%"
    
    try:
        if isinstance(value, str):
            value = float(value.replace(',', '.'))
        
        return f"{value:.{decimals}f}%"
    except (ValueError, TypeError):
        return "0%"

def clean_text(text):
    """Limpar texto removendo caracteres especiais desnecessários"""
    if not text:
        return ""
    
    # Remove quebras de linha extras e espaços múltiplos
    text = re.sub(r'\s+', ' ', str(text).strip())
    
    return text

def truncate_text(text, max_length=50, suffix="..."):
    """Truncar texto se for muito longo"""
    if not text:
        return ""
    
    text = str(text).strip()
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def format_decimal(value, decimals=2):
    """Formatar número decimal"""
    if value is None:
        return "0,00"
    
    try:
        if isinstance(value, str):
            value = float(value.replace(',', '.'))
        
        formatted = f"{value:.{decimals}f}"
        return formatted.replace('.', ',')
    except (ValueError, TypeError):
        return "0,00"

def validate_email(email):
    """Validar formato de email"""
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_cnpj(cnpj):
    """Validar CNPJ (validação básica de formato)"""
    if not cnpj:
        return False
    
    # Remove caracteres não numéricos
    cnpj_clean = re.sub(r'\D', '', str(cnpj))
    
    # Verifica se tem 14 dígitos
    return len(cnpj_clean) == 14

def validate_cep(cep):
    """Validar CEP (validação básica de formato)"""
    if not cep:
        return False
    
    # Remove caracteres não numéricos
    cep_clean = re.sub(r'\D', '', str(cep))
    
    # Verifica se tem 8 dígitos
    return len(cep_clean) == 8

# Função para converter valores de moeda
def convert_currency(value, from_currency="BRL", to_currency="USD", rate=5.0):
    """Converter valor entre moedas (função básica)"""
    if not value:
        return 0
    
    try:
        if isinstance(value, str):
            value = float(value.replace(',', '.'))
        
        if from_currency == to_currency:
            return value
        
        # Conversão básica (em produção, usar API de câmbio)
        if from_currency == "BRL" and to_currency == "USD":
            return value / rate
        elif from_currency == "USD" and to_currency == "BRL":
            return value * rate
        
        return value
    except (ValueError, TypeError):
        return 0