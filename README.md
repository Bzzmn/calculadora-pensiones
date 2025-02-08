# Calculadora de Pensiones API

API REST para calcular estimaciones de pensiones bajo los sistemas pre-reforma y post-reforma de pensiones en Chile.

## 🚀 Características

- Cálculo de pensiones bajo sistema pre-reforma
- Cálculo de pensiones bajo sistema post-reforma
- Estimación de aportes y rentabilidades
- Cálculo de beneficios adicionales (BSPA, compensación por género, etc.)
- Dockerizado para fácil despliegue
- CI/CD con GitHub Actions

## 🛠️ Tecnologías

- Python 3.9
- FastAPI
- Docker
- GitHub Actions
- Coolify (para despliegue)

## 📋 Prerequisitos

- Python 3.9+
- Docker
- Make (opcional, para usar comandos simplificados)

## 🔧 Instalación

### Usando Docker

```bash
Clonar el repositorio
git clone <https://github.com/tu-usuario/pension-calculator.git>
cd pension-calculator
Construir y ejecutar con Make (desarrollo)
make all-dev
O construir y ejecutar con Make (producción)
make all-prod
Sin Make, usando Docker directamente
docker build -t pension-calculator .
docker run -d -p 8000:80 pension-calculator
```

### Instalación Local

```bash
Crear y activar entorno virtual
python -m venv venv
source venv/bin/activate # En Windows: venv\Scripts\activate
Instalar dependencias
pip install -r requirements.txt
Ejecutar servidor
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 🔍 Uso

### Endpoint de Cálculo de Pensiones

```json
POST /calculate_pension

{
    "current_age_years": 41,
    "current_age_months": 6,
    "retirement_age": 65,
    "current_balance": 28998190,
    "monthly_salary": 2564066,
    "worker_rate": 0.10,
    "annual_interest_rate": 0.0311,
    "salary_growth_rate": 0.0125,
    "equivalent_fund_rate": 0.0391,
    "gender": "F"
}
```

### Respuesta

```json
{
    "pre_reforma": {
        "saldo_acumulado": 123456789,
        "aporte_sis": 1234567,
        "aporte_empleador": 1234567,
        "aporte_trabajador": 12345678,
        "pension_mensual": 123456,
        "pension_total": 123456,
        "rentabilidad_acumulada": 1234567
    },
    "post_reforma": {
        "saldo_acumulado": 123456789,
        "aporte_sis": 1234567,
        "aporte_compensacion_expectativa_vida": 123456,
        "aporte_fapp": 1234567,
        "bono_seguridad_previsional": 12345,
        "aporte_empleador": 1234567,
        "aporte_trabajador": 12345678,
        "pension_mensual": 123456,
        "pension_adicional": 12345,
        "pension_total": 135801,
        "rentabilidad_acumulada": 1234567
    },
    "expectativa_vida": {
        "anos": 25,
        "meses": 6
    }
}
```

## 🚀 Despliegue

El proyecto está configurado para desplegarse automáticamente usando GitHub Actions y Coolify:

1. Hacer push a la rama main o crear un tag
2. GitHub Actions construirá y publicará la imagen en Docker Hub
3. Coolify detectará la nueva imagen y actualizará el servicio

## 🔐 Variables de Entorno

Para el despliegue con GitHub Actions, necesitas configurar los siguientes secrets:

- `DOCKER_USERNAME`: Usuario de Docker Hub
- `DOCKER_TOKEN`: Token de acceso de Docker Hub
- `COOLIFY_WEBHOOK`: URL del webhook de Coolify
- `COOLIFY_TOKEN`: Token de autenticación de Coolify

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE.md](LICENSE.md) para detalles

## ✨ Contribuir

Las contribuciones son bienvenidas. Por favor, abre un issue primero para discutir los cambios que te gustaría hacer.

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request
