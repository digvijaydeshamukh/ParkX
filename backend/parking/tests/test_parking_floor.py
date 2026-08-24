from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from parking.models import ParkingArea, ParkingFloor


class ParkingFloorAPITestCase(APITestCase):

    def setUp(self):

        self.parking_owner = User.objects.create_user(
            username="parking_owner",
            email="parkingowner@example.com",
            password="Test@12345",
            role="parking_owner",
        )

        self.other_parking_owner = User.objects.create_user(
            username="other_owner",
            email="otherowner@example.com",
            password="Test@12345",
            role="parking_owner",
        )

        self.vehicle_owner = User.objects.create_user(
            username="vehicle_owner",
            email="vehicleowner@example.com",
            password="Test@12345",
            role="vehicle_owner",
        )

        self.parking_area = ParkingArea.objects.create(
            owner=self.parking_owner,
            name="ParkX Parking",
            address="123 Main Road",
            city="Pune",
            description="Test parking",
        )

        self.other_parking_area = ParkingArea.objects.create(
            owner=self.other_parking_owner,
            name="Other Parking",
            address="456 Main Road",
            city="Pune",
            description="Other parking",
        )

        self.floor = ParkingFloor.objects.create(
            parking_area=self.parking_area,
            floor_number=1,
            name="Floor 1",
        )

    def floor_list_url(self, area):
        return reverse(
            "parking-floor-list-create",
            kwargs={"area_id": area.pk},
        )

    def floor_detail_url(self, area, floor):
        return reverse(
            "parking-floor-detail",
            kwargs={
                "area_id": area.pk,
                "floor_id": floor.pk,
            },
        )

    # ==================================================
    # VIEW FLOORS
    # ==================================================

    def test_vehicle_owner_can_view_floors(self):

        self.client.force_authenticate(
            user=self.vehicle_owner
        )

        response = self.client.get(
            self.floor_list_url(self.parking_area)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

    def test_other_parking_owner_can_view_floors(self):

        self.client.force_authenticate(
            user=self.other_parking_owner
        )

        response = self.client.get(
            self.floor_list_url(self.parking_area)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    # ==================================================
    # CREATE FLOOR
    # ==================================================

    def test_owner_can_create_floor(self):

        self.client.force_authenticate(
            user=self.parking_owner
        )

        response = self.client.post(
            self.floor_list_url(self.parking_area),
            {
                "floor_number": 2,
                "name": "Floor 2",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            ParkingFloor.objects.filter(
                parking_area=self.parking_area,
                floor_number=2,
            ).exists()
        )

    def test_vehicle_owner_cannot_create_floor(self):

        self.client.force_authenticate(
            user=self.vehicle_owner
        )

        response = self.client.post(
            self.floor_list_url(self.parking_area),
            {
                "floor_number": 2,
                "name": "Floor 2",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_other_owner_cannot_create_floor(self):

        self.client.force_authenticate(
            user=self.other_parking_owner
        )

        response = self.client.post(
            self.floor_list_url(self.parking_area),
            {
                "floor_number": 2,
                "name": "Unauthorized Floor",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    # ==================================================
    # UPDATE FLOOR
    # ==================================================

    def test_owner_can_update_floor(self):

        self.client.force_authenticate(
            user=self.parking_owner
        )

        response = self.client.patch(
            self.floor_detail_url(
                self.parking_area,
                self.floor,
            ),
            {
                "name": "Updated Floor",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.floor.refresh_from_db()

        self.assertEqual(
            self.floor.name,
            "Updated Floor",
        )

    def test_vehicle_owner_cannot_update_floor(self):

        self.client.force_authenticate(
            user=self.vehicle_owner
        )

        response = self.client.patch(
            self.floor_detail_url(
                self.parking_area,
                self.floor,
            ),
            {
                "name": "Unauthorized Update",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_other_owner_cannot_update_floor(self):

        self.client.force_authenticate(
            user=self.other_parking_owner
        )

        response = self.client.patch(
            self.floor_detail_url(
                self.parking_area,
                self.floor,
            ),
            {
                "name": "Unauthorized Update",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    # ==================================================
    # DELETE FLOOR
    # ==================================================

    def test_owner_can_delete_floor(self):

        self.client.force_authenticate(
            user=self.parking_owner
        )

        response = self.client.delete(
            self.floor_detail_url(
                self.parking_area,
                self.floor,
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            ParkingFloor.objects.filter(
                pk=self.floor.pk
            ).exists()
        )

    def test_vehicle_owner_cannot_delete_floor(self):

        self.client.force_authenticate(
            user=self.vehicle_owner
        )

        response = self.client.delete(
            self.floor_detail_url(
                self.parking_area,
                self.floor,
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_other_owner_cannot_delete_floor(self):

        self.client.force_authenticate(
            user=self.other_parking_owner
        )

        response = self.client.delete(
            self.floor_detail_url(
                self.parking_area,
                self.floor,
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        # ==================================================
    # FLOOR NUMBER VALIDATION
    # ==================================================

    def test_create_floor_with_valid_minimum_number(self):

        self.client.force_authenticate(
            user=self.parking_owner
        )

        response = self.client.post(
            self.floor_list_url(self.parking_area),
            {
                "floor_number": -5,
                "name": "Basement 5",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_create_floor_with_valid_maximum_number(self):

        self.client.force_authenticate(
            user=self.parking_owner
        )

        response = self.client.post(
            self.floor_list_url(self.parking_area),
            {
                "floor_number": 20,
                "name": "Floor 20",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_create_floor_below_minimum_number(self):

        self.client.force_authenticate(
            user=self.parking_owner
        )

        response = self.client.post(
            self.floor_list_url(self.parking_area),
            {
                "floor_number": -6,
                "name": "Basement 6",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "floor_number",
            response.data,
        )

    def test_create_floor_above_maximum_number(self):

        self.client.force_authenticate(
            user=self.parking_owner
        )

        response = self.client.post(
            self.floor_list_url(self.parking_area),
            {
                "floor_number": 21,
                "name": "Floor 21",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "floor_number",
            response.data,
        )

    # ==================================================
    # FLOOR NUMBER UNIQUENESS
    # ==================================================

    def test_duplicate_floor_number_in_same_area_is_rejected(self):

        self.client.force_authenticate(
            user=self.parking_owner
        )

        response = self.client.post(
            self.floor_list_url(self.parking_area),
            {
                "floor_number": 1,
                "name": "Duplicate Floor",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "floor_number",
            response.data,
        )

    def test_same_floor_number_allowed_in_different_area(self):

            self.client.force_authenticate(
                user=self.other_parking_owner
            )

            response = self.client.post(
                self.floor_list_url(self.other_parking_area),
                {
                    "floor_number": 1,
                    "name": "Floor 1",
                },
                format="json",
            )

            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
            )

            self.assertTrue(
                ParkingFloor.objects.filter(
                    parking_area=self.other_parking_area,
                    floor_number=1,
                ).exists()
            )