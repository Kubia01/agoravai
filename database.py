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

    # Tabela Clientes
    c.execute('''CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        contato TEXT,
        nome_fantasia TEXT,
        cnpj TEXT UNIQUE,
        endereco TEXT,
        cidade TEXT,
        estado TEXT,
        cep TEXT,
        pais TEXT DEFAULT 'Brasil',
        telefone TEXT,
        email TEXT,
        site TEXT,
        prazo_pagamento TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Tabela Contatos do Cliente
    c.execute('''CREATE TABLE IF NOT EXISTS contatos_cliente (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER NOT NULL,
        nome TEXT NOT NULL,
        cargo TEXT,
        email TEXT,
        telefone TEXT,
        principal BOOLEAN DEFAULT 0,
        FOREIGN KEY (cliente_id) REFERENCES clientes(id)
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

    # NOVA: Tabela Produtos/Serviços/Kits
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

    # NOVA: Tabela Itens do Kit (relaciona produtos/serviços que compõem um kit)
    c.execute('''CREATE TABLE IF NOT EXISTS kit_composicao (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kit_id INTEGER NOT NULL,
        produto_id INTEGER NOT NULL,
        quantidade REAL NOT NULL DEFAULT 1,
        FOREIGN KEY (kit_id) REFERENCES produtos(id),
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

    # Tabela Itens da Cotação (ATUALIZADA)
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

    # Tabela Itens do Kit (mantida para compatibilidade)
    c.execute('''CREATE TABLE IF NOT EXISTS kit_itens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_cotacao_id INTEGER NOT NULL,
        tipo TEXT NOT NULL,
        nome TEXT NOT NULL,
        quantidade REAL NOT NULL,
        valor_unitario REAL NOT NULL,
        descricao TEXT,
        FOREIGN KEY (item_cotacao_id) REFERENCES itens_cotacao(id)
    )''')

    # database.py - Atualize a criação da tabela relatorios_tecnicos
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
        condicao_encontrada TEXT,
        placa_identificacao TEXT,
        acoplamento TEXT,
        aspectos_rotores TEXT,
        valvulas_acopladas TEXT,
        data_recebimento_equip TEXT,
        parafusos_pinos TEXT,
        superficie_vedacao TEXT,
        cotacao_id INTEGER,
        tempo_trabalho_total TEXT,
        tempo_deslocamento_total TEXT,
        servicos_propostos TEXT,
        pecas_recomendadas TEXT,
        data_pecas TEXT,
        fotos TEXT,
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
