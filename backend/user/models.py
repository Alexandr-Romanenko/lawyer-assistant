import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(max_length=200, unique=True)
    is_verified = models.BooleanField(default=False)
    registered_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'username'  # или 'email', если захочешь
    REQUIRED_FIELDS = ['email']  # если username — основной, то email требуется

class EmailVerification(models.Model):
    verification_code = models.UUIDField(default=uuid.uuid4, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verifications')
    created_at = models.DateTimeField(auto_now_add=True)
