import re
from datetime import datetime

def format_currency(value):
    """Formatar valor como moeda brasileira"""
    try:
        if isinstance(value, str):
            value = float(value.replace(',', '.'))
        return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except (ValueError, TypeError):
        return "R$ 0,00"

def format_date(date_str):
    """Formatar data para exibição"""
    if not date_str:
        return ""
    try:
        if isinstance(date_str, str):
            if len(date_str) == 10 and '-' in date_str:
                # Formato YYYY-MM-DD para DD/MM/YYYY
                return datetime.strptime(date_str, '%Y-%m-%d').strftime('%d/%m/%Y')
            elif len(date_str) == 10 and '/' in date_str:
                # Já está no formato DD/MM/YYYY
                return date_str
        return str(date_str)
    except:
        return str(date_str)

def format_cnpj(cnpj):
    """Formatar CNPJ"""
    if not cnpj:
        return ""
    # Remove caracteres não numéricos
    cnpj = re.sub(r'\D', '', cnpj)
    if len(cnpj) != 14:
        return cnpj
    # Formatar: XX.XXX.XXX/XXXX-XX
    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:14]}"

def format_phone(phone):
    """Formatar telefone"""
    if not phone:
        return ""
    # Remove caracteres não numéricos
    phone = re.sub(r'\D', '', phone)
    if len(phone) == 11:
        # Celular: (XX) 9XXXX-XXXX
        return f"({phone[:2]}) {phone[2]}{phone[3:7]}-{phone[7:11]}"
    elif len(phone) == 10:
        # Fixo: (XX) XXXX-XXXX
        return f"({phone[:2]}) {phone[2:6]}-{phone[6:10]}"
    return phone

def format_cep(cep):
    """Formatar CEP"""
    if not cep:
        return ""
    # Remove caracteres não numéricos
    cep = re.sub(r'\D', '', cep)
    if len(cep) == 8:
        return f"{cep[:5]}-{cep[5:8]}"
    return cep

def validate_cnpj(cnpj):
    """Validar CNPJ"""
    if not cnpj:
        return False
    
    # Remove caracteres não numéricos
    cnpj = re.sub(r'\D', '', cnpj)
    
    if len(cnpj) != 14:
        return False
    
    # Verifica se todos os dígitos são iguais
    if cnpj == cnpj[0] * 14:
        return False
    
    # Validação do primeiro dígito verificador
    soma = 0
    peso = 5
    for i in range(12):
        soma += int(cnpj[i]) * peso
        peso -= 1
        if peso < 2:
            peso = 9
    
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    
    if int(cnpj[12]) != digito1:
        return False
    
    # Validação do segundo dígito verificador
    soma = 0
    peso = 6
    for i in range(13):
        soma += int(cnpj[i]) * peso
        peso -= 1
        if peso < 2:
            peso = 9
    
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