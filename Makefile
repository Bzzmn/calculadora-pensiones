# Variables
IMAGE_NAME = pension-calculator
CONTAINER_NAME = pension-calculator-app
DEV_PORT = 8000
PROD_PORT = 80

# Comandos principales
.PHONY: build run-dev run-prod stop clean all-dev all-prod

# Construir la imagen
build: update-requirements compile
	docker build -t $(IMAGE_NAME) .

# Ejecutar el contenedor en desarrollo
run-dev:
	docker run -d \
		--name $(CONTAINER_NAME) \
		-p $(DEV_PORT):8000 \
		-v $(PWD)/.env:/app/.env \
		-v $(PWD)/app:/app/app \
		-v $(PWD)/config.py:/app/config.py \
		-e ENVIRONMENT=development \
		-e PORT=8000 \
		$(IMAGE_NAME)

# Ejecutar el contenedor en producción
run-prod:
	docker run -d \
		--name $(CONTAINER_NAME) \
		-p $(PROD_PORT):80 \
		--restart unless-stopped \
		-e PORT=80 \
		$(IMAGE_NAME)

# Detener y eliminar el contenedor
stop:
	docker stop $(CONTAINER_NAME) || true
	docker rm $(CONTAINER_NAME) || true

# Limpiar imágenes y contenedores
clean: stop clean-build
	docker rmi -f $(IMAGE_NAME) || true

# Reconstruir y reiniciar para desarrollo
all-dev: clean build run-dev

# Reconstruir y reiniciar para producción
all-prod: clean build run-prod

# Ver logs del contenedor
logs:
	docker logs -f $(CONTAINER_NAME)

# Estado del contenedor
status:
	docker ps -a | grep $(CONTAINER_NAME)

# Compilar el código
compile:
	PYTHONPATH=$(PWD) python setup.py build_ext --inplace

# Agregar clean-build para limpiar archivos de compilación
clean-build:
	sudo rm -rf build/
	sudo rm -f app/calculator/*.so
	sudo rm -f app/calculator/*.c
	sudo rm -f app/calculator/*.pyd
	sudo rm -f app/calculator/*.pyc
	sudo find . -type d -name "__pycache__" -exec rm -rf {} +

# Actualizar requirements.txt desde pyproject.toml
update-requirements:
	pip install toml
	python -c 'import toml; f = open("pyproject.toml"); p = toml.load(f); print("\n".join(p["project"]["dependencies"]))' > requirements.txt

# Limpiar y reinstalar todo el entorno
clean-all:
	sudo rm -rf .venv/
	sudo rm -rf build/
	sudo rm -rf dist/
	sudo rm -rf *.egg-info/
	sudo find . -type d -name "__pycache__" -exec rm -rf {} +
	sudo find . -type f -name "*.pyc" -delete
	sudo find . -type f -name "*.so" -delete
	sudo find . -type f -name "*.c" -delete
	/usr/bin/python3.11 -m venv .venv
	. .venv/bin/activate && \
	pip install uv && \
	uv pip install --upgrade pip && \
	uv pip install -e . && \
	make compile