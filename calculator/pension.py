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

#########################
# Sistema Pre-reforma  #
#########################

def calculate_pension_pre_reform(current_age: float,
                                 retirement_age: float,
                                 current_balance: float,
                                 monthly_salary: float,
                                 worker_rate: float,
                                 annual_interest_rate: float,
                                 salary_growth_rate: float,
                                 gender: str) -> tuple[float, float, float, float, float, float]:
    """
    Calcula el saldo acumulado y la pensión mensual estimada bajo el sistema pre-reforma.
    Sólo se acumula el aporte del trabajador (10% del sueldo); el 1.5% del empleador va al SIS.
    """
    # Estimar los aportes históricos del trabajador (asumiendo que comenzó a los 25 años)
    years_contributed = current_age - 25 if current_age > 25 else 0
    estimated_historical_contribution = current_balance / ((1 + annual_interest_rate) ** years_contributed)
    
    monthly_interest_rate = (1 + annual_interest_rate) ** (1/12) - 1
    # Calcular la expectativa de vida en base al género y, por ende, los años de pensión:
    life_expectancy = 86.6 if gender.upper() == 'M' else 90.8
    pension_annuity_years = life_expectancy - retirement_age
    months_to_retirement = int((retirement_age - current_age) * 12)
    balance = current_balance

    # Calcular totales
    total_worker_contribution = estimated_historical_contribution  # Comenzamos con los aportes históricos estimados
    total_employer_contribution = 0
    total_sis = 0
    
    for month in range(months_to_retirement):
        contribution = monthly_salary * worker_rate
        sis = monthly_salary * 0.015  # 1.5% para SIS
        
        total_worker_contribution += contribution 
        total_employer_contribution += sis
        total_sis += sis
        
        balance = (balance + contribution) * (1 + monthly_interest_rate)
        if month % 6 == 5:
            monthly_salary *= (1 + salary_growth_rate)
    
    final_balance = balance
    total_pension_months = int(pension_annuity_years * 12)
    monthly_pension = final_balance / total_pension_months
    PENSION_MINIMA = 214000
    if monthly_pension < PENSION_MINIMA:
        monthly_pension = PENSION_MINIMA

    # Calcular la rentabilidad total (diferencia entre saldo final y aportes totales)
    total_returns = final_balance - total_worker_contribution

    return final_balance, monthly_pension, total_worker_contribution, total_employer_contribution, total_sis, total_returns

#########################
# Sistema Post-reforma #
#########################

def calculate_pension_post_reform(current_age: float,
                                  retirement_age: float,
                                  current_balance: float,
                                  monthly_salary: float,
                                  worker_rate: float,
                                  annual_interest_rate: float,
                                  salary_growth_rate: float,
                                  gender: str,
                                  equivalent_fund_rate: float) -> tuple[float, float, float, float, float, float, float, float, float, float, float]:
    """
    Calcula el saldo acumulado y la pensión mensual estimada bajo el sistema post-reforma.
    Se acumulan:
      - El aporte del trabajador (10% del sueldo) en la cuenta individual.
      - Aporte adicional del empleador, que se introduce gradualmente (hasta 7% extra),
        distribuido de la siguiente forma:
            • SIS/compensación para mujeres: según f_compensacion_mujeres (no se acumula).
            • Aporte directo a la cuenta individual: según f_individual_total (la diferencia extra sobre el 10%).
            • Aporte a FAPP: según f_FAPP_target.
    """
    # Estimar los aportes históricos del trabajador (asumiendo que comenzó a los 25 años)
    years_contributed = current_age - 25 if current_age > 25 else 0
    estimated_historical_contribution = current_balance / ((1 + annual_interest_rate) ** years_contributed)
    
    # Convertir tasas anuales a mensuales
    monthly_interest_rate = (1 + annual_interest_rate) ** (1/12) - 1
    monthly_fapp_rate = (1 + equivalent_fund_rate) ** (1/12) - 1  # Tasa mensual para FAPP
    months_to_retirement = int((retirement_age - current_age) * 12)
    life_expectancy = 86.6 if gender.upper() == 'M' else 90.8
    pension_annuity_years = life_expectancy - retirement_age

    balance_individual = current_balance
    balance_FAPP = 0.0
    total_worker_contribution = estimated_historical_contribution
    total_employer_contribution = 0
    total_sis = 0
    total_women_compensation = 0
    total_FAPP = 0  # Inicializar total_FAPP

    for month in range(months_to_retirement):
        # Aporte total a cuenta individual según función objetivo
        individual_contribution = monthly_salary * f_individual_total(month)
        total_worker_contribution += individual_contribution

        # SIS (1.5% del sueldo, pagado por el trabajador)
        sis_contribution = monthly_salary * 0.015
        total_sis += sis_contribution

        # Aporte compensación mujeres (según función)
        women_comp = monthly_salary * f_compensacion_mujeres(month)
        total_women_compensation += women_comp

        # Aporte FAPP (según función)
        fapp_contribution = monthly_salary * f_FAPP_target(month)
        total_FAPP += fapp_contribution
        
        # Total aporte empleador (compensación + FAPP)
        employer_contribution = women_comp + fapp_contribution + sis_contribution
        total_employer_contribution += employer_contribution

        # Actualización de saldos con tasas diferentes
        balance_individual = (balance_individual + individual_contribution) * (1 + monthly_interest_rate)
        balance_FAPP = (balance_FAPP + fapp_contribution) * (1 + monthly_fapp_rate)  # Usa tasa FAPP
        
        if month % 6 == 5:
            monthly_salary *= (1 + salary_growth_rate)
    
    final_balance_individual = balance_individual
    total_pension_months = int(pension_annuity_years * 12)
    monthly_pension_female = final_balance_individual / total_pension_months

    # Calcular pensión como mujer
    monthly_pension_female = final_balance_individual / total_pension_months
    
    # Si es mujer, calcular también como si fuera hombre
    additional_pension = 0
    if gender.upper() == 'F':
        # Recalcular con expectativa de vida masculina
        pension_annuity_years_male = 86.6 - retirement_age
        total_pension_months_male = int(pension_annuity_years_male * 12)
        monthly_pension_male = final_balance_individual / total_pension_months_male
        
        # Calcular pensión adicional (diferencia con mínimo de 10000)
        pension_difference = monthly_pension_male - monthly_pension_female
        additional_pension = max(pension_difference, 10000)
    
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
    months_from_reform_start = 6  # Asumiendo que estamos calculando desde la implementación inicial
    pgu_amount = get_pgu_amount(retirement_age, months_from_reform_start)
    
    if monthly_pension_female < pgu_amount:
        monthly_pension_female = pgu_amount
    
    # Calcular el bono de seguridad previsional amortizable (BSPA)
    monthly_BSPA = balance_FAPP / 240  # Distribuir el FAPP en 240 cuotas mensuales
    
    # Calcular pensión total incluyendo BSPA
    total_pension = monthly_pension_female + additional_pension + monthly_BSPA

    # Calcular la rentabilidad total de la cuenta individual
    total_direct_contributions = total_worker_contribution + total_employer_contribution - total_sis - total_women_compensation
    total_returns = final_balance_individual - total_direct_contributions

    return (final_balance_individual, monthly_pension_female, total_pension, additional_pension,
            balance_FAPP, monthly_BSPA, total_sis, total_women_compensation, total_worker_contribution, 
            total_employer_contribution, total_returns)

def main():
    # Parámetros de ejemplo:
    current_age = 41             # Edad actual (años)
    retirement_age = 65          # Edad de jubilación (años)
    current_balance = 28998190 # Saldo actual en cuenta individual (pesos)
    monthly_salary = 2564066   # Sueldo bruto mensual (pesos)
    worker_rate = 0.10           # Aporte del trabajador: 10%
    annual_interest_rate = 0.0311  # Rendimiento anual: 3.11% de acuerdo a rendimientos historicos de fondos de pensiones y tasa implicita de rentas vitalicias.
    salary_growth_rate = 0.0125  # Crecimiento salarial anual: 1.25% de acuerdo a estimacion OCDE
    equivalent_fund_rate = 0.0391  # Rendimiento anual del Fondo equivalente FAPP
    gender = 'F'                 # 'M' para hombre, 'F' para mujer

    print("\n=== Sistema Pre-reforma ===")
    final_balance_pre, pension_pre, worker_total_pre, employer_total_pre, sis_total_pre, returns_pre = calculate_pension_pre_reform(
        current_age,
        retirement_age,
        current_balance,
        monthly_salary,
        worker_rate,
        annual_interest_rate,
        salary_growth_rate,
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
        worker_rate,
        annual_interest_rate,
        salary_growth_rate,
        gender,
        equivalent_fund_rate
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