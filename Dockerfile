# Build stage
FROM python:3.9-slim as builder

WORKDIR /app

# Instalar dependencias de compilación
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar solo los archivos necesarios para la compilación
COPY requirements.txt requirements-build.txt ./
COPY setup.py ./
COPY calculator ./calculator/

# Instalar dependencias de compilación
RUN pip install --no-cache-dir -r requirements-build.txt

# Compilar el código
RUN python setup.py build_ext --inplace

# Runtime stage
FROM python:3.9-slim

WORKDIR /app

# Copiar solo los archivos necesarios
COPY --from=builder /app/calculator/*.so ./calculator/
COPY --from=builder /app/calculator/__init__.py ./calculator/
COPY requirements.txt .
COPY main.py .

# Instalar solo dependencias de runtime
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"] 