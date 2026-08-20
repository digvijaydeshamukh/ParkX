
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User


class ChangePasswordAPITest(APITestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="change_password_user",
            email="password@example.com",
            password="OldPassword@123",
            first_name="Test",
            last_name="User",
            phone="9876543210",
            phone_verified=True,
        )

        self.client.force_authenticate(
            user=self.user
        )

        self.change_password_url = (
            "/api/accounts/change-password/"
        )

    # ==================================================
    # Successful Password Change
    # ==================================================

    def test_change_password_success(self):

        response = self.client.post(
            self.change_password_url,
            {
                "current_password": "OldPassword@123",
                "new_password": "NewPassword@123",
                "confirm_password": "NewPassword@123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["message"],
            "Password changed successfully.",
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

    # ==================================================
    # Wrong Current Password
    # ==================================================

    def test_change_password_wrong_current_password(self):

        response = self.client.post(
            self.change_password_url,
            {
                "current_password": "WrongPassword@123",
                "new_password": "NewPassword@123",
                "confirm_password": "NewPassword@123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "current_password",
            response.data,
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(
                "OldPassword@123"
            )
        )

    # ==================================================
    # Password Confirmation
    # ==================================================

    def test_change_password_mismatch(self):

        response = self.client.post(
            self.change_password_url,
            {
                "current_password": "OldPassword@123",
                "new_password": "NewPassword@123",
                "confirm_password": "DifferentPassword@123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "confirm_password",
            response.data,
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(
                "OldPassword@123"
            )
        )

    # ==================================================
    # Invalid New Password
    # ==================================================

    def test_change_password_invalid_new_password(self):

        response = self.client.post(
            self.change_password_url,
            {
                "current_password": "OldPassword@123",
                "new_password": "123",
                "confirm_password": "123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "new_password",
            response.data,
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(
                "OldPassword@123"
            )
        )

    # ==================================================
    # Same Password
    # ==================================================

    def test_change_password_same_as_current_password(self):

        response = self.client.post(
            self.change_password_url,
            {
                "current_password": "OldPassword@123",
                "new_password": "OldPassword@123",
                "confirm_password": "OldPassword@123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(
                "OldPassword@123"
            )
        )

    # ==================================================
    # Unauthenticated User
    # ==================================================

    def test_unauthenticated_user_cannot_change_password(self):

        self.client.force_authenticate(
            user=None
        )

        response = self.client.post(
            self.change_password_url,
            {
                "current_password": "OldPassword@123",
                "new_password": "NewPassword@123",
                "confirm_password": "NewPassword@123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    # ==================================================
    # Missing Current Password
    # ==================================================

    def test_change_password_missing_current_password(self):

        response = self.client.post(
            self.change_password_url,
            {
                "new_password": "NewPassword@123",
                "confirm_password": "NewPassword@123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "current_password",
            response.data,
        )

    # ==================================================
    # Missing New Password
    # ==================================================

    def test_change_password_missing_new_password(self):

        response = self.client.post(
            self.change_password_url,
            {
                "current_password": "OldPassword@123",
                "confirm_password": "NewPassword@123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "new_password",
            response.data,
        )

    # ==================================================
    # Missing Confirmation Password
    # ==================================================

    def test_change_password_missing_confirmation(self):

        response = self.client.post(
            self.change_password_url,
            {
                "current_password": "OldPassword@123",
                "new_password": "NewPassword@123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "confirm_password",
            response.data,
        )

    # ==================================================
    # Old Password Must Stop Working
    # ==================================================

    def test_old_password_cannot_login_after_change(self):

        response = self.client.post(
            self.change_password_url,
            {
                "current_password": "OldPassword@123",
                "new_password": "NewPassword@123",
                "confirm_password": "NewPassword@123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.user.refresh_from_db()

        self.assertFalse(
            self.user.check_password(
                "OldPassword@123"
            )
        )

    # ==================================================
    # New Password Must Work
    # ==================================================

    def test_new_password_works_after_change(self):

        response = self.client.post(
            self.change_password_url,
            {
                "current_password": "OldPassword@123",
                "new_password": "NewPassword@123",
                "confirm_password": "NewPassword@123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(
                "NewPassword@123"
            )
        )
