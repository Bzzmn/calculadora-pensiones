from langchain.text_splitter import CharacterTextSplitter
from pinecone import Pinecone
import voyageai
from config import settings
import os

def load_knowledge_base():
    try:
        # Inicializar Voyage AI
        voyage_client = voyageai.Client(
            api_key=settings.VOYAGE_API_KEY
        )
        
        # Inicializar Pinecone
        pinecone = Pinecone(
            api_key=settings.PINECONE_API_KEY
        )
        
        # Leer todos los archivos de la carpeta knowledge_base/pension
        knowledge_texts = []
        knowledge_dir = "knowledge_base/pension"
        
        for filename in os.listdir(knowledge_dir):
            if filename.endswith(".txt"):
                with open(os.path.join(knowledge_dir, filename), 'r', encoding='utf-8') as file:
                    knowledge_texts.append(file.read())
        
        # Dividir textos en chunks más pequeños
        text_splitter = CharacterTextSplitter(
            chunk_size=500,  # Reducido para evitar chunks demasiado largos
            chunk_overlap=50
        )
        texts = text_splitter.split_text('\n'.join(knowledge_texts))
        
        # Generar embeddings usando Voyage AI
        voyage_batch_size = 128
        embeds = []
        
        for i in range(0, len(texts), voyage_batch_size):
            batch = texts[i:i + voyage_batch_size]
            batch_embeds = voyage_client.embed(
                texts=batch,
                model="voyage-2",
                input_type="document",
                truncation=True
            ).embeddings
            embeds.extend(batch_embeds)
        
        # Configurar índice de Pinecone
        index_name = "pension-knowledge"
        dimension = 1024  # Dimensión de voyage-2
        
        # Crear índice si no existe
        if index_name not in pinecone.list_indexes():
            pinecone.create_index(
                name=index_name,
                dimension=dimension,
                metric='cosine',
                spec={
                    'serverless': {
                        'cloud': settings.PINECONE_CLOUD,
                        'region': settings.PINECONE_REGION
                    }
                }
            )
        
        # Conectar al índice
        index = pinecone.Index(index_name)
        
        # Preparar datos para upsert
        ids = [str(i) for i in range(len(texts))]
        metadata = [{'text': text} for text in texts]
        vectors = list(zip(ids, embeds, metadata))
        
        # Upsert en batches
        batch_size = 128
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            index.upsert(vectors=batch)
        
        print("Base de conocimiento cargada exitosamente")
        
    except Exception as e:
        print(f"Error cargando base de conocimiento: {e}")

if __name__ == "__main__":
    load_knowledge_base() 