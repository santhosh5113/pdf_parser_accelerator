from sentence_transformers import SentenceTransformer
from typing import List, Union
import threading

# Singleton pattern to ensure only one model is loaded
class BGEEmbedder:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(BGEEmbedder, cls).__new__(cls)
                    cls._instance.model = SentenceTransformer('BAAI/bge-base-en-v1.5')
        return cls._instance

    def embed_texts(self, texts: Union[str, List[str]]):
        if isinstance(texts, str):
            texts = [texts]
        return self.model.encode(texts, show_progress_bar=False, normalize_embeddings=True)

# Usage: from database.bge_embedder import BGEEmbedder
# embedder = BGEEmbedder()
# embeddings = embedder.embed_texts(["your text here"]) 