#!/bin/sh

# Waits for PostgreSQL server availability
until pg_isready -h db -p 5432; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"

# Runs migrations to database
python manage.py migrate

# Starts server
python manage.py runserver 0.0.0.0:8000