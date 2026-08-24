from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from .validators import phone_number_validator,vehicle_registration_validator

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
        max_length=15,
        blank=True,
        null=True,
        validators=[phone_number_validator]
    )

    phone_verified = models.BooleanField(default=False)

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

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):

        old_image = None

        if self.pk:

            try:
                old_user = User.objects.get(
                    pk=self.pk
                )

                old_image = old_user.profile_image

            except User.DoesNotExist:
                pass


        super().save(*args, **kwargs)


        if (
            old_image
            and old_image != self.profile_image
            and old_image.name
        ):

            old_image.delete(
                save=False
            )


    def __str__(self):
        return self.email

def get_expiry_time():
    return timezone.now() + timedelta(days=settings.PENDING_REGISTRATION_EXPIRY_DAYS)

#Pending Registratin Model
class PendingRegistration(models.Model):
    first_name = models.CharField(max_length=150)

    last_name = models.CharField(max_length=150)

    email = models.EmailField(unique=True,db_index=True)

    phone = models.CharField(max_length=15, validators=[phone_number_validator])

    password = models.CharField(max_length=255)

    role = models.CharField(
         max_length=20,
         choices=Roles.choices,
         default=Roles.VEHICLE_OWNER
    )

    otp_hash = models.CharField(max_length=255)

    otp_created_at = models.DateTimeField(default=timezone.now)

    created_at = models.DateTimeField(auto_now_add=True)

    expires_at = models.DateTimeField(default=get_expiry_time)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
         return self.email

# Forgot Password Model
class PasswordResetOTP(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="password_reset_otps"
    )

    otp_hash = models.CharField(max_length=255)

    otp_created_at = models.DateTimeField(default=timezone.now)

    expires_at = models.DateTimeField()

    reset_token_jti = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True
    )

    reset_token_expires_at = models.DateTimeField(
    null=True,
    blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email

# Phone verification
class PhoneVerificationOTP(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="phone_verification_otps"
    )

    phone = models.CharField(
        max_length=15,
        validators=[phone_number_validator]
    )

    otp_hash = models.CharField(
        max_length=255
    )

    otp_created_at = models.DateTimeField(
        default=timezone.now
    )

    expires_at = models.DateTimeField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.user.email} - {self.phone}"

# Change contact details model
class ContactChangeType(models.TextChoices):
    EMAIL = "email", "Email"
    PHONE = "phone", "Phone"


class ContactChangeOTP(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="contact_change_otps"
    )

    contact_type = models.CharField(
        max_length=10,
        choices=ContactChangeType.choices
    )

    new_contact = models.CharField(
        max_length=254
    )

    otp_hash = models.CharField(
        max_length=255
    )

    otp_created_at = models.DateTimeField(
        default=timezone.now
    )

    expires_at = models.DateTimeField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return (
            f"{self.user.email} - "
            f"{self.contact_type} - "
            f"{self.new_contact}"
        )