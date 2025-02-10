from fastapi import FastAPI, HTTPException, Depends, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
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
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from uuid import UUID
from config import settings
from utils.pdf_generator import PensionPDFGenerator
from utils.email_template import get_email_template
from utils.email_sender import EmailSender

# Crear la instancia de FastAPI con el prefijo /api
app = FastAPI(
    title="Pension Calculator API",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configura esto según tus necesidades
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración MongoDB
mongodb_client: Optional[AsyncIOMotorClient] = None

@app.on_event("startup")
async def startup_db_client():
    global mongodb_client
    mongodb_client = AsyncIOMotorClient(settings.MONGODB_URL)

@app.on_event("shutdown")
async def shutdown_db_client():
    if mongodb_client:
        mongodb_client.close()

async def get_collection():
    db = mongodb_client[settings.MONGODB_DB_NAME]
    return db[settings.MONGODB_COLLECTION]

# Definir el modelo de datos para las operaciones básicas
class OperationInput(BaseModel):
    number1: float
    number2: float
    operation: str

# Definir el modelo de datos para el cálculo de pensiones
class PensionInput(BaseModel):
    sessionId: str
    name: str
    current_age_years: int
    current_age_months: int
    retirement_age: float
    current_balance: float
    monthly_salary: float
    gender: str
    ideal_pension: float = 0
    nivel_estudios: str = ""

# Modelo para la respuesta simplificada
class SimplifiedResponse(BaseModel):
    sessionId: str
    pre_reforma: Dict[str, Any]
    post_reforma: Dict[str, Any]

# Endpoint de bienvenida
@app.get("/")
async def root():
    return {"message": "Bienvenido a la calculadora de pensiones API"}

async def save_calculation_result(collection, session_id: str, calculation_result: dict):
    document = {
        "sessionId": session_id,
        "timestamp": datetime.utcnow(),
        "pre_reforma": calculation_result["pre_reforma"],
        "post_reforma": calculation_result["post_reforma"],
        "pension_objetivo": calculation_result["pension_objetivo"],
        "metadata": calculation_result["metadata"],
        "constants": {
            "ANNUAL_INTEREST_RATE": ANNUAL_INTEREST_RATE,
            "SALARY_GROWTH_RATE": SALARY_GROWTH_RATE,
            "EQUIVALENT_FUND_RATE": EQUIVALENT_FUND_RATE,
            "INFLATION_RATE": INFLATION_RATE
        }
    }
    await collection.insert_one(document)

# Endpoint para calcular pensiones
@app.post("/api/calculate_pension")
@app.post("/calculate_pension")
async def calculate_pension(input_data: PensionInput):
    try:
        if input_data.gender.upper() not in ['M', 'F']:
            raise HTTPException(status_code=400, detail="Género debe ser 'M' o 'F'")
            
        current_age = input_data.current_age_years + (input_data.current_age_months/12)
        life_expectancy = 86.6 if input_data.gender.upper() == 'M' else 90.8

        # Calcular sistema pre-reforma
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
         worker_total_post, employer_total_post, returns_post,
         pgu_applied_post) = calculate_pension_post_reform(
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
        
        # Resultado completo para MongoDB
        full_result = {
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
                "pension_mensual_base": total_pension_post,
                "pension_adicional_compensacion": additional_pension_post,
                "pension_total": total_pension_post + additional_pension_post + monthly_bspa,
                "pgu_aplicada": pgu_applied_post
            },
            "pension_objetivo": {
                "valor_presente": input_data.ideal_pension,
                "valor_futuro": calculate_future_value(
                    input_data.ideal_pension,
                    input_data.retirement_age - current_age
                ),
                "tasa_inflacion_anual": INFLATION_RATE,
                "brecha_mensual_post_reforma": max(0, calculate_future_value(
                    input_data.ideal_pension,
                    input_data.retirement_age - current_age
                ) - (total_pension_post + additional_pension_post + monthly_bspa))
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
            }, 
            "constants": {
                "ANNUAL_INTEREST_RATE": ANNUAL_INTEREST_RATE,
                "SALARY_GROWTH_RATE": SALARY_GROWTH_RATE,
                "EQUIVALENT_FUND_RATE": EQUIVALENT_FUND_RATE,
                "INFLATION_RATE": INFLATION_RATE
            }
        }

        # Calcular valores para pension_objetivo
        valor_futuro = calculate_future_value(
            input_data.ideal_pension,
            input_data.retirement_age - current_age
        )
        
        pension_total_post = total_pension_post + additional_pension_post + monthly_bspa
        brecha_mensual = max(0, valor_futuro - pension_total_post)

        # Guardar resultado completo en MongoDB
        collection = await get_collection()
        await save_calculation_result(
            collection,
            input_data.sessionId,
            full_result
        )

        # Preparar respuesta simplificada para el frontend
        simplified_response = {
            "sessionId": input_data.sessionId,
            "pre_reforma": {
                "pension_total": round(pension_pre, 2),
                "saldo_acumulado": {
                    "aporte_trabajador": round(worker_total_pre, 2),
                    "aporte_empleador": 0,
                    "rentabilidad_acumulada": round(returns_pre, 2)
                }
            },
            "post_reforma": {
                "pension_total": round(total_pension_post + additional_pension_post + monthly_bspa, 2),
                "pension_mensual_base": round(total_pension_post, 2),
                "pension_adicional_compensacion": round(additional_pension_post, 2),
                "bono_seguridad_previsional": round(monthly_bspa, 2),
                "saldo_acumulado": {
                    "aporte_trabajador": round(worker_total_post, 2),
                    "aporte_empleador": round(employer_total_post, 2),
                    "rentabilidad_acumulada": round(returns_post, 2)
                }
            },
            "pension_objetivo": {
                "valor_presente": round(input_data.ideal_pension, 2),
                "valor_futuro": round(calculate_future_value(
                    input_data.ideal_pension,
                    input_data.retirement_age - current_age
                ), 2),
                "brecha_mensual_post_reforma": round(max(0, calculate_future_value(
                    input_data.ideal_pension,
                    input_data.retirement_age - current_age
                ) - (total_pension_post + additional_pension_post + monthly_bspa)), 2)
            },
            "metadata": {
                "expectativa_vida": round(life_expectancy, 2),
                "genero": input_data.gender.upper()
            }
        }

        return simplified_response

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

@app.get("/api/get_session/{session_id}")
async def get_session(session_id: str = Path(..., title="Session ID")):
    try:
        collection = await get_collection()
        result = await collection.find_one({"sessionId": session_id})
        
        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"Session with ID {session_id} not found"
            )

        # Convertir ObjectId a str para serialización JSON
        result["_id"] = str(result["_id"])
        
        # Preparar respuesta en el formato solicitado
        simplified_response = {
            "sessionId": session_id,
            "pre_reforma": {
                "pension_total": round(result["pre_reforma"]["pension_total"], 2),
                "saldo_acumulado": {
                    "aporte_trabajador": round(result["pre_reforma"]["saldo_acumulado"]["aporte_trabajador"], 2),
                    "aporte_empleador": round(result["pre_reforma"]["saldo_acumulado"]["aporte_empleador"], 2),
                    "rentabilidad_acumulada": round(result["pre_reforma"]["saldo_acumulado"]["rentabilidad_acumulada"], 2)
                }
            },
            "post_reforma": {
                "pension_total": round(result["post_reforma"]["pension_total"], 2),
                "pension_mensual_base": round(result["post_reforma"]["pension_mensual_base"], 2),
                "pension_adicional_compensacion": round(result["post_reforma"]["pension_adicional_compensacion"], 2),
                "bono_seguridad_previsional": round(result["post_reforma"]["bono_seguridad_previsional"], 2),
                "saldo_acumulado": {
                    "aporte_trabajador": round(result["post_reforma"]["saldo_acumulado"]["aporte_trabajador"], 2),
                    "aporte_empleador": round(result["post_reforma"]["saldo_acumulado"]["aporte_empleador"], 2),
                    "rentabilidad_acumulada": round(result["post_reforma"]["saldo_acumulado"]["rentabilidad_acumulada"], 2)
                }
            },
            "pension_objetivo": {
                "valor_presente": round(result["pension_objetivo"]["valor_presente"], 2),
                "valor_futuro": round(result["pension_objetivo"]["valor_futuro"], 2),
                "brecha_mensual_post_reforma": round(result["pension_objetivo"]["brecha_mensual_post_reforma"], 2)
            },
            "metadata": {
                "expectativa_vida": round(result["metadata"]["expectativa_vida"], 2),
                "genero": result["metadata"]["genero"]
            }
        }

        return simplified_response

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving session: {str(e)}"
        )

class EmailRequest(BaseModel):
    session_id: str
    email: EmailStr
    optin_comercial: bool

@app.post("/api/send_pdf")
async def send_pdf(request: EmailRequest):
    try:
        # Obtener datos de la sesión
        collection = await get_collection()
        session_data = await collection.find_one({"sessionId": request.session_id})
        
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")

        # Obtener el nombre desde los datos de la sesión
        nombre = session_data["metadata"]["nombre"]
        if not nombre:
            nombre = "Usuario"  # Valor por defecto si no hay nombre

        # # Generar PDF
        # pdf_generator = PensionPDFGenerator()
        # pdf_content = pdf_generator.generate_pdf(session_data)

        # # Obtener template del email
        # html_content = get_email_template(nombre)

        # # Enviar email
        # email_sender = EmailSender()
        # success = await email_sender.send_email(
        #     recipient_email=request.email,
        #     subject="Simulación de Pensión",
        #     html_content=html_content,
        #     pdf_content=pdf_content
        # )

        success = True

        print("Sending email to: ", nombre)
        print("Email: ", request.email)

        if not success:
            raise HTTPException(status_code=500, detail="Error sending email")

        # Actualizar el documento en MongoDB con el email y optin_comercial
        update_result = await collection.update_one(
            {"sessionId": request.session_id},
            {
                "$set": {
                    "email": request.email,
                    "optin_comercial": request.optin_comercial,
                    "email_sent_date": datetime.utcnow()
                }
            }
        )

        if update_result.modified_count == 0:
            print(f"Warning: No se pudo actualizar el documento para sessionId: {request.session_id}")

        return {"message": "Email sent successfully"}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

