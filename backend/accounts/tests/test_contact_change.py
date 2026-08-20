
from datetime import timedelta

from django.test import override_settings
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import (
    User,
    ContactChangeOTP,
    ContactChangeType,
)
from accounts.utils import make_otp_hash


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    OTP_EXPIRY_MINUTES=5,
    OTP_RESEND_COOLDOWN_SECONDS=60,
)
class ContactChangeAPITest(APITestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="contact_test_user",
            email="old@example.com",
            password="Test@12345",
            first_name="Test",
            last_name="User",
            phone="9876543210",
            phone_verified=True,
        )

        self.client.force_authenticate(
            user=self.user
        )

        self.change_url = (
            "/api/accounts/contact/change/"
        )

        self.verify_url = (
            "/api/accounts/contact/change/verify-otp/"
        )

        self.resend_url = (
            "/api/accounts/contact/change/resend-otp/"
        )

    # ==================================================
    # Helper
    # ==================================================

    def create_contact_otp(
        self,
        contact_type,
        new_contact,
        otp="123456",
        expired=False,
    ):

        now = timezone.now()

        if expired:
            expires_at = now - timedelta(minutes=1)
        else:
            expires_at = now + timedelta(minutes=5)

        return ContactChangeOTP.objects.create(
            user=self.user,
            contact_type=contact_type,
            new_contact=new_contact,
            otp_hash=make_otp_hash(otp),
            otp_created_at=now,
            expires_at=expires_at,
        )

    # ==================================================
    # Request Email Change
    # ==================================================

    def test_request_email_change_success(self):

        response = self.client.post(
            self.change_url,
            {
                "contact_type": "email",
                "new_contact": "new@example.com",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["message"],
            "OTP sent successfully to the new contact.",
        )

        contact_otp = ContactChangeOTP.objects.get(
            user=self.user
        )

        self.assertEqual(
            contact_otp.contact_type,
            ContactChangeType.EMAIL,
        )

        self.assertEqual(
            contact_otp.new_contact,
            "new@example.com",
        )

        self.user.refresh_from_db()

        self.assertEqual(
            self.user.email,
            "old@example.com",
        )

    def test_request_email_change_current_email(self):

        response = self.client.post(
            self.change_url,
            {
                "contact_type": "email",
                "new_contact": "old@example.com",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "new_contact",
            response.data,
        )

        self.assertEqual(
            ContactChangeOTP.objects.count(),
            0,
        )

    def test_request_email_change_duplicate_email(self):

        User.objects.create_user(
            username="another_user",
            email="taken@example.com",
            password="Test@12345",
        )

        response = self.client.post(
            self.change_url,
            {
                "contact_type": "email",
                "new_contact": "taken@example.com",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "new_contact",
            response.data,
        )

        self.assertEqual(
            ContactChangeOTP.objects.count(),
            0,
        )

    # ==================================================
    # Verify Email Change
    # ==================================================

    def test_verify_email_change_success(self):

        self.create_contact_otp(
            contact_type=ContactChangeType.EMAIL,
            new_contact="new@example.com",
        )

        response = self.client.post(
            self.verify_url,
            {
                "otp": "123456",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["message"],
            "Contact details changed successfully.",
        )

        self.user.refresh_from_db()

        self.assertEqual(
            self.user.email,
            "new@example.com",
        )

        self.assertEqual(
            ContactChangeOTP.objects.count(),
            0,
        )

    def test_verify_email_change_invalid_otp(self):

        self.create_contact_otp(
            contact_type=ContactChangeType.EMAIL,
            new_contact="new@example.com",
        )

        response = self.client.post(
            self.verify_url,
            {
                "otp": "999999",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.user.refresh_from_db()

        self.assertEqual(
            self.user.email,
            "old@example.com",
        )

        self.assertEqual(
            ContactChangeOTP.objects.count(),
            1,
        )

    def test_verify_email_change_expired_otp(self):

        self.create_contact_otp(
            contact_type=ContactChangeType.EMAIL,
            new_contact="new@example.com",
            expired=True,
        )

        response = self.client.post(
            self.verify_url,
            {
                "otp": "123456",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.user.refresh_from_db()

        self.assertEqual(
            self.user.email,
            "old@example.com",
        )

        self.assertEqual(
            ContactChangeOTP.objects.count(),
            0,
        )

    def test_email_change_otp_cannot_be_reused(self):

        self.create_contact_otp(
            contact_type=ContactChangeType.EMAIL,
            new_contact="new@example.com",
        )

        response = self.client.post(
            self.verify_url,
            {
                "otp": "123456",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        response = self.client.post(
            self.verify_url,
            {
                "otp": "123456",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # ==================================================
    # Request Phone Change
    # ==================================================

    def test_request_phone_change_success(self):

        response = self.client.post(
            self.change_url,
            {
                "contact_type": "phone",
                "new_contact": "9123456789",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        contact_otp = ContactChangeOTP.objects.get(
            user=self.user
        )

        self.assertEqual(
            contact_otp.contact_type,
            ContactChangeType.PHONE,
        )

        self.assertEqual(
            contact_otp.new_contact,
            "9123456789",
        )

        self.user.refresh_from_db()

        self.assertEqual(
            self.user.phone,
            "9876543210",
        )

    def test_request_phone_change_current_phone(self):

        response = self.client.post(
            self.change_url,
            {
                "contact_type": "phone",
                "new_contact": "9876543210",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "new_contact",
            response.data,
        )

        self.assertEqual(
            ContactChangeOTP.objects.count(),
            0,
        )

    def test_request_phone_change_duplicate_phone(self):

        User.objects.create_user(
            username="another_phone_user",
            email="another@example.com",
            password="Test@12345",
            phone="9123456789",
            phone_verified=True,
        )

        response = self.client.post(
            self.change_url,
            {
                "contact_type": "phone",
                "new_contact": "9123456789",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "new_contact",
            response.data,
        )

        self.assertEqual(
            ContactChangeOTP.objects.count(),
            0,
        )

    # ==================================================
    # Verify Phone Change
    # ==================================================

    def test_verify_phone_change_success(self):

        self.create_contact_otp(
            contact_type=ContactChangeType.PHONE,
            new_contact="9123456789",
        )

        response = self.client.post(
            self.verify_url,
            {
                "otp": "123456",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.user.refresh_from_db()

        self.assertEqual(
            self.user.phone,
            "9123456789",
        )

        self.assertTrue(
            self.user.phone_verified
        )

        self.assertEqual(
            ContactChangeOTP.objects.count(),
            0,
        )

    # ==================================================
    # Authentication
    # ==================================================

    def test_unauthenticated_user_cannot_request_contact_change(
        self
    ):

        self.client.force_authenticate(
            user=None
        )

        response = self.client.post(
            self.change_url,
            {
                "contact_type": "email",
                "new_contact": "new@example.com",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_unauthenticated_user_cannot_verify_contact_change(
        self
    ):

        self.client.force_authenticate(
            user=None
        )

        response = self.client.post(
            self.verify_url,
            {
                "otp": "123456",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    # ==================================================
    # Resend Contact Change OTP
    # ==================================================

    def test_resend_contact_change_otp_cooldown(self):

        self.create_contact_otp(
            contact_type=ContactChangeType.EMAIL,
            new_contact="new@example.com",
        )

        response = self.client.post(
            self.resend_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_429_TOO_MANY_REQUESTS,
        )

        self.assertIn(
            "remaining_seconds",
            response.data,
        )

    def test_resend_contact_change_otp_success_after_cooldown(
        self
    ):

        contact_otp = self.create_contact_otp(
            contact_type=ContactChangeType.EMAIL,
            new_contact="new@example.com",
        )

        contact_otp.otp_created_at = (
            timezone.now()
            - timedelta(seconds=61)
        )

        contact_otp.save(
            update_fields=[
                "otp_created_at"
            ]
        )

        response = self.client.post(
            self.resend_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["message"],
            "Contact change OTP resent successfully.",
        )

        new_otp = ContactChangeOTP.objects.get(
            user=self.user
        )

        self.assertEqual(
            new_otp.contact_type,
            ContactChangeType.EMAIL,
        )

        self.assertEqual(
            new_otp.new_contact,
            "new@example.com",
        )

    def test_unauthenticated_user_cannot_resend_contact_change_otp(
        self
    ):

        self.client.force_authenticate(
            user=None
        )

        response = self.client.post(
            self.resend_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_resend_contact_change_otp_without_pending_request(
        self
    ):

        response = self.client.post(
            self.resend_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "otp",
            response.data,
        )

    def test_resend_phone_contact_change_otp_success_after_cooldown(
        self
    ):

        contact_otp = self.create_contact_otp(
            contact_type=ContactChangeType.PHONE,
            new_contact="9123456789",
        )

        contact_otp.otp_created_at = (
            timezone.now()
            - timedelta(seconds=61)
        )

        contact_otp.save(
            update_fields=[
                "otp_created_at"
            ]
        )

        response = self.client.post(
            self.resend_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["message"],
            "Contact change OTP resent successfully.",
        )

        new_otp = ContactChangeOTP.objects.get(
            user=self.user
        )

        self.assertEqual(
            new_otp.contact_type,
            ContactChangeType.PHONE,
        )

        self.assertEqual(
            new_otp.new_contact,
            "9123456789",
        )

