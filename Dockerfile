# Build stage
FROM python:3.11-slim AS builder

WORKDIR /app

# Instalar dependencias de compilación y Cython
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip install Cython

# Copiar archivos necesarios para la compilación
COPY setup.py .
COPY pyproject.toml .
COPY app/ ./app/

# Compilar
RUN python setup.py build_ext --inplace

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema incluyendo wkhtmltopdf
RUN apt-get update && apt-get install -y \
    wkhtmltopdf \
    && rm -rf /var/lib/apt/lists/*

# Instalar uv
RUN pip install uv

# Copiar archivos compilados desde el builder
COPY --from=builder /app/app/calculator/*.so ./app/calculator/
COPY --from=builder /app/app/calculator/*.c ./app/calculator/
COPY --from=builder /app/app/calculator/__init__.py ./app/calculator/

# Copiar archivos de la aplicación
COPY pyproject.toml .
COPY app/ ./app/
COPY config.py .
COPY entrypoint.sh .

# Instalar dependencias usando uv con --system
RUN uv pip install --system -e .

# Exponer el puerto
EXPOSE 8000

# Hacer ejecutable el entrypoint
RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]