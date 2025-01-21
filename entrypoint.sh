#!/bin/sh

export PGPASSWORD="${DB_PASSWORD}"

# Espera o postgres ficar pronto
echo "Waiting for postgres..."
while ! nc -z postgres 5432; do
  sleep 5
done
echo "PostgreSQL started"


# Criar database
psql -h postgres -p 5432 -U "${DB_USER}" -d postgres <<-EOSQL
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = '${DB_DATABASE}') THEN
        CREATE DATABASE ${DB_DATABASE} WITH ENCODING='UTF8' LC_COLLATE='en_US.utf8' LC_CTYPE='en_US.utf8' TEMPLATE template0;
    END IF;
END
\$\$;
EOSQL

# Conectar ao banco criado e criar schemas
psql -h postgres -p 5432 -U "${DB_USER}" -d "${DB_DATABASE}" <<-EOSQL
    CREATE SCHEMA IF NOT EXISTS bronze;
    CREATE SCHEMA IF NOT EXISTS silver;
    CREATE SCHEMA IF NOT EXISTS gold;
EOSQL

# Executar a aplicação
python run.py