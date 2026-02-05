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

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    """
    Registers a new user and sends an email verification link.
    """
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        self._send_verification_email(user)

    def _send_verification_email(self, user):
        """
        Generates and sends the email verification link.
        """
        token = email_verification_token.make_token(user)

        verify_path = reverse(
            "email-verify",
            kwargs={"uid": user.pk, "token": token},
        )

        verify_url = f"http://localhost:8000{verify_path}"

        subject = "Verify your email address"
        message = (
            f"Hi {user.username},\n\n"
            f"Please verify your email by clicking the link below:\n"
            f"{verify_url}\n\n"
            f"If you did not create this account, you can ignore this email."
        )

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

from django.shortcuts import get_object_or_404

class VerifyEmailView(generics.GenericAPIView):
    """
    Verifies a user's email using a one-time token.
    """

    def get(self, request, uid, token):
        user = get_object_or_404(User, pk=uid)

        if not email_verification_token.check_token(user, token):
            return Response(
                {"detail": "Invalid or expired verification link."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.is_email_verified = True
        user.save(update_fields=["is_email_verified"])

        return Response(
            {"detail": "Email successfully verified."},
            status=status.HTTP_200_OK,
        )

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


    
