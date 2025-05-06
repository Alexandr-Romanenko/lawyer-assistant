# адаптировать ChromaDBHandler под async
#
# Важное замечание:
# Текущий Chroma (локальный, через chromadb) работает синхронно.
# Async-подход нужен будет, когда ты, например:
#
# перейдешь на Qdrant, Weaviate, Milvus, Chroma Server,
#
# или будешь делать вызовы через сеть (http/grpc).
#
# Тогда сетевые операции = можно и нужно будет делать асинхронно.
#
# Вот план адаптации:
# 1. Переписать ChromaDBHandler в стиле "готов к async"
# Методы будут async.
#
# Внутри пока просто будет синхронный вызов (await sync_to_async(...) через asgiref).
#
# В будущем легко заменить на настоящие асинхронные клиенты.
#
# 2. Установить asgiref (если еще не установлен)
# bash
# Копировать
# Редактировать
# pip install asgiref
# Это легковесная библиотека от Django-экосистемы для превращения sync-функций в async-функции.
#
# Вот адаптированный пример:
# chroma_db_async.py
# python
# Копировать
# Редактировать
# import torch
# import logging
# from asgiref.sync import sync_to_async
# from langchain_community.vectorstores import Chroma
# from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from config.app_config import AppConfig
#
# logger = logging.getLogger(__name__)
#
# class ChromaDBHandlerAsync:
#     def __init__(self, persist_directory=None, collection_name=None):
#         self.persist_directory = persist_directory or AppConfig.CHROMA_PATH
#         self.collection_name = collection_name or AppConfig.COLLECTION_NAME
#         self.embedding_model = None
#         self.db = None
#
#     async def init_embedding_model(self):
#         if not self.embedding_model:
#             logger.info("Инициализация модели эмбеддингов...")
#             self.embedding_model = HuggingFaceEmbeddings(
#                 model_name=AppConfig.LM_MODEL_NAME,
#                 model_kwargs={"device": "cpu"},  # или cuda
#                 encode_kwargs={"normalize_embeddings": True},
#             )
#
#     async def split_text(self, text: str, chunk_size=1000, chunk_overlap=100):
#         splitter = RecursiveCharacterTextSplitter(
#             chunk_size=chunk_size,
#             chunk_overlap=chunk_overlap,
#         )
#         documents = splitter.create_documents([text])
#         return documents
#
#     async def save_documents(self, documents, ids=None):
#         await self.init_embedding_model()
#
#         texts = [doc.page_content for doc in documents]
#         metadatas = [doc.metadata for doc in documents]
#         ids = ids or [f"doc_{i}" for i in range(len(documents))]
#
#         logger.info(f"Сохраняем {len(documents)} документов в Chroma...")
#
#         self.db = await sync_to_async(Chroma.from_texts)(
#             texts=texts,
#             embedding=self.embedding_model,
#             ids=ids,
#             metadatas=metadatas,
#             persist_directory=self.persist_directory,
#             collection_name=self.collection_name,
#             collection_metadata={"hnsw:space": "cosine"},
#         )
#         await sync_to_async(self.db.persist)()
#
#     async def close(self):
#         logger.info("Закрытие Chroma DB...")
#         if self.db:
#             del self.db
#             self.db = None
#         if torch.cuda.is_available():
#             torch.cuda.empty_cache()
# Как будет выглядеть новый таск:
# python
# Копировать
# Редактировать
# from celery import shared_task
# from api.models import DecisionStatus, CourtDecision
# from celery_tasks.utils import extract_text_from_url, extract_metadata
# from chroma_db_async import ChromaDBHandlerAsync
# import asyncio
#
# @shared_task(bind=True, max_retries=3, queue="decision_processing")
# def decision_processing_task(self, url: str, decision_id: str):
#     asyncio.run(_decision_processing(url, decision_id))
#
# async def _decision_processing(url: str, decision_id: str):
#     try:
#         decision, _ = await sync_to_async(CourtDecision.objects.get_or_create)(decision_id=int(decision_id))
#         if decision.status == DecisionStatus.DONE:
#             return "Already processed"
#
#         if torch.cuda.is_available():
#             torch.cuda.empty_cache()
#
#         # 1. Извлекаем текст
#         cleaned_text = await sync_to_async(extract_text_from_url)(url)
#
#         # 2. Извлекаем метаданные
#         decision_metadata = await sync_to_async(extract_metadata)(cleaned_text)
#
#         # 3. Работа с Chroma
#         chroma_handler = ChromaDBHandlerAsync()
#
#         documents = await chroma_handler.split_text(cleaned_text)
#
#         # Добавляем метаданные
#         for doc in documents:
#             doc.metadata.update({
#                 "decision_id": decision_id,
#                 "number": decision_metadata.number,
#                 "proceeding": decision_metadata.proceeding,
#             })
#
#         await chroma_handler.save_documents(documents)
#
#         # 4. Сохраняем статус решения
#         decision.decision_number = decision_metadata.number
#         decision.proceeding_number = decision_metadata.proceeding
#         decision.status = DecisionStatus.DONE
#         await sync_to_async(decision.save)(update_fields=["decision_number", "proceeding_number", "status"])
#
#         await chroma_handler.close()
#
#         if torch.cuda.is_available():
#             torch.cuda.empty_cache()
#
#         return "Done"
#
#     except Exception as e:
#         logger.error(f"Ошибка обработки решения {decision_id}: {str(e)}")
#         if torch.cuda.is_available():
#             torch.cuda.empty_cache()
#         raise
