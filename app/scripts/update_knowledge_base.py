import sys
from pathlib import Path

# Agregar el directorio raíz al PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from utils.knowledge_base_loader import load_knowledge_base

if __name__ == "__main__":
    print("Iniciando carga de base de conocimiento...")
    load_knowledge_base()
    print("Proceso completado") 