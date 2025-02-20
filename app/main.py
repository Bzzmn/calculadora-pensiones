import os
from fastapi import FastAPI, HTTPException, Depends, Path, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from app.calculator.pension_core import (
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
from datetime import datetime, timedelta
from uuid import UUID
from config import settings
from app.utils.pdf_generator import PensionPDFGenerator
from app.utils.email_template import get_email_template
from app.utils.email_sender import EmailSender
import jwt
import logging

# Crear la instancia de FastAPI con el prefijo /api
app = FastAPI(
    title="Pension Calculator API",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    expose_headers=["*"],
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
        (final_balance_post, monthly_pension_post, additional_pension_post,
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
                "pension_mensual_base": monthly_pension_post,
                "pension_adicional_compensacion": additional_pension_post,
                "pension_total": monthly_pension_post + additional_pension_post + monthly_bspa,
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
                ) - (monthly_pension_post + additional_pension_post + monthly_bspa))
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
        
        pension_total_post = monthly_pension_post + additional_pension_post + monthly_bspa
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
                "pension_total": round(monthly_pension_post + additional_pension_post + monthly_bspa, 2),
                "pension_mensual_base": round(monthly_pension_post, 2),
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
                ) - (monthly_pension_post + additional_pension_post + monthly_bspa)), 2)
            },
            "metadata": {
                "expectativa_vida": round(life_expectancy, 2),
                "genero": input_data.gender.upper()
            }
        }

        return simplified_response

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

@app.post("/api/send_email")
async def send_pdf(request: EmailRequest):
    try:
        # Obtener datos de la sesión
        collection = await get_collection()
        session_data = await collection.find_one({"sessionId": request.session_id})
        
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")

        # Generar PDF en memoria
        pdf_generator = PensionPDFGenerator()
        pdf_content = pdf_generator.generate_pdf_bytes(session_data)

        # Obtener el nombre desde los datos de la sesión
        nombre = session_data["metadata"]["nombre"]
        if not nombre:
            nombre = "Usuario"

        # Generar URL de unsubscribe
        token = generate_unsubscribe_token(request.email)
        unsubscribe_url = f"{settings.THEFULLSTACK_FRONTEND_URL}/unsubscribe?token={token}"
        print(f"Unsubscribe URL: {unsubscribe_url}")

        # Obtener template del email con URL de unsubscribe
        html_content = get_email_template(nombre, unsubscribe_url)

        # Enviar email
        email_sender = EmailSender()
        success = await email_sender.send_email(
            recipient_email=request.email,
            subject="Planificador de Pensión",
            html_content=html_content,
            pdf_content=pdf_content,
            from_name="The Fullstack"
        )

        if not success:
            raise HTTPException(status_code=500, detail="Error sending email")

        # Obtener la colección newsletter
        db = mongodb_client[settings.MONGODB_DB_NAME]
        newsletter_collection = db['newsletter']

        # Buscar si el email ya existe
        existing_subscriber = await newsletter_collection.find_one({"email": request.email})

        if existing_subscriber:
            # Actualizar el sessionId si el email ya existe
            await newsletter_collection.update_one(
                {"email": request.email},
                {
                    "$set": {
                        "sessionId": request.session_id,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
        else:
            # Crear nuevo registro si el email no existe
            await newsletter_collection.insert_one({
                "email": request.email,
                "sessionId": request.session_id,
                "optin_comercial": request.optin_comercial,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })

        return {
            "message": "Email sent successfully",
            "details": {
                "email": request.email,
                "sent_date": datetime.utcnow(),
                "optin_comercial": request.optin_comercial
            }
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Función para generar token de unsubscribe
def generate_unsubscribe_token(email: str) -> str:
    payload = {
        "email": email,
        "exp": datetime.utcnow() + timedelta(days=30),
        "type": "unsubscribe"
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

# Endpoint para generar URL de unsubscribe
@app.get("/api/newsletter/unsubscribe-url/{email}")
async def get_unsubscribe_url(email: str):
    token = generate_unsubscribe_token(email)
    unsubscribe_url = f"{settings.THEFULLSTACK_FRONTEND_URL}/unsubscribe?token={token}"
    return {"unsubscribe_url": unsubscribe_url}

class UnsubscribeRequest(BaseModel):
    token: str

@app.post("/api/newsletter/unsubscribe", status_code=status.HTTP_200_OK)
async def process_unsubscribe(request: UnsubscribeRequest):
    try:
        # Decodificar y validar token
        try:
            payload = jwt.decode(request.token, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token ha expirado"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )

        # Validar tipo de token
        if payload.get("type") != "unsubscribe":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tipo de token inválido"
            )

        email: Optional[str] = payload.get("email")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email no encontrado en el token"
            )
        
        # Obtener la colección newsletter
        db = mongodb_client[settings.MONGODB_DB_NAME]
        newsletter_collection = db['newsletter']

        # Buscar y eliminar el registro
        result = await newsletter_collection.delete_one({"email": email})

        if result.deleted_count == 0:
            logging.warning(f"Intento de desuscripción para email no suscrito: {email}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email no encontrado en la lista de suscripción"
            )

        logging.info(f"Desuscripción exitosa para: {email}")
        return {
            "status": "success",
            "message": "Te has dado de baja exitosamente de nuestra lista de correos.",
            "email": email
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        logging.error(f"Error inesperado en desuscripción: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

