from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from calculator.pension import calculate_pension_pre_reform, calculate_pension_post_reform

# Crear la instancia de FastAPI
app = FastAPI()

# Definir el modelo de datos para las operaciones básicas
class OperationInput(BaseModel):
    number1: float
    number2: float
    operation: str

# Definir el modelo de datos para el cálculo de pensiones
class PensionInput(BaseModel):
    current_age_years: int
    current_age_months: int
    retirement_age: float
    current_balance: float
    monthly_salary: float
    worker_rate: float = 0.10
    annual_interest_rate: float = 0.0311
    salary_growth_rate: float = 0.0125
    equivalent_fund_rate: float = 0.0391
    gender: str

# Endpoint de bienvenida
@app.get("/")
async def root():
    return {"message": "Bienvenido a la calculadora de pensiones API"}

# Endpoint para calcular pensiones
@app.post("/calculate_pension")
async def calculate_pension(input_data: PensionInput):
    try:
        # Validar género
        if input_data.gender.upper() not in ['M', 'F']:
            raise HTTPException(status_code=400, detail="Género debe ser 'M' o 'F'")
            
        # Convertir años y meses a edad decimal
        current_age = input_data.current_age_years + (input_data.current_age_months / 12)

        # Calcular sistema pre-reforma
        final_balance_pre, pension_pre, worker_total_pre, employer_total_pre, sis_total_pre, returns_pre = calculate_pension_pre_reform(
            current_age,
            input_data.retirement_age,
            input_data.current_balance,
            input_data.monthly_salary,
            input_data.worker_rate,
            input_data.annual_interest_rate,
            input_data.salary_growth_rate,
            input_data.gender
        )

        # Calcular sistema post-reforma
        (final_balance_post, pension_post, total_pension_post, additional_pension_post,
         fapp_balance, monthly_bspa, sis_total_post, women_comp_total, worker_total_post, 
         employer_total_post, returns_post) = calculate_pension_post_reform(
            current_age,
            input_data.retirement_age,
            input_data.current_balance,
            input_data.monthly_salary,
            input_data.worker_rate,
            input_data.annual_interest_rate,
            input_data.salary_growth_rate,
            input_data.gender,
            input_data.equivalent_fund_rate
        )

        # Calcular años y meses de pensión
        life_expectancy = 86.6 if input_data.gender.upper() == 'M' else 90.8
        total_pension_years = life_expectancy - input_data.retirement_age
        pension_years = int(total_pension_years)
        pension_months = int((total_pension_years - pension_years) * 12)

        return {
            "pre_reforma": {
                "saldo_acumulado": final_balance_pre,
                "aporte_sis": sis_total_pre,
                "aporte_empleador": employer_total_pre,
                "aporte_trabajador": worker_total_pre,
                "pension_mensual": pension_pre,
                "pension_total": pension_pre,
                "rentabilidad_acumulada": returns_pre
            },
            "post_reforma": {
                "saldo_acumulado": final_balance_post,
                "aporte_sis": sis_total_post,
                "aporte_compensacion_expectativa_vida": women_comp_total,
                "aporte_fapp": fapp_balance,
                "bono_seguridad_previsional": monthly_bspa,
                "aporte_empleador": employer_total_post,
                "aporte_trabajador": worker_total_post,
                "pension_mensual": pension_post,
                "pension_adicional": additional_pension_post if input_data.gender.upper() == 'F' else 0,
                "pension_total": total_pension_post,
                "rentabilidad_acumulada": returns_post
            },
            "expectativa_vida": {
                "anos": pension_years,
                "meses": pension_months
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
