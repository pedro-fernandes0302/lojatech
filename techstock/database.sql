PRAGMA foreign_keys = OFF;
DROP VIEW IF EXISTS estoque_fisico;
DROP TABLE IF EXISTS itens_venda;
DROP TABLE IF EXISTS vendas;
DROP TABLE IF EXISTS movimentacoes;
DROP TABLE IF EXISTS ativos_digitais;
DROP TABLE IF EXISTS clientes;
DROP TABLE IF EXISTS produtos;
DROP TABLE IF EXISTS fornecedor;
DROP TABLE IF EXISTS categoria;
DROP TABLE IF EXISTS usuarios;

CREATE TABLE usuarios (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE COLLATE NOCASE,
    senha_hash TEXT NOT NULL,
    perfil TEXT NOT NULL CHECK (perfil IN ('GERENTE', 'OPERADOR')),
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE categoria (
    id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_categoria TEXT NOT NULL UNIQUE,
    descricao TEXT NOT NULL DEFAULT ''
);
CREATE TABLE fornecedor (
    id_fornecedor INTEGER PRIMARY KEY AUTOINCREMENT,
    razao_social TEXT NOT NULL,
    cnpj TEXT NOT NULL UNIQUE,
    telefone TEXT,
    email TEXT NOT NULL UNIQUE COLLATE NOCASE
);
CREATE TABLE produtos (
    id_produto INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT NOT NULL UNIQUE,
    nome_produto TEXT NOT NULL,
    fabricante TEXT NOT NULL,
    preco REAL NOT NULL CHECK (preco > 0),
    tipo TEXT NOT NULL CHECK (tipo IN ('Hardware', 'Software', 'Periferico')),
    especificacao TEXT NOT NULL DEFAULT '',
    modalidade TEXT,
    estoque_atual INTEGER NOT NULL DEFAULT 0 CHECK (estoque_atual >= 0),
    estoque_minimo INTEGER NOT NULL DEFAULT 0 CHECK (estoque_minimo >= 0),
    localizacao TEXT NOT NULL,
    id_categoria INTEGER NOT NULL REFERENCES categoria(id_categoria) ON DELETE RESTRICT,
    id_fornecedor INTEGER NOT NULL REFERENCES fornecedor(id_fornecedor) ON DELETE RESTRICT
);
-- estoque_atual é a única fonte de saldo; a VIEW mantém compatibilidade sem duplicar estoque.
CREATE VIEW estoque_fisico AS
SELECT id_produto AS id_estoque, id_produto, estoque_atual AS quantidade
FROM produtos WHERE tipo IN ('Hardware', 'Periferico');
CREATE TABLE ativos_digitais (
    id_licenca INTEGER PRIMARY KEY AUTOINCREMENT,
    id_produto INTEGER NOT NULL REFERENCES produtos(id_produto) ON DELETE RESTRICT,
    chave TEXT NOT NULL UNIQUE,
    modalidade TEXT NOT NULL,
    id_venda INTEGER REFERENCES vendas(id_venda) ON DELETE RESTRICT
);
CREATE TABLE clientes (
    id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE COLLATE NOCASE,
    telefone TEXT,
    cnpj TEXT NOT NULL UNIQUE
);
CREATE TABLE vendas (
    id_venda INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_pedido TEXT NOT NULL UNIQUE,
    id_cliente INTEGER NOT NULL REFERENCES clientes(id_cliente) ON DELETE RESTRICT,
    id_usuario INTEGER NOT NULL REFERENCES usuarios(id_usuario) ON DELETE RESTRICT,
    data_venda TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status_venda TEXT NOT NULL DEFAULT 'Concluida',
    valor_total_centavos INTEGER NOT NULL DEFAULT 0 CHECK (valor_total_centavos >= 0)
);
CREATE TABLE itens_venda (
    id_item INTEGER PRIMARY KEY AUTOINCREMENT,
    id_venda INTEGER NOT NULL REFERENCES vendas(id_venda) ON DELETE RESTRICT,
    id_produto INTEGER NOT NULL REFERENCES produtos(id_produto) ON DELETE RESTRICT,
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    preco_unitario_centavos INTEGER NOT NULL CHECK (preco_unitario_centavos > 0),
    subtotal_centavos INTEGER NOT NULL CHECK (
        subtotal_centavos = quantidade * preco_unitario_centavos
    ),
    UNIQUE (id_venda, id_produto)
);
CREATE TABLE movimentacoes (
    id_movimentacao INTEGER PRIMARY KEY AUTOINCREMENT,
    id_produto INTEGER NOT NULL REFERENCES produtos(id_produto) ON DELETE RESTRICT,
    id_venda INTEGER REFERENCES vendas(id_venda) ON DELETE RESTRICT,
    id_usuario INTEGER REFERENCES usuarios(id_usuario) ON DELETE RESTRICT,
    tipo TEXT NOT NULL CHECK (tipo IN ('ENTRADA', 'SAIDA')),
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    data_hora TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    observacao TEXT
);
CREATE TRIGGER movimentacoes_sem_update
BEFORE UPDATE ON movimentacoes
BEGIN
    SELECT RAISE(ABORT, 'Livro-Razão é imutável');
END;
CREATE TRIGGER movimentacoes_sem_delete
BEFORE DELETE ON movimentacoes
BEGIN
    SELECT RAISE(ABORT, 'Livro-Razão é imutável');
END;
CREATE TRIGGER itens_venda_sem_update BEFORE UPDATE ON itens_venda
BEGIN
    SELECT RAISE(ABORT, 'Item de venda é imutável');
END;
CREATE TRIGGER itens_venda_sem_delete BEFORE DELETE ON itens_venda
BEGIN
    SELECT RAISE(ABORT, 'Item de venda é imutável');
END;
CREATE TRIGGER vendas_sem_delete BEFORE DELETE ON vendas
BEGIN
    SELECT RAISE(ABORT, 'Venda não pode ser apagada');
END;
CREATE TRIGGER vendas_total_imutavel
BEFORE UPDATE OF valor_total_centavos ON vendas
WHEN OLD.valor_total_centavos <> 0
BEGIN
    SELECT RAISE(ABORT, 'Total da venda é imutável');
END;

INSERT INTO categoria (nome_categoria, descricao) VALUES
('Processadores', 'Componentes de processamento'),
('Memorias', 'Memorias RAM'),
('Armazenamento', 'Unidades SSD'),
('Perifericos', 'Acessorios de informatica'),
('Softwares', 'Programas e licencas');
INSERT INTO fornecedor (razao_social, cnpj, telefone, email) VALUES
('AMD Distribuidora', '12345678000190', '62999999999', 'contato@amd.com'),
('Kingston Brasil', '23456789000191', '62988888888', 'contato@kingston.com'),
('Microsoft Brasil', '34567890000192', '62977777777', 'contato@microsoft.com');
INSERT INTO produtos
(sku, nome_produto, fabricante, preco, tipo, especificacao, modalidade, estoque_atual, estoque_minimo, localizacao, id_categoria, id_fornecedor)
VALUES
('PROC001', 'Ryzen 5500', 'AMD', 529.99, 'Hardware', 'Processador AMD Ryzen 5', NULL, 10, 3, 'Prateleira A1', 1, 1),
('RAM001', 'Memoria RAM 16GB', 'Kingston', 300.00, 'Hardware', 'Memoria DDR4 16GB', NULL, 20, 5, 'Prateleira A2', 2, 2),
('SSD001', 'SSD Kingston 1TB', 'Kingston', 450.00, 'Hardware', 'SSD NVMe 1TB', NULL, 15, 4, 'Prateleira B1', 3, 2),
('SOFT001', 'Microsoft 365', 'Microsoft', 400.00, 'Software', 'Suite de escritorio', 'Assinatura anual', 2, 2, 'Cofre digital', 5, 3),
('SOFT002', 'Windows 11 Pro', 'Microsoft', 800.00, 'Software', 'Sistema operacional Windows 11', 'OEM', 1, 2, 'Cofre digital', 5, 3),
('PER001', 'Mouse USB', 'Kingston', 50.00, 'Periferico', 'Mouse optico USB', NULL, 1, 3, 'Prateleira C1', 4, 2);
INSERT INTO ativos_digitais (id_produto, chave, modalidade) VALUES
(4, 'DEMO-M365-0001', 'Assinatura anual'),
(4, 'DEMO-M365-0002', 'Assinatura anual'),
(5, 'DEMO-WIN-0001', 'OEM');
INSERT INTO clientes (nome, email, telefone, cnpj) VALUES
('TechStore Cliente A', 'compras@cliente-a.com.br', '62999999999', '45678900000193'),
('TechStore Cliente B', 'financeiro@cliente-b.com.br', '62988888888', '56789000000194');
INSERT INTO movimentacoes (id_produto, tipo, quantidade, observacao) VALUES
(1, 'ENTRADA', 10, 'Estoque inicial'),
(2, 'ENTRADA', 20, 'Estoque inicial'),
(3, 'ENTRADA', 15, 'Estoque inicial'),
(4, 'ENTRADA', 2, 'Estoque inicial'),
(5, 'ENTRADA', 1, 'Estoque inicial'),
(6, 'ENTRADA', 1, 'Estoque inicial');
PRAGMA foreign_keys = ON;
