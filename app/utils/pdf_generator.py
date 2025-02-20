from jinja2 import Environment, FileSystemLoader
import pdfkit
import os
from datetime import datetime
from .pension_advisor import PensionAdvisor

class PensionPDFGenerator:
    def __init__(self):
        self.template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
        self.env = Environment(loader=FileSystemLoader(self.template_dir))
        self.template = self.env.get_template('plantilla.html')
        self.advisor = PensionAdvisor()
        
    def format_currency(self, value):
        if value is None:
            return "$0"
        
        value = round(value)  # Eliminamos decimales
        parts = str(abs(value)).split('.')
        integer_part = parts[0]
        
        formatted_integer = ""
        for i, digit in enumerate(reversed(integer_part)):
            if i > 0 and i % 3 == 0:
                formatted_integer = "." + formatted_integer
            formatted_integer = digit + formatted_integer
        
        result = f"${formatted_integer}"
        return "-" + result if value < 0 else result

    def format_age(self, age):
        return f"{int(age)} años"

    def calculate_percentage_change(self, new_value, old_value):
        if old_value == 0:
            return 0
        return ((new_value - old_value) / old_value) * 100

    def generate_pdf(self, data):
        try:
            # Calcular años y meses para la edad actual
            edad_decimal = data['metadata']['edad']
            edad_anos = int(edad_decimal)
            edad_meses = round((edad_decimal - edad_anos) * 12)

            # Calcular años y meses para la expectativa de vida
            expectativa_decimal = data['metadata']['expectativa_vida']
            expectativa_anos = int(expectativa_decimal)
            expectativa_meses = round((expectativa_decimal - expectativa_anos) * 12)

            # Obtener consejos personalizados
            consejos = self.advisor.get_personalized_advice(data)
            
            # Preparar el contexto para la plantilla
            context = {
                # Información Personal
                'nombre': data['metadata']['nombre'],
                'edad': edad_anos,
                'meses': edad_meses,
                'edad_jubilacion': int(data['metadata']['edad_jubilacion']),
                'expectativa_anos': expectativa_anos,
                'expectativa_meses': expectativa_meses,
                'salario_mensual': data['metadata']['salario_mensual'],
                'nivel_estudios': data['metadata'].get('estudios', 'Universitario completo'),

                # Métricas Principales
                'pension_post_reforma': data['post_reforma']['pension_total'],
                'incremento_porcentaje': round(self.calculate_percentage_change(
                    data['post_reforma']['pension_total'],
                    data['pre_reforma']['pension_total']
                )),
                'saldo_cuenta': data['post_reforma']['saldo_acumulado']['saldo_cuenta_individual'],
                'rentabilidad_porcentaje': round((data['post_reforma']['saldo_acumulado']['rentabilidad_acumulada'] / 
                                                data['post_reforma']['saldo_acumulado']['saldo_cuenta_individual']) * 100),
                'brecha_mensual': data['pension_objetivo']['brecha_mensual_post_reforma'],
                'pension_objetivo': data['pension_objetivo']['valor_futuro'],

                # Valores para la sección de información personal
                'pension_ideal_hoy': data['pension_objetivo']['valor_presente'],
                'pension_ideal_jubilar': data['pension_objetivo']['valor_futuro'],

                # Análisis Comparativo
                'pension_pre_reforma': data['pre_reforma']['pension_total'],
                'porcentaje_pre_reforma': 50,
                'porcentaje_post_reforma': round((data['post_reforma']['pension_total'] / 
                                                data['pre_reforma']['pension_total']) * 50),

                # Desglose Post-Reforma
                'pension_base': data['post_reforma']['pension_mensual_base'],
                'compensacion_expectativa': data['post_reforma'].get('pension_adicional_compensacion', 0),
                'cuota_fondo': data['post_reforma'].get('bono_seguridad_previsional', 0),
                'genero': data['metadata']['genero'],

                # Lista de consejos
                'consejos': consejos
            }

            # Generar HTML
            html_content = self.template.render(**context)
            
            # Asegurar que el directorio existe
            pdf_dir = os.path.abspath('pdfs')
            os.makedirs(pdf_dir, exist_ok=True)

            # Generar nombre único para el PDF
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"simulacion_{timestamp}.pdf"
            output_path = os.path.join(pdf_dir, output_filename)

            # Configuración de pdfkit
            options = {
                'page-size': 'A4',
                'margin-top': '0.5in',
                'margin-right': '0.75in',
                'margin-bottom': '0.75in',
                'margin-left': '0.75in',
                'encoding': "UTF-8",
                'enable-local-file-access': None,
                'quiet': '',
                'no-pdf-compression': None  # Agregado para evitar problemas de generación múltiple
            }

            # Limpiar archivos existentes con el mismo nombre base
            for file in os.listdir(pdf_dir):
                if file.startswith(f"simulacion_{timestamp}"):
                    try:
                        os.remove(os.path.join(pdf_dir, file))
                    except Exception as e:
                        print(f"Error al limpiar archivo existente: {e}")

            # Generar PDF
            pdfkit.from_string(html_content, output_path, options=options)
            
            # Verificar que solo existe un archivo con este timestamp
            matching_files = [f for f in os.listdir(pdf_dir) if f.startswith(f"simulacion_{timestamp}")]
            if len(matching_files) > 1:
                # Si hay más de un archivo, mantener solo el más reciente
                matching_files.sort(key=lambda x: os.path.getmtime(os.path.join(pdf_dir, x)))
                for old_file in matching_files[:-1]:
                    try:
                        os.remove(os.path.join(pdf_dir, old_file))
                    except Exception as e:
                        print(f"Error al eliminar archivo duplicado: {e}")

            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                return output_path
            else:
                raise Exception("El archivo PDF no se generó correctamente")

        except Exception as e:
            print(f"Error generando PDF: {str(e)}")
            raise

    def format_decimal(self, value):
        if value is None:
            return "0"
        return f"{value:.1f}"

    def _format_advice(self, advice_list):
        """
        Formatea los consejos para asegurar que se ajusten correctamente al espacio disponible.
        Retorna una lista de consejos con el formato adecuado.
        """
        formatted_advice = []
        for i, advice in enumerate(advice_list, 1):
            # Dividir el consejo en líneas si es muy largo (aproximadamente 80 caracteres por línea)
            words = advice.split()
            lines = []
            current_line = []
            current_length = 0
            
            for word in words:
                if current_length + len(word) + 1 <= 80:  # +1 por el espacio
                    current_line.append(word)
                    current_length += len(word) + 1
                else:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                    current_length = len(word)
            
            if current_line:
                lines.append(' '.join(current_line))
            
            # Unir las líneas con el formato deseado
            formatted_advice.append({
                'number': i,
                'text': '\n'.join(lines),
                'lines': len(lines)  # Para ajustar el espaciado en la plantilla
            })
        
        return formatted_advice 

    def generate_pdf_bytes(self, data):
        try:
            # Calcular años y meses para la edad actual
            edad_decimal = data['metadata']['edad']
            edad_anos = int(edad_decimal)
            edad_meses = round((edad_decimal - edad_anos) * 12)

            # Calcular años y meses para la expectativa de vida
            expectativa_decimal = data['metadata']['expectativa_vida']
            expectativa_anos = int(expectativa_decimal)
            expectativa_meses = round((expectativa_decimal - expectativa_anos) * 12)

            # Obtener consejos personalizados
            consejos = self.advisor.get_personalized_advice(data)
            
            # Preparar el contexto para la plantilla
            context = {
                # Información Personal
                'nombre': data['metadata']['nombre'],
                'edad': edad_anos,
                'meses': edad_meses,
                'edad_jubilacion': int(data['metadata']['edad_jubilacion']),
                'expectativa_anos': expectativa_anos,
                'expectativa_meses': expectativa_meses,
                'salario_mensual': data['metadata']['salario_mensual'],
                'nivel_estudios': data['metadata'].get('estudios', 'Universitario completo'),

                # Métricas Principales
                'pension_post_reforma': data['post_reforma']['pension_total'],
                'incremento_porcentaje': round(self.calculate_percentage_change(
                    data['post_reforma']['pension_total'],
                    data['pre_reforma']['pension_total']
                )),
                'saldo_cuenta': data['post_reforma']['saldo_acumulado']['saldo_cuenta_individual'],
                'rentabilidad_porcentaje': round((data['post_reforma']['saldo_acumulado']['rentabilidad_acumulada'] / 
                                                data['post_reforma']['saldo_acumulado']['saldo_cuenta_individual']) * 100),
                'brecha_mensual': data['pension_objetivo']['brecha_mensual_post_reforma'],
                'pension_objetivo': data['pension_objetivo']['valor_futuro'],

                # Valores para la sección de información personal
                'pension_ideal_hoy': data['pension_objetivo']['valor_presente'],
                'pension_ideal_jubilar': data['pension_objetivo']['valor_futuro'],

                # Análisis Comparativo
                'pension_pre_reforma': data['pre_reforma']['pension_total'],
                'porcentaje_pre_reforma': 50,
                'porcentaje_post_reforma': round((data['post_reforma']['pension_total'] / 
                                                data['pre_reforma']['pension_total']) * 50),

                # Desglose Post-Reforma
                'pension_base': data['post_reforma']['pension_mensual_base'],
                'compensacion_expectativa': data['post_reforma'].get('pension_adicional_compensacion', 0),
                'cuota_fondo': data['post_reforma'].get('bono_seguridad_previsional', 0),
                'genero': data['metadata']['genero'],

                # Lista de consejos
                'consejos': consejos
            }

            # Generar HTML
            html_content = self.template.render(**context)

            # Configuración de pdfkit
            options = {
                'page-size': 'A4',
                'margin-top': '0.25in',
                'margin-right': '0.75in',
                'margin-bottom': '0.75in',
                'margin-left': '0.75in',
                'encoding': "UTF-8",
                'enable-local-file-access': None,
                'quiet': ''
            }

            # Generar PDF en bytes
            pdf_content = pdfkit.from_string(html_content, False, options=options)
            return pdf_content

        except Exception as e:
            print(f"Error generando PDF: {str(e)}")
            raise 