import logging

from celery import Celery
from celery import shared_task

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

from api.models import DecisionStatus, CourtDecision
from celery_tasks.utils import extract_text_from_url, extract_metadata

logger = logging.getLogger("tasks")


@shared_task(bind=True, max_retries=3, queue="decision_processing")
def decision_processing_task(self, url: str, decision_id: str):
    decision, created = CourtDecision.objects.get_or_create(decision_id=int(decision_id))
    if decision.status == DecisionStatus.DONE:
        return "Already processed"

    try:
        # 1. Получаем и чистим текст
        cleaned_text = extract_text_from_url(url)

        # 2. Получаем метаданные
        decision_metadata = extract_metadata(cleaned_text)
        print(decision_metadata)

        # 3. Разбиваем на чанки
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = splitter.split_text(cleaned_text)
        # print(chunks)

        # 4. Получаем данные по решению из БД
        decision = CourtDecision.objects.get(decision_id=int(decision_id))
        # print(decision)

        # 5. Добавляем метаданные к каждому куску
        documents = [
            Document(
                page_content=chunk,
                metadata={
                    "decision_id": int(decision_id),
                    "decision_number": decision_metadata.number,
                }
            )
            for chunk in chunks
        ]

        # 6. Инициализируем Chroma
        embedding_fn = SentenceTransformerEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embedding_fn)

        # 7. Добавляем документы
        vectorstore.add_documents(documents)
        vectorstore.persist()

        # 8. Обновляем статус в БД
        decision.decision_number = decision_metadata.number
        decision.proceeding_number = decision_metadata.proceeding
        decision.decision_date = decision_metadata.date
        decision.status = DecisionStatus.DONE
        decision.save(update_fields=["decision_number", "proceeding_number", "decision_date", "status"])

        logger.info(f"Processed decision {decision_id} and stored in vector DB.")
        return f"Success"

    except Exception as e:
        logger.error(f"Error processing decision {decision_id}: {str(e)}")
        raise self.retry(exc=e, countdown=10)
