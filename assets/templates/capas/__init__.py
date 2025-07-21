"""
Módulo para templates de capas personalizadas
"""

import sys
import os

# Adicionar o diretório atual ao path
current_dir = os.path.dirname(__file__)
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    from .base_capa import CapaBase
    from .capa_valdir import CapaValdir
    from .capa_vagner import CapaVagner
    from .capa_rogerio import CapaRogerio
    from .capa_raquel import CapaRaquel
except ImportError:
    from base_capa import CapaBase
    from capa_valdir import CapaValdir
    from capa_vagner import CapaVagner
    from capa_rogerio import CapaRogerio
    from capa_raquel import CapaRaquel

# Mapeamento de usuários para classes de template
TEMPLATES_USUARIOS = {
    'valdir': CapaValdir,
    'vagner': CapaVagner,
    'rogerio': CapaRogerio,
    'raquel': CapaRaquel
}

def obter_template_usuario(username):
    """Retorna a classe de template para o usuário especificado"""
    return TEMPLATES_USUARIOS.get(username.lower(), CapaBase)