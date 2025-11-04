#!/bin/sh

# Wait until PostgreSQL is ready
echo "Waiting for the database to be ready..."
until nc -z -v -w30 "$POSTGRES_HOST" "$POSTGRES_PORT"
do
  echo "Waiting for database connection..."
  sleep 2
done
echo "Database is ready!"
