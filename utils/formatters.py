import re
from datetime import datetime

def format_cnpj(cnpj):
    """Formatar CNPJ no padrão XX.XXX.XXX/XXXX-XX"""
    if not cnpj:
        return ""
    
    # Remove todos os caracteres não numéricos
    cnpj_clean = re.sub(r'\D', '', cnpj)
    
    # Verifica se tem 14 dígitos
    if len(cnpj_clean) == 14:
        return f"{cnpj_clean[:2]}.{cnpj_clean[2:5]}.{cnpj_clean[5:8]}/{cnpj_clean[8:12]}-{cnpj_clean[12:]}"
    
    return cnpj

def format_phone(phone):
    """Formatar telefone no padrão (XX) XXXXX-XXXX ou (XX) XXXX-XXXX"""
    if not phone:
        return ""
    
    # Remove todos os caracteres não numéricos
    phone_clean = re.sub(r'\D', '', phone)
    
    # Celular (11 dígitos)
    if len(phone_clean) == 11:
        return f"({phone_clean[:2]}) {phone_clean[2:7]}-{phone_clean[7:]}"
    # Telefone fixo (10 dígitos)
    elif len(phone_clean) == 10:
        return f"({phone_clean[:2]}) {phone_clean[2:6]}-{phone_clean[6:]}"
    
    return phone

def format_currency(value):
    """Formatar valor monetário"""
    if value is None:
        return "R$ 0,00"
    
    try:
        # Garantir que é float
        if isinstance(value, str):
            value = float(value.replace(',', '.'))
        
        return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except (ValueError, TypeError):
        return "R$ 0,00"

def format_date(date_value):
    """Formatar data"""
    if not date_value:
        return ""
    
    # Se já é string no formato correto, retorna
    if isinstance(date_value, str):
        return date_value
    
    # Se é objeto datetime, formatar
    try:
        return date_value.strftime("%d/%m/%Y")
    except:
        return str(date_value)

def validate_cnpj(cnpj):
    """Validar CNPJ"""
    if not cnpj:
        return True  # CNPJ é opcional
    
    # Remove caracteres não numéricos
    cnpj = re.sub(r'\D', '', cnpj)
    
    # Verifica se tem 14 dígitos
    if len(cnpj) != 14:
        return False
    
    # Verifica se todos os dígitos são iguais
    if cnpj == cnpj[0] * 14:
        return False
    
    # Calcula o primeiro dígito verificador
    peso = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj[i]) * peso[i] for i in range(12))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    
    if int(cnpj[12]) != digito1:
        return False
    
    # Calcula o segundo dígito verificador
    peso = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj[i]) * peso[i] for i in range(13))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    
    return int(cnpj[13]) == digito2

def validate_email(email):
    """Validar email"""
    if not email:
        return True  # Email é opcional
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def clean_number(value):
    """Limpar e converter string para número"""
    if not value:
        return 0.0
    try:
        # Remove espaços e converte vírgula para ponto
        cleaned = str(value).strip().replace(',', '.')
        return float(cleaned)
    except (ValueError, TypeError):
        return 0.0

def format_cep(cep):
    """Formatar CEP no padrão 00000-000"""
    if not cep:
        return ""
    
    # Remove todos os caracteres não numéricos
    cep_clean = re.sub(r'\D', '', cep)
    
    # Verifica se tem 8 dígitos
    if len(cep_clean) == 8:
        return f"{cep_clean[:5]}-{cep_clean[5:]}"
    
    return cep