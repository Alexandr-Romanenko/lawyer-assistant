from datetime import timedelta

from django.utils import timezone
from django.contrib.auth import authenticate

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.reverse import reverse_lazy
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView

from celery_tasks.tasks import send_email_verification_link

from user.serializers import LoginSerializer, RegisterSerializer
from user.models import EmailVerification, User


class LoginViewset(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            user = authenticate(request, email=email, password=password)

            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email
                    },
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                })
            else:
                return Response(
                    {"detail": "Неправильный email или пароль"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterViewset(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def action_after_registration(self, user: User):
        verification_code = EmailVerification.generate_verification_link(user)
        if verification_code:
            send_email_verification_link.delay(user.id, verification_code)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            self.action_after_registration(user)
            return Response({
                "user": {
                    "id": user.id,
                    "first_name": user.first_name,
                    "second_name": user.second_name,
                    "email": user.email,
                },
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyUserView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, code):
        try:
            email_verification_instance = EmailVerification.objects.get(verification_code=code)
            if timezone.now() - email_verification_instance.created_at < timedelta(hours=3):
                user_instance = email_verification_instance.user
                user_instance.is_verified = True
                user_instance.save(update_fields=["is_verified"])
                email_verification_instance.delete()
                return Response({
                    "status": "success",
                    "data": "Your email has been verified"
                })
            else:
                email_verification_instance.delete()
                return Response({
                    "status": "error",
                    "data": "Verification link has expired"
                }, status=status.HTTP_400_BAD_REQUEST)

        except EmailVerification.DoesNotExist:
            return Response({
                "status": "error",
                "data": "Invalid verification code"
            }, status=status.HTTP_404_NOT_FOUND)


class LogoutView(APIView):

    def post(self, request, *args, **kwargs):
        token: Token = request.auth
        token.delete()
        return Response('You have successfully completed your session!')
