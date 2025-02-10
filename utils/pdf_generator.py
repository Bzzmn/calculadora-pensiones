from fpdf import FPDF

class PensionPDFGenerator:
    def __init__(self):
        pass
        
    def format_currency(self, value):
        # Formato personalizado para moneda chilena
        if value is None:
            return "$0"
        
        # Redondear a 2 decimales
        value = round(value, 2)
        
        # Separar parte entera y decimal
        parts = str(abs(value)).split('.')
        integer_part = parts[0]
        decimal_part = parts[1] if len(parts) > 1 else "00"
        
        # Agregar separadores de miles
        formatted_integer = ""
        for i, digit in enumerate(reversed(integer_part)):
            if i > 0 and i % 3 == 0:
                formatted_integer = "." + formatted_integer
            formatted_integer = digit + formatted_integer
        
        # Construir string final
        result = f"${formatted_integer},{decimal_part}"
        
        # Agregar signo negativo si es necesario
        if value < 0:
            result = "-" + result
            
        return result

    def generate_pdf(self, data):
        pdf = FPDF()
        pdf.add_page()
        
        # Configuración de la página
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'Informe de Simulación de Pensión', 0, 1, 'C')
        
        # Metadata
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f"Género: {data['metadata']['genero']}", 0, 1)
        pdf.cell(0, 10, f"Expectativa de vida: {data['metadata']['expectativa_vida']} años", 0, 1)
        
        # Pre-reforma
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Sistema Actual', 0, 1)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f"Pensión total: {self.format_currency(data['pre_reforma']['pension_total'])}", 0, 1)
        
        # Post-reforma
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Sistema Propuesto', 0, 1)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f"Pensión total: {self.format_currency(data['post_reforma']['pension_total'])}", 0, 1)
        pdf.cell(0, 10, f"Pensión base: {self.format_currency(data['post_reforma']['pension_mensual_base'])}", 0, 1)
        
        # Pensión objetivo
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Pensión Objetivo', 0, 1)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f"Valor presente: {self.format_currency(data['pension_objetivo']['valor_presente'])}", 0, 1)
        pdf.cell(0, 10, f"Valor futuro: {self.format_currency(data['pension_objetivo']['valor_futuro'])}", 0, 1)
        
        return pdf.output(dest='S').encode('latin-1') 