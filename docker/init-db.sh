#!/bin/bash
# Crea las bases de datos del ecosistema dentro del Postgres compartido.
# Se ejecuta automáticamente en el primer arranque del contenedor postgres
# (montado en /docker-entrypoint-initdb.d/).
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE auth_db;
    CREATE DATABASE afiliados_db;
EOSQL