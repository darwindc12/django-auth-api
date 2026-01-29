from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.urls import reverse

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    RegisterSerializer,
)
from .tokens import email_verification_token
from drf_spectacular.utils import extend_schema, OpenApiResponse


User = get_user_model()

class RegisterView(generics.CreateAPIView):
    """
    Register a new user.

    - Creates a user account
    - Sends an email verification link
    """

    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        user = serializer.save()

        token = email_verification_token.make_token(user)
        verification_url = self._build_verification_url(user, token)

        self._send_verification_email(user.email, verification_url)

    def _build_verification_url(self, user, token) -> str:
        path = reverse("email-verify", args=[user.pk, token])
        return f"http://localhost:8000{path}"

    def _send_verification_email(self, email: str, url: str) -> None:
        send_mail(
            subject="Verify your email address",
            message=f"Click the link to verify your account:\n{url}",
            from_email=None,
            recipient_list=[email],
        )


class VerifyEmailView(generics.GenericAPIView):
    """
    Verify a user's email address.
    """

    def get(self, request, uid: int, token: str):
        user = get_object_or_404(User, pk=uid)

        if not email_verification_token.check_token(user, token):
            return Response(
                {"detail": "Invalid or expired token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.is_email_verified = True
        user.save(update_fields=["is_email_verified"])

        return Response({"detail": "Email verified successfully"})
class LoginView(TokenObtainPairView):
    """
    JWT login view with email verification check.
    """

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        email = request.data.get("email")
        user = User.objects.filter(email=email).first()

        if user and not user.is_email_verified:
            return Response(
                {"detail": "Please verify your email before logging in."},
                status=status.HTTP_403_FORBIDDEN,
            )

        return response
class MeView(APIView):
    """
    Returns the authenticated user's profile.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        return Response(
            {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "is_email_verified": user.is_email_verified,
            },
            status=status.HTTP_200_OK,
        )

@extend_schema(
    summary="Register a new user",
    description="Creates a new user account and sends an email verification link.",
    responses={
        201: OpenApiResponse(description="User created successfully"),
        400: OpenApiResponse(description="Invalid input"),
    },
)
class RegisterView(generics.CreateAPIView):
    ...