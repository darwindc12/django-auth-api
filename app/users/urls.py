from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView,
    VerifyEmailView,
    LoginView,
    MeView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("verify/<int:uid>/<str:token>/", VerifyEmailView.as_view(), name="email-verify"),

    path("login/", LoginView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),

    path("me/", MeView.as_view(), name="me"),
]
