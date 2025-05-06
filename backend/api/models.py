from django.db import models


class DecisionStatus(models.TextChoices):
    ABSENT = 'absent', 'Absent'
    DONE = 'done', 'Done'


class CourtDecision(models.Model):
    decision_id = models.CharField(max_length=150, unique=True)
    decision_number = models.CharField(max_length=150)
    proceeding_number = models.CharField(max_length=150)
    status = models.CharField(
        max_length=10,
        choices=DecisionStatus.choices,
        default=DecisionStatus.ABSENT
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.decision_id} - {self.get_status_display()}"

