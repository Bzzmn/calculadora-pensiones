from datetime import datetime, date

# Constantes del sistema
REFORM_START_DATE = date(2025, 2, 1)  # Fecha de inicio de la reforma
WORKER_RATE = 0.10                    # Aporte del trabajador: 10%
ANNUAL_INTEREST_RATE = 0.0311         # Rendimiento anual: 3.11%
SALARY_GROWTH_RATE = 0.0125           # Crecimiento salarial anual: 1.25%
EQUIVALENT_FUND_RATE = 0.0391         # Rendimiento anual del Fondo equivalente FAPP: 3.91%
PENSION_MINIMA = 214000               # Pensión mínima garantizada
INFLATION_RATE = 0.03      

monthly_interest_rate = (1 + ANNUAL_INTEREST_RATE) ** (1/12) - 1  
monthly_equivalent_fund_rate = (1 + EQUIVALENT_FUND_RATE) ** (1/12) - 1

def effective_additional_rate(month_index: int) -> float:
    """
    Devuelve la tasa extra del empleador, en fracción, según el mes (m=0: febrero 2025).
    Piecewise:
      - m < 5: 0.0
      - 5 <= m < 13: 0.01 (1%)
      - 13 <= m < 25: 0.02 (2%)
      - 25 <= m < 37: 0.027 (2,7%)
      - 37 <= m < 49: 0.035 (3,5%)
      - 49 <= m < 61: 0.042 (4,2%)
      - 61 <= m < 73: 0.049 (4,9%)
      - 73 <= m < 85: 0.056 (5,6%)
      - 85 <= m < 97: 0.063 (6,3%)
      - m >= 97: 0.07 (7%)
    """
    if month_index < 5:
        return 0.0
    elif month_index < 13:
        return 0.01
    elif month_index < 25:
        return 0.02
    elif month_index < 37:
        return 0.027
    elif month_index < 49:
        return 0.035
    elif month_index < 61:
        return 0.042
    elif month_index < 73:
        return 0.049
    elif month_index < 85:
        return 0.056
    elif month_index < 97:
        return 0.063
    else:
        return 0.07

def f_individual_total(month_index: int) -> float:
    """
    Devuelve el porcentaje total (en fracción) que se acumula en la cuenta individual en el sistema post-reforma,
    incluyendo el aporte base del trabajador (10%) más el extra directo del empleador.
    Valores:
      - m < 5: 0.10 
      - 5 <= m < 13: 0.101
      - 13 <= m < 25: 0.101
      - 25 <= m < 37: 0.102
      - 37 <= m < 49: 0.11
      - 49 <= m < 61: 0.117
      - 61 <= m < 73: 0.124
      - 73 <= m < 85: 0.131
      - 85 <= m < 97: 0.138
      - 97 <= m < 241: 0.145
      - 241 <= m < 361: lineal de 0.145 a 0.16
      - m >= 361: 0.16
    """
    if month_index < 5:
        return 0.10
    elif month_index < 13:
        return 0.101
    elif month_index < 25:
        return 0.101
    elif month_index < 37:
        return 0.102
    elif month_index < 49:
        return 0.11
    elif month_index < 61:
        return 0.117
    elif month_index < 73:
        return 0.124
    elif month_index < 85:
        return 0.131
    elif month_index < 97:
        return 0.138
    elif month_index < 241:
        return 0.145
    elif month_index < 361:
        # Interpolación lineal de 0.145 a 0.16
        return 0.145 + ((month_index - 241) / (361 - 241)) * (0.16 - 0.145)
    else:
        return 0.16

def f_compensacion_mujeres(month_index: int) -> float:
    """
    Devuelve el porcentaje (en fracción) destinado al SIS/compensación para mujeres.
      - m < 5: 0
      - 5 <= m < 13: 0.009 (0.9%)
      - m >= 13: 0.01 (1%)
    """
    if month_index < 5:
        return 0.0
    elif month_index < 13:
        return 0.009
    else:
        return 0.01

def f_FAPP_target(month_index: int) -> float:
    """
    Devuelve el porcentaje (en fracción) destinado al FAPP para financiar el beneficio por año cotizado.
      - m < 13: 0
      - m en [13, 25): 0.009
      - m en [25, 241): 0.015
      - m en [241, 361): disminuye linealmente de 0.015 a 0
      - m >= 361: 0
    """
    if month_index < 13:
        return 0.0
    elif month_index < 25:
        return 0.009
    elif month_index < 241:
        return 0.015
    elif month_index < 361:
        return 0.015 - ((month_index - 241) / (361 - 241)) * 0.015
    else:
        return 0.0
    
def get_months_from_reform_start() -> int:
    """
    Calcula cuántos meses han pasado desde el inicio de la reforma (febrero 2025)
    hasta la fecha actual.
    """
    today = date.today()
    if today < REFORM_START_DATE:
        return 0
    
    months = (today.year - REFORM_START_DATE.year) * 12 + (today.month - REFORM_START_DATE.month)
    return max(0, months)

#########################
# Sistema Pre-reforma  #
#########################

def calculate_future_value(present_value: float, years: float, inflation_rate: float = INFLATION_RATE) -> float:
    """
    Calcula el valor futuro de un monto considerando la inflación.
    
    Args:
        present_value: Valor presente del monto
        years: Años hasta el momento futuro
        inflation_rate: Tasa de inflación anual (por defecto INFLATION_RATE)
    
    Returns:
        float: Valor futuro del monto
    """
    return present_value * (1 + inflation_rate) ** years


def calculate_pension_pre_reform(current_age: float,
                                 retirement_age: float,
                                 current_balance: float,
                                 monthly_salary: float,
                                 gender: str) -> tuple[float, ...]:
    """
    Calcula el saldo acumulado y la pensión mensual estimada bajo el sistema pre-reforma.
    Sólo se acumula el aporte del trabajador (10% del sueldo); el 1.5% del empleador va al SIS.
    
    Args:
        current_age: Edad actual en formato decimal (años + meses/12)
        retirement_age: Edad de jubilación
        current_balance: Saldo actual en cuenta individual
        monthly_salary: Sueldo bruto mensual
        gender: Género ('M' o 'F')
    """
    # Calcular la expectativa de vida en base al género y, por ende, los años de pensión:
    life_expectancy = 86.6 if gender.upper() == 'M' else 90.8
    total_pension_months = int((life_expectancy - retirement_age) * 12)
    months_to_retirement = int((retirement_age - current_age) * 12)
    
    # 2. Inicialización de acumuladores
    balance = current_balance
    accumulated_returns = 0  # Nuevo acumulador para rentabilidad
    total_worker_contribution = 0
    total_employer_contribution = 0
    total_sis = 0

    # 3. Acumulación mensual hasta jubilación
    for month in range(months_to_retirement):
        # Aporte mensual del trabajador (10%)
        contribution = monthly_salary * WORKER_RATE
        total_worker_contribution += contribution
        
        # Calcular rentabilidad del mes
        monthly_return = (balance + contribution) * monthly_interest_rate
        accumulated_returns += monthly_return
        
        # Actualización del saldo incluyendo rentabilidad
        balance = (balance + contribution) * (1 + monthly_interest_rate)
        
        # SIS (1.5% del empleador)
        sis = monthly_salary * 0.015
        total_sis += sis
        
        # Actualización del sueldo cada 6 meses
        if month % 6 == 5:
            monthly_salary *= (1 + SALARY_GROWTH_RATE)
    
    # 4. Estimar componentes del saldo actual (current_balance)
    years_contributed = current_age - 25 if current_age > 25 else 0
    initial_estimated_returns = current_balance - (current_balance / (1 + ANNUAL_INTEREST_RATE) ** years_contributed)
    initial_worker_contribution = current_balance - initial_estimated_returns
    
    # 5. Estimar el SIS histórico basado en la contribución histórica del trabajador
    # Si 10% del sueldo = initial_worker_contribution, entonces el sueldo total histórico fue:
    historical_total_salary = initial_worker_contribution / WORKER_RATE
    # El SIS histórico sería el 1.5% de ese sueldo total
    historical_sis = historical_total_salary * 0.015
    
    # 6. Actualizar totales finales
    total_worker_contribution += initial_worker_contribution  # Agregar contribución histórica
    total_sis += historical_sis  # Agregar SIS histórico # Todo el aporte del empleador va al SIS
    accumulated_returns += initial_estimated_returns  # Agregar rentabilidad histórica

    # Calcular la pensión mensual
    monthly_pension = balance / total_pension_months


    # Calcular si aplica PGU
    if monthly_pension < 214000:
        monthly_pension = 214000
        pgu_applied = True
    else:
        pgu_applied = False

    return (balance,                    # saldo_acumulado
            monthly_pension,  # pension_mensual
            total_worker_contribution,   # aporte_trabajador (incluye histórico)
            total_employer_contribution, # aporte_empleador (todo va a SIS)
            total_sis,                  # aporte_sis (incluye histórico)
            accumulated_returns,       # rentabilidad_acumulada (incluye histórica)
            pgu_applied)              # indica si se aplicó PGU

#########################
# Sistema Post-reforma #
#########################

def calculate_pension_post_reform(current_age: float,
                                retirement_age: float,
                                current_balance: float,
                                monthly_salary: float,
                                gender: str) -> tuple[float, ...]:
    """
    Calcula considerando el momento actual en relación a feb 2025
    """
    # Obtener el mes actual en relación a febrero 2025
    current_month_index = get_months_from_reform_start()
    months_to_retirement = int((retirement_age - current_age) * 12)
    life_expectancy = 86.6 if gender.upper() == 'M' else 90.8
    total_pension_months = int((life_expectancy - retirement_age) * 12)

    # 1. Inicialización de acumuladores para cálculos futuros
    balance = current_balance
    balance_FAPP = 0
    accumulated_returns = 0
    total_worker_contribution = 0
    total_employer_contribution = 0
    total_sis = 0
    total_women_compensation = 0
    accumulated_FAPP_contribution = 0

    # 2. Acumulación mensual hasta jubilación
    for month in range(months_to_retirement):
        reform_month_index = current_month_index + month
        
        # Aplicar tasas según el mes correspondiente desde feb 2025
        individual_rate = f_individual_total(reform_month_index)
        women_comp_rate = f_compensacion_mujeres(reform_month_index)
        fapp_rate = f_FAPP_target(reform_month_index)
        
        # Calcular aportes mensuales
        contribution = monthly_salary * individual_rate
        worker_contribution = monthly_salary * WORKER_RATE
        sis_contribution = monthly_salary * 0.015
        women_comp = monthly_salary * women_comp_rate
        fapp_contribution = monthly_salary * fapp_rate
        accumulated_FAPP_contribution += fapp_contribution

        # Calcular rentabilidad del mes
        monthly_return = (balance + contribution) * monthly_interest_rate
        accumulated_returns += monthly_return
        
        # Actualizar acumuladores
        total_worker_contribution += worker_contribution
        total_employer_contribution += (individual_rate - WORKER_RATE) * monthly_salary
        total_sis += sis_contribution
        total_women_compensation += women_comp
        
        # Actualizar saldos incluyendo rentabilidad
        balance = (balance + contribution) * (1 + monthly_interest_rate)
        balance_FAPP = (balance_FAPP + fapp_contribution) * (1 + monthly_equivalent_fund_rate)

        
        if month % 6 == 5:
            monthly_salary *= (1 + SALARY_GROWTH_RATE)

    # 3. Estimar componentes del saldo actual (current_balance)
    years_contributed = current_age - 25 if current_age > 25 else 0
    initial_estimated_returns = current_balance - (current_balance / (1 + ANNUAL_INTEREST_RATE) ** years_contributed)
    initial_worker_contribution = current_balance - initial_estimated_returns
    
    # 4. Estimar el SIS histórico y otros aportes históricos
    historical_total_salary = initial_worker_contribution / WORKER_RATE
    historical_sis = historical_total_salary * 0.015
    
    # 5. Actualizar totales finales
    total_worker_contribution += initial_worker_contribution
    total_sis += historical_sis
   

    # Calcular los meses de pensión para ambos géneros al inicio de la función
    life_expectancy_male = 86.6
    life_expectancy_female = 90.8
    pension_annuity_years_male = life_expectancy_male - retirement_age
    pension_annuity_years_female = life_expectancy_female - retirement_age
    total_pension_months_male = int(pension_annuity_years_male * 12)
    total_pension_months_female = int(pension_annuity_years_female * 12)

    # Si es mujer, calcular también como si fuera hombre
    additional_pension = 0
    monthly_BSPA = balance_FAPP / 240

    if gender.upper() == 'F':
        # Calcular pensión adicional (diferencia con mínimo de 10000)
        pension_difference = (balance / total_pension_months_male) - (balance / total_pension_months_female)
        additional_pension = max(pension_difference, 10000)
        monthly_pension = (balance / total_pension_months_female)
    else:
        monthly_pension = (balance / total_pension_months_male)
        additional_pension = 0
    
    # Aplicar PGU según corresponda
    def get_pgu_amount(age: float, months_from_start: int) -> float:
        if months_from_start >= 30:
            # Después de 30 meses, todos los mayores de 65 reciben $250.000
            return 250000
        elif months_from_start >= 18 and age >= 75:
            # Después de 18 meses, mayores de 75 reciben $250.000
            return 250000
        elif months_from_start >= 6 and age >= 82:
            # Después de 6 meses, mayores de 82 reciben $250.000
            return 250000
        else:
            # PGU base actual
            return 214000

    # Calcular la PGU correspondiente (considerando 6 meses desde feb 2025)
    pgu_amount = get_pgu_amount(retirement_age, current_month_index)
    
    if monthly_pension < pgu_amount:
        monthly_pension = pgu_amount
        pgu_applied = True
    else:
        pgu_applied = False


    # Calcular la rentabilidad total de la cuenta individual
    total_returns = accumulated_returns + initial_estimated_returns

    return (balance,                  # saldo_cuenta_individual
            monthly_pension,            # pension_total
            additional_pension,       # pension_adicional
            balance_FAPP,            # balance_fapp
            monthly_BSPA,            # bono_seguridad_previsional
            total_sis,               # aporte_sis
            total_women_compensation, # aporte_compensacion_expectativa_vida
            total_worker_contribution,# aporte_trabajador
            total_employer_contribution, # aporte_empleador
            total_returns,           # rentabilidad_acumulada
            pgu_applied)             # pgu_aplicada


def main():
    # Parámetros de ejemplo:
    current_age_years = 41      # Años
    current_age_months = 6      # Meses
    current_age = current_age_years + (current_age_months / 12)  # Convertir a formato decimal
    retirement_age = 65          # Edad de jubilación (años)
    current_balance = 28998190   # Saldo actual en cuenta individual (pesos)
    monthly_salary = 2564066     # Sueldo bruto mensual (pesos)
    gender = 'F'                 # 'M' para hombre, 'F' para mujer

    print("\n=== Sistema Pre-reforma ===")
    final_balance_pre, pension_pre, worker_total_pre, employer_total_pre, sis_total_pre, returns_pre = calculate_pension_pre_reform(
        current_age,
        retirement_age,
        current_balance,
        monthly_salary,
        gender
    )
    
    # Cálculo de años y meses común para ambos sistemas
    life_expectancy = 86.6 if gender.upper() == 'M' else 90.8
    total_pension_years = life_expectancy - retirement_age
    pension_years = int(total_pension_years)
    pension_months = int((total_pension_years - pension_years) * 12)

    print(f"Saldo acumulado en cuenta individual: {final_balance_pre:,.0f} pesos")
    print(f"Aporte al seguro de invalidez y sobrevivencia: {sis_total_pre:,.0f} pesos")
    print(f"Aporte total empleador: {employer_total_pre:,.0f} pesos")
    print(f"Aporte total trabajador: {worker_total_pre:,.0f} pesos")
    print(f"Pensión mensual estimada: {pension_pre:,.0f} pesos")
    print(f"Pensión total: {pension_pre:,.0f} pesos")  # Mismo valor para mantener equivalencia
    print(f"Rentabilidad total acumulada: {returns_pre:,.0f} pesos")
    print(f"Años de pensión según expectativa de vida: {pension_years} años y {pension_months} meses")

    print("\n=== Sistema Post-reforma ===")
    (final_balance_post, pension_post, total_pension_post, additional_pension_post,
     fapp_balance, monthly_bspa, sis_total_post, women_comp_total, worker_total_post, 
     employer_total_post, returns_post) = calculate_pension_post_reform(
        current_age,
        retirement_age,
        current_balance,
        monthly_salary,
        gender
    )
    print(f"Saldo acumulado en cuenta individual: {final_balance_post:,.0f} pesos")
    print(f"Aporte al seguro de invalidez y sobrevivencia: {sis_total_post:,.0f} pesos")
    print(f"Aporte compensación por diferencias de expectativa de vida: {women_comp_total:,.0f} pesos")
    print(f"Aporte con reembolso garantizado al FAPP: {fapp_balance:,.0f} pesos")
    print(f"Bono de seguridad previsional amortizable: {monthly_bspa:,.0f} pesos")
    print(f"Aporte total empleador: {employer_total_post:,.0f} pesos")
    print(f"Aporte total trabajador: {worker_total_post:,.0f} pesos")
    print(f"Pensión mensual estimada: {pension_post:,.0f} pesos")
    if additional_pension_post > 0:
        print(f"Pensión adicional por diferencias de expectativa de vida: {additional_pension_post:,.0f} pesos")
    print(f"Pensión total: {total_pension_post:,.0f} pesos")
    print(f"Rentabilidad total acumulada: {returns_post:,.0f} pesos")
    print(f"Años de pensión según expectativa de vida: {pension_years} años y {pension_months} meses")

if __name__ == "__main__":
    main()