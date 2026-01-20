
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import User


class UserPublicSerializer(serializers.ModelSerializer):
    """
    Serializer used for returning user data safely.
    Never expose sensitive fields here.
    """

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "is_email_verified",
            "date_joined",
        )
        read_only_fields = fields


class RegisterSerializer(serializers.ModelSerializer):
    """
    Handles user registration.
    Responsible ONLY for creating users.
    """

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = ("email", "username", "password")

    def validate_email(self, value):
        """
        Ensure email uniqueness in a human-readable way.
        """
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists."
            )
        return value.lower()

    def validate_password(self, value):
        """
        Run Django's built-in password validators.
        """
        validate_password(value)
        return value

    def create(self, validated_data):
        """
        Create user using Django's create_user
        to ensure password hashing.
        """
        user = User.objects.create_user(
            email=validated_data["email"],
            username=validated_data["username"],
            password=validated_data["password"],
        )

        # Email verification happens later
        user.is_active = True
        user.save(update_fields=["is_active"])

        return user


class LoginSerializer(serializers.Serializer):
    """
    Validates user credentials.
    JWT generation is handled by the view.
    """

    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(
            request=self.context.get("request"),
            username=email,
            password=password,
        )

        if not user:
            raise serializers.ValidationError(
                "Invalid email or password."
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "This account is disabled."
            )

        if not user.is_email_verified:
            raise serializers.ValidationError(
                "Email address is not verified."
            )

        attrs["user"] = user
        return attrs
