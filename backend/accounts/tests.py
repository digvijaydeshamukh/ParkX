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
        self.client.post(self.url, self.payload, format="json")

        response = self.client.post(
            self.url,
            self.payload,
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