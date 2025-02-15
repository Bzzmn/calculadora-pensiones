from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from pinecone import Pinecone
import voyageai
from config import settings

class PensionAdvisor:
    def __init__(self):
        try:
            # Configurar cliente para Qwen usando langchain
            self.llm = ChatOpenAI(
                openai_api_key=settings.OPENAI_API_KEY,
                openai_api_base=settings.OPENAI_API_BASE,
                model_name="qwen-plus",
                temperature=0.7,
                max_tokens=2000
            )
            
            # Inicializar Voyage AI
            self.voyage_client = voyageai.Client(
                api_key=settings.VOYAGE_API_KEY
            )
            
            # Conectar a Pinecone
            pinecone = Pinecone(
                api_key=settings.PINECONE_API_KEY,
                environment=settings.PINECONE_REGION
            )
            
            # Conectar al índice existente
            self.knowledge_base = pinecone.Index("pension-knowledge")
            
        except Exception as e:
            print(f"Error inicializando PensionAdvisor: {e}")
            self.is_development = True

    def get_personalized_advice(self, session_data):
        try:
            if hasattr(self, 'is_development') and self.is_development:
                return self._get_development_advice(session_data)

            # Calcular métricas
            edad = session_data["metadata"]["edad"]
            salario = session_data["metadata"]["salario_mensual"]
            pension_actual = session_data["post_reforma"]["pension_total"]
            pension_objetivo = session_data["pension_objetivo"]["valor_futuro"]
            brecha = session_data["pension_objetivo"]["brecha_mensual_post_reforma"]
            
            anos_para_jubilacion = 65 - edad
            tasa_reemplazo = (pension_actual / salario) * 100

            # Crear query embedding
            query = f"consejos para persona de {int(edad)} años con tasa de reemplazo {int(tasa_reemplazo)}%"
            query_embedding = self.voyage_client.embed(
                texts=[query],
                model="voyage-2",
                input_type="query",
                truncation=True
            ).embeddings[0]

            # Buscar documentos relevantes
            results = self.knowledge_base.query(
                vector=query_embedding,
                top_k=2,
                include_metadata=True
            )
            
            context = "\n".join(match['metadata']['text'] for match in results['matches'])

            # Preparar el prompt con el contexto
            prompt = f"""
            Basándote en la siguiente información de nuestra base de conocimiento:

            {context}

            Genera 5 consejos personalizados para un cliente con estas características:

            - Edad actual: {int(edad)} años
            - Años para jubilación: {int(anos_para_jubilacion)}
            - Salario mensual actual: {self._format_currency(salario)}
            - Pensión proyectada: {self._format_currency(pension_actual)}
            - Pensión objetivo: {self._format_currency(pension_objetivo)}
            - Brecha mensual: {self._format_currency(brecha)}
            - Tasa de reemplazo: {int(tasa_reemplazo)}%

            Los consejos deben ser:
            1. Específicos para la edad y etapa de vida del cliente
            2. Abordar la brecha previsional de manera práctica
            3. Incluir recomendaciones de inversión y ahorro
            4. Considerar aspectos de planificación financiera a largo plazo
            5. El último consejo DEBE ser un mensaje positivo y alentador sobre la importancia 
               de planificar con tiempo la jubilación, enfatizando el poder del interés compuesto 
               y cómo las acciones tempranas pueden tener un gran impacto en el futuro.

            Formato: Genera exactamente 5 consejos concisos pero informativos, 
            en lenguaje claro y profesional, con recomendaciones accionables.
            """

            # Consultar al modelo usando langchain
            messages = [
                SystemMessage(content="Eres un asesor previsional experto que proporciona consejos claros y accionables."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            response_text = response.content

            # Procesar y formatear consejos
            consejos = [
                consejo.strip()
                    .replace('**', '')  # Eliminar marcadores de negrita
                    .replace('*', '')   # Eliminar cursivas
                    .split(': ', 1)[-1] # Eliminar numeración y título en negrita
                for consejo in response_text.split('\n')
                if consejo.strip() and not consejo.startswith('Consejo')
            ]

            # Asegurar que tenemos exactamente 5 consejos
            while len(consejos) < 5:
                if len(consejos) == 4:
                    consejos.append("Recuerde que el tiempo es su mejor aliado en la planificación de su jubilación. El interés compuesto puede multiplicar significativamente sus ahorros, por lo que cada peso ahorrado hoy trabajará para usted durante muchos años, construyendo un futuro financiero más sólido.")
                else:
                    consejos.append("Considere buscar asesoría financiera profesional para desarrollar una estrategia personalizada.")
            
            print("Consejos generados:", consejos)
            return consejos[:5]

        except Exception as e:
            print(f"Error generando consejos: {e}")
            return self._get_development_advice(session_data)

    def _get_development_advice(self, session_data):
        # Consejos por defecto para desarrollo
        edad = session_data["metadata"]["edad"]
        brecha = session_data["pension_objetivo"]["brecha_mensual_post_reforma"]
        pension_actual = session_data["post_reforma"]["pension_total"]
        
        return [
            f"Considerando su edad actual de {int(edad)} años, le recomendamos aumentar sus ahorros voluntarios en un 15% de su salario mensual para reducir la brecha previsional.",
            
            "Evalúe la posibilidad de diversificar sus inversiones a través de APV en fondos mutuos o similares, lo que podría mejorar su rentabilidad a largo plazo.",
            
            f"Con una pensión proyectada de {self._format_currency(pension_actual)}, sugerimos revisar sus gastos futuros y considerar estrategias adicionales de ahorro para mantener su nivel de vida.",
            
            f"Para cubrir la brecha de {self._format_currency(brecha)}, considere asesorarse con un experto financiero para desarrollar un plan de inversión personalizado.",
            
            "Recuerde que el tiempo es su mejor aliado en la planificación de su jubilación. El interés compuesto puede multiplicar significativamente sus ahorros, por lo que cada peso ahorrado hoy trabajará para usted durante muchos años, construyendo un futuro financiero más sólido."
        ]

    def _format_currency(self, value):
        if value is None:
            return "$0"
        
        value = round(value)
        formatted = "{:,.0f}".format(value).replace(",", ".")
        return f"${formatted}" 