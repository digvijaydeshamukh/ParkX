from datetime import timedelta

from django.core import mail
from django.test import override_settings
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User, PasswordResetOTP
from accounts.utils import make_otp_hash


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"
)
class ForgotPasswordAPITest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="parkx_testuser",
            email="sonu@example.com",
            phone="9876543210",
            first_name="Sonu",
            last_name="Patil",
            password="OldPassword@123",
        )

        self.forgot_url = "/api/accounts/forgot-password/"
        self.verify_otp_url = "/api/accounts/verify-reset-otp/"
        self.reset_password_url = "/api/accounts/reset-password/"

    # ==================================================
    # Forgot Password
    # ==================================================

    def test_forgot_password_success(self):
        response = self.client.post(
            self.forgot_url,
            {
                "email": self.user.email
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data["message"],
            (
                "If an account exists with this email, "
                "a password reset OTP has been sent."
            )
        )

        self.assertEqual(
            PasswordResetOTP.objects.filter(
                user=self.user
            ).count(),
            1
        )

        self.assertEqual(
            len(mail.outbox),
            1
        )

    def test_forgot_password_non_existing_email(self):
        response = self.client.post(
            self.forgot_url,
            {
                "email": "doesnotexist@example.com"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data["message"],
            (
                "If an account exists with this email, "
                "a password reset OTP has been sent."
            )
        )

        self.assertEqual(
            PasswordResetOTP.objects.count(),
            0
        )

        self.assertEqual(
            len(mail.outbox),
            0
        )

    def test_forgot_password_invalid_email(self):
        response = self.client.post(
            self.forgot_url,
            {
                "email": "invalid-email"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            "email",
            response.data
        )

        self.assertEqual(
            PasswordResetOTP.objects.count(),
            0
        )

    # ==================================================
    # Verify Reset OTP
    # ==================================================

    def create_reset_otp(
        self,
        otp="123456",
        expired=False
    ):
        now = timezone.now()

        if expired:
            expires_at = now - timedelta(minutes=1)
        else:
            expires_at = now + timedelta(minutes=5)

        return PasswordResetOTP.objects.create(
            user=self.user,
            otp_hash=make_otp_hash(otp),
            otp_created_at=now,
            expires_at=expires_at,
        )

    def test_verify_reset_otp_success(self):
        self.create_reset_otp()

        response = self.client.post(
            self.verify_otp_url,
            {
                "email": self.user.email,
                "otp": "123456"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data["message"],
            "OTP verified successfully."
        )

        self.assertIn(
            "reset_token",
            response.data
        )

        reset_otp = PasswordResetOTP.objects.get(
            user=self.user
        )

        self.assertIsNotNone(
            reset_otp.reset_token_jti
        )

        self.assertIsNotNone(
            reset_otp.reset_token_expires_at
        )

    def test_verify_reset_otp_invalid_otp(self):
        self.create_reset_otp()

        response = self.client.post(
            self.verify_otp_url,
            {
                "email": self.user.email,
                "otp": "999999"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            "Invalid or expired OTP.",
            response.data
        )

    def test_verify_reset_otp_expired(self):
        self.create_reset_otp(
            expired=True
        )

        response = self.client.post(
            self.verify_otp_url,
            {
                "email": self.user.email,
                "otp": "123456"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            "Invalid or expired OTP.",
            response.data
        )

        self.assertEqual(
            PasswordResetOTP.objects.count(),
            0
        )

    def test_verify_reset_otp_non_existing_email(self):
        response = self.client.post(
            self.verify_otp_url,
            {
                "email": "doesnotexist@example.com",
                "otp": "123456"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            "Invalid or expired OTP.",
            response.data
        )

    def test_verify_reset_otp_missing_otp(self):
        response = self.client.post(
            self.verify_otp_url,
            {
                "email": self.user.email
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            "otp",
            response.data
        )

    # ==================================================
    # Reset Password
    # ==================================================

    def get_reset_token(self):
        self.create_reset_otp()

        response = self.client.post(
            self.verify_otp_url,
            {
                "email": self.user.email,
                "otp": "123456"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        return response.data["reset_token"]

    def test_reset_password_success(self):
        reset_token = self.get_reset_token()

        response = self.client.post(
            self.reset_password_url,
            {
                "reset_token": reset_token,
                "password": "NewPassword@123",
                "confirm_password": "NewPassword@123"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data["message"],
            "Password reset successfully."
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(
                "NewPassword@123"
            )
        )

        self.assertFalse(
            self.user.check_password(
                "OldPassword@123"
            )
        )

        # Reset-token record should be deleted
        self.assertEqual(
            PasswordResetOTP.objects.count(),
            0
        )

    def test_reset_password_mismatch(self):
        reset_token = self.get_reset_token()

        response = self.client.post(
            self.reset_password_url,
            {
                "reset_token": reset_token,
                "password": "NewPassword@123",
                "confirm_password": "WrongPassword@123"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            "confirm_password",
            response.data
        )

        # Token must remain valid after validation failure
        self.assertEqual(
            PasswordResetOTP.objects.count(),
            1
        )

    def test_reset_password_invalid_token(self):
        response = self.client.post(
            self.reset_password_url,
            {
                "reset_token": "invalid-token",
                "password": "NewPassword@123",
                "confirm_password": "NewPassword@123"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            "Invalid or expired reset token.",
            response.data
        )

    def test_reset_token_can_be_used_after_password_mismatch(self):
        reset_token = self.get_reset_token()

        # First attempt: wrong confirmation password
        response = self.client.post(
            self.reset_password_url,
            {
                "reset_token": reset_token,
                "password": "NewPassword@123",
                "confirm_password": "WrongPassword@123"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        # Second attempt: correct confirmation password
        response = self.client.post(
            self.reset_password_url,
            {
                "reset_token": reset_token,
                "password": "NewPassword@123",
                "confirm_password": "NewPassword@123"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_reset_token_cannot_be_reused(self):
        reset_token = self.get_reset_token()

        # First successful password reset
        response = self.client.post(
            self.reset_password_url,
            {
                "reset_token": reset_token,
                "password": "NewPassword@123",
                "confirm_password": "NewPassword@123"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        # Try to use the same token again
        response = self.client.post(
            self.reset_password_url,
            {
                "reset_token": reset_token,
                "password": "AnotherPassword@123",
                "confirm_password": "AnotherPassword@123"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            "Invalid or expired reset token.",
            response.data
        )

    def test_reset_password_missing_token(self):
        response = self.client.post(
            self.reset_password_url,
            {
                "password": "NewPassword@123",
                "confirm_password": "NewPassword@123"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            "reset_token",
            response.data
        )

    def test_reset_password_password_mismatch_does_not_change_password(self):
        reset_token = self.get_reset_token()

        response = self.client.post(
            self.reset_password_url,
            {
                "reset_token": reset_token,
                "password": "NewPassword@123",
                "confirm_password": "WrongPassword@123"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(
                "OldPassword@123"
            )
        )

