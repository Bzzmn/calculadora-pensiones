# Build stage
FROM python:3.9-slim as builder

WORKDIR /app

# Instalar dependencias de compilación y Cython
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip install Cython

# Copiar archivos necesarios para la compilación
COPY setup.py .
COPY calculator/ ./calculator/

# Compilar
RUN python setup.py build_ext --inplace

# Runtime stage
FROM python:3.9-slim

WORKDIR /app

# Instalar uv
RUN pip install uv

# Copiar archivos compilados desde el builder
COPY --from=builder /app/calculator/*.so ./calculator/
COPY --from=builder /app/calculator/__init__.py ./calculator/

# Copiar archivos de la aplicación
COPY requirements.txt .
COPY main.py .
COPY config.py .
COPY utils/ ./utils/
COPY templates/ ./templates/

# Instalar dependencias usando uv
RUN uv pip install --system -r requirements.txt

# Exponer el puerto
EXPOSE 80

# Script para manejar el inicio según el ambiente
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]