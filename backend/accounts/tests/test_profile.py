from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User


class ProfileAPITestCase(APITestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="profile_test_user",
            email="profile@example.com",
            password="Test@12345",
            first_name="Test",
            last_name="User",
            phone="9876543210",
        )

        self.client.force_authenticate(
            user=self.user
        )

        self.url = "/api/accounts/profile/"

    def test_get_profile(self):

        response = self.client.get(
            self.url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data["email"],
            "profile@example.com"
        )

        self.assertEqual(
            response.data["first_name"],
            "Test"
        )

    def test_update_profile(self):

        data = {
            "first_name": "Updated",
            "last_name": "User",
        }

        response = self.client.patch(
            self.url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.user.refresh_from_db()

        self.assertEqual(
            self.user.first_name,
            "Updated"
        )

        self.assertEqual(
            self.user.last_name,
            "User"
        )

    def test_email_cannot_be_updated(self):

        data = {
            "email": "newemail@example.com",
        }

        response = self.client.patch(
            self.url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.user.refresh_from_db()

        self.assertEqual(
            self.user.email,
            "profile@example.com"
        )

    def test_phone_cannot_be_updated(self):

        data = {
            "phone": "9123456789",
        }

        response = self.client.patch(
            self.url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.user.refresh_from_db()

        self.assertEqual(
            self.user.phone,
            "9876543210"
        )

    def test_unauthenticated_user_cannot_access_profile(self):

        self.client.force_authenticate(
            user=None
        )

        response = self.client.get(
            self.url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )