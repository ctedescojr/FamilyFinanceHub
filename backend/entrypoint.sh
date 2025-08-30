#!/bin/sh

# Aborta o script se qualquer comando falhar
set -e

echo "Aguardando o banco de dados..."
python manage.py wait_for_db

echo "Aplicando migrações do banco de dados..."
python manage.py migrate

echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Executa o comando principal do container (o que vem depois de 'docker-compose run ...')
exec "$@"