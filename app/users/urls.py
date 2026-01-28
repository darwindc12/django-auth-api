from django.urls import path

from .views import (
    RegisterView,
    VerifyEmailView,
)

app_name = "users"

urlpatterns = [
    # ──────────────────────────────
    # Authentication & Registration
    # ──────────────────────────────
    path(
        "register/",
        RegisterView.as_view(),
        name="register",
    ),

    # ──────────────────────────────
    # Email Verification
    # ──────────────────────────────
    path(
        "verify-email/<int:uid>/<str:token>/",
        VerifyEmailView.as_view(),
        name="verify-email",
    ),
]