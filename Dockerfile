# Build stage
FROM python:3.9-slim as builder

WORKDIR /app

# Instalar dependencias de compilación
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos necesarios para la compilación
COPY requirements.txt requirements-build.txt ./

# Instalar Cython y otras dependencias de compilación
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir Cython numpy

# Copiar el código fuente
COPY setup.py .
COPY calculator/ ./calculator/

# Compilar el código
RUN python setup.py build_ext --inplace

# Runtime stage
FROM python:3.9-slim

WORKDIR /app

# Copiar solo los archivos necesarios desde el builder
COPY --from=builder /app/calculator/*.so ./calculator/
COPY --from=builder /app/calculator/__init__.py ./calculator/

# Copiar el resto de los archivos de la aplicación
COPY requirements.txt .
COPY main.py .
COPY config.py .
COPY utils/ ./utils/

# Instalar dependencias de runtime
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto
EXPOSE 80

# Script para manejar el inicio según el ambiente
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]