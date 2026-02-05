from django.contrib.auth.tokens import PasswordResetTokenGenerator


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    """
    Generates a one-time, time-sensitive token for email verification.

    The token becomes invalid if:
    - The user verifies their email
    - The token expires
    """

    def _make_hash_value(self, user, timestamp):
        """
        Token becomes invalid once the user verifies their email.
        """
        return f"{user.pk}{timestamp}{user.is_email_verified}"


email_verification_token = EmailVerificationTokenGenerator()
