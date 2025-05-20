import re
from celery_tasks.tasks import decision_processing_task


class DecisionProcessor:
    def __init__(self, input_text: str):
        self.raw_data = input_text
        self.decision_ids = []
        self.urls = []

    def extract_ids(self) -> list[str]:
        self.decision_ids = re.findall(r'^\d{7,9}', self.raw_data, re.MULTILINE)
        return self.decision_ids

    def process_all(self, user_channel_id: str) -> list[str]:
        tasks = []
        for decision_id in self.decision_ids:
            url = ""
            self.urls.append(url)
            decision_processing_task.delay(url, decision_id, user_channel_id)
            tasks.append(decision_id)

        return tasks
