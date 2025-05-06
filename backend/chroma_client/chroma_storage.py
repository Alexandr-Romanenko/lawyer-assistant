import os
import torch
import logging
# from langchain_community.vectorstores import Chroma
# from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from config.app_config import AppConfig
from langchain.schema import Document
#from loguru import logger

logger = logging.getLogger(__name__)


# from langchain.embeddings import HuggingFaceEmbeddings
# from langchain.vectorstores import Chroma


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

    def close(self):
        logger.info("Закрытие Chroma DB...")
        self.db = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()





## Последний неправильно работающий от чата ЖПТ
# class ChromaDBHandler:
#     def __init__(self, persist_directory=None, collection_name=None):
#         self.persist_directory = persist_directory or AppConfig.CHROMA_PATH
#         self.collection_name = collection_name or AppConfig.COLLECTION_NAME
#         self.embedding_model = None
#         self.db = None
#
#     def init_embedding_model(self):
#         if not self.embedding_model:
#             logger.info("Инициализация модели эмбеддингов...")
#             self.embedding_model = HuggingFaceEmbeddings(
#                 model_name=AppConfig.LM_MODEL_NAME,
#                 model_kwargs={"device": "cpu"},  # замените на 'cuda' при необходимости
#                 encode_kwargs={"normalize_embeddings": True},
#             )
#
#     def load_db(self):
#         if not self.embedding_model:
#             self.init_embedding_model()
#
#         logger.info("Загрузка существующей базы Chroma...")
#         self.db = Chroma(
#             embedding_function=self.embedding_model,
#             persist_directory=self.persist_directory,
#             collection_name=self.collection_name,
#         )
#
#     def split_text(self, text: str):
#         splitter = RecursiveCharacterTextSplitter(
#             chunk_size=AppConfig.MAX_CHUNK_SIZE,
#             chunk_overlap=AppConfig.CHUNK_OVERLAP,
#         )
#         return splitter.create_documents([text])
#
#     def save_documents(self, documents, ids=None):
#         self.init_embedding_model()
#
#         texts = [doc.page_content for doc in documents]
#         metadatas = [doc.metadata for doc in documents]
#         ids = ids or [f"doc_{i}" for i in range(len(documents))]
#
#         logger.info(f"Сохраняем {len(documents)} документов в Chroma...")
#
#         self.db = Chroma.from_texts(
#             texts=texts,
#             embedding=self.embedding_model,
#             ids=ids,
#             metadatas=metadatas,
#             persist_directory=self.persist_directory,
#             collection_name=self.collection_name,
#             collection_metadata={"hnsw:space": "cosine"},
#         )
#         self.db.persist()
#
#     def similarity_search(self, query: str, with_score: bool = False, k: int = 10):
#         if not self.db:
#             self.load_db()
#
#         logger.info(f"Поиск похожих документов по запросу: «{query}», top_k={k}")
#         try:
#             if with_score:
#                 results = self.db.similarity_search_with_score(query=query, k=k)
#             else:
#                 results = self.db.similarity_search(query=query, k=k)
#             logger.debug(f"Найдено {len(results)} результатов.")
#             return results
#         except Exception as e:
#             logger.exception(f"Ошибка при поиске: {e}")
#             raise
#
#     def close(self):
#         logger.info("Освобождение ресурсов Chroma DB...")
#         self.db = None
#         if torch.cuda.is_available():
#             torch.cuda.empty_cache()




# import torch
# import logging
# # from langchain_community.vectorstores import Chroma
# # from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_community.vectorstores import Chroma
# from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from config.app_config import AppConfig
#
# logger = logging.getLogger(__name__)
#
# class ChromaDBHandler:
#     def __init__(self, persist_directory=None, collection_name=None):
#         self.persist_directory = persist_directory or AppConfig.CHROMA_PATH
#         self.collection_name = collection_name or AppConfig.COLLECTION_NAME
#         self.embedding_model = None
#         self.db = None
#
#     def init_embedding_model(self):
#         if not self.embedding_model:
#             logger.info("Инициализация модели эмбеддингов...")
#             self.embedding_model = HuggingFaceEmbeddings(
#                 model_name=AppConfig.LM_MODEL_NAME,
#                 model_kwargs={"device": "cpu"},  # или cuda при наличии
#                 encode_kwargs={"normalize_embeddings": True},
#             )
#
#     def split_text(self, text: str):
#         splitter = RecursiveCharacterTextSplitter(
#             chunk_size=AppConfig.MAX_CHUNK_SIZE,
#             chunk_overlap=AppConfig.CHUNK_OVERLAP,
#         )
#         return splitter.create_documents([text])
#
#     def save_documents(self, documents, ids=None):
#         self.init_embedding_model()
#
#         texts = [doc.page_content for doc in documents]
#         metadatas = [doc.metadata for doc in documents]
#         ids = ids or [f"doc_{i}" for i in range(len(documents))]
#
#         logger.info(f"Сохраняем {len(documents)} документов в Chroma...")
#
#         self.db = Chroma.from_texts(
#             texts=texts,
#             embedding=self.embedding_model,
#             ids=ids,
#             metadatas=metadatas,
#             persist_directory=self.persist_directory,
#             collection_name=self.collection_name,
#             collection_metadata={"hnsw:space": "cosine"},
#         )
#
#     # def save_documents(self, documents, ids=None):
#     #     self.init_embedding_model()
#     #
#     #     texts = [doc.page_content for doc in documents]
#     #     metadatas = [doc.metadata for doc in documents]
#     #     ids = ids or [f"doc_{i}" for i in range(len(documents))]
#     #
#     #     logger.info(f"Сохраняем {len(documents)} документов в Chroma...")
#     #
#     #     self.db = Chroma.from_texts(
#     #         texts=texts,
#     #         embedding=self.embedding_model,
#     #         ids=ids,
#     #         metadatas=metadatas,
#     #         persist_directory=self.persist_directory,
#     #         collection_name=self.collection_name,
#     #         collection_metadata={"hnsw:space": "cosine"},
#     #     )
#     #     self.db.persist()
#
#     async def asimilarity_search(self, query: str, with_score: bool, k: int = 10):
#         if not self.db:
#             raise RuntimeError("ChromaVectorStore is not initialized.")
#         logger.info(f"Поиск похожих документов по запросу: «{query}», top_k={k}")
#         try:
#             if with_score:
#                 results = await self.db.asimilarity_search_with_score(
#                     query=query, k=k
#                 )
#             else:
#                 results = await self.db.asimilarity_search(query=query, k=k)
#             logger.debug(f"Найдено {len(results)} результатов.")
#             return results
#         except Exception as e:
#             logger.exception(f"Ошибка при поиске: {e}")
#             raise
#
#     def close(self):
#         logger.info("Закрытие Chroma DB...")
#         if self.db:
#             del self.db
#             self.db = None
#         if torch.cuda.is_available():
#             torch.cuda.empty_cache()
