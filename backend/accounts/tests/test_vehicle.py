from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User, Vehicle, VehicleType


class VehicleAPITestCase(APITestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="vehicle_test_user",
            email="vehicleuser@example.com",
            password="Test@12345",
            first_name="Vehicle",
            last_name="User",
            phone="9876543210",
        )

        self.client.force_authenticate(
            user=self.user
        )

        self.url = "/api/accounts/vehicles/"

    def test_list_vehicles(self):

        response = self.client.get(
            self.url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_create_first_vehicle(self):

        data = {
            "vehicle_type": "car",
            "registration_number": "MH12AB1234",
            "brand": "Hyundai",
            "model": "Creta",
            "color": "White",
        }

        response = self.client.post(
            self.url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        vehicle = Vehicle.objects.get(
            registration_number="MH12AB1234"
        )

        self.assertTrue(
            vehicle.is_default
        )

    def test_second_vehicle_is_not_default(self):

        Vehicle.objects.create(
            user=self.user,
            vehicle_type="car",
            registration_number="MH12AB1234",
            brand="Hyundai",
            model="Creta",
            color="White",
            is_default=True,
        )

        data = {
            "vehicle_type": "bike",
            "registration_number": "MH14CD5678",
            "brand": "Honda",
            "model": "Activa",
            "color": "Black",
        }

        response = self.client.post(
            self.url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        vehicle = Vehicle.objects.get(
            registration_number="MH14CD5678"
        )

        self.assertFalse(
            vehicle.is_default
        )