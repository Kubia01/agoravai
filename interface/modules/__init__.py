from .dashboard import DashboardModule
from .clientes import ClientesModule
from .produtos import ProdutosModule
from .tecnicos import TecnicosModule
from .cotacoes import CotacoesModule
from .relatorios_tecnicos import RelatoriosTecnicosModule
from .usuarios import UsuariosModule
from .permissoes import PermissoesModule
from .consultas import ConsultasModule

from .editor_template_pdf import EditorTemplatePDFModule

__all__ = [
    'DashboardModule',
    'ClientesModule',
    'ProdutosModule',
    'TecnicosModule',
    'CotacoesModule',
    'RelatoriosTecnicosModule',
    'UsuariosModule',
    'PermissoesModule',
    'ConsultasModule',
    'EditorTemplatePDFModule'
]