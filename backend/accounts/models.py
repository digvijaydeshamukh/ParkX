from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

# Create your models here.
class Roles(models.TextChoices):
    VEHICLE_OWNER = "vehicle_owner", "Vehicle Owner"
    PARKING_OWNER = "parking_owner", "Parking Owner"


#User Model
class User(AbstractUser):
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

def get_expiry_time():
    return timezone.now() + timedelta(days=settings.PENDING_REGISTRATION_EXPIRY_DAYS)

#Pending Registratin Model
class PendingRegistration(models.Model):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)

    username = models.CharField(
         max_length=150,
         unique=True,
         db_index=True
    )

    email = models.EmailField(unique=True,db_index=True)

    phone = models.CharField(max_length=15, unique=True)

    password = models.CharField(max_length=255)

    role = models.CharField(
         max_length=20,
         choices=Roles.choices,
         default=Roles.VEHICLE_OWNER
    )

    otp = models.CharField(max_length=255)

    otp_created_at = models.DateTimeField(default=timezone.now)

    created_at = models.DateTimeField(auto_now_add=True)

    expires_at = models.DateTimeField(default=get_expiry_time)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
         return self.username
