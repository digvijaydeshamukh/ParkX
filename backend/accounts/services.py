from .models import (
    PendingRegistration,
    Roles,
    User,
    PasswordResetOTP,
)
from .utils import (
    generate_otp,
    make_otp_hash,
    hash_password,
    verify_otp_hash,
    generate_unique_username,
)
from django.utils import timezone
from .email import send_registration_otp,send_password_reset_otp
from datetime import timedelta
from django.conf import settings
from rest_framework.exceptions import ValidationError
from django.db import transaction
from rest_framework_simplejwt.tokens import UntypedToken,AccessToken
from rest_framework_simplejwt.exceptions import TokenError

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

# Generate and send a password-reset OTP.
def forgot_password(email):
    email = email.lower()

    user = User.objects.filter(
        email__iexact=email
    ).first()

    # Do not reveal whether the email exists.
    if not user:
        return

    # Remove any previous OTP.
    PasswordResetOTP.objects.filter(
        user=user
    ).delete()

    # Generate a new OTP.
    otp = generate_otp()

    # Hash OTP before storing it.
    otp_hash = make_otp_hash(otp)

    now = timezone.now()

    # Calculate OTP expiration.
    expires_at = now + timedelta(
        minutes=settings.OTP_EXPIRY_MINUTES
    )

    # Store OTP information.
    PasswordResetOTP.objects.create(
        user=user,
        otp_hash=otp_hash,
        otp_created_at=now,
        expires_at=expires_at,
    )

    # Send plain OTP only through email.
    send_password_reset_otp(
        email=user.email,
        first_name=user.first_name,
        otp=otp,
    )

def verify_password_reset_otp(email, otp):
    email = email.lower()

    user = User.objects.filter(
        email__iexact=email
    ).first()

    if not user:
        raise ValidationError("Invalid or expired OTP.")

    reset_otp = PasswordResetOTP.objects.filter(
        user=user
    ).first()

    if not reset_otp:
        raise ValidationError("Invalid or expired OTP.")

    # Check OTP expiration
    if timezone.now() >= reset_otp.expires_at:
        reset_otp.delete()
        raise ValidationError("Invalid or expired OTP.")

    # Verify OTP
    if not verify_otp_hash(
        otp,
        reset_otp.otp_hash
    ):
        raise ValidationError("Invalid or expired OTP.")

    # Create password reset token
    reset_token = AccessToken.for_user(user)

    reset_token["token_type"] = "password_reset"

    reset_token.set_exp(
        lifetime=timedelta(minutes=10)
    )

    # Store reset-token information
    reset_otp.reset_token_jti = reset_token["jti"]

    reset_otp.reset_token_expires_at = timezone.now() + timedelta(
        minutes=10
    )

    reset_otp.save(
        update_fields=[
            "reset_token_jti",
            "reset_token_expires_at",
            "updated_at"
        ]
    )

    return str(reset_token)

# Reset Password
def reset_password(reset_token, password):
    try:
        token = UntypedToken(reset_token)
    except TokenError:
        raise ValidationError(
            "Invalid or expired reset token."
        )

    if token.get("token_type") != "password_reset":
        raise ValidationError(
            "Invalid reset token."
        )

    user_id = token.get("user_id")
    jti = token.get("jti")

    reset_otp = PasswordResetOTP.objects.filter(
        user_id=user_id,
        reset_token_jti=jti
    ).first()

    if not reset_otp:
        raise ValidationError(
            "Invalid or expired reset token."
        )

    # Check reset-token expiration
    if (
        reset_otp.reset_token_expires_at is None
        or timezone.now() >= reset_otp.reset_token_expires_at
    ):
        reset_otp.delete()

        raise ValidationError(
            "Invalid or expired reset token."
        )

    user = User.objects.filter(
        id=user_id
    ).first()

    if not user:
        raise ValidationError(
            "Invalid reset token."
        )

    user.set_password(password)

    user.save(
        update_fields=["password"]
    )

    # Make reset token single-use
    reset_otp.delete()