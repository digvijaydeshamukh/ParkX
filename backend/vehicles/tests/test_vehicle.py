from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from vehicles.models import Vehicle


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

        self.other_user = User.objects.create_user(
            username="other_vehicle_user",
            email="othervehicle@example.com",
            password="Test@12345",
            first_name="Other",
            last_name="User",
            phone="9123456789",
        )

        self.client.force_authenticate(
            user=self.user
        )

        self.list_url = reverse(
            "vehicle-list-create"
        )

    def vehicle_detail_url(self, vehicle):

        return reverse(
            "vehicle-detail",
            kwargs={
                "pk": vehicle.pk
            }
        )

    def set_default_url(self, vehicle):

        return reverse(
            "vehicle-set-default",
            kwargs={
                "pk": vehicle.pk
            }
        )

    def create_vehicle(
        self,
        user=None,
        registration_number="MH12AB1234",
        vehicle_type="car",
        is_default=False,
    ):

        return Vehicle.objects.create(
            user=user or self.user,
            vehicle_type=vehicle_type,
            registration_number=registration_number,
            brand="Hyundai",
            model="Creta",
            color="White",
            is_default=is_default,
        )

    # ==================================================
    # LIST VEHICLES
    # ==================================================

    def test_list_vehicles_success(self):

        self.create_vehicle(
            registration_number="MH12AB1234"
        )

        self.create_vehicle(
            registration_number="MH14CD5678",
            vehicle_type="bike"
        )

        response = self.client.get(
            self.list_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data),
            2
        )

    def test_list_vehicles_returns_only_current_users_vehicles(self):

        self.create_vehicle(
            registration_number="MH12AB1234"
        )

        self.create_vehicle(
            user=self.other_user,
            registration_number="MH14CD5678"
        )

        response = self.client.get(
            self.list_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data),
            1
        )

        self.assertEqual(
            response.data[0]["registration_number"],
            "MH12AB1234"
        )

    def test_list_vehicles_default_vehicle_first(self):

        normal_vehicle = self.create_vehicle(
            registration_number="MH12AB1234",
            is_default=False
        )

        default_vehicle = self.create_vehicle(
            registration_number="MH14CD5678",
            vehicle_type="bike",
            is_default=True
        )

        response = self.client.get(
            self.list_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data[0]["id"],
            default_vehicle.id
        )

        self.assertEqual(
            response.data[1]["id"],
            normal_vehicle.id
        )

    # ==================================================
    # CREATE VEHICLE
    # ==================================================

    def test_create_first_vehicle_success(self):

        data = {
            "vehicle_type": "car",
            "registration_number": "MH12AB1234",
            "brand": "Hyundai",
            "model": "Creta",
            "color": "White",
        }

        response = self.client.post(
            self.list_url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            Vehicle.objects.count(),
            1
        )

        vehicle = Vehicle.objects.get(
            registration_number="MH12AB1234"
        )

        self.assertEqual(
            vehicle.user,
            self.user
        )

        self.assertTrue(
            vehicle.is_default
        )

    def test_create_second_vehicle_is_not_default(self):

        self.create_vehicle(
            registration_number="MH12AB1234",
            is_default=True
        )

        data = {
            "vehicle_type": "bike",
            "registration_number": "MH14CD5678",
            "brand": "Honda",
            "model": "Activa",
            "color": "Black",
        }

        response = self.client.post(
            self.list_url,
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

    def test_create_vehicle_assigns_current_user(self):

        data = {
            "vehicle_type": "car",
            "registration_number": "MH12AB1234",
            "brand": "Toyota",
            "model": "Fortuner",
            "color": "Black",
        }

        response = self.client.post(
            self.list_url,
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

        self.assertEqual(
            vehicle.user,
            self.user
        )

    def test_create_duplicate_registration_number(self):

        self.create_vehicle(
            registration_number="MH12AB1234"
        )

        data = {
            "vehicle_type": "car",
            "registration_number": "MH12AB1234",
            "brand": "Honda",
            "model": "City",
            "color": "Red",
        }

        response = self.client.post(
            self.list_url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            Vehicle.objects.filter(
                registration_number="MH12AB1234"
            ).count(),
            1
        )

    def test_create_vehicle_invalid_vehicle_type(self):

        data = {
            "vehicle_type": "truck",
            "registration_number": "MH12AB1234",
            "brand": "Tata",
            "model": "Truck",
            "color": "White",
        }

        response = self.client.post(
            self.list_url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_create_vehicle_invalid_registration_number(self):

        data = {
            "vehicle_type": "car",
            "registration_number": "INVALID",
            "brand": "Hyundai",
            "model": "Creta",
            "color": "White",
        }

        response = self.client.post(
            self.list_url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    # ==================================================
    # GET VEHICLE DETAIL
    # ==================================================

    def test_get_vehicle_detail_success(self):

        vehicle = self.create_vehicle()

        response = self.client.get(
            self.vehicle_detail_url(vehicle)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data["registration_number"],
            vehicle.registration_number
        )

    def test_get_nonexistent_vehicle(self):

        response = self.client.get(
            reverse(
                "vehicle-detail",
                kwargs={
                    "pk": 99999
                }
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

        self.assertEqual(
            response.data["detail"],
            "Vehicle not found."
        )

    def test_user_cannot_get_other_users_vehicle(self):

        vehicle = self.create_vehicle(
            user=self.other_user
        )

        response = self.client.get(
            self.vehicle_detail_url(vehicle)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    # ==================================================
    # UPDATE VEHICLE
    # ==================================================

    def test_update_vehicle_success(self):

        vehicle = self.create_vehicle()

        data = {
            "brand": "Honda",
            "model": "City",
            "color": "Red",
        }

        response = self.client.patch(
            self.vehicle_detail_url(vehicle),
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        vehicle.refresh_from_db()

        self.assertEqual(
            vehicle.brand,
            "Honda"
        )

        self.assertEqual(
            vehicle.model,
            "City"
        )

        self.assertEqual(
            vehicle.color,
            "Red"
        )

    def test_update_vehicle_registration_number(self):

        vehicle = self.create_vehicle()

        data = {
            "registration_number": "MH20XY9999"
        }

        response = self.client.patch(
            self.vehicle_detail_url(vehicle),
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        vehicle.refresh_from_db()

        self.assertEqual(
            vehicle.registration_number,
            "MH20XY9999"
        )

    def test_update_other_users_vehicle(self):

        vehicle = self.create_vehicle(
            user=self.other_user
        )

        response = self.client.patch(
            self.vehicle_detail_url(vehicle),
            {
                "brand": "Changed"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

        vehicle.refresh_from_db()

        self.assertEqual(
            vehicle.brand,
            "Hyundai"
        )

    def test_update_nonexistent_vehicle(self):

        response = self.client.patch(
            reverse(
                "vehicle-detail",
                kwargs={
                    "pk": 99999
                }
            ),
            {
                "brand": "Honda"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    # ==================================================
    # DELETE VEHICLE
    # ==================================================

    def test_delete_vehicle_success(self):

        vehicle = self.create_vehicle()

        response = self.client.delete(
            self.vehicle_detail_url(vehicle)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertFalse(
            Vehicle.objects.filter(
                pk=vehicle.pk
            ).exists()
        )

    def test_delete_non_default_vehicle(self):

        default_vehicle = self.create_vehicle(
            registration_number="MH12AB1234",
            is_default=True
        )

        second_vehicle = self.create_vehicle(
            registration_number="MH14CD5678",
            is_default=False
        )

        response = self.client.delete(
            self.vehicle_detail_url(second_vehicle)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        default_vehicle.refresh_from_db()

        self.assertTrue(
            default_vehicle.is_default
        )

    def test_delete_default_vehicle_assigns_another_default(self):

        default_vehicle = self.create_vehicle(
            registration_number="MH12AB1234",
            is_default=True
        )

        second_vehicle = self.create_vehicle(
            registration_number="MH14CD5678",
            is_default=False
        )

        response = self.client.delete(
            self.vehicle_detail_url(default_vehicle)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        second_vehicle.refresh_from_db()

        self.assertTrue(
            second_vehicle.is_default
        )

    def test_delete_other_users_vehicle(self):

        vehicle = self.create_vehicle(
            user=self.other_user
        )

        response = self.client.delete(
            self.vehicle_detail_url(vehicle)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

        self.assertTrue(
            Vehicle.objects.filter(
                pk=vehicle.pk
            ).exists()
        )

    def test_delete_nonexistent_vehicle(self):

        response = self.client.delete(
            reverse(
                "vehicle-detail",
                kwargs={
                    "pk": 99999
                }
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    # ==================================================
    # SET DEFAULT VEHICLE
    # ==================================================

    def test_set_default_vehicle_success(self):

        first_vehicle = self.create_vehicle(
            registration_number="MH12AB1234",
            is_default=True
        )

        second_vehicle = self.create_vehicle(
            registration_number="MH14CD5678",
            is_default=False
        )

        response = self.client.post(
            self.set_default_url(second_vehicle)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        first_vehicle.refresh_from_db()
        second_vehicle.refresh_from_db()

        self.assertFalse(
            first_vehicle.is_default
        )

        self.assertTrue(
            second_vehicle.is_default
        )

    def test_set_default_vehicle_when_already_default(self):

        vehicle = self.create_vehicle(
            is_default=True
        )

        response = self.client.post(
            self.set_default_url(vehicle)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        vehicle.refresh_from_db()

        self.assertTrue(
            vehicle.is_default
        )

    def test_set_default_other_users_vehicle(self):

        vehicle = self.create_vehicle(
            user=self.other_user
        )

        response = self.client.post(
            self.set_default_url(vehicle)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

        vehicle.refresh_from_db()

        self.assertFalse(
            vehicle.is_default
        )

    def test_set_default_nonexistent_vehicle(self):

        response = self.client.post(
            reverse(
                "vehicle-set-default",
                kwargs={
                    "pk": 99999
                }
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    # ==================================================
    # AUTHENTICATION
    # ==================================================

    def test_unauthenticated_user_cannot_list_vehicles(self):

        self.client.force_authenticate(
            user=None
        )

        response = self.client.get(
            self.list_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_unauthenticated_user_cannot_create_vehicle(self):

        self.client.force_authenticate(
            user=None
        )

        response = self.client.post(
            self.list_url,
            {
                "vehicle_type": "car",
                "registration_number": "MH12AB1234",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_unauthenticated_user_cannot_access_vehicle_detail(self):

        vehicle = self.create_vehicle()

        self.client.force_authenticate(
            user=None
        )

        response = self.client.get(
            self.vehicle_detail_url(vehicle)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_unauthenticated_user_cannot_delete_vehicle(self):

        vehicle = self.create_vehicle()

        self.client.force_authenticate(
            user=None
        )

        response = self.client.delete(
            self.vehicle_detail_url(vehicle)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_unauthenticated_user_cannot_set_default_vehicle(self):

        vehicle = self.create_vehicle()

        self.client.force_authenticate(
            user=None
        )

        response = self.client.post(
            self.set_default_url(vehicle)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )