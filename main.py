from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from calculator.pension_core import (
    calculate_pension_pre_reform, 
    calculate_pension_post_reform,
    calculate_future_value,
    WORKER_RATE,
    ANNUAL_INTEREST_RATE,
    SALARY_GROWTH_RATE,
    EQUIVALENT_FUND_RATE,
    INFLATION_RATE
)

# Crear la instancia de FastAPI
app = FastAPI()

# Definir el modelo de datos para las operaciones básicas
class OperationInput(BaseModel):
    number1: float
    number2: float
    operation: str

# Definir el modelo de datos para el cálculo de pensiones
class PensionInput(BaseModel):
    name: str
    current_age_years: int
    current_age_months: int
    retirement_age: float
    current_balance: float
    monthly_salary: float
    gender: str
    ideal_pension: float = 0
    nivel_estudios: str = ""

# Endpoint de bienvenida
@app.get("/")
async def root():
    return {"message": "Bienvenido a la calculadora de pensiones API"}

# Endpoint para calcular pensiones
@app.post("/calculate_pension")
async def calculate_pension(input_data: PensionInput):
    try:
        if input_data.gender.upper() not in ['M', 'F']:
            raise HTTPException(status_code=400, detail="Género debe ser 'M' o 'F'")
            
        current_age = input_data.current_age_years + (input_data.current_age_months/12)
        life_expectancy = 86.6 if input_data.gender.upper() == 'M' else 90.8

        # Calcular sistema pre-reforma usando constantes
        (final_balance_pre, pension_pre, worker_total_pre, 
         employer_total_pre, sis_total_pre, returns_pre,
         pgu_applied_pre) = calculate_pension_pre_reform(
            current_age,
            input_data.retirement_age,
            input_data.current_balance,
            input_data.monthly_salary,
            input_data.gender
        )

        # Calcular sistema post-reforma
        (final_balance_post, total_pension_post, additional_pension_post,
         fapp_balance, monthly_bspa, sis_total_post, women_comp_total, 
         worker_total_post, employer_total_post, returns_post, pgu_applied_post) = calculate_pension_post_reform(
            current_age,
            input_data.retirement_age,
            input_data.current_balance,
            input_data.monthly_salary,
            input_data.gender
        )

        # Calcular años y meses de pensión
        total_pension_years = life_expectancy - input_data.retirement_age
        pension_years = int(total_pension_years)
        pension_months = int((total_pension_years - pension_years) * 12)

        # Calcular años hasta jubilación
        years_to_retirement = input_data.retirement_age - (input_data.current_age_years + input_data.current_age_months/12)
        
        # Calcular valor futuro de la pensión ideal
        future_ideal_pension = calculate_future_value(
            input_data.ideal_pension,
            years_to_retirement
        )

        return {
            "pre_reforma": {
                "saldo_acumulado": {
                    "saldo_cuenta_individual": final_balance_pre,
                    "aporte_trabajador": worker_total_pre,
                    "aporte_empleador": 0,
                    "rentabilidad_acumulada": returns_pre
                },
                "aporte_sis": sis_total_pre,
                "pension_mensual_base": pension_pre,
                "pension_total": pension_pre,
                "pgu_aplicada": pgu_applied_pre
            },
            "post_reforma": {
                "saldo_acumulado": {
                    "saldo_cuenta_individual": final_balance_post,
                    "aporte_trabajador": worker_total_post,
                    "aporte_empleador": employer_total_post,
                    "rentabilidad_acumulada": returns_post
                },
                "aporte_sis": sis_total_post,
                "aporte_compensacion_expectativa_vida": women_comp_total,
                "balance_fapp": fapp_balance,
                "bono_seguridad_previsional": monthly_bspa,
                "pension_mensual_base": total_pension_post - additional_pension_post - monthly_bspa,
                "pension_adicional_compensacion": additional_pension_post,
                "pension_total": total_pension_post,
                "pgu_aplicada": pgu_applied_post
            },
            "pension_objetivo": {
                "valor_presente": input_data.ideal_pension,
                "valor_futuro": future_ideal_pension,
                "tasa_inflacion_anual": INFLATION_RATE,
                "brecha_mensual_post_reforma": future_ideal_pension - total_pension_post
            },
            "metadata": {
                "nombre": input_data.name,
                "edad": current_age,
                "genero": input_data.gender,
                "edad_jubilacion": input_data.retirement_age,
                "balance_actual": input_data.current_balance,
                "salario_mensual": input_data.monthly_salary,
                "estudios": input_data.nivel_estudios,
                "expectativa_vida": life_expectancy
            }
        }
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mantener el endpoint original de operaciones básicas
@app.post("/calculate")
async def calculate(input_data: OperationInput):
    try:
        if input_data.operation == "suma":
            result = input_data.number1 + input_data.number2
        elif input_data.operation == "resta":
            result = input_data.number1 - input_data.number2
        elif input_data.operation == "multiplicacion":
            result = input_data.number1 * input_data.number2
        elif input_data.operation == "division":
            if input_data.number2 == 0:
                raise HTTPException(status_code=400, detail="No se puede dividir por cero")
            result = input_data.number1 / input_data.number2
        else:
            raise HTTPException(status_code=400, detail="Operación no válida")
        
        return {
            "operation": input_data.operation,
            "number1": input_data.number1,
            "number2": input_data.number2,
            "result": result
        }
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
