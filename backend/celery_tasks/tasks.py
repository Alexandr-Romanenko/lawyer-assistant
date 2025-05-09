import torch
import logging
import gc
from celery import shared_task, group, chord
from api.models import DecisionStatus, CourtDecision
from celery_tasks.utils import extract_text_from_url, extract_metadata, split_text_into_chunks
from chroma_client.chroma_storage import ChromaDBHandler

logger = logging.getLogger("tasks")

@shared_task(bind=True, max_retries=2, queue="decision_processing")
def decision_processing_task(self, url: str, decision_id: str):  # ***** Del self ?
    try:
        decision, _ = CourtDecision.objects.get_or_create(decision_id=decision_id)
        if decision.status == DecisionStatus.DONE:
            return {"status": "already_done", "decision_id": decision_id}

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        cleaned_text = extract_text_from_url(url)
        decision_metadata = extract_metadata(cleaned_text)

        chroma_handler = ChromaDBHandler()
        documents = split_text_into_chunks(cleaned_text, decision_id, decision_metadata)

        ids = [f"{decision_id}_chunk_{i}" for i in range(len(documents))]
        chroma_handler.save_documents(documents, ids, decision_id)

        decision.decision_number = decision_metadata.number
        decision.proceeding_number = decision_metadata.proceeding
        decision.status = DecisionStatus.DONE
        decision.save(update_fields=["decision_number", "proceeding_number", "status"])

        chroma_handler.close()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        # Явно удаляем тяжелые объекты
        del cleaned_text
        del decision_metadata
        del documents
        del chroma_handler

        # Принудительно запускаем сборщик мусора
        gc.collect()

        return {"status": "success", "decision_id": decision_id}

    except Exception as e:
        logger.error(f"Ошибка обработки решения {decision_id}: {str(e)}")
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        return {"status": "error", "decision_id": decision_id, "error_message": str(e)}


@shared_task
def finalize_upload_task(results):
    errors = []
    successes = []

    for result in results:
        if result.get("status") == "error":
            errors.append(result)
        else:
            successes.append(result)

    return {
        "message": "Загрузка завершена",
        "submitted_ids": [r.get("decision_id") for r in results],
        "successful_ids": [r.get("decision_id") for r in successes],
        "errors": errors,
        "success_count": len(successes),
        "error_count": len(errors),
    }


# @shared_task
# def final_search_task(results):
#     """
#     Финальная задача, которая вызывается после выполнения всех задач группы.
#     """
#     errors = []
#     successes = []
#
#     for result in results:
#         if result.get("status") == "error":
#             errors.append(result)
#         else:
#             successes.append(result)
#
#     if errors:
#         logger.warning(f"В ходе обработки возникли ошибки в {len(errors)} задачах")
#         for error in errors:
#             logger.error(f"Ошибка в решении {error.get('decision_id')}: {error.get('error_message')}")
#
#     # Выполняем поиск только по успешно обработанным решениям
#     chroma_handler = ChromaDBHandler()
#
#     # Например, поиск по всем успешным decision_id
#     query_ids = [success["decision_id"] for success in successes]
#     found_documents = chroma_handler.search_documents_by_ids(query_ids)
#
#     chroma_handler.close()
#
#     return {
#         "message": "Финальный поиск завершен",
#         "found_documents_count": len(found_documents),
#         "errors_count": len(errors),
#         "successful_ids": query_ids,
#     }


# @shared_task(bind=True, max_retries=2, queue="decision_processing")
# def decision_processing_task(self, url: str, decision_id: str):
#     try:
#         decision, _ = CourtDecision.objects.get_or_create(decision_id=int(decision_id))
#         if decision.status == DecisionStatus.DONE:
#             return "Already processed"
#
#         if torch.cuda.is_available():
#             torch.cuda.empty_cache()
#
#         # 1. Извлекаем текст
#         cleaned_text = extract_text_from_url(url)
#
#         # 2. Извлекаем метаданные
#         decision_metadata = extract_metadata(cleaned_text)
#
#         # 3. Инициализация работы с Chroma
#         chroma_handler = ChromaDBHandler()
#
#         # 4. Разбиваем текст
#         documents = chroma_handler.split_text(cleaned_text)
#
#         # Присоединяем метаданные к каждому чанку
#         for doc in documents:
#             doc.metadata.update({
#                 "decision_id": decision_id,
#                 "number": decision_metadata.number,
#                 #"proceeding": decision_metadata.proceeding,
#                 # можно добавить дату и другие поля
#             })
#
#         # 5. Сохраняем в базу
#         chroma_handler.save_documents(documents)
#
#         # 6. Обновляем статус решения
#         decision.decision_number = decision_metadata.number
#         decision.proceeding_number = decision_metadata.proceeding
#         decision.status = DecisionStatus.DONE
#         decision.save(update_fields=["decision_number", "proceeding_number", "status"])
#
#         # 7. Очистка
#         chroma_handler.close()
#         if torch.cuda.is_available():
#             torch.cuda.empty_cache()
#
#         return "Done"
#
#     except Exception as e:
#         logger.error(f"Ошибка обработки решения {decision_id}: {str(e)}")
#         if torch.cuda.is_available():
#             torch.cuda.empty_cache()
#         raise self.retry(exc=e, countdown=10)


# @shared_task
# def final_search_task(results):
#     """
#     Вызывается после завершения всех decision_processing_task.
#     Здесь запускаем поиск в векторной базе данных.
#     """
#     # Здесь можно делать поиск по Chroma или что угодно ещё
#     chroma_handler = ChromaDBHandler()
#
#     # Например, поиск всех документов по определённым метаданным
#     found_documents = chroma_handler.search_documents(query="your_query_here")
#
#     chroma_handler.close()
#
#     return {"message": "Поиск завершен", "found_documents_count": len(found_documents)}


