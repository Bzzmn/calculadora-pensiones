# Calculadora de Pensiones API

API REST para calcular estimaciones de pensiones bajo los sistemas pre-reforma y post-reforma de pensiones en Chile (2025).

## 🚀 Características

- Cálculo de pensiones bajo sistema pre-reforma
- Cálculo de pensiones bajo sistema post-reforma
- Estimación de aportes y rentabilidades
- Cálculo de beneficios adicionales (BSPA, compensación por género, etc.)
- Código optimizado con Cython
- Dockerizado para fácil despliegue
- CI/CD con GitHub Actions

## 🛠️ Tecnologías

- Python 3.9
- FastAPI
- Cython (optimización)
- Docker
- GitHub Actions
- Coolify (para despliegue)

## 📋 Prerequisitos

- Python 3.9+
- Docker
- Make (opcional, para usar comandos simplificados)
- build-essential y python3-dev (para compilación)

## 🔧 Instalación

### Usando Docker (Recomendado)

```bash
# Clonar el repositorio
git clone <https://github.com/tu-usuario/pension-calculator.git>
cd pension-calculator

# Construir y ejecutar con Make (desarrollo)
make all-dev

# O construir y ejecutar con Make (producción)
make all-prod

# Sin Make, usando Docker directamente
docker build -t pension-calculator .
docker run -d -p 8000:80 pension-calculator
```

### Instalación Local

```bash
# Crear y activar entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias de compilación
pip install -r requirements-build.txt

# Compilar el código
make compile  # O: python setup.py build_ext --inplace

# Instalar dependencias de runtime
pip install -r requirements.txt

# Ejecutar servidor
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 🔍 Uso

### Endpoint de Cálculo de Pensiones

```json
POST /calculate_pension

{
    "name": "Macarena",
    "current_age_years": 41,
    "current_age_months": 6,
    "retirement_age": 65,
    "current_balance": 28998190,
    "monthly_salary": 2564066,
    "gender": "F",
    "ideal_pension": 1400000,
    "nivel_estudios": "Universitario completo"
}
```

### Respuesta

```json
{
  "pre_reforma": {
    "saldo_acumulado": {
      "saldo_cuenta_individual": 197736378.2051801,
      "aporte_trabajador": 115086357.6412105,
      "aporte_empleador": 0,
      "rentabilidad_acumulada": 82650020.56396952
    },
    "aporte_sis": 17262953.64618157,
    "pension_mensual_base": 639923.5540620716,
    "pension_total": 639923.5540620716,
    "pgu_aplicada": false
  },
  "post_reforma": {
    "saldo_acumulado": {
      "saldo_cuenta_individual": 245549494.61654654,
      "aporte_trabajador": 115086357.6412105,
      "aporte_empleador": 36449513.82990185,
      "rentabilidad_acumulada": 94013623.14543419
    },
    "aporte_sis": 17262953.64618157,
    "aporte_compensacion_expectativa_vida": 9610187.455537103,
    "balance_fapp": 20646016.934654858,
    "bono_seguridad_previsional": 86025.0705610619,
    "pension_mensual_base": 794658.5586296006,
    "pension_adicional_compensacion": 153408.9881524325,
    "pension_total": 1034092.6173430949,
    "pgu_aplicada": false
  },
  "pension_objetivo": {
    "valor_presente": 1400000.0,
    "valor_futuro": 2804160.1694053626,
    "tasa_inflacion_anual": 0.03,
    "brecha_mensual_post_reforma": 1770067.5520622677
  },
  "metadata": {
    "nombre": "Macarena",
    "edad": 41.5,
    "genero": "F",
    "edad_jubilacion": 65.0,
    "balance_actual": 28998190.0,
    "salario_mensual": 2564066.0,
    "estudios": "Universitario completo",
    "expectativa_vida": 90.8
  }
}
```

## 🔧 Comandos Make Disponibles

- `make compile`: Compila el código usando Cython
- `make clean-build`: Limpia archivos de compilación
- `make build`: Construye la imagen Docker
- `make run-dev`: Ejecuta el contenedor en modo desarrollo
- `make run-prod`: Ejecuta el contenedor en modo producción
- `make stop`: Detiene y elimina el contenedor
- `make logs`: Muestra los logs del contenedor
- `make status`: Muestra el estado del contenedor

## 📦 Estructura del Proyecto

```
pension-calculator/
├── calculator/
│   ├── __init__.py
│   └── pension.py
├── .github/
│   └── workflows/
│       └── docker-build-deploy.yml
├── Dockerfile
├── Makefile
├── README.md
├── main.py
├── requirements.txt
├── requirements-build.txt
└── setup.py
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

## 📊 Constantes y Fórmulas del Sistema

### Constantes Principales
- WORKER_RATE = 0.10 (Aporte base del trabajador: 10%)
- ANNUAL_INTEREST_RATE = 0.0311 (Rendimiento anual: 3.11%)
- SALARY_GROWTH_RATE = 0.05 (Crecimiento salarial anual: 5%)
- EQUIVALENT_FUND_RATE = 0.0391 (Rendimiento FAPP: 3.91%)
- INFLATION_RATE = 0.03 (Inflación anual: 3%)
- PENSION_MINIMA = 214,000 (Pensión mínima garantizada)

### Tasas Derivadas
- Tasa de interés mensual = (1 + ANNUAL_INTEREST_RATE)^(1/12) - 1
- Tasa de crecimiento salarial trimestral = (1 + SALARY_GROWTH_RATE)^(1/4) - 1

### Fórmulas Principales

#### Saldo Acumulado Mensual

```python
balance = (balance + contribution) (1 + monthly_interest_rate)
```

#### Pensión Mensual Base

```python
monthly_pension = saldo_total / meses_expectativa_vida
```

donde meses_expectativa_vida = (expectativa_vida - edad_jubilacion) * 12

#### Compensación Mujeres
Para mujeres, se calcula una pensión adicional:

```python
pension_difference = (balance / meses_hombre) - (balance / meses_mujer)
additional_pension = max(pension_difference, 10000)
```

#### Bono de Seguridad Previsional (BSPA)

```python
monthly_BSPA = balance_FAPP / 240 # Amortizado en 20 años
```

#### Valor Futuro Considerando Inflación

```python
future_value = present_value (1 + inflation_rate)^years

### Expectativas de Vida
- Hombres: 86.6 años
- Mujeres: 90.8 años

### Tasas Progresivas del Empleador
El sistema post-reforma incluye tasas progresivas que aumentan con el tiempo:
- Meses 0-4: 0%
- Meses 5-12: 1%
- Meses 13-24: 2%
- Meses 25-36: 2.7%
- Meses 37-48: 3.5%
- Meses 49-60: 4.2%
- Meses 61-72: 4.9%
- Meses 73-84: 5.6%
- Meses 85-96: 6.3%
- Meses 97+: 7%


## 📝 Notas Adicionales

- El código está optimizado para rendimiento usando Cython
- El código está documentado con comentarios y docstrings
- El código está probado con pytest
- Para simplificar el calculo no se consideran cargas familiares ni otros aportes como APV.