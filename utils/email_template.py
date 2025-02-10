def get_email_template(nombre):
    return f"""
    <html>
    <body>
        <h2>Simulación de Pensión</h2>
        <p>Estimado/a {nombre},</p>
        <p>Adjunto encontrará el informe detallado de su simulación de pensión.</p>
        <p>Saludos cordiales,</p>
        <p>Equipo de Simulación de Pensiones</p>
    </body>
    </html>
    """ 