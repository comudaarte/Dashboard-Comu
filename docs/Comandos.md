# Comandos Alembic

## Atualização Alembic
    docker-compose exec api bash
    cd src
    alembic upgrade head

# Comando Banco de dados

docker-compose exec db psql -U metrics_user -d metrics_db - Acessar Banco de Dados

docker-compose up - Iniciar o banco

docker-compose exec db psql -U metrics_user -d metrics_db -c "SELECT id, id_transacao_origem, assinatura_id, produto_nome, status, valor, taxa_reembolso, plataforma, valor_bruto, valor_liquido, metodo_pagamento, motivo_recusa, tipo_recusa, data_transacao, nome_oferta FROM transacoes ORDER BY id DESC LIMIT 5;" - PLanilha Transações

## Acessar Tabelas

SELECT * FROM clientes;
SELECT * FROM assinaturas;
SELECT * FROM transacoes;

## Excluir todos os dados de uma tabela

DELETE FROM transacoes;
DELETE FROM assinaturas;
DELETE FROM clientes;

## Excluir todos os dados e resetar o contador de IDs (sequência)

TRUNCATE TABLE transacoes RESTART IDENTITY CASCADE;
TRUNCATE TABLE assinaturas RESTART IDENTITY CASCADE;
TRUNCATE TABLE clientes RESTART IDENTITY CASCADE;

## Excluir dados de um cliente específico (exemplo por email)

DELETE FROM transacoes WHERE cliente_id = (SELECT id FROM clientes WHERE email = 'email@cliente.com');
DELETE FROM assinaturas WHERE cliente_id = (SELECT id FROM clientes WHERE email = 'email@cliente.com');
DELETE FROM clientes WHERE email = 'email@cliente.com';

DELETE FROM transacoes WHERE id =