import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from user.managers import UserManager
import logging

logger = logging.getLogger(__name__)


class User(AbstractUser):
    username = None
    first_name = models.CharField(max_length=254)
    second_name = models.CharField(max_length=254)
    email = models.EmailField(max_length=200, unique=True)
    is_verified = models.BooleanField(default=False)
    registered_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()


class EmailVerification(models.Model):
    verification_code = models.UUIDField(default=uuid.uuid4, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verifications')
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def generate_verification_link(cls, user: User):
        try:
            record = cls.objects.create(user=user)
            return str(record.verification_code)
        except Exception as e:
            logger.exception(f"Error generating verification link for user {user.id}: {e}")
            return None

    # def generate_of_verification_link(user_id: int):
    #     try:
    #         code = str(uuid.uuid4())
    #         new_link = EmailVerification(verification_code=code, user=user_id)
    #         new_link.save(update_fields=["verification_code", "user"])
    #
    #         return new_link.verification_code
    #
    #     except Exception as e:
    #         pass
