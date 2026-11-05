# TechStock Manager

Sistema web de gestÃ£o de inventÃ¡rio para a TechStore InformÃ¡tica, desenvolvido com Flask, SQLite e Bootstrap 5. Gerencia produtos fÃ­sicos, licenÃ§as de software, categorias, fornecedores e movimentaÃ§Ãµes de estoque.

## PrÃ©-requisitos

- Python 3.10 ou superior
- pip

## InstalaÃ§Ã£o e execuÃ§Ã£o

```powershell
cd techstock
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

TambÃ©m Ã© possÃ­vel iniciar com o Flask:

```powershell
flask --app app run --debug
```

Acesse http://127.0.0.1:5000.

## Organização das rotas

As rotas estão separadas na pasta `routers`. O arquivo `app.py` cria a aplicação e registra os Blueprints.

## Banco de dados

Na primeira execuÃ§Ã£o, `techstock.db` Ã© criado automaticamente se nÃ£o existir. Para recriar manualmente, primeiro exclua o arquivo `techstock.db` e execute `python app.py` ou `python -c "from db import init_db; init_db()"`.

## Rotas principais

- `/` â€” dashboard de estoque;
- `/produtos/novo` â€” cadastro de produto;
- `/produtos/<id>/excluir` â€” descontinuaÃ§Ã£o de produto (POST);
- `/movimentacoes/nova` â€” entrada ou saÃ­da de estoque;
- `/movimentacoes` â€” histÃ³rico;
- `/categorias` â€” lista e cadastro de categorias;
- `/categorias/<id>/excluir` â€” exclusÃ£o de categoria (POST);
- `/fornecedores` â€” lista e cadastro de fornecedores;
- `/fornecedores/<id>/excluir` â€” exclusÃ£o de fornecedor (POST).

## Estrutura das tabelas

- **categorias:** identificador Ãºnico e nome Ãºnico;
- **fornecedores:** razÃ£o social, CNPJ Ãºnico, telefone e e-mail;
- **produtos:** SKU Ãºnico, fabricante, tipo, licenÃ§a opcional, preÃ§o, estoques, localizaÃ§Ã£o e vÃ­nculos obrigatÃ³rios com categoria e fornecedor;
- **movimentacoes:** produto, tipo ENTRADA/SAIDA, quantidade positiva, data/hora e observaÃ§Ã£o.

A integridade referencial Ã© ativada em cada conexÃ£o com `PRAGMA foreign_keys = ON`. Categorias, fornecedores e produtos vinculados nÃ£o podem ser excluÃ­dos enquanto houver dependÃªncias. Entradas e saÃ­das sÃ£o aplicadas no mesmo estoque em uma Ãºnica transaÃ§Ã£o. SaÃ­das maiores que o saldo sÃ£o recusadas sem alteraÃ§Ã£o de dados.

## Regras de negÃ³cio

- PreÃ§o deve ser maior que zero.
- Estoques nÃ£o podem ser negativos.
- Tipos aceitos: Hardware, Software e PerifÃ©rico.
- Modalidades aceitas: Assinatura Anual, PerpÃ©tua/ESD e OEM.
- Produto Ã© destacado quando `estoque_atual <= estoque_minimo`.
- Toda movimentaÃ§Ã£o deve ter quantidade inteira positiva.

## Reset completo

Para repor categorias, fornecedores, produtos e movimentaÃ§Ãµes de demonstraÃ§Ã£o:

```powershell
Remove-Item -Force .\techstock.db -ErrorAction SilentlyContinue
python app.py
```

Alternativamente, dentro do diretÃ³rio do projeto:

```powershell
python -c "from db import init_db; init_db()"
```

A execuÃ§Ã£o automÃ¡tica recria o banco na inicializaÃ§Ã£o e pode ser interrompida com Ctrl+C.

