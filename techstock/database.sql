PRAGMA foreign_keys = OFF;
DROP TABLE IF EXISTS itens_venda;
DROP TABLE IF EXISTS vendas;
DROP TABLE IF EXISTS clientes;
DROP TABLE IF EXISTS ativos_digitais;
DROP TABLE IF EXISTS estoque_fisico;
DROP TABLE IF EXISTS movimentacoes;
DROP TABLE IF EXISTS produtos;
DROP TABLE IF EXISTS fornecedor;
DROP TABLE IF EXISTS categoria;

CREATE TABLE categoria (
    id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_categoria TEXT NOT NULL UNIQUE,
    descricao TEXT NOT NULL
);
CREATE TABLE fornecedor (
    id_fornecedor INTEGER PRIMARY KEY AUTOINCREMENT,
    razao_social TEXT NOT NULL,
    cnpj TEXT NOT NULL UNIQUE,
    telefone TEXT NOT NULL,
    email TEXT NOT NULL
);
CREATE TABLE produtos (
    id_produto INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT NOT NULL UNIQUE,
    nome_produto TEXT NOT NULL,
    fabricante TEXT NOT NULL,
    preco REAL NOT NULL CHECK (preco > 0),
    tipo TEXT NOT NULL CHECK (tipo IN ('Hardware', 'Software', 'Periferico')),
    especificacao TEXT NOT NULL,
    modalidade TEXT,
    estoque_atual INTEGER NOT NULL DEFAULT 0 CHECK (estoque_atual >= 0),
    estoque_minimo INTEGER NOT NULL CHECK (estoque_minimo >= 0),
    localizacao TEXT NOT NULL,
    id_categoria INTEGER NOT NULL,
    id_fornecedor INTEGER NOT NULL,
    FOREIGN KEY (id_categoria) REFERENCES categoria(id_categoria) ON DELETE RESTRICT,
    FOREIGN KEY (id_fornecedor) REFERENCES fornecedor(id_fornecedor) ON DELETE RESTRICT
);
CREATE TABLE movimentacoes (
    id_movimentacao INTEGER PRIMARY KEY AUTOINCREMENT,
    id_produto INTEGER NOT NULL,
    tipo TEXT NOT NULL CHECK (tipo IN ('Entrada', 'Saida')),
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    data_hora TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    observacao TEXT,
    FOREIGN KEY (id_produto) REFERENCES produtos(id_produto) ON DELETE RESTRICT
);
CREATE TABLE estoque_fisico (
    id_estoque INTEGER PRIMARY KEY AUTOINCREMENT,
    id_produto INTEGER NOT NULL,
    quantidade INTEGER NOT NULL CHECK (quantidade >= 0),
    FOREIGN KEY (id_produto) REFERENCES produtos(id_produto) ON DELETE RESTRICT
);
CREATE TABLE ativos_digitais (
    id_licenca INTEGER PRIMARY KEY AUTOINCREMENT,
    id_produto INTEGER NOT NULL,
    chave TEXT NOT NULL UNIQUE,
    modalidade TEXT NOT NULL,
    FOREIGN KEY (id_produto) REFERENCES produtos(id_produto) ON DELETE RESTRICT
);
CREATE TABLE clientes (
    id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT,
    telefone TEXT,
    cnpj TEXT NOT NULL UNIQUE
);
CREATE TABLE vendas (
    id_venda INTEGER PRIMARY KEY AUTOINCREMENT,
    id_cliente INTEGER NOT NULL,
    data_vendas TEXT,
    status_venda TEXT NOT NULL,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente) ON DELETE RESTRICT
);
CREATE TABLE itens_venda (
    id_item INTEGER PRIMARY KEY AUTOINCREMENT,
    id_venda INTEGER NOT NULL,
    id_produto INTEGER NOT NULL,
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    preco_unitario REAL NOT NULL CHECK (preco_unitario > 0),
    FOREIGN KEY (id_venda) REFERENCES vendas(id_venda) ON DELETE RESTRICT,
    FOREIGN KEY (id_produto) REFERENCES produtos(id_produto) ON DELETE RESTRICT
);

INSERT INTO categoria (nome_categoria, descricao) VALUES
('Processadores','Componentes de processamento'),
('Memorias','Memorias RAM'),
('Armazenamento','Unidades SSD'),
('Perifericos','Acessorios de informatica'),
('Softwares','Programas e licencas');

INSERT INTO fornecedor (razao_social,cnpj,telefone,email) VALUES
('AMD Distribuidora','12345678000190','62999999999','contato@amd.com'),
('Kingston Brasil','23456789000191','62988888888','contato@kingston.com'),
('Microsoft Brasil','34567890000192','62977777777','contato@microsoft.com');

INSERT INTO produtos (sku,nome_produto,fabricante,preco,tipo,especificacao,modalidade,estoque_atual,estoque_minimo,localizacao,id_categoria,id_fornecedor) VALUES
('PROC001','Ryzen 5500','AMD',529.99,'Hardware','Processador AMD Ryzen 5',NULL,10,3,'Prateleira A1',1,1),
('RAM001','Memoria RAM 16GB','Kingston',300.00,'Hardware','Memoria DDR4 16GB',NULL,20,5,'Prateleira A2',2,2),
('SSD001','SSD Kingston 1TB','Kingston',450.00,'Hardware','SSD NVMe 1TB',NULL,15,4,'Prateleira B1',3,2),
('SOFT001','Microsoft 365','Microsoft',400.00,'Software','Suite de escritorio','Assinatura anual',10,2,'Cofre digital',5,3),
('SOFT002','Windows 11 Pro','Microsoft',800.00,'Software','Sistema operacional Windows 11','OEM',8,2,'Cofre digital',5,3),
('PER001','Mouse USB','Kingston',50.00,'Periferico','Mouse optico USB',NULL,12,3,'Prateleira C1',4,2);

INSERT INTO estoque_fisico (id_produto,quantidade) VALUES (1,10),(2,20),(3,15),(6,12);
INSERT INTO ativos_digitais (id_produto,chave,modalidade) VALUES
(4,'XXXX-XXXX-XXXX-1111','Assinatura anual'),
(5,'XXXX-XXXX-XXXX-2222','OEM');
INSERT INTO clientes (nome,email,telefone,cnpj) VALUES
('Pedro Fernandes','pratofeito@email.com','62999999999','45678900000193'),
('Vitor Ferreira','vitorramos@email.com','62988888888','56789000000194');
INSERT INTO vendas (id_cliente,data_vendas,status_venda) VALUES
(1,'2026-11-05','Concluida'),(2,'2026-11-05','Pendente');
INSERT INTO itens_venda (id_venda,id_produto,quantidade,preco_unitario) VALUES
(1,1,1,529.99),(1,2,2,300.00),(2,4,1,400.00);
INSERT INTO movimentacoes (id_produto,tipo,quantidade,data_hora,observacao) VALUES
(1,'Entrada',10,'2026-11-05 09:00:00','Estoque inicial'),
(2,'Entrada',20,'2026-11-05 09:01:00','Estoque inicial'),
(3,'Entrada',15,'2026-11-05 09:02:00','Estoque inicial'),
(4,'Entrada',10,'2026-11-05 09:03:00','Estoque inicial'),
(5,'Entrada',8,'2026-11-05 09:04:00','Estoque inicial'),
(6,'Entrada',12,'2026-11-05 09:05:00','Estoque inicial');
PRAGMA foreign_keys = ON;
