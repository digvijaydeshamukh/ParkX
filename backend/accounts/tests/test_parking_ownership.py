from django.test import TestCase
from rest_framework.exceptions import ValidationError

from accounts.models import User, Roles
from accounts.services import resolve_parking_ownership
from parking.models import ParkingArea


class ParkingOwnershipResolutionTests(TestCase):

    def setUp(self):

        self.old_owner = User.objects.create_user(
            username="old_owner",
            email="oldowner@test.com",
            password="TestPassword123",
            role=Roles.PARKING_OWNER,
        )

        self.new_owner_1 = User.objects.create_user(
            username="new_owner_1",
            email="newowner1@test.com",
            password="TestPassword123",
            role=Roles.PARKING_OWNER,
        )

        self.new_owner_2 = User.objects.create_user(
            username="new_owner_2",
            email="newowner2@test.com",
            password="TestPassword123",
            role=Roles.PARKING_OWNER,
        )

        self.parking_a = ParkingArea.objects.create(
            owner=self.old_owner,
            name="Parking A",
            address="Address A",
            city="Pune",
        )

        self.parking_b = ParkingArea.objects.create(
            owner=self.old_owner,
            name="Parking B",
            address="Address B",
            city="Pune",
        )

        self.parking_c = ParkingArea.objects.create(
            owner=self.old_owner,
            name="Parking C",
            address="Address C",
            city="Pune",
        )

    def test_reassign_one_area_and_unspecified_areas_become_inactive(self):

        decisions = [
            {
                "parking_area_id": self.parking_a.id,
                "action": "reassign",
                "new_owner_id": self.new_owner_1.id,
            }
        ]

        resolve_parking_ownership(
            user=self.old_owner,
            decisions=decisions,
            operation="demote",
        )

        self.parking_a.refresh_from_db()
        self.parking_b.refresh_from_db()
        self.parking_c.refresh_from_db()
        self.old_owner.refresh_from_db()

        # A was reassigned
        self.assertEqual(
            self.parking_a.owner,
            self.new_owner_1,
        )

        self.assertTrue(
            self.parking_a.is_active
        )

        # B and C were not specified,
        # therefore they become inactive.
        self.assertFalse(
            self.parking_b.is_active
        )

        self.assertFalse(
            self.parking_c.is_active
        )

        # Original owner was demoted.
        self.assertEqual(
            self.old_owner.role,
            Roles.VEHICLE_OWNER,
        )

    def test_reassign_multiple_areas_to_different_owners(self):

        decisions = [
            {
                "parking_area_id": self.parking_a.id,
                "action": "reassign",
                "new_owner_id": self.new_owner_1.id,
            },
            {
                "parking_area_id": self.parking_b.id,
                "action": "reassign",
                "new_owner_id": self.new_owner_2.id,
            },
            {
                "parking_area_id": self.parking_c.id,
                "action": "deactivate",
            },
        ]

        resolve_parking_ownership(
            user=self.old_owner,
            decisions=decisions,
            operation="demote",
        )

        self.parking_a.refresh_from_db()
        self.parking_b.refresh_from_db()
        self.parking_c.refresh_from_db()

        self.assertEqual(
            self.parking_a.owner,
            self.new_owner_1,
        )

        self.assertTrue(
            self.parking_a.is_active
        )

        self.assertEqual(
            self.parking_b.owner,
            self.new_owner_2,
        )

        self.assertTrue(
            self.parking_b.is_active
        )

        self.assertIsNone(
            self.parking_c.owner
        )

        self.assertFalse(
            self.parking_c.is_active
        )

    def test_explicit_deactivation_makes_area_inactive(self):

        decisions = [
            {
                "parking_area_id": self.parking_a.id,
                "action": "deactivate",
            },
        ]

        resolve_parking_ownership(
            user=self.old_owner,
            decisions=decisions,
            operation="demote",
        )

        self.parking_a.refresh_from_db()

        self.assertFalse(
            self.parking_a.is_active
        )

    def test_reassignment_requires_parking_owner(self):

        vehicle_owner = User.objects.create_user(
            username="vehicle_owner",
            email="vehicle@test.com",
            password="TestPassword123",
            role=Roles.VEHICLE_OWNER,
        )

        decisions = [
            {
                "parking_area_id": self.parking_a.id,
                "action": "reassign",
                "new_owner_id": vehicle_owner.id,
            }
        ]

        with self.assertRaises(ValidationError):

            resolve_parking_ownership(
                user=self.old_owner,
                decisions=decisions,
                operation="demote",
            )

    def test_cannot_reassign_to_same_owner(self):

        decisions = [
            {
                "parking_area_id": self.parking_a.id,
                "action": "reassign",
                "new_owner_id": self.old_owner.id,
            }
        ]

        with self.assertRaises(ValidationError):

            resolve_parking_ownership(
                user=self.old_owner,
                decisions=decisions,
                operation="demote",
            )

    def test_invalid_parking_area_is_rejected(self):

        another_owner = User.objects.create_user(
            username="another_owner",
            email="another@test.com",
            password="TestPassword123",
            role=Roles.PARKING_OWNER,
        )

        another_area = ParkingArea.objects.create(
            owner=another_owner,
            name="Another Parking",
            address="Another Address",
            city="Pune",
        )

        decisions = [
            {
                "parking_area_id": another_area.id,
                "action": "reassign",
                "new_owner_id": self.new_owner_1.id,
            }
        ]

        with self.assertRaises(ValidationError):

            resolve_parking_ownership(
                user=self.old_owner,
                decisions=decisions,
                operation="demote",
            )

    def test_delete_owner_after_reassignment(self):

        decisions = [
            {
                "parking_area_id": self.parking_a.id,
                "action": "reassign",
                "new_owner_id": self.new_owner_1.id,
            },
            {
                "parking_area_id": self.parking_b.id,
                "action": "reassign",
                "new_owner_id": self.new_owner_2.id,
            },
            {
                "parking_area_id": self.parking_c.id,
                "action": "deactivate",
            },
        ]

        old_owner_id = self.old_owner.id

        resolve_parking_ownership(
            user=self.old_owner,
            decisions=decisions,
            operation="delete",
        )

        # Original owner must be deleted.
        self.assertFalse(
            User.objects.filter(
                id=old_owner_id
            ).exists()
        )

        # Reassigned areas still exist.
        self.assertTrue(
            ParkingArea.objects.filter(
                id=self.parking_a.id,
                owner=self.new_owner_1,
                is_active=True,
            ).exists()
        )

        self.assertTrue(
            ParkingArea.objects.filter(
                id=self.parking_b.id,
                owner=self.new_owner_2,
                is_active=True,
            ).exists()
        )

        # Deactivated area still exists.
        self.assertTrue(
            ParkingArea.objects.filter(
                id=self.parking_c.id,
                is_active=False,
            ).exists()
        )