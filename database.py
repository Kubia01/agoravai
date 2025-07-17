import sqlite3
import os
import hashlib

DB_NAME = "crm_compressores.db"
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

def criar_banco():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Tabela Usuários
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'operador',
        nome_completo TEXT,
        email TEXT,
        telefone TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Tabela Clientes - ATUALIZADA
    c.execute('''CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        nome_fantasia TEXT,
        cnpj TEXT UNIQUE,
        inscricao_estadual TEXT,
        inscricao_municipal TEXT,
        endereco TEXT,
        numero TEXT,
        complemento TEXT,
        bairro TEXT,
        cidade TEXT,
        estado TEXT,
        cep TEXT,
        telefone TEXT,
        email TEXT,
        site TEXT,
        prazo_pagamento TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Tabela Contatos do Cliente - NOVA
    c.execute('''CREATE TABLE IF NOT EXISTS contatos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER NOT NULL,
        nome TEXT NOT NULL,
        cargo TEXT,
        telefone TEXT,
        email TEXT,
        observacoes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
    )''')

    # Tabela Técnicos
    c.execute('''CREATE TABLE IF NOT EXISTS tecnicos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        especialidade TEXT,
        telefone TEXT,
        email TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Tabela Produtos/Serviços/Kits
    c.execute('''CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        tipo TEXT NOT NULL CHECK (tipo IN ('Serviço', 'Produto', 'Kit')),
        ncm TEXT,
        valor_unitario REAL DEFAULT 0,
        descricao TEXT,
        ativo BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Tabela Itens do Kit - RENOMEADA
    c.execute('''CREATE TABLE IF NOT EXISTS kit_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kit_id INTEGER NOT NULL,
        produto_id INTEGER NOT NULL,
        quantidade REAL NOT NULL DEFAULT 1,
        FOREIGN KEY (kit_id) REFERENCES produtos(id) ON DELETE CASCADE,
        FOREIGN KEY (produto_id) REFERENCES produtos(id)
    )''')

    # Tabela Cotações
    c.execute('''CREATE TABLE IF NOT EXISTS cotacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero_proposta TEXT NOT NULL UNIQUE,
        cliente_id INTEGER NOT NULL,
        responsavel_id INTEGER NOT NULL,
        data_criacao DATE NOT NULL,
        data_validade DATE,
        modelo_compressor TEXT,
        numero_serie_compressor TEXT,
        descricao_atividade TEXT,
        observacoes TEXT,
        valor_total REAL DEFAULT 0,
        tipo_frete TEXT DEFAULT 'FOB',
        condicao_pagamento TEXT,
        prazo_entrega TEXT,
        moeda TEXT DEFAULT 'BRL',
        status TEXT DEFAULT 'Em Aberto',
        caminho_arquivo_pdf TEXT,
        relacao_pecas TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (cliente_id) REFERENCES clientes(id),
        FOREIGN KEY (responsavel_id) REFERENCES usuarios(id)
    )''')

    # Tabela Itens da Cotação
    c.execute('''CREATE TABLE IF NOT EXISTS itens_cotacao (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cotacao_id INTEGER NOT NULL,
        produto_id INTEGER,
        tipo TEXT NOT NULL,
        item_nome TEXT NOT NULL,
        quantidade REAL NOT NULL,
        descricao TEXT,
        valor_unitario REAL NOT NULL,
        valor_total_item REAL NOT NULL,
        eh_kit BOOLEAN DEFAULT 0,
        kit_id INTEGER,
        mao_obra REAL DEFAULT 0,
        deslocamento REAL DEFAULT 0,
        estadia REAL DEFAULT 0,
        FOREIGN KEY (cotacao_id) REFERENCES cotacoes(id),
        FOREIGN KEY (produto_id) REFERENCES produtos(id),
        FOREIGN KEY (kit_id) REFERENCES itens_cotacao(id)
    )''')

    # Tabela Relatórios Técnicos - ATUALIZADA com campos das abas 2 e 3
    c.execute('''CREATE TABLE IF NOT EXISTS relatorios_tecnicos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero_relatorio TEXT NOT NULL UNIQUE,
        cliente_id INTEGER NOT NULL,
        responsavel_id INTEGER NOT NULL,
        data_criacao DATE NOT NULL,
        formulario_servico TEXT,
        tipo_servico TEXT,
        descricao_servico TEXT,
        data_recebimento DATE,
        
        -- Aba 1: Condição Inicial
        condicao_encontrada TEXT,
        placa_identificacao TEXT,
        acoplamento TEXT,
        aspectos_rotores TEXT,
        valvulas_acopladas TEXT,
        data_recebimento_equip TEXT,
        
        -- Aba 2: Peritagem do Subconjunto
        parafusos_pinos TEXT,
        superficie_vedacao TEXT,
        engrenagens TEXT,
        bico_injertor TEXT,
        rolamentos TEXT,
        aspecto_oleo TEXT,
        data_peritagem TEXT,
        
        -- Aba 3: Desmembrando Unidade Compressora
        interf_desmontagem TEXT,
        aspecto_rotores_aba3 TEXT,
        aspecto_carcaca TEXT,
        interf_mancais TEXT,
        galeria_hidraulica TEXT,
        data_desmembracao TEXT,
        
        -- Aba 4: Relação de Peças e Serviços
        servicos_propostos TEXT,
        pecas_recomendadas TEXT,
        data_pecas TEXT,
        
        -- Outros campos
        cotacao_id INTEGER,
        tempo_trabalho_total TEXT,
        tempo_deslocamento_total TEXT,
        fotos TEXT,
        anexos_aba1 TEXT,
        anexos_aba2 TEXT,
        anexos_aba3 TEXT,
        anexos_aba4 TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        
        FOREIGN KEY (cliente_id) REFERENCES clientes(id),
        FOREIGN KEY (responsavel_id) REFERENCES usuarios(id),
        FOREIGN KEY (cotacao_id) REFERENCES cotacoes(id)
    )''')

    # Tabela Eventos de Campo
    c.execute('''CREATE TABLE IF NOT EXISTS eventos_campo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        relatorio_id INTEGER NOT NULL,
        tecnico_id INTEGER NOT NULL,
        data_hora DATETIME NOT NULL,
        evento TEXT NOT NULL,
        tipo TEXT NOT NULL,
        FOREIGN KEY (relatorio_id) REFERENCES relatorios_tecnicos(id),
        FOREIGN KEY (tecnico_id) REFERENCES tecnicos(id)
    )''')

    # Migração de dados se necessário
    try:
        # Verificar se existe a coluna 'contato' na tabela clientes (estrutura antiga)
        c.execute("PRAGMA table_info(clientes)")
        columns = [column[1] for column in c.fetchall()]
        
        if 'contato' in columns:
            print("Migrando estrutura antiga de clientes...")
            
            # Migrar dados da coluna 'contato' para a nova tabela 'contatos'
            c.execute("SELECT id, contato FROM clientes WHERE contato IS NOT NULL AND contato != ''")
            clientes_com_contato = c.fetchall()
            
            for cliente_id, contato in clientes_com_contato:
                # Inserir contato principal
                c.execute("""
                    INSERT OR IGNORE INTO contatos (cliente_id, nome, cargo, observacoes)
                    VALUES (?, ?, ?, ?)
                """, (cliente_id, contato, "Contato Principal", "Migrado da estrutura anterior"))
                
            # Remover colunas antigas da tabela clientes (SQLite não suporta DROP COLUMN diretamente)
            # Vamos criar uma nova tabela e migrar os dados
            c.execute('''CREATE TABLE IF NOT EXISTS clientes_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                nome_fantasia TEXT,
                cnpj TEXT UNIQUE,
                inscricao_estadual TEXT,
                inscricao_municipal TEXT,
                endereco TEXT,
                numero TEXT,
                complemento TEXT,
                bairro TEXT,
                cidade TEXT,
                estado TEXT,
                cep TEXT,
                telefone TEXT,
                email TEXT,
                site TEXT,
                prazo_pagamento TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            
            # Migrar dados essenciais
            c.execute("""
                INSERT INTO clientes_new (id, nome, nome_fantasia, cnpj, endereco, cidade, estado, cep, telefone, email, site, prazo_pagamento, created_at, updated_at)
                SELECT id, nome, nome_fantasia, cnpj, endereco, cidade, estado, cep, telefone, email, site, prazo_pagamento, created_at, updated_at
                FROM clientes
            """)
            
            # Renomear tabelas
            c.execute("DROP TABLE clientes")
            c.execute("ALTER TABLE clientes_new RENAME TO clientes")
            
            print("Migração concluída!")
            
    except sqlite3.Error as e:
        print(f"Erro durante migração: {e}")
    
    # Verificar se kit_composicao existe e renomear para kit_items
    try:
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='kit_composicao'")
        if c.fetchone():
            print("Renomeando tabela kit_composicao para kit_items...")
            c.execute("ALTER TABLE kit_composicao RENAME TO kit_items")
            print("Renomeação concluída!")
    except sqlite3.Error as e:
        print(f"Erro ao renomear tabela: {e}")

    # Adicionar usuários padrão
    try:
        admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
        c.execute("INSERT OR IGNORE INTO usuarios (username, password, role, nome_completo, email, telefone) VALUES (?, ?, ?, ?, ?, ?)",
                  ('admin', admin_password, 'admin', 'Administrador Master', 'admin@empresa.com', '(11) 99999-9999'))
        
        master_password = hashlib.sha256('master123'.encode()).hexdigest()
        c.execute("INSERT OR IGNORE INTO usuarios (username, password, role, nome_completo, email, telefone) VALUES (?, ?, ?, ?, ?, ?)",
                  ('master', master_password, 'admin', 'Usuário Master', 'master@empresa.com', '(11) 98888-8888'))
    except sqlite3.IntegrityError:
        pass

    conn.commit()
    conn.close()

if __name__ == "__main__":
    criar_banco()
    print("Banco de dados criado com sucesso!")
