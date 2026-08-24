from django.conf import settings
from django.db import models, transaction

from .validators import vehicle_registration_validator


class VehicleType(models.TextChoices):
    CAR = "car", "Car"
    BIKE = "bike", "Bike"


class Vehicle(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="vehicles",
    )

    vehicle_type = models.CharField(
        max_length=10,
        choices=VehicleType.choices,
    )

    registration_number = models.CharField(
        max_length=20,
        unique=True,
        validators=[vehicle_registration_validator],
    )

    brand = models.CharField(
        max_length=50,
        blank=True,
    )

    model = models.CharField(
        max_length=50,
        blank=True,
    )

    color = models.CharField(
        max_length=30,
        blank=True,
    )

    is_default = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def save(self, *args, **kwargs):

        self.registration_number = (
            self.registration_number.strip().upper()
        )

        with transaction.atomic():

            if self.is_default:

                Vehicle.objects.filter(
                    user=self.user,
                    is_default=True,
                ).exclude(
                    pk=self.pk
                ).update(
                    is_default=False
                )

            super().save(*args, **kwargs)