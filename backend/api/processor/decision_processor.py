import re
from celery.tasks import decision_processing_task

class DecisionProcessor:
    def __init__(self, input_text: str):
        self.raw_data = input_text
        self.decision_ids = []
        self.urls = []

    def extract_ids(self) -> list[str]:
        """
        Извлекает номера решений из текста.
        """
        self.decision_ids = re.findall(r'^\d{7,8}', self.raw_data, re.MULTILINE)
        return self.decision_ids
    

    def generate_urls(self):
        """
        Генерирует список URL на основе извлечённых ID.
        """

        self.urls = []
        for decision_id in self.decision_ids:
            url = f"https://reyestr.court.gov.ua/Review/{decision_id}"
            self.urls.append(url) # If it needed?
            decision_processing_task.delay(url, decision_id)

        return {"submitted_ids": self.decision_ids, "message": "Tasks have been queued"}

    
    def run(self):
        self.extract_ids()
        self.generate_urls()
