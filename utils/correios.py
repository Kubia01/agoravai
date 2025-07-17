"""
Módulo para busca de CEP e formatação de endereços
"""
import requests
import re

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

def buscar_cep(cep):
    """
    Buscar informações de endereço através do CEP
    Utiliza a API ViaCEP (gratuita)
    """
    if not cep:
        return None
        
    # Limpar CEP
    cep_clean = re.sub(r'\D', '', cep)
    
    if len(cep_clean) != 8:
        return None
    
    try:
        # Usar API ViaCEP
        url = f"https://viacep.com.br/ws/{cep_clean}/json/"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            # Verificar se retornou erro
            if 'erro' in data:
                return None
                
            return {
                'cep': format_cep(cep_clean),
                'logradouro': data.get('logradouro', ''),
                'complemento': data.get('complemento', ''),
                'bairro': data.get('bairro', ''),
                'cidade': data.get('localidade', ''),
                'uf': data.get('uf', ''),
                'ibge': data.get('ibge', ''),
                'gia': data.get('gia', ''),
                'ddd': data.get('ddd', ''),
                'siafi': data.get('siafi', '')
            }
    except requests.RequestException:
        # Se não conseguir acessar a API, retorna None
        pass
    except Exception:
        # Qualquer outro erro, retorna None
        pass
    
    return None

def validate_cep(cep):
    """Validar formato do CEP"""
    if not cep:
        return False
        
    # Limpar CEP
    cep_clean = re.sub(r'\D', '', cep)
    
    # Verificar se tem exatamente 8 dígitos
    return len(cep_clean) == 8