from .models import (
    PendingRegistration,
    Roles,
    User,
)
from .utils import (
    generate_otp,
    make_otp_hash,
    hash_password,
    verify_otp_hash,
    generate_unique_username,
)
from django.utils import timezone
from .email import send_registration_otp
from datetime import timedelta
from django.conf import settings
from rest_framework.exceptions import ValidationError
from django.db import transaction

def get_pending_registration(email):
    """
    Returns the pending registration for the given email.
    Returns None if no pending registration exists.
    """
    return PendingRegistration.objects.filter(email= email).first()


def register_user(validated_data):
    # Register a user by creating or updating a pending registration.
    
    pending_registration = get_pending_registration(validated_data["email"])

    otp = generate_otp()
    otp_hash = make_otp_hash(otp)
    hashed_password = hash_password(
        validated_data["password"]
    )

    pending_registration_data = {
        "first_name" : validated_data["first_name"],
        "last_name" : validated_data["last_name"],
        "email" : validated_data["email"].lower(),
        "phone" : validated_data["phone"],
        "password" : hashed_password,
        "role" : Roles.VEHICLE_OWNER, 
        "otp_hash" : otp_hash,
        "otp_created_at" :timezone.now()
     }

    if pending_registration:
        for field , value in pending_registration_data.items():
            setattr(pending_registration,field,value)

        pending_registration.save()

    else:
        pending_registration = PendingRegistration.objects.create(
            **pending_registration_data
        )

        #send otp email
    send_registration_otp(
    email=validated_data["email"],
    first_name=validated_data["first_name"],
    otp=otp,
    )

    return pending_registration

# Checks OTP expired
def is_otp_expired(pending_registration):

    # Returns True if the OTP has expired.

    expiry_time = (
        pending_registration.otp_created_at
        + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)
    )

    return timezone.now() > expiry_time


def verify_registration_otp(validated_data):
    
    # Verify the OTP and create the user account.
    
    email = validated_data["email"]
    otp = validated_data["otp"]

    pending_registration = get_pending_registration(email)

    if not pending_registration:
        raise ValidationError({
            "email": ["No pending registration found."]
        })

    if timezone.now() > pending_registration.expires_at:
        raise ValidationError({
            "email": ["Registration request has expired."]
        })

    if is_otp_expired(pending_registration):
        raise ValidationError({
            "otp":["otp has expired."]
        })

    if not verify_otp_hash(
        otp,
        pending_registration.otp_hash
    ):
        raise ValidationError({
            "otp": ["Invalid OTP."]
        })

    
    with transaction.atomic():
        if User.objects.filter(email__iexact=pending_registration.email).exists():
                raise ValidationError({
                    "email": ["Email is already registered."]
                })
        
        if User.objects.filter(phone=pending_registration.phone).exists():
            raise ValidationError({
                "phone": ["Phone number already registered."]
            })

        user = User.objects.create(
            username = generate_unique_username(),
            first_name=pending_registration.first_name,
            last_name=pending_registration.last_name,
            email=pending_registration.email,
            phone=pending_registration.phone,
            password=pending_registration.password,
            role=pending_registration.role,
            is_active = True
        )

        pending_registration.delete()

    return user