#!/bin/bash

PORT=${PORT:-80}

if [ "$ENVIRONMENT" = "development" ]; then
    echo "Running in development mode..."
    # Usar variables de entorno del archivo .env
    exec uvicorn app.main:app --host 0.0.0.0 --port $PORT --reload
else
    echo "Running in production mode..."
    # Usar variables de entorno del sistema
    exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
fi 