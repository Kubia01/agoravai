import re
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