from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from parking.models import ParkingArea

class ParkingAreaAPITestCase(APITestCase):


    def setUp(self):

        self.parking_owner = User.objects.create_user(
            username="parking_owner",
            email="parkingowner@example.com",
            password="Test@12345",
            first_name="Parking",
            last_name="Owner",
            phone="9876543210",
            role="parking_owner",
        )

        self.other_parking_owner = User.objects.create_user(
            username="other_parking_owner",
            email="otherowner@example.com",
            password="Test@12345",
            first_name="Other",
            last_name="Owner",
            phone="9123456789",
            role="parking_owner",
        )

        self.vehicle_owner = User.objects.create_user(
            username="vehicle_owner",
            email="vehicleowner@example.com",
            password="Test@12345",
            first_name="Vehicle",
            last_name="Owner",
            phone="8765432109",
            role="vehicle_owner",
        )

        self.client.force_authenticate(
            user=self.parking_owner
        )

        self.list_url = reverse(
            "parking-area-list-create"
        )

    def detail_url(self, parking_area):

        return reverse(
            "parking-area-detail",
            kwargs={
                "pk": parking_area.pk
            }
        )

    def create_parking_area(
        self,
        owner=None,
        name="ParkX Parking",
        city="Pune",
    ):

        return ParkingArea.objects.create(
            owner=owner or self.parking_owner,
            name=name,
            address="123 Main Road",
            city=city,
            description="Test parking area",
            latitude=18.520400,
            longitude=73.856700,
            is_active=True,
        )

    # ==================================================
    # LIST PARKING AREAS
    # ==================================================

    def test_list_parking_areas_success(self):

        self.create_parking_area(
            name="Parking Area 1"
        )

        self.create_parking_area(
            name="Parking Area 2",
            city="Mumbai"
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

    def test_list_parking_areas_returns_only_current_owner_areas(self):

        self.create_parking_area(
            name="My Parking"
        )

        self.create_parking_area(
            owner=self.other_parking_owner,
            name="Other Owner Parking"
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
            response.data[0]["name"],
            "My Parking"
        )

    def test_list_parking_areas_ordered_by_newest_first(self):

        first_area = self.create_parking_area(
            name="First Parking"
        )

        second_area = self.create_parking_area(
            name="Second Parking"
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
            second_area.id
        )

        self.assertEqual(
            response.data[1]["id"],
            first_area.id
        )

    # ==================================================
    # CREATE PARKING AREA
    # ==================================================

    def test_parking_owner_can_create_parking_area(self):

        data = {
            "name": "New ParkX Parking",
            "address": "456 MG Road",
            "city": "Pune",
            "description": "New parking area",
            "latitude": 18.520400,
            "longitude": 73.856700,
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
            ParkingArea.objects.count(),
            1
        )

        parking_area = ParkingArea.objects.get(
            name="New ParkX Parking"
        )

        self.assertEqual(
            parking_area.owner,
            self.parking_owner
        )

        self.assertEqual(
            response.data["owner"],
            self.parking_owner.id
        )

    def test_vehicle_owner_cannot_create_parking_area(self):

        self.client.force_authenticate(
            user=self.vehicle_owner
        )

        data = {
            "name": "Vehicle Owner Parking",
            "address": "456 MG Road",
            "city": "Pune",
            "description": "Should not be created",
        }

        response = self.client.post(
            self.list_url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        self.assertEqual(
            response.data["detail"],
            "Only parking owners can create parking areas."
        )

        self.assertEqual(
            ParkingArea.objects.count(),
            0
        )

    def test_create_parking_area_ignores_owner_from_request(self):

        data = {
            "owner": self.other_parking_owner.id,
            "name": "Owner Security Test",
            "address": "789 Main Road",
            "city": "Pune",
            "description": "Owner should be authenticated user",
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

        parking_area = ParkingArea.objects.get(
            name="Owner Security Test"
        )

        self.assertEqual(
            parking_area.owner,
            self.parking_owner
        )

    def test_create_parking_area_invalid_data(self):

        data = {
            "name": "",
            "address": "",
            "city": "",
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
            ParkingArea.objects.count(),
            0
        )

    # ==================================================
    # GET PARKING AREA DETAIL
    # ==================================================

    def test_get_parking_area_detail_success(self):

        parking_area = self.create_parking_area()

        response = self.client.get(
            self.detail_url(parking_area)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data["id"],
            parking_area.id
        )

        self.assertEqual(
            response.data["name"],
            parking_area.name
        )

    def test_vehicle_owner_can_view_parking_area(self):

        parking_area = self.create_parking_area()

        self.client.force_authenticate(
            user=self.vehicle_owner
        )

        response = self.client.get(
            self.detail_url(parking_area)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data["id"],
            parking_area.id
        )

    def test_other_parking_owner_can_view_parking_area(self):

        parking_area = self.create_parking_area(
            owner=self.parking_owner
        )

        self.client.force_authenticate(
            user=self.other_parking_owner
        )

        response = self.client.get(
            self.detail_url(parking_area)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_get_nonexistent_parking_area(self):

        response = self.client.get(
            reverse(
                "parking-area-detail",
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
    # UPDATE PARKING AREA - PUT
    # ==================================================

    def test_owner_can_update_parking_area_with_put(self):

        parking_area = self.create_parking_area()

        data = {
            "name": "Updated Parking",
            "address": "Updated Address",
            "city": "Mumbai",
            "description": "Updated description",
            "latitude": 19.076000,
            "longitude": 72.877700,
            "is_active": False,
        }

        response = self.client.put(
            self.detail_url(parking_area),
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        parking_area.refresh_from_db()

        self.assertEqual(
            parking_area.name,
            "Updated Parking"
        )

        self.assertEqual(
            parking_area.city,
            "Mumbai"
        )

        self.assertFalse(
            parking_area.is_active
        )

    def test_other_owner_cannot_update_parking_area_with_put(self):

        parking_area = self.create_parking_area()

        self.client.force_authenticate(
            user=self.other_parking_owner
        )

        response = self.client.put(
            self.detail_url(parking_area),
            {
                "name": "Unauthorized Update",
                "address": "Changed Address",
                "city": "Mumbai",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        parking_area.refresh_from_db()

        self.assertEqual(
            parking_area.name,
            "ParkX Parking"
        )

    def test_vehicle_owner_cannot_update_parking_area_with_put(self):

        parking_area = self.create_parking_area()

        self.client.force_authenticate(
            user=self.vehicle_owner
        )

        response = self.client.put(
            self.detail_url(parking_area),
            {
                "name": "Unauthorized Update",
                "address": "Changed Address",
                "city": "Mumbai",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    # ==================================================
    # UPDATE PARKING AREA - PATCH
    # ==================================================

    def test_owner_can_patch_parking_area(self):

        parking_area = self.create_parking_area()

        response = self.client.patch(
            self.detail_url(parking_area),
            {
                "name": "Patched Parking",
                "city": "Nashik",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        parking_area.refresh_from_db()

        self.assertEqual(
            parking_area.name,
            "Patched Parking"
        )

        self.assertEqual(
            parking_area.city,
            "Nashik"
        )

    def test_other_owner_cannot_patch_parking_area(self):

        parking_area = self.create_parking_area()

        self.client.force_authenticate(
            user=self.other_parking_owner
        )

        response = self.client.patch(
            self.detail_url(parking_area),
            {
                "name": "Unauthorized Patch"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        parking_area.refresh_from_db()

        self.assertEqual(
            parking_area.name,
            "ParkX Parking"
        )

    def test_vehicle_owner_cannot_patch_parking_area(self):

        parking_area = self.create_parking_area()

        self.client.force_authenticate(
            user=self.vehicle_owner
        )

        response = self.client.patch(
            self.detail_url(parking_area),
            {
                "name": "Unauthorized Patch"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    # ==================================================
    # DELETE PARKING AREA
    # ==================================================

    def test_owner_can_delete_parking_area(self):

        parking_area = self.create_parking_area()

        response = self.client.delete(
            self.detail_url(parking_area)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

        self.assertFalse(
            ParkingArea.objects.filter(
                pk=parking_area.pk
            ).exists()
        )

    def test_other_owner_cannot_delete_parking_area(self):

        parking_area = self.create_parking_area()

        self.client.force_authenticate(
            user=self.other_parking_owner
        )

        response = self.client.delete(
            self.detail_url(parking_area)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        self.assertTrue(
            ParkingArea.objects.filter(
                pk=parking_area.pk
            ).exists()
        )

    def test_vehicle_owner_cannot_delete_parking_area(self):

        parking_area = self.create_parking_area()

        self.client.force_authenticate(
            user=self.vehicle_owner
        )

        response = self.client.delete(
            self.detail_url(parking_area)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        self.assertTrue(
            ParkingArea.objects.filter(
                pk=parking_area.pk
            ).exists()
        )

    def test_delete_nonexistent_parking_area(self):

        response = self.client.delete(
            reverse(
                "parking-area-detail",
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

    def test_unauthenticated_user_cannot_get_parking_area_detail(self):

        parking_area = self.create_parking_area()

        self.client.force_authenticate(
            user=None
        )

        response = self.client.get(
            self.detail_url(parking_area)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_unauthenticated_user_cannot_update_parking_area(self):

        parking_area = self.create_parking_area()

        self.client.force_authenticate(
            user=None
        )

        response = self.client.patch(
            self.detail_url(parking_area),
            {
                "name": "Unauthorized"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_unauthenticated_user_cannot_delete_parking_area(self):

        parking_area = self.create_parking_area()

        self.client.force_authenticate(
            user=None
        )

        response = self.client.delete(
            self.detail_url(parking_area)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    # ==================================================
# PARKING AREA VALIDATION
# ==================================================

    def test_create_parking_area_rejects_blank_name(self):

        response = self.client.post(
            self.list_url,
            {
                "name": "   ",
                "address": "123 Main Road",
                "city": "Pune",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            "name",
            response.data
        )


    def test_create_parking_area_rejects_blank_address(self):

        response = self.client.post(
            self.list_url,
            {
                "name": "ParkX Parking",
                "address": "   ",
                "city": "Pune",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            "address",
            response.data
        )


    def test_create_parking_area_rejects_blank_city(self):

        response = self.client.post(
            self.list_url,
            {
                "name": "ParkX Parking",
                "address": "123 Main Road",
                "city": "   ",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            "city",
            response.data
        )


    def test_create_parking_area_rejects_invalid_latitude(self):

        response = self.client.post(
            self.list_url,
            {
                "name": "ParkX Parking",
                "address": "123 Main Road",
                "city": "Pune",
                "latitude": 91,
                "longitude": 73.856700,
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            "latitude",
            response.data
        )


    def test_create_parking_area_rejects_invalid_longitude(self):

        response = self.client.post(
            self.list_url,
            {
                "name": "ParkX Parking",
                "address": "123 Main Road",
                "city": "Pune",
                "latitude": 18.520400,
                "longitude": 181,
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            "longitude",
            response.data
        )


    def test_create_parking_area_strips_whitespace_from_text_fields(self):

        response = self.client.post(
            self.list_url,
            {
                "name": "  ParkX Parking  ",
                "address": "  123 Main Road  ",
                "city": "  Pune  ",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        parking_area = ParkingArea.objects.get(
            pk=response.data["id"]
        )

        self.assertEqual(
            parking_area.name,
            "ParkX Parking"
        )

        self.assertEqual(
            parking_area.address,
            "123 Main Road"
        )

        self.assertEqual(
            parking_area.city,
            "Pune"
        )