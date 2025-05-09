import torch
import logging
import gc
from celery import shared_task
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
