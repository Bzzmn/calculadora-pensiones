#!/bin/bash

if [ "$ENVIRONMENT" = "development" ]; then
    echo "Running in development mode..."
    # Usar variables de entorno del archivo .env
    exec uvicorn main:app --host 0.0.0.0 --port 80 --reload
else
    echo "Running in production mode..."
    # Usar variables de entorno del sistema
    exec uvicorn main:app --host 0.0.0.0 --port 80
fi 