from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User, Roles


class LoginAPITest(APITestCase):

    def setUp(self):
        self.url = reverse("login")

        self.email = "login@test.com"
        self.password = "Password@123"

        self.user = User.objects.create_user(
            username="parkx_testuser",
            email=self.email,
            password=self.password,
            phone="9876543210",
            role=Roles.VEHICLE_OWNER,
        )

    def test_login_success(self):
        payload = {
            "email": self.email,
            "password": self.password,
        }

        response = self.client.post(
            self.url,
            payload,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_invalid_password(self):
        payload = {
            "email": self.email,
            "password": "WrongPassword@123",
        }

        response = self.client.post(
            self.url,
            payload,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

        self.assertEqual(
            response.data["detail"],
            "Invalid email or password."
        )

    def test_login_invalid_email(self):
        payload = {
            "email": "doesnotexist@test.com",
            "password": self.password,
        }

        response = self.client.post(
            self.url,
            payload,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

        self.assertEqual(
            response.data["detail"],
            "Invalid email or password."
        )

    def test_login_missing_email(self):
        payload = {
            "password": self.password,
        }

        response = self.client.post(
            self.url,
            payload,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn("email", response.data)

    def test_login_missing_password(self):
        payload = {
            "email": self.email,
        }

        response = self.client.post(
            self.url,
            payload,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn("password", response.data)

    def test_refresh_token(self):
        payload = {
            "email": self.email,
            "password": self.password,
        }

        login_response = self.client.post(
            self.url,
            payload,
            format="json"
        )

        refresh_token = login_response.data["refresh"]

        refresh_url = reverse("token-refresh")

        response = self.client.post(
            refresh_url,
            {
                "refresh": refresh_token,
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertIn("access", response.data)