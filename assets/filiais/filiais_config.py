"""
Configuração das filiais da empresa para geração de PDFs
"""

FILIAIS = {
    1: {
        "nome": "WORLD COMP COMPRESSORES LTDA",
        "endereco": "Rua Fernando Pessoa, nº 11 – Batistini – São Bernardo do Campo – SP",
        "cep": "09844-390",
        "cnae_fiscal": "23222222",
        "cnpj": "10.644.944/0001-55",
        "inscricao_estadual": "635.970.206.110",
        "telefones": "(11) 4543-6893 / 4543-6857",
        "email": "contato@worldcompressores.com.br",
        "logo_path": "assets/logos/world_comp_brasil.jpg"
    },
    2: {
        "nome": "WORLD COMP DO BRASIL COMPRESSORES LTDA",
        "endereco": "Rua Fernando Pessoa, nº 17 – Batistini – São Bernardo do Campo – SP",
        "cep": "09844-390",
        "cnpj": "22.790.603/0001-77",
        "inscricao_estadual": "635.835.470.115",
        "telefones": "(11) 4543-6896 / 4543-6857 / 4357-8062",
        "email": "rogerio@worldcompressores.com.br",
        "logo_path": "assets/logos/world_comp_brasil.jpg"
    }
}

# Configuração de usuários que podem gerar cotações com templates personalizados
USUARIOS_COTACAO = {
    "valdir": {
        "nome_completo": "Valdir",
        "template_capa": "assets/templates/capas/capa_valdir.py",
        "assinatura": "Valdir\nVendas"
    },
    "vagner": {
        "nome_completo": "Vagner Cerqueira",
        "template_capa": "assets/templates/capas/capa_vagner.py",
        "assinatura": "Vagner Cerqueira\nVendas"
    },
    "rogerio": {
        "nome_completo": "Rogério Cerqueira",
        "template_capa": "assets/templates/capas/capa_rogerio.py",
        "assinatura": "Rogério Cerqueira\nVendas"
    },
    "raquel": {
        "nome_completo": "Raquel",
        "template_capa": "assets/templates/capas/capa_raquel.py",
        "assinatura": "Raquel\nVendas"
    }
}

def obter_filial(filial_id):
    """Retorna informações da filial pelo ID"""
    return FILIAIS.get(filial_id)

def obter_usuario_cotacao(username):
    """Retorna configurações do usuário para cotação"""
    return USUARIOS_COTACAO.get(username.lower())

def listar_filiais():
    """Retorna lista de filiais disponíveis"""
    return [(id, info["nome"]) for id, info in FILIAIS.items()]