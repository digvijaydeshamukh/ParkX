from django.conf import settings
from django.db import models


# Parking Area Model
class ParkingArea(models.Model):

    owner = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.PROTECT,
    related_name="parking_areas",
    null=True,
    blank=True,
    )

    name = models.CharField(
        max_length=100,
    )

    address = models.TextField()

    city = models.CharField(
        max_length=100,
    )

    description = models.TextField(
        blank=True,
    )

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return self.name


# Parking Floor Model
class ParkingFloor(models.Model):

    parking_area = models.ForeignKey(
        ParkingArea,
        on_delete=models.CASCADE,
        related_name="floors",
    )

    floor_number = models.IntegerField()

    name = models.CharField(
        max_length=100,
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "parking_area",
                    "floor_number",
                ],
                name="unique_floor_per_parking_area",
            ),
        ]

        ordering = [
            "floor_number",
        ]

    def __str__(self):
        if self.name:
            return f"{self.parking_area.name} - {self.name}"

        if self.floor_number < 0:
            return (
                f"{self.parking_area.name} - "
                f"Basement {abs(self.floor_number)}"
            )

        if self.floor_number == 0:
            return f"{self.parking_area.name} - Ground Floor"

        return (
            f"{self.parking_area.name} - "
            f"Floor {self.floor_number}"
        )