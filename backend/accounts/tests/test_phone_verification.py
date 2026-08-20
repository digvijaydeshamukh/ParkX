from datetime import timedelta

from django.test import override_settings
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import (
    User,
    PhoneVerificationOTP,
)
from accounts.utils import make_otp_hash
from django.urls import reverse

@override_settings(
    PHONE_OTP_EXPIRY_MINUTES=5,
    PHONE_OTP_RESEND_COOLDOWN_SECONDS=60,
)
class PhoneVerificationAPITest(APITestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="phone_test_user",
            email="phone@example.com",
            password="Test@12345",
            first_name="Test",
            last_name="User",
            phone="9876543210",
            phone_verified=False,
        )

        self.send_url = reverse(
    "send-phone-verification-otp"
)

        self.verify_url = reverse(
            "verify-phone-otp"
        )

        self.resend_url = reverse(
            "resend-phone-verification-otp"
        )

        self.client.force_authenticate(
            user=self.user
        )

    # ==================================================
    # Send Phone Verification OTP
    # ==================================================

    def test_send_phone_verification_otp_success(self):

        response = self.client.post(
            self.send_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data["message"],
            "Phone verification OTP sent successfully."
        )

        self.assertEqual(
            PhoneVerificationOTP.objects.filter(
                user=self.user
            ).count(),
            1
        )

    def test_send_phone_otp_unauthenticated(self):

        self.client.force_authenticate(
            user=None
        )

        response = self.client.post(
            self.send_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_send_phone_otp_when_phone_missing(self):

        self.user.phone = None
        self.user.save()

        response = self.client.post(
            self.send_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            PhoneVerificationOTP.objects.count(),
            0
        )

    def test_send_phone_otp_when_already_verified(self):

        self.user.phone_verified = True
        self.user.save()

        response = self.client.post(
            self.send_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            PhoneVerificationOTP.objects.count(),
            0
        )

    # ==================================================
    # Verify Phone OTP
    # ==================================================

    def create_phone_otp(
        self,
        otp="123456",
        expired=False
    ):

        now = timezone.now()

        if expired:
            expires_at = now - timedelta(minutes=1)
        else:
            expires_at = now + timedelta(minutes=5)

        return PhoneVerificationOTP.objects.create(
            user=self.user,
            phone=self.user.phone,
            otp_hash=make_otp_hash(otp),
            otp_created_at=now,
            expires_at=expires_at,
        )

    def test_verify_phone_otp_success(self):

        self.create_phone_otp()

        response = self.client.post(
            self.verify_url,
            {
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
            "Phone number verified successfully."
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.phone_verified
        )

        self.assertEqual(
            PhoneVerificationOTP.objects.count(),
            0
        )

    def test_verify_phone_otp_invalid(self):

        self.create_phone_otp()

        response = self.client.post(
            self.verify_url,
            {
                "otp": "999999"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.user.refresh_from_db()

        self.assertFalse(
            self.user.phone_verified
        )

        self.assertEqual(
            PhoneVerificationOTP.objects.count(),
            1
        )

    def test_verify_phone_otp_expired(self):

        self.create_phone_otp(
            expired=True
        )

        response = self.client.post(
            self.verify_url,
            {
                "otp": "123456"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.user.refresh_from_db()

        self.assertFalse(
            self.user.phone_verified
        )

        self.assertEqual(
            PhoneVerificationOTP.objects.count(),
            0
        )

    def test_verify_phone_otp_missing(self):

        self.create_phone_otp()

        response = self.client.post(
            self.verify_url,
            {},
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

    def test_verify_phone_otp_unauthenticated(self):

        self.client.force_authenticate(
            user=None
        )

        response = self.client.post(
            self.verify_url,
            {
                "otp": "123456"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_verify_phone_otp_when_already_verified(self):

        self.user.phone_verified = True
        self.user.save()

        self.create_phone_otp()

        response = self.client.post(
            self.verify_url,
            {
                "otp": "123456"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.phone_verified
        )

    def test_phone_otp_cannot_be_reused(self):

        self.create_phone_otp()

        response = self.client.post(
            self.verify_url,
            {
                "otp": "123456"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        # Try using the same OTP again

        response = self.client.post(
            self.verify_url,
            {
                "otp": "123456"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    # ==================================================
    # Resend Phone Verification OTP
    # ==================================================

    def test_resend_phone_otp_success(self):

        response = self.client.post(
            self.resend_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data["message"],
            "Phone verification OTP resent successfully."
        )

        self.assertEqual(
            PhoneVerificationOTP.objects.filter(
                user=self.user
            ).count(),
            1
        )

    def test_resend_phone_otp_unauthenticated(self):

        self.client.force_authenticate(
            user=None
        )

        response = self.client.post(
            self.resend_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_resend_phone_otp_when_phone_missing(self):

        self.user.phone = None
        self.user.save()

        response = self.client.post(
            self.resend_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_resend_phone_otp_when_already_verified(self):

        self.user.phone_verified = True
        self.user.save()

        response = self.client.post(
            self.resend_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_resend_phone_otp_cooldown(self):

        response = self.client.post(
            self.resend_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        # Immediately request again

        response = self.client.post(
            self.resend_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_429_TOO_MANY_REQUESTS
        )

        self.assertIn(
            "remaining_seconds",
            response.data
        )