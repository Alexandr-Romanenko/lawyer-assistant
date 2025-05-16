import os


class AppConfig:
    #BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    LM_MODEL_NAME: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    CHROMA_PATH: str = os.path.join(BASE_DIR, "chroma_db")
    COLLECTION_NAME: str = "chroma_docs"
    MAX_CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50
    DOMAIN_NAME: str = "127.0.0.1:8000"
