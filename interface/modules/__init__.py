from .dashboard import DashboardModule
from .clientes import ClientesModule
from .produtos import ProdutosModule
from .tecnicos import TecnicosModule
from .cotacoes import CotacoesModule
from .relatorios import RelatoriosModule
from .usuarios import UsuariosModule
from .permissoes import PermissoesModule
from .correcoes import CorrecoesModule
from .editor_pdf import EditorPDFModule

__all__ = [
    'DashboardModule',
    'ClientesModule',
    'ProdutosModule',
    'TecnicosModule',
    'CotacoesModule',
    'RelatoriosModule',
    'UsuariosModule',
    'PermissoesModule',
    'CorrecoesModule',
    'EditorPDFModule'
]