def get_email_template(nombre, unsubscribe_url):
    return f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bienvenido a The Fullstack</title>
</head>
<body style="margin: 0; padding: 0; background-color: #000000; color: #ffffff; font-family: Arial, sans-serif; line-height: 1.6;">
    <table width="100%" cellpadding="0" cellspacing="0" role="presentation" style="max-width: 600px; margin: 0 auto; background-color: #000000;">
        <!-- Header -->
        <tr>
            <td style="padding: 24px 32px;">
                <table width="100%" cellpadding="0" cellspacing="0" role="presentation">
                    <tr>
                        <td>
                            <img 
                                src="https://general-images-bucket.s3.sa-east-1.amazonaws.com/logo_thefullstack/fullstack_horizontal_color_blackbg.png" 
                                alt="The Fullstack Logo" 
                                style="height: 60px; width: auto; vertical-align: middle; margin-bottom: 8px;"
                            >
                        </td>
                    </tr>
                </table>
            </td>
        </tr>

        <!-- Main Content -->
        <tr>
            <td style="padding: 48px 32px;">
                <!-- Welcome Section -->
                <h1 style="font-size: 42px; font-weight: bold; margin-bottom: 24px; line-height: 1.2;">
                    ¡Bienvenido a<br>
                    The Fullstack! 🎊
                </h1>
                
                <div style="color: #9CA3AF; font-size: 18px; margin-bottom: 32px; max-width: 500px;">
                    <p style="margin-bottom: 24px;">
                        ¡Hola! Soy Álvaro y me complace darte la bienvenida a mi newsletter, tu fuente de información sobre tecnología aplicada a la vida real.<br><br>Durante los últimos meses he estado trabajando en diversos proyectos, utilizando modelos de inteligencia artificial, herramientas de automatización y desarrollando aplicaciones web. Quiero compartir contigo todo lo que he aprendido y mostrarte cómo puedes aplicar estos conocimientos en tu día a día, a través de proyectos e ideas que iré desarrollando.
                    </p>
                    <p style="margin-bottom: 24px;">
                        Mi compromiso contigo es ofrecer contenido de calidad, actualizado cada mes y sin rodeos: información práctica que te ayude a ahorrar tiempo y aumentar tu productividad.
                    </p>
                    <p style="margin-bottom: 24px;">
                        Si estás leyendo esto, es porque logré captar tu atención, ganar tu confianza al entregarte algo valioso de forma gratuita, y ofrecerte un extra a cambio de tu suscripción.<br><br>Cada paso de este camino ha sido planificado cuidadosamente, aplicando técnicas de marketing digital, growth hacking, desarrollo web, comunicación, diseño e inteligencia artificial. Estos son los temas que me apasionan, y quiero que formes parte de este viaje.
                    </p>
                    <p style="margin-bottom: 24px;">
                        Quédate, ponte cómodo y prepárate: ¡esto se va a poner muy interesante!
                    </p>
                </div>

                <!-- Topics Section -->
                <div style="border-top: 1px solid #1F2937; border-bottom: 1px solid #1F2937; padding: 32px 0; margin: 0 -32px 48px -32px; background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(139, 92, 246, 0.1));">
                    <div style="padding: 0 32px;">
                        <h2 style="font-size: 24px; font-weight: bold; margin-bottom: 24px;">Tu Ventana al Futuro Digital</h2>
                        <p style="color: #9CA3AF; font-size: 16px; margin-bottom: 24px;">
                            Algunas de las temáticas que podrás encontrar en cada newsletter:
                        </p>
                        <table width="100%" cellpadding="0" cellspacing="0" role="presentation">
                            <tr>
                                <td style="padding-bottom: 16px;">
                                    <table cellpadding="0" cellspacing="0" role="presentation" style="width: 100%;">
                                        <tr>
                                            <td style="width: 32px;">
                                                ✅
                                            </td>
                                            <td style="padding-left: 12px; color: #D1D5DB; vertical-align: middle;">Inteligencia Artificial y sus aplicaciones prácticas</td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                            <tr>
                                <td style="padding-bottom: 16px;">
                                    <table cellpadding="0" cellspacing="0" role="presentation" style="width: 100%;">
                                        <tr>
                                            <td style="width: 32px;">
                                                ✅
                                            </td>
                                            <td style="padding-left: 12px; color: #D1D5DB; vertical-align: middle;">Automatización y optimización de procesos</td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                            <tr>
                                <td style="padding-bottom: 16px;">
                                    <table cellpadding="0" cellspacing="0" role="presentation" style="width: 100%;">
                                        <tr>
                                            <td style="width: 32px;">
                                                ✅
                                            </td>
                                            <td style="padding-left: 12px; color: #D1D5DB; vertical-align: middle;">Desarrollos en Web3 y blockchain</td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                            <tr>
                                <td style="padding-bottom: 16px;">
                                    <table cellpadding="0" cellspacing="0" role="presentation" style="width: 100%;">
                                        <tr>
                                            <td style="width: 32px;">
                                                ✅
                                            </td>
                                            <td style="padding-left: 12px; color: #D1D5DB; vertical-align: middle;">Finanzas descentralizadas (DeFi)</td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                            <tr>
                                <td>
                                    <table cellpadding="0" cellspacing="0" role="presentation" style="width: 100%;">
                                        <tr>
                                            <td style="width: 32px;">
                                                ✅
                                            </td>
                                            <td style="padding-left: 12px; color: #D1D5DB; vertical-align: middle;">Tendencias tecnológicas emergentes</td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                        </table>
                    </div>
                </div>

                <!-- Document Section -->
                <div style="border: 2px solid #1F2937; border-radius: 12px; padding: 24px 32px; margin-top: 32px;">
                    <table width="100%" cellpadding="0" cellspacing="0" role="presentation">
                        <tr>
                            <td style="display: flex; align-items: center;">
                                <img src="https://general-images-bucket.s3.sa-east-1.amazonaws.com/attached_icon.png" alt="Clip" style="width: 48px; height: 48px; margin-right: 16px;"/>
                                <p style="margin: 0; color: #9CA3AF; font-size: 14px;">
                                    <span style="color: #60A5FA; font-weight: 500;">simulacion_pension.pdf</span> va adjunto a este correo.
                                </p>
                            </td>
                        </tr>
                    </table>
                </div>
            </td>
        </tr>

        <!-- Footer -->
        <tr>
            <td style="padding: 48px 32px; border-top: 1px solid #1F2937;">
                <table width="100%" cellpadding="0" cellspacing="0" role="presentation">
                    <tr>
                        <td style="text-align: center; padding-bottom: 24px;">
                            <a href="https://www.thefullstack.digital">
                                <img 
                                    src="https://general-images-bucket.s3.sa-east-1.amazonaws.com/logo_thefullstack/fullstack_square_color_blackbg.png" 
                                    alt="The Fullstack Logo" 
                                    style="height: 170px; width: auto; margin-bottom: 12px;"
                                >
                            </a>
                        </td>
                    </tr>
                    <tr>
                        <td style="text-align: center; padding-bottom: 16px;">
                            <table cellpadding="0" cellspacing="0" role="presentation" style="margin: 0 auto;">
                                <tr>
                                    <td style="padding: 0 8px;">
                                        <a href="https://www.linkedin.com/in/alvaro-acevedo-ing" style="text-decoration: none;">
                                            <img src="https://general-images-bucket.s3.sa-east-1.amazonaws.com/likedin.png" alt="LinkedIn" width="32" height="32">
                                        </a>
                                    </td>
                                    <td style="padding: 0 8px;">
                                        <a href="https://www.github.com/bzzmn/" style="text-decoration: none;">
                                            <img src="https://general-images-bucket.s3.sa-east-1.amazonaws.com/github.png" alt="GitHub" width="32" height="32">
                                        </a>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <tr>
                        <td style="text-align: center; color: #6B7280; padding-bottom: 16px;">
                            © 2025 The Fullstack. Opensource to the bone.
                        </td>
                    </tr>
                    <tr>
                        <td style="text-align: center;">
                            <a href="{unsubscribe_url}" style="color: #9CA3AF; text-decoration: none; font-size: 14px; border-bottom: 1px solid #374151;">Unsubscribe</a>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
    """ 