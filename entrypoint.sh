#!/bin/bash

# Espera o postgres ficar pronto
echo "Waiting for postgres..."
while ! nc -z postgres 5432; do
  sleep 1
done
echo "PostgreSQL started"

# Executa o script principal
python run.py