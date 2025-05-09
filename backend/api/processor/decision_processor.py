import re
from celery import chord
from celery_tasks.tasks import decision_processing_task, finalize_upload_task


class DecisionProcessor:
    def __init__(self, input_text: str):
        self.raw_data = input_text
        self.decision_ids = []
        self.urls = []

    def extract_ids(self) -> list[str]:
        self.decision_ids = re.findall(r'^\d{7,9}', self.raw_data, re.MULTILINE)
        return self.decision_ids

    def process_all(self) -> dict:
        #tasks = []
        for decision_id in self.decision_ids:
            url = f"https://reyestr.court.gov.ua/Review/{decision_id}"
            self.urls.append(url)
            decision_processing_task.delay(url, decision_id)
            #tasks.append(decision_processing_task(url, decision_id))

        #callback = finalize_upload_task.s()
        #chord_result = chord(tasks)(callback)
        #chord(tasks)(callback)
        return {"message": "Решения отправлены на обработку"}

        # Ждём итоговый callback, который вернёт агрегированные данные
        # final_result = chord_result.get(timeout=60000)
        # print(final_result)
        # return final_result

    # def process_all(self) -> dict:
    #     tasks = []
    #     for decision_id in self.decision_ids:
    #         url = f"https://reyestr.court.gov.ua/Review/{decision_id}"
    #         self.urls.append(url)
    #         tasks.append(decision_processing_task.s(url, decision_id))
    #
    #     # Выполняем chord и ждем результат синхронно
    #     async_result = chord(tasks)(finalize_upload_task.s())
    #     result = async_result.get(timeout=300)
    #     print(result)
    #
    #     return result
