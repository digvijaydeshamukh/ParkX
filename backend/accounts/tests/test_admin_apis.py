from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User, Roles


class AdminUserAPITests(APITestCase):

    def setUp(self):

        # Admin / Superuser
        self.admin = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="Admin@12345",
        )

        # Normal Vehicle Owner
        self.vehicle_owner = User.objects.create_user(
            username="vehicleowner",
            email="vehicle@example.com",
            password="User@12345",
            role=Roles.VEHICLE_OWNER,
        )

        # Existing Parking Owner
        self.parking_owner = User.objects.create_user(
            username="parkingowner",
            email="parking@example.com",
            password="Owner@12345",
            role=Roles.PARKING_OWNER,
        )

    # ==========================================================
    # CREATE PARKING OWNER
    # ==========================================================

    def test_admin_can_create_parking_owner(self):

        self.client.force_authenticate(
            user=self.admin
        )

        url = reverse("create-list-parking-owner")

        data = {
            "first_name": "New",
            "last_name": "Owner",
            "email": "newowner@example.com",
            "phone": "9876543210",
            "password": "Owner@12345",
            "confirm_password": "Owner@12345",
        }

        response = self.client.post(
            url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        user = User.objects.get(
            email="newowner@example.com"
        )

        self.assertEqual(
            user.role,
            Roles.PARKING_OWNER,
        )

    def test_non_admin_cannot_create_parking_owner(self):

        self.client.force_authenticate(
            user=self.vehicle_owner
        )

        url = reverse("create-list-parking-owner")

        data = {
            "first_name": "New",
            "last_name": "Owner",
            "email": "newowner@example.com",
            "phone": "9876543210",
            "password": "Owner@12345",
            "confirm_password": "Owner@12345",
        }

        response = self.client.post(
            url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_create_parking_owner_duplicate_email_fails(self):

        self.client.force_authenticate(
            user=self.admin
        )

        url = reverse("create-list-parking-owner")

        data = {
            "first_name": "Duplicate",
            "last_name": "Owner",
            "email": self.vehicle_owner.email,
            "phone": "9876543211",
            "password": "Owner@12345",
            "confirm_password": "Owner@12345",
        }

        response = self.client.post(
            url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # ==========================================================
    # PROMOTE USER
    # ==========================================================

    def test_admin_can_promote_vehicle_owner(self):

        self.client.force_authenticate(
            user=self.admin
        )

        url = reverse(
            "promote-parking-owner",
            kwargs={
                "user_id": self.vehicle_owner.id
            },
        )

        response = self.client.patch(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.vehicle_owner.refresh_from_db()

        self.assertEqual(
            self.vehicle_owner.role,
            Roles.PARKING_OWNER,
        )

    def test_non_admin_cannot_promote_user(self):

        self.client.force_authenticate(
            user=self.vehicle_owner
        )

        url = reverse(
            "promote-parking-owner",
            kwargs={
                "user_id": self.parking_owner.id
            },
        )

        response = self.client.patch(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_promote_existing_parking_owner_fails(self):

        self.client.force_authenticate(
            user=self.admin
        )

        url = reverse(
            "promote-parking-owner",
            kwargs={
                "user_id": self.parking_owner.id
            },
        )

        response = self.client.patch(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.parking_owner.refresh_from_db()

        self.assertEqual(
            self.parking_owner.role,
            Roles.PARKING_OWNER,
        )

    def test_promote_nonexistent_user(self):

        self.client.force_authenticate(
            user=self.admin
        )

        url = reverse(
            "promote-parking-owner",
            kwargs={
                "user_id": 999999
            },
        )

        response = self.client.patch(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    # ==========================================================
    # DEMOTE PARKING OWNER
    # ==========================================================

    def test_admin_can_demote_parking_owner(self):

        self.client.force_authenticate(
            user=self.admin
        )

        url = reverse(
            "demote-parking-owner",
            kwargs={
                "user_id": self.parking_owner.id
            },
        )

        response = self.client.patch(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.parking_owner.refresh_from_db()

        self.assertEqual(
            self.parking_owner.role,
            Roles.VEHICLE_OWNER,
        )

    def test_non_admin_cannot_demote_parking_owner(self):

        self.client.force_authenticate(
            user=self.vehicle_owner
        )

        url = reverse(
            "demote-parking-owner",
            kwargs={
                "user_id": self.parking_owner.id
            },
        )

        response = self.client.patch(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.parking_owner.refresh_from_db()

        self.assertEqual(
            self.parking_owner.role,
            Roles.PARKING_OWNER,
        )

    def test_demote_vehicle_owner_fails(self):

        self.client.force_authenticate(
            user=self.admin
        )

        url = reverse(
            "demote-parking-owner",
            kwargs={
                "user_id": self.vehicle_owner.id
            },
        )

        response = self.client.patch(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.vehicle_owner.refresh_from_db()

        self.assertEqual(
            self.vehicle_owner.role,
            Roles.VEHICLE_OWNER,
        )

    def test_demote_nonexistent_user(self):

        self.client.force_authenticate(
            user=self.admin
        )

        url = reverse(
            "demote-parking-owner",
            kwargs={
                "user_id": 999999
            },
        )

        response = self.client.patch(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    # ==========================================================
    # DELETE PARKING OWNER
    # ==========================================================

    def test_admin_can_delete_parking_owner(self):

        self.client.force_authenticate(
            user=self.admin
        )

        user_id = self.parking_owner.id

        url = reverse(
            "delete-parking-owner",
            kwargs={
                "user_id": user_id
            },
        )

        response = self.client.delete(url)

        # Your current API returns 200
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertFalse(
            User.objects.filter(
                id=user_id
            ).exists()
        )

    def test_non_admin_cannot_delete_parking_owner(self):

        self.client.force_authenticate(
            user=self.vehicle_owner
        )

        user_id = self.parking_owner.id

        url = reverse(
            "delete-parking-owner",
            kwargs={
                "user_id": user_id
            },
        )

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertTrue(
            User.objects.filter(
                id=user_id
            ).exists()
        )

    def test_delete_vehicle_owner_using_parking_owner_endpoint_fails(self):

        self.client.force_authenticate(
            user=self.admin
        )

        user_id = self.vehicle_owner.id

        url = reverse(
            "delete-parking-owner",
            kwargs={
                "user_id": user_id
            },
        )

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertTrue(
            User.objects.filter(
                id=user_id
            ).exists()
        )

    def test_delete_nonexistent_parking_owner(self):

        self.client.force_authenticate(
            user=self.admin
        )

        url = reverse(
            "delete-parking-owner",
            kwargs={
                "user_id": 999999
            },
        )

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    # ==========================================================
    # DELETE ANY USER
    # ==========================================================

    def test_admin_can_delete_vehicle_owner(self):

        self.client.force_authenticate(
            user=self.admin
        )

        user_id = self.vehicle_owner.id

        url = reverse(
            "delete-user",
            kwargs={
                "user_id": user_id
            },
        )

        response = self.client.delete(url)

        # Your current API returns 200
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertFalse(
            User.objects.filter(
                id=user_id
            ).exists()
        )

    def test_admin_can_delete_parking_owner_using_delete_user(self):

        self.client.force_authenticate(
            user=self.admin
        )

        user_id = self.parking_owner.id

        url = reverse(
            "delete-user",
            kwargs={
                "user_id": user_id
            },
        )

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertFalse(
            User.objects.filter(
                id=user_id
            ).exists()
        )

    def test_non_admin_cannot_delete_user(self):

        self.client.force_authenticate(
            user=self.vehicle_owner
        )

        user_id = self.parking_owner.id

        url = reverse(
            "delete-user",
            kwargs={
                "user_id": user_id
            },
        )

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertTrue(
            User.objects.filter(
                id=user_id
            ).exists()
        )

    def test_delete_nonexistent_user(self):

        self.client.force_authenticate(
            user=self.admin
        )

        url = reverse(
            "delete-user",
            kwargs={
                "user_id": 999999
            },
        )

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    # ==========================================================
    # ADMIN SELF DELETE PROTECTION
    # ==========================================================

    def test_admin_cannot_delete_self(self):

        self.client.force_authenticate(
            user=self.admin
        )

        url = reverse(
            "delete-user",
            kwargs={
                "user_id": self.admin.id
            },
        )

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertTrue(
            User.objects.filter(
                id=self.admin.id
            ).exists()
        )