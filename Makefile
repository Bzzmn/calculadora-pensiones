# Variables
IMAGE_NAME = pension-calculator
CONTAINER_NAME = pension-calculator-app
DEV_PORT = 8000
PROD_PORT = 80

# Comandos principales
.PHONY: build run-dev run-prod stop clean all-dev all-prod

# Construir la imagen
build:
	docker build -t $(IMAGE_NAME) .

# Ejecutar el contenedor en desarrollo
run-dev:
	docker run -d \
		--name $(CONTAINER_NAME) \
		-p $(DEV_PORT):80 \
		$(IMAGE_NAME)

# Ejecutar el contenedor en producción
run-prod:
	docker run -d \
		--name $(CONTAINER_NAME) \
		-p $(PROD_PORT):80 \
		--restart unless-stopped \
		$(IMAGE_NAME)

# Detener y eliminar el contenedor
stop:
	docker stop $(CONTAINER_NAME) || true
	docker rm $(CONTAINER_NAME) || true

# Limpiar imágenes y contenedores
clean: stop
	docker rmi $(IMAGE_NAME) || true

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