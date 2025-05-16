from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from user.views import RegisterViewset, LoginViewset, VerifyUserView

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/register/', RegisterViewset.as_view({'post': 'create'}), name='user_register'),
    path('user/login/', LoginViewset.as_view({'post': 'create'}), name='login'),
    path('user/verify/<uuid:code>/', VerifyUserView.as_view(), name='user_verify'),
]