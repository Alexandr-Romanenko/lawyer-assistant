import os
import torch

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from config.app_config import AppConfig
from langchain.schema import Document

from typing import List, Optional, Dict, Any, Tuple

import logging
logger = logging.getLogger(__name__)


class ChromaDBHandler:
    def __init__(self, persist_directory=None, collection_name=None):
        self.persist_directory = persist_directory or AppConfig.CHROMA_PATH
        self.collection_name = collection_name or AppConfig.COLLECTION_NAME
        self.embedding_model = None
        self.db = None

    def init_embedding_model(self):
        if not self.embedding_model:
            logger.info("Инициализация модели эмбеддингов...")
            self.embedding_model = HuggingFaceEmbeddings(
                model_name=AppConfig.LM_MODEL_NAME,
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True},
            )

    def load_or_create_db(self):
        self.init_embedding_model()
        db_exists = os.path.exists(self.persist_directory) and os.listdir(self.persist_directory)

        if db_exists:
            logger.info("Загрузка существующей базы Chroma...")
            self.db = Chroma(
                embedding_function=self.embedding_model,
                persist_directory=self.persist_directory,
                collection_name=self.collection_name,
            )
        else:
            logger.info(f"Создание новой базы Chroma в каталоге: {self.persist_directory}")
            self.db = Chroma.from_texts(
                texts=[],
                embedding=self.embedding_model,
                persist_directory=self.persist_directory,
                collection_name=self.collection_name,
                collection_metadata={"hnsw:space": "cosine"},
            )

    def save_documents(self, documents: list[Document], ids: list[str], decision_id: str):
        if not self.db:
            self.load_or_create_db()

        try:
            self.db.add_documents(documents=documents, ids=ids)
            logger.info(f"Документ: «{decision_id}», добавлен в Векторное хранилище")

        except Exception as e:
            logger.exception(f"Ошибка при добавлении документов: {e}")
            raise

    def similarity_search(self, query: str, with_score: bool = False, k: int = 10):
        if not self.db:
            self.load_or_create_db()

        logger.info(f"Поиск похожих документов: «{query}», top_k={k}")
        try:
            if with_score:
                return self.db.similarity_search_with_score(query=query, k=k)
            return self.db.similarity_search(query=query, k=k)
        except Exception as e:
            logger.exception(f"Ошибка при поиске: {e}")
            raise

    def similarity_search_by_vector(
            self,
            query: str | List[float],
            k: int = 10,
            filter: Optional[Dict[str, str]] = None,
            where_document: Optional[Dict[str, str]] = None,
            **kwargs: Any
    ) -> List[Tuple[Document, float]]:
        if not self.db:
            self.load_or_create_db()

        logger.info("Поиск по вектору (или тексту с преобразованием)...")

        # Получаем вектор из текста, если передана строка
        if isinstance(query, str):
            if not self.embedding_model:
                self.init_embedding_model()
            embedding = self.embedding_model.embed_query(query)
        else:
            embedding = query  # уже вектор

        # доступ к коллекции
        collection = self.db._collection

        try:
            result = collection.query(
                query_embeddings=[embedding],
                n_results=k,
                where=filter,
                where_document=where_document,
                include=["documents", "metadatas", "distances"],
                **kwargs
            )

            documents = result.get("documents", [[]])[0]
            metadatas = result.get("metadatas", [[]])[0]
            distances = result.get("distances", [[]])[0]

            results = []
            for doc, meta, dist in zip(documents, metadatas, distances):
                score = 1 - dist if dist is not None else None  # косинусная мера
                results.append((Document(page_content=doc, metadata=meta), score))

            return results

        except Exception as e:
            logger.exception(f"Ошибка при поиске по вектору: {e}")
            raise

    def similarity_search_by_vector_with_relevance_scores(
            self,
            embedding: List[float],
            k: int = 4,
            filter: Optional[Dict[str, str]] = None,
            where_document: Optional[Dict[str, str]] = None,
            **kwargs: Any
    ) -> List[Tuple[Document, float]]:
        if not self.db:
            self.load_or_create_db()

        logger.info("Поиск по вектору с оценками релевантности...")

        try:
            result = self.db._collection.query(
                query_embeddings=[embedding],
                n_results=k,
                where=filter,
                where_document=where_document,
                include=["documents", "metadatas", "distances"],
                **kwargs
            )

            documents = result.get("documents", [[]])[0]
            metadatas = result.get("metadatas", [[]])[0]
            distances = result.get("distances", [[]])[0]

            results: List[Tuple[Document, float]] = []
            for doc, meta, dist in zip(documents, metadatas, distances):
                if doc is not None:
                    relevance_score = dist  # меньше — лучше
                    results.append((Document(page_content=doc, metadata=meta), relevance_score))

            return results

        except Exception as e:
            logger.exception(f"Ошибка при поиске с оценками релевантности: {e}")
            raise

    def close(self):
        logger.info("Закрытие Chroma DB...")
        self.db = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
