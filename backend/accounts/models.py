from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    class Roles(models.TextChoices):
        VEHICLE_OWNER = "vehicle_owner", "Vehicle Owner"
        PARKING_OWNER = "parking_owner", "Parking Owner"

    email = models.EmailField(
        unique=True,
        db_index=True
    )

    phone = models.CharField(
        unique=True,
        max_length=15
    )

    profile_image = models.ImageField(
        upload_to="profile_images/",
        blank=True,
        null=True
    )

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.VEHICLE_OWNER
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username
