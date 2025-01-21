FROM python:3.10

WORKDIR /app

RUN apt-get update && apt-get install -y netcat-openbsd postgresql-client

# Configurar pip para usar mirrors mais rápidos e aumentar timeout
RUN pip config set global.index-url https://pypi.org/simple/ && \
    pip config set global.timeout 100

COPY . .

RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry config installer.max-workers 4 && \
    poetry install --no-interaction --no-ansi --no-cache

# Criar script de entrada
COPY entrypoint.sh .

# Mudar para modo mais permissivo
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]