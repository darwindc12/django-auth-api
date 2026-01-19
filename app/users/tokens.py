from django.contrib.auth.tokens import PasswordResetTokenGenerator


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    """
    Generates a one-time, time-sensitive token for email verification.

    The token becomes invalid if:
    - The user verifies their email
    - The token expires
    """

    def _make_hash_value(self, user, timestamp):
        return (
            f"{user.pk}"
            f"{user.is_email_verified}"
            f"{timestamp}"
        )


email_verification_token = EmailVerificationTokenGenerator()
