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
            logger.info("Initialization of the embedding model")
            self.embedding_model = HuggingFaceEmbeddings(
                model_name=AppConfig.LM_MODEL_NAME,
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True},
            )

    def load_or_create_db(self):
        self.init_embedding_model()
        db_exists = os.path.exists(self.persist_directory) and os.listdir(self.persist_directory)

        if db_exists:
            logger.info("Loading an existing Chroma database")
            self.db = Chroma(
                embedding_function=self.embedding_model,
                persist_directory=self.persist_directory,
                collection_name=self.collection_name,
            )
        else:
            logger.info(f"Creating a new Chroma base in the catalog: {self.persist_directory}")
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
            logger.info(f"Document: «{decision_id}» added to Vector Storage")

        except Exception as e:
            logger.exception(f"Error adding documents: {e}")
            raise

    def similarity_search(self, query: str, with_score: bool = False, k: int = 10):
        if not self.db:
            self.load_or_create_db()

        logger.info(f"Search for similar documents: «{query}», top_k={k}")
        try:
            if with_score:
                return self.db.similarity_search_with_score(query=query, k=k)
            return self.db.similarity_search(query=query, k=k)
        except Exception as e:
            logger.exception(f"Error while searching: {e}")
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

        logger.info("Search by vector (or text with transformation)")

        # Get a vector from text if a string is passed
        if isinstance(query, str):
            if not self.embedding_model:
                self.init_embedding_model()
            embedding = self.embedding_model.embed_query(query)
        else:
            embedding = query

        # Access to collection
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
                score = 1 - dist if dist is not None else None
                results.append((Document(page_content=doc, metadata=meta), score))

            return results

        except Exception as e:
            logger.exception(f"Error while searching by vector: {e}")
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

        logger.info("Vector search with relevance scores")

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
                    relevance_score = dist
                    results.append((Document(page_content=doc, metadata=meta), relevance_score))

            return results

        except Exception as e:
            logger.exception(f"Error when searching with relevance scores: {e}")
            raise

    def close(self):
        logger.info("Closing Chroma DB")
        self.db = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
