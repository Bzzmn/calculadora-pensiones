import sys
from pathlib import Path

# Agregar el directorio raíz del proyecto al PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from config import settings
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

# Configurar el modelo
llm = ChatOpenAI(
    model_name="qwen-plus",
    temperature=0.7,
    max_tokens=2000,
)

# Crear mensajes
messages = [
    SystemMessage(content="Eres un asesor previsional experto que proporciona consejos claros y accionables."),
    HumanMessage(content="Si tengo 50 años, ¿qué consejo me das sobre mi jubilación?")
]

# Realizar consulta
response = llm.invoke(messages)

print(response.content)