#!/bin/sh

export PGPASSWORD="${DB_PASSWORD}"

# Espera o postgres ficar pronto
echo "Waiting for postgres..."
while ! nc -z brt_postgres ${DB_PORT}; do
  sleep 5
done
echo "PostgreSQL started"


# Criar database
psql -h brt_postgres -p ${DB_PORT} -U "${DB_USER}" -d postgres <<-EOSQL
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = '${DB_DATABASE}') THEN
        CREATE DATABASE ${DB_DATABASE} WITH ENCODING='UTF8' LC_COLLATE='en_US.utf8' LC_CTYPE='en_US.utf8' TEMPLATE template0;
    END IF;
END
\$\$;
EOSQL

# Conectar ao banco criado e criar schemas
psql -h brt_postgres -p ${DB_PORT} -U "${DB_USER}" -d "${DB_DATABASE}" <<-EOSQL
    CREATE SCHEMA IF NOT EXISTS bronze;
    CREATE SCHEMA IF NOT EXISTS silver;
    CREATE SCHEMA IF NOT EXISTS gold;
EOSQL

# Configurar Prefect para usar servidor local e iniciar agente
prefect backend server
prefect server create-tenant -n civitas || true
prefect create project staging --skip-if-exists
prefect agent local start --name 'worker' -l 'pipelines' --no-hostname-label