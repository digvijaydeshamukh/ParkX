from .models import PendingRegistration
from django.contrib.auth.hashers import make_password
from .utils import generate_otp,make_otp_hash
from django.utils import timezone
from .email import send_registration_otp

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
    hashed_password = make_password(
        validated_data["password"]
    )

    pending_registration_data = {
        "first_name" : validated_data["first_name"],
        "last_name" : validated_data["last_name"],
        "email" : validated_data["email"],
        "phone" : validated_data["phone"],
        "password" : hashed_password,
        "role" : validated_data["role"], 
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
