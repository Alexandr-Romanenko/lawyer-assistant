import smtplib
import torch
import gc

from celery import shared_task
from celery_tasks.utils import extract_text_from_url, extract_metadata, split_text_into_chunks, \
    get_email_template_user_verification, get_smtp_config
from api.models import DecisionStatus, CourtDecision
from chroma_client.chroma_storage import ChromaDBHandler

import logging
logger = logging.getLogger("tasks")


@shared_task(bind=True, max_retries=2, queue="decision_processing")
def decision_processing_task(self, url: str, decision_id: str):
    import redis
    import json

    redis_client = redis.Redis(host="localhost", port=6379, db=0)

    user = self.requester.user

    def notify(status: str, detail: str = ""):
        message = {
            "decision_id": decision_id,
            "status": status,
            "detail": detail,
        }
        redis_client.publish(f"user:{user.id}", json.dumps(message))

    try:
        decision, _ = CourtDecision.objects.get_or_create(decision_id=decision_id)
        if decision.status == DecisionStatus.DONE:
            notify("already_done")
            return {"status": "already_done", "decision_id": decision_id}

        notify("started", "Processing started")

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        cleaned_text = extract_text_from_url(url)
        notify("text_extracted", "Text extracted")

        decision_metadata = extract_metadata(cleaned_text)
        notify("metadata_extracted", "Metadata extracted")

        chroma_handler = ChromaDBHandler()
        documents = split_text_into_chunks(cleaned_text, decision_id, decision_metadata)
        notify("chunks_created", f"{len(documents)} chunks created")

        ids = [f"{decision_id}_chunk_{i}" for i in range(len(documents))]
        chroma_handler.save_documents(documents, ids, decision_id)
        notify("documents_saved", "Documents saved to Chroma")

        decision.decision_number = decision_metadata.number
        decision.proceeding_number = decision_metadata.proceeding
        decision.status = DecisionStatus.DONE
        decision.save(update_fields=["decision_number", "proceeding_number", "status"])
        notify("done", "Decision processing completed")

        chroma_handler.close()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        del cleaned_text, decision_metadata, documents, chroma_handler
        gc.collect()

        return {"status": "success", "decision_id": decision_id}

    except Exception as e:
        notify("error", str(e))
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        return {"status": "error", "decision_id": decision_id, "error_message": str(e)}

# Working code BEFORE web-sockets
# @shared_task(bind=True, max_retries=2, queue="decision_processing")
# def decision_processing_task(self, url: str, decision_id: str):  # ***** Del self ?
#     try:
#         decision, _ = CourtDecision.objects.get_or_create(decision_id=decision_id)
#         if decision.status == DecisionStatus.DONE:
#             return {"status": "already_done", "decision_id": decision_id}
#
#         if torch.cuda.is_available():
#             torch.cuda.empty_cache()
#
#         cleaned_text = extract_text_from_url(url)
#         decision_metadata = extract_metadata(cleaned_text)
#
#         chroma_handler = ChromaDBHandler()
#         documents = split_text_into_chunks(cleaned_text, decision_id, decision_metadata)
#
#         ids = [f"{decision_id}_chunk_{i}" for i in range(len(documents))]
#         chroma_handler.save_documents(documents, ids, decision_id)
#
#         decision.decision_number = decision_metadata.number
#         decision.proceeding_number = decision_metadata.proceeding
#         decision.status = DecisionStatus.DONE
#         decision.save(update_fields=["decision_number", "proceeding_number", "status"])
#
#         chroma_handler.close()
#         if torch.cuda.is_available():
#             torch.cuda.empty_cache()
#
#         # Явно удаляем тяжелые объекты
#         del cleaned_text
#         del decision_metadata
#         del documents
#         del chroma_handler
#
#         # Принудительно запускаем сборщик мусора
#         gc.collect()
#
#         return {"status": "success", "decision_id": decision_id}
#
#     except Exception as e:
#         logger.error(f"Ошибка обработки решения {decision_id}: {str(e)}")
#         if torch.cuda.is_available():
#             torch.cuda.empty_cache()
#         return {"status": "error", "decision_id": decision_id, "error_message": str(e)}


@shared_task(max_retries=2, queue="email_sending")
def send_email_verification_link(user_id: int, verification_code: str):
    try:
        email = get_email_template_user_verification(user_id, verification_code)
        if email is None:
            raise ValueError(f"Could not generate email: user with id {user_id} not found")

        smtp_config = get_smtp_config()

        if not all(smtp_config.values()):
            raise ValueError("Incomplete SMTP configuration")

        with smtplib.SMTP_SSL(smtp_config["host"], smtp_config["port"]) as server:
            server.login(smtp_config["user"], smtp_config["password"])
            server.send_message(email)

    except Exception as e:
        logger.error(f"Error sending message to user with id {user_id}: {str(e)}")
        send_email_verification_link.retry(exc=e, countdown=60)
