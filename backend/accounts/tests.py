from django.test import TestCase
from django.urls import reverse
from django.core import mail
from rest_framework import status
from rest_framework.test import APITestCase
from .models import PendingRegistration
from django.test import override_settings

# Create your tests here.

@override_settings(
    EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
)
class RegisterAPITest(APITestCase):
    def setUp(self):
        self.url = reverse("register")

        self.payload = {
            "first_name" : "Digvijay",
            "last_name" : "Deshmukh",
            "email" : "digvijayde32@gmail.com",
            "phone" : "9960219195",
            "password" : "Password@123"
        }

    def test_register_success(self):
        response = self.client.post(
            self.url,
            self.payload,
            format = "json"
        )

        self.assertEqual(response.status_code,status.HTTP_201_CREATED)

        self.assertEqual(
            response.data["message"],
            "OTP sent successfully."
        )

        self.assertEqual(
            response.data["email"],
            self.payload["email"]
        )

        self.assertEqual(
        PendingRegistration.objects.count(),
        1
        )

    def test_register_existing_pending_registration(self):
        # First registration
        self.client.post(self.url, self.payload, format="json")

        pending = PendingRegistration.objects.get(
            email=self.payload["email"]
        )

        old_otp_hash = pending.otp_hash

        # Register again with updated data
        updated_payload = self.payload.copy()
        updated_payload["first_name"] = "Rahul"

        response = self.client.post(
            self.url,
            updated_payload,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            PendingRegistration.objects.count(),
            1
        )

        pending.refresh_from_db()

        self.assertEqual(
            pending.first_name,
            "Rahul"
        )

        self.assertNotEqual(
            pending.otp_hash,
            old_otp_hash
        )

    #Missing First Name
    def test_register_missing_first_name(self):
        payload = self.payload.copy()
        payload.pop("first_name")

        response = self.client.post(
            self.url,
            payload,
            format = "json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            "first_name",
            response.data
        )

        self.assertEqual(
            PendingRegistration.objects.count(),
            0
        )

    #Missing Last name
    def test_register_missing_last_name(self):
        payload = self.payload.copy()
        payload.pop("last_name")

        response = self.client.post(
            self.url,
            payload,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("last_name", response.data)
        self.assertEqual(PendingRegistration.objects.count(), 0)

    #Missing Email
    def test_register_missing_email(self):
        payload = self.payload.copy()
        payload.pop("email")

        response = self.client.post(
            self.url,
            payload,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertEqual(PendingRegistration.objects.count(), 0)

    #Missing Phone
    def test_register_missing_phone(self):
        payload = self.payload.copy()
        payload.pop("phone")

        response = self.client.post(
            self.url,
            payload,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("phone", response.data)
        self.assertEqual(PendingRegistration.objects.count(), 0)

    # Missing password
    def test_register_missing_password(self):
        payload = self.payload.copy()
        payload.pop("password")

        response = self.client.post(
            self.url,
            payload,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)
        self.assertEqual(PendingRegistration.objects.count(), 0)


    # Invalid Email
    def test_register_invalid_email(self):
        payload = self.payload.copy()
        payload["email"] = "invalid-email"

        response = self.client.post(
            self.url,
            payload,
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
            PendingRegistration.objects.count(),
            0
        )

    #Invalid phone
    def test_register_invalid_phone(self):
        payload = self.payload.copy()
        payload["phone"] = "12345"

        response = self.client.post(
            self.url,
            payload,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            "phone",
            response.data
        )

        self.assertEqual(
            PendingRegistration.objects.count(),
            0
        )