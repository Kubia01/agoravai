import json
import os
import shutil
import sqlite3
from datetime import datetime

class TemplateManager:
    """Gerenciador de templates do sistema"""
    
    def __init__(self, db_name="crm_compressores.db"):
        self.db_name = db_name
        self.base_template_path = "data/pdf_template_base.json"
        self.templates_dir = "data/templates"
        self.user_templates_dir = os.path.join(self.templates_dir, "usuarios")
        self.client_templates_dir = os.path.join(self.templates_dir, "clientes")
        
        # Criar diretórios necessários
        os.makedirs(self.templates_dir, exist_ok=True)
        os.makedirs(self.user_templates_dir, exist_ok=True)
        os.makedirs(self.client_templates_dir, exist_ok=True)
        
        # Garantir que o template base existe
        self.ensure_base_template()
    
    def ensure_base_template(self):
        """Garantir que o template base existe"""
        if not os.path.exists(self.base_template_path):
            base_template = self.get_default_template()
            self.save_base_template(base_template)
    
    def get_default_template(self):
        """Obter template padrão do sistema"""
        return {
            "versao": "1.0",
            "criado_em": datetime.now().isoformat(),
            "tipo": "base",
            "pagina_1": {
                "tipo": "capa",
                "editavel": ["background_image", "overlay_image"],
                "elementos": {
                    "background_image": None,
                    "overlay_image": None,
                    "texto_empresa": "{{empresa.nome}}",
                    "texto_contato": "A/C SR. {{cliente.contato}}",
                    "data": "{{proposta.data}}",
                    "numero_proposta": "{{proposta.numero}}"
                },
                "posicionamento": {
                    "titulo": {"x": 50, "y": 100, "fonte": "Arial", "tamanho": 16, "cor": "#FFFFFF"},
                    "empresa": {"x": 50, "y": 250, "fonte": "Arial", "tamanho": 12, "cor": "#FFFFFF"},
                    "contato": {"x": 50, "y": 270, "fonte": "Arial", "tamanho": 10, "cor": "#FFFFFF"}
                }
            },
            "pagina_2": {
                "tipo": "apresentacao",
                "editavel": ["texto_apresentacao", "logo", "informacoes_empresa"],
                "elementos": {
                    "logo": "assets/logos/world_comp_brasil.jpg",
                    "empresa_nome": "{{empresa.nome}}",
                    "empresa_endereco": "{{empresa.endereco}}",
                    "empresa_telefone": "{{empresa.telefones}}",
                    "empresa_email": "{{empresa.email}}",
                    "responsavel_nome": "{{usuario.nome}}",
                    "responsavel_telefone": "{{usuario.telefone}}",
                    "texto_apresentacao": """Prezados Senhores,

Agradecemos a sua solicitação e apresentamos nossas condições comerciais para fornecimento de peças para o compressor.

A World Comp coloca-se a disposição para analisar, corrigir, prestar esclarecimentos para adequação das especificações e necessidades dos clientes, para tanto basta informar o número da proposta e revisão.

Atenciosamente,"""
                },
                "validacao": {
                    "texto_obrigatorio": True,
                    "dados_empresa_obrigatorios": ["nome", "endereco", "telefones", "email"],
                    "dados_usuario_obrigatorios": ["nome"]
                }
            },
            "pagina_3": {
                "tipo": "sobre_empresa",
                "editavel": ["conteudo_completo", "secoes"],
                "elementos": {
                    "titulo": "SOBRE A WORLD COMP",
                    "conteudo": """Há mais de uma década no mercado de manutenção de compressores de ar de parafuso, de diversas marcas, atendemos clientes em todo território brasileiro.""",
                    "secoes": [
                        {
                            "titulo": "FORNECIMENTO, SERVIÇO E LOCAÇÃO",
                            "conteudo": "A World Comp oferece os serviços de Manutenção Preventiva e Corretiva em Compressores e Unidades Compressoras, Venda de peças, Locação de compressores, Recuperação de Unidades Compressoras, Recuperação de Trocadores de Calor e Contrato de Manutenção em compressores de marcas como: Atlas Copco, Ingersoll Rand, Chicago Pneumatic entre outros."
                        },
                        {
                            "titulo": "CONTE CONOSCO PARA UMA PARCERIA",
                            "conteudo": "Adaptamos nossa oferta para suas necessidades, objetivos e planejamento. Trabalhamos para que seu processo seja eficiente."
                        },
                        {
                            "titulo": "MELHORIA CONTÍNUA",
                            "conteudo": "Continuamente investindo em comprometimento, competência e eficiência de nossos serviços, produtos e estrutura para garantirmos a máxima eficiência de sua produtividade."
                        },
                        {
                            "titulo": "QUALIDADE DE SERVIÇOS",
                            "conteudo": "Com uma equipe de técnicos altamente qualificados e constantemente treinados para atendimentos em todos os modelos de compressores de ar, a World Comp oferece garantia de excelente atendimento e produtividade superior com rapidez e eficácia."
                        }
                    ]
                }
            },
            "pagina_4": {
                "tipo": "proposta",
                "editavel": ["ordem_elementos"],
                "elementos": {
                    "ordem": ["dados_proposta", "dados_cliente", "dados_compressor", "descricao_servico", "relacao_pecas", "tabela_itens", "valor_total", "condicoes_comerciais", "observacoes"],
                    "dados_proposta": "{{proposta.numero}} - {{proposta.data}}",
                    "dados_cliente": "{{cliente.nome}} - {{cliente.cnpj}}",
                    "dados_compressor": "{{compressor.modelo}} - {{compressor.serie}}",
                    "descricao_servico": "{{servico.descricao}}",
                    "relacao_pecas": "{{pecas.relacao}}",
                    "tabela_itens": "{{itens_cotacao}}",
                    "valor_total": "{{proposta.valor_total}}",
                    "condicoes_comerciais": "{{condicoes.comerciais}}",
                    "observacoes": "{{proposta.observacoes}}"
                },
                "validacao": {
                    "dados_obrigatorios": ["proposta.numero", "proposta.data", "cliente.nome"],
                    "elementos_nao_editaveis": ["tabela_itens", "valor_total"]
                }
            },
            "cabecalho": {
                "template": "{{empresa.nome}} | PROPOSTA COMERCIAL | NUMERO: {{proposta.numero}} | DATA: {{proposta.data}}",
                "campos_editaveis": ["empresa.nome"],
                "campos_obrigatorios": ["proposta.numero", "proposta.data"],
                "posicao": "top",
                "altura": 20,
                "estilo": {
                    "fonte": "Arial",
                    "tamanho": 8,
                    "cor": "#000000",
                    "fundo": "#f0f0f0"
                }
            },
            "rodape": {
                "template": "{{empresa.endereco}} | CNPJ: {{empresa.cnpj}} | E-mail: {{empresa.email}} | Fone: {{empresa.telefones}}",
                "campos_editaveis": ["empresa.endereco", "empresa.cnpj", "empresa.email", "empresa.telefones"],
                "campos_obrigatorios": ["empresa.cnpj"],
                "posicao": "bottom",
                "altura": 15,
                "estilo": {
                    "fonte": "Arial",
                    "tamanho": 8,
                    "cor": "#000000",
                    "fundo": "#f0f0f0"
                }
            },
            "validacao_global": {
                "campos_sistema_obrigatorios": [
                    "empresa.nome",
                    "empresa.cnpj", 
                    "empresa.endereco",
                    "empresa.telefones",
                    "empresa.email"
                ],
                "permitir_edicao_apenas_campos_existentes": True,
                "backup_automatico": True,
                "versioning": True
            }
        }
    
    def save_base_template(self, template):
        """Salvar template base"""
        try:
            os.makedirs(os.path.dirname(self.base_template_path), exist_ok=True)
            with open(self.base_template_path, 'w', encoding='utf-8') as f:
                json.dump(template, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Erro ao salvar template base: {e}")
            return False
    
    def load_base_template(self):
        """Carregar template base"""
        try:
            if os.path.exists(self.base_template_path):
                with open(self.base_template_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return self.get_default_template()
        except Exception as e:
            print(f"Erro ao carregar template base: {e}")
            return self.get_default_template()
    
    def get_user_template_path(self, username):
        """Obter caminho do template do usuário"""
        return os.path.join(self.user_templates_dir, f"{username}.json")
    
    def get_client_template_path(self, client_id):
        """Obter caminho do template do cliente"""
        return os.path.join(self.client_templates_dir, f"cliente_{client_id}.json")
    
    def save_user_template(self, username, template):
        """Salvar template personalizado do usuário"""
        try:
            # Adicionar metadados
            template['metadata'] = {
                'tipo': 'usuario',
                'usuario': username,
                'criado_em': datetime.now().isoformat(),
                'versao': '1.0',
                'baseado_em': 'template_base'
            }
            
            template_path = self.get_user_template_path(username)
            with open(template_path, 'w', encoding='utf-8') as f:
                json.dump(template, f, ensure_ascii=False, indent=2)
            
            # Registrar no banco de dados
            self.register_template_in_db('usuario', username, template_path)
            return True
            
        except Exception as e:
            print(f"Erro ao salvar template do usuário {username}: {e}")
            return False
    
    def save_client_template(self, client_id, template):
        """Salvar template personalizado do cliente"""
        try:
            # Adicionar metadados
            template['metadata'] = {
                'tipo': 'cliente',
                'cliente_id': client_id,
                'criado_em': datetime.now().isoformat(),
                'versao': '1.0',
                'baseado_em': 'template_base'
            }
            
            template_path = self.get_client_template_path(client_id)
            with open(template_path, 'w', encoding='utf-8') as f:
                json.dump(template, f, ensure_ascii=False, indent=2)
            
            # Registrar no banco de dados
            self.register_template_in_db('cliente', str(client_id), template_path)
            return True
            
        except Exception as e:
            print(f"Erro ao salvar template do cliente {client_id}: {e}")
            return False
    
    def load_user_template(self, username):
        """Carregar template do usuário ou base como fallback"""
        user_template_path = self.get_user_template_path(username)
        
        try:
            if os.path.exists(user_template_path):
                with open(user_template_path, 'r', encoding='utf-8') as f:
                    template = json.load(f)
                    # Verificar se é válido
                    if self.validate_template(template):
                        return template
                    else:
                        print(f"Template do usuário {username} inválido, usando base")
            
            # Fallback para template base
            return self.load_base_template()
            
        except Exception as e:
            print(f"Erro ao carregar template do usuário {username}: {e}")
            return self.load_base_template()
    
    def load_client_template(self, client_id):
        """Carregar template do cliente ou base como fallback"""
        client_template_path = self.get_client_template_path(client_id)
        
        try:
            if os.path.exists(client_template_path):
                with open(client_template_path, 'r', encoding='utf-8') as f:
                    template = json.load(f)
                    # Verificar se é válido
                    if self.validate_template(template):
                        return template
                    else:
                        print(f"Template do cliente {client_id} inválido, usando base")
            
            # Fallback para template base
            return self.load_base_template()
            
        except Exception as e:
            print(f"Erro ao carregar template do cliente {client_id}: {e}")
            return self.load_base_template()
    
    def get_template_for_proposal(self, username, client_id=None):
        """Obter template para uma proposta específica (prioridade: cliente > usuário > base)"""
        # 1. Tentar template específico do cliente
        if client_id:
            client_template = self.load_client_template(client_id)
            if client_template and client_template.get('metadata', {}).get('tipo') == 'cliente':
                return client_template
        
        # 2. Tentar template do usuário
        user_template = self.load_user_template(username)
        if user_template and user_template.get('metadata', {}).get('tipo') == 'usuario':
            return user_template
        
        # 3. Fallback para template base
        return self.load_base_template()
    
    def validate_template(self, template):
        """Validar estrutura do template"""
        required_keys = ['pagina_1', 'pagina_2', 'pagina_3', 'pagina_4', 'cabecalho', 'rodape']
        
        if not isinstance(template, dict):
            return False
        
        for key in required_keys:
            if key not in template:
                return False
        
        # Validar estrutura básica de cada página
        for i in range(1, 5):
            page_key = f'pagina_{i}'
            page = template[page_key]
            
            if not isinstance(page, dict):
                return False
                
            if 'tipo' not in page or 'elementos' not in page:
                return False
        
        return True
    
    def register_template_in_db(self, tipo, identificador, caminho):
        """Registrar template no banco de dados"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Criar tabela se não existir
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS templates_personalizados (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipo TEXT NOT NULL,
                    identificador TEXT NOT NULL,
                    caminho TEXT NOT NULL,
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ativo BOOLEAN DEFAULT 1,
                    UNIQUE(tipo, identificador)
                )
            ''')
            
            # Inserir ou atualizar
            cursor.execute('''
                INSERT OR REPLACE INTO templates_personalizados 
                (tipo, identificador, caminho, criado_em, ativo) 
                VALUES (?, ?, ?, ?, 1)
            ''', (tipo, identificador, caminho, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Erro ao registrar template no banco: {e}")
            return False
    
    def list_user_templates(self):
        """Listar todos os templates de usuários"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT identificador, caminho, criado_em 
                FROM templates_personalizados 
                WHERE tipo = 'usuario' AND ativo = 1
                ORDER BY criado_em DESC
            ''')
            
            templates = cursor.fetchall()
            conn.close()
            return templates
            
        except Exception as e:
            print(f"Erro ao listar templates de usuários: {e}")
            return []
    
    def list_client_templates(self):
        """Listar todos os templates de clientes"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT identificador, caminho, criado_em 
                FROM templates_personalizados 
                WHERE tipo = 'cliente' AND ativo = 1
                ORDER BY criado_em DESC
            ''')
            
            templates = cursor.fetchall()
            conn.close()
            return templates
            
        except Exception as e:
            print(f"Erro ao listar templates de clientes: {e}")
            return []
    
    def backup_template(self, template_path):
        """Criar backup de um template"""
        try:
            if not os.path.exists(template_path):
                return False
            
            backup_dir = os.path.join(self.templates_dir, "backups")
            os.makedirs(backup_dir, exist_ok=True)
            
            # Nome do backup com timestamp
            filename = os.path.basename(template_path)
            name, ext = os.path.splitext(filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{name}_backup_{timestamp}{ext}"
            backup_path = os.path.join(backup_dir, backup_filename)
            
            shutil.copy2(template_path, backup_path)
            return backup_path
            
        except Exception as e:
            print(f"Erro ao criar backup: {e}")
            return None
    
    def restore_from_backup(self, backup_path, target_path):
        """Restaurar template de um backup"""
        try:
            if os.path.exists(backup_path):
                shutil.copy2(backup_path, target_path)
                return True
            return False
        except Exception as e:
            print(f"Erro ao restaurar backup: {e}")
            return False
    
    def validate_field_access(self, field_path, available_fields):
        """Validar se um campo pode ser editado baseado nos dados disponíveis"""
        parts = field_path.split('.')
        if len(parts) != 2:
            return False
        
        category, field = parts
        return category in available_fields and field in available_fields[category]
    
    def get_template_validation_report(self, template, available_fields):
        """Gerar relatório de validação do template"""
        report = {
            'valido': True,
            'avisos': [],
            'erros': [],
            'campos_invalidos': []
        }
        
        # Validar campos do cabeçalho
        if 'cabecalho' in template:
            campos_editaveis = template['cabecalho'].get('campos_editaveis', [])
            for campo in campos_editaveis:
                if not self.validate_field_access(campo, available_fields):
                    report['campos_invalidos'].append(f"Cabeçalho: {campo}")
                    report['valido'] = False
        
        # Validar campos do rodapé
        if 'rodape' in template:
            campos_editaveis = template['rodape'].get('campos_editaveis', [])
            for campo in campos_editaveis:
                if not self.validate_field_access(campo, available_fields):
                    report['campos_invalidos'].append(f"Rodapé: {campo}")
                    report['valido'] = False
        
        # Verificar estrutura das páginas
        for i in range(1, 5):
            page_key = f'pagina_{i}'
            if page_key not in template:
                report['erros'].append(f"Página {i} não encontrada")
                report['valido'] = False
        
        # Verificar validação global
        if 'validacao_global' in template:
            campos_obrigatorios = template['validacao_global'].get('campos_sistema_obrigatorios', [])
            for campo in campos_obrigatorios:
                if not self.validate_field_access(campo, available_fields):
                    report['erros'].append(f"Campo obrigatório não disponível: {campo}")
                    report['valido'] = False
        
        return report
    
    def delete_user_template(self, username):
        """Deletar template do usuário"""
        try:
            template_path = self.get_user_template_path(username)
            
            # Criar backup antes de deletar
            backup_path = self.backup_template(template_path)
            
            if os.path.exists(template_path):
                os.remove(template_path)
            
            # Marcar como inativo no banco
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE templates_personalizados 
                SET ativo = 0 
                WHERE tipo = 'usuario' AND identificador = ?
            ''', (username,))
            conn.commit()
            conn.close()
            
            return True, backup_path
            
        except Exception as e:
            print(f"Erro ao deletar template do usuário {username}: {e}")
            return False, None
    
    def delete_client_template(self, client_id):
        """Deletar template do cliente"""
        try:
            template_path = self.get_client_template_path(client_id)
            
            # Criar backup antes de deletar
            backup_path = self.backup_template(template_path)
            
            if os.path.exists(template_path):
                os.remove(template_path)
            
            # Marcar como inativo no banco
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE templates_personalizados 
                SET ativo = 0 
                WHERE tipo = 'cliente' AND identificador = ?
            ''', (str(client_id),))
            conn.commit()
            conn.close()
            
            return True, backup_path
            
        except Exception as e:
            print(f"Erro ao deletar template do cliente {client_id}: {e}")
            return False, None