from .models import (
    PendingRegistration,
    Roles,
    User,
    PasswordResetOTP,
    PhoneVerificationOTP,
    ContactChangeOTP,
    ContactChangeType,
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
from .sms import send_sms_otp

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
        
        if User.objects.filter(
            phone=pending_registration.phone,
            phone_verified=True
            ).exists():
            raise ValidationError({
                "phone": ["Phone number already registered."]
            })

        user = User.objects.create(
            username = generate_unique_username(),
            first_name=pending_registration.first_name,
            last_name=pending_registration.last_name,
            email=pending_registration.email,
            phone=pending_registration.phone,
            phone_verified=False,
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

# Resend Otp 
def resend_password_reset_otp(email):
    email = email.lower()

    user = User.objects.filter(
        email__iexact=email
    ).first()

    if not user:
        return None

    existing_otp = PasswordResetOTP.objects.filter(
        user=user
    ).first()

    if existing_otp:
        cooldown_expires_at = (
            existing_otp.otp_created_at
            + timedelta(
                seconds=settings.OTP_RESEND_COOLDOWN_SECONDS
            )
        )

        now = timezone.now()

        if now < cooldown_expires_at:
            remaining_seconds = int(
                (
                    cooldown_expires_at - now
                ).total_seconds()
            ) + 1

            return remaining_seconds

        existing_otp.delete()

    otp = generate_otp()

    otp_hash = make_otp_hash(otp)

    now = timezone.now()

    expires_at = now + timedelta(
        minutes=settings.OTP_EXPIRY_MINUTES
    )

    PasswordResetOTP.objects.create(
        user=user,
        otp_hash=otp_hash,
        otp_created_at=now,
        expires_at=expires_at,
    )

    send_password_reset_otp(
        email=user.email,
        first_name=user.first_name,
        otp=otp,
    )

    return None

def _create_phone_verification_otp(user, phone):
    otp = generate_otp()
    otp_hash = make_otp_hash(otp)

    now = timezone.now()

    expires_at = now + timedelta(
        minutes=settings.OTP_EXPIRY_MINUTES
    )

    PhoneVerificationOTP.objects.create(
        user=user,
        phone=phone,
        otp_hash=otp_hash,
        otp_created_at=now,
        expires_at=expires_at,
    )

    send_sms_otp(
        phone=phone,
        otp=otp,
    )

def send_phone_verification_otp_service(user):
    if not user.phone:
        raise ValidationError({
            "phone": [
                "No phone number is associated with this account."
            ]
        })

    if user.phone_verified:
        raise ValidationError({
            "phone": [
                "Phone number is already verified."
            ]
        })

    PhoneVerificationOTP.objects.filter(
        user=user
    ).delete()

    _create_phone_verification_otp(
        user=user,
        phone=user.phone
    )

def resend_phone_verification_otp(user):

    if not user.phone:
        raise ValidationError({
            "phone": [
                "No phone number is associated with this account."
            ]
        })

    if user.phone_verified:
        raise ValidationError({
            "phone": [
                "Phone number is already verified."
            ]
        })

    existing_otp = PhoneVerificationOTP.objects.filter(
        user=user
    ).first()

    if existing_otp:
        cooldown_expires_at = (
            existing_otp.otp_created_at
            + timedelta(
                seconds=settings.OTP_RESEND_COOLDOWN_SECONDS
            )
        )

        now = timezone.now()

        if now < cooldown_expires_at:
            remaining_seconds = int(
                (
                    cooldown_expires_at - now
                ).total_seconds()
            ) + 1

            return remaining_seconds

        existing_otp.delete()

    _create_phone_verification_otp(
        user=user,
        phone=user.phone
    )

    return None

def verify_phone_otp(user, otp):
    """
    Verify the phone verification OTP for the authenticated user.
    """

    if not user.phone:
        raise ValidationError({
            "phone": [
                "No phone number is associated with this account."
            ]
        })

    if user.phone_verified:
        raise ValidationError({
            "phone": [
                "Phone number is already verified."
            ]
        })

    phone_otp = PhoneVerificationOTP.objects.filter(
        user=user
    ).first()

    if not phone_otp:
        raise ValidationError({
            "otp": [
                "No verification OTP found."
            ]
        })

    # Make sure the OTP belongs to the user's current phone.
    if phone_otp.phone != user.phone:
        phone_otp.delete()

        raise ValidationError({
            "otp": [
                "Invalid verification request."
            ]
        })

    # Check OTP expiration.
    if timezone.now() >= phone_otp.expires_at:
        phone_otp.delete()

        raise ValidationError({
            "otp": [
                "OTP has expired."
            ]
        })

    # Verify hashed OTP.
    if not verify_otp_hash(
        otp,
        phone_otp.otp_hash
    ):
        raise ValidationError({
            "otp": [
                "Invalid OTP."
            ]
        })

    # Prevent two verified users from owning the same phone.
    if User.objects.filter(
        phone=user.phone,
        phone_verified=True
    ).exclude(
        id=user.id
    ).exists():
        phone_otp.delete()

        raise ValidationError({
            "phone": [
                "Phone number is already registered."
            ]
        })

    # Mark phone as verified.
    user.phone_verified = True

    user.save(
        update_fields=[
            "phone_verified",
            "updated_at"
        ]
    )

    # OTP is single-use.
    phone_otp.delete()
    
    return user

# def request_phone_number_change(user, new_phone):
#     """
#     Starts the phone number change process.

#     The new phone number is stored in PhoneVerificationOTP
#     and is not written to User until OTP verification succeeds.
#     """

#     if not new_phone:
#         raise ValidationError({
#             "phone": [
#                 "Phone number is required."
#             ]
#         })

#     # If the submitted number is the current number
#     if user.phone == new_phone:

#         if user.phone_verified:
#             raise ValidationError({
#                 "phone": [
#                     "This is already your verified phone number."
#                 ]
#             })

#         raise ValidationError({
#             "phone": [
#                 "This is already your current phone number."
#             ]
#         })

#     # Prevent another verified user from owning the phone number.
#     if User.objects.filter(
#         phone=new_phone,
#         phone_verified=True
#     ).exclude(
#         id=user.id
#     ).exists():

#         raise ValidationError({
#             "phone": [
#                 "Phone number already registered."
#             ]
#         })

#     # Remove any existing phone verification OTP.
#     PhoneVerificationOTP.objects.filter(
#         user=user
#     ).delete()

#     # Create OTP for the NEW phone.
#     _create_phone_verification_otp(
#         user=user,
#         phone=new_phone
#     )

# def verify_phone_number_change(user, otp):
#     """
#     Verifies the OTP for a phone number change.

#     The new phone number is applied to the user only
#     after successful OTP verification.
#     """

#     phone_otp = PhoneVerificationOTP.objects.filter(
#         user=user
#     ).first()

#     if not phone_otp:
#         raise ValidationError({
#             "otp": [
#                 "No phone change verification OTP found."
#             ]
#         })

#     # Check OTP expiration.
#     if timezone.now() >= phone_otp.expires_at:

#         phone_otp.delete()

#         raise ValidationError({
#             "otp": [
#                 "OTP has expired."
#             ]
#         })

#     # Verify hashed OTP.
#     if not verify_otp_hash(
#         otp,
#         phone_otp.otp_hash
#     ):
#         raise ValidationError({
#             "otp": [
#                 "Invalid OTP."
#             ]
#         })

#     new_phone = phone_otp.phone

#     # Make sure nobody verified this number while
#     # the OTP was pending.
#     if User.objects.filter(
#         phone=new_phone,
#         phone_verified=True
#     ).exclude(
#         id=user.id
#     ).exists():

#         phone_otp.delete()

#         raise ValidationError({
#             "phone": [
#                 "Phone number already registered."
#             ]
#         })

    # # Apply the new phone only after successful OTP verification.
    # user.phone = new_phone
    # user.phone_verified = True

    # user.save(
    #     update_fields=[
    #         "phone",
    #         "phone_verified",
    #         "updated_at"
    #     ]
    # )

    # # OTP is single-use.
    # phone_otp.delete()

    # return user

def _create_contact_change_otp(user, contact_type, new_contact):
    """
    Generates, hashes, stores, and sends an OTP for a contact change.
    """

    otp = generate_otp()
    otp_hash = make_otp_hash(otp)

    now = timezone.now()

    expires_at = now + timedelta(
        minutes=settings.OTP_EXPIRY_MINUTES
    )

    ContactChangeOTP.objects.create(
        user=user,
        contact_type=contact_type,
        new_contact=new_contact,
        otp_hash=otp_hash,
        otp_created_at=now,
        expires_at=expires_at,
    )

    if contact_type == "email":
        send_registration_otp(
            email=new_contact,
            first_name=user.first_name,
            otp=otp,
        )

    elif contact_type == "phone":
        send_sms_otp(
            phone=new_contact,
            otp=otp,
        )


def request_contact_change(user, contact_type, new_contact):
    """
    Starts the contact change process.

    The new email/phone is stored only in ContactChangeOTP.
    The User record is not changed until OTP verification succeeds.
    """

    # Remove any existing contact-change OTP.
    ContactChangeOTP.objects.filter(
        user=user
    ).delete()

    _create_contact_change_otp(
        user=user,
        contact_type=contact_type,
        new_contact=new_contact,
    )


def verify_contact_change(user, otp):
    """
    Verifies the contact-change OTP and updates the user's
    email or phone only after successful OTP verification.
    """

    contact_otp = ContactChangeOTP.objects.filter(
        user=user
    ).first()

    if not contact_otp:
        raise ValidationError({
            "otp": [
                "No contact change verification OTP found."
            ]
        })

    # Check OTP expiration.
    if timezone.now() >= contact_otp.expires_at:

        contact_otp.delete()

        raise ValidationError({
            "otp": [
                "OTP has expired."
            ]
        })

    # Verify the hashed OTP.
    if not verify_otp_hash(
        otp,
        contact_otp.otp_hash
    ):
        raise ValidationError({
            "otp": [
                "Invalid OTP."
            ]
        })

    contact_type = contact_otp.contact_type
    new_contact = contact_otp.new_contact

    # Check again for duplicate contact.
    # Another user could have registered this contact
    # while the OTP was pending.

    if contact_type == ContactChangeType.EMAIL:

        if User.objects.filter(
            email__iexact=new_contact
        ).exclude(
            id=user.id
        ).exists():

            contact_otp.delete()

            raise ValidationError({
                "new_contact": [
                    "Email is already registered."
                ]
            })

        user.email = new_contact

        user.save(
            update_fields=[
                "email",
                "updated_at",
            ]
        )

    elif contact_type == ContactChangeType.PHONE:

        if User.objects.filter(
            phone=new_contact,
            phone_verified=True
        ).exclude(
            id=user.id
        ).exists():

            contact_otp.delete()

            raise ValidationError({
                "new_contact": [
                    "Phone number is already registered."
                ]
            })

        user.phone = new_contact
        user.phone_verified = True

        user.save(
            update_fields=[
                "phone",
                "phone_verified",
                "updated_at",
            ]
        )

    else:

        contact_otp.delete()

        raise ValidationError({
            "contact_type": [
                "Invalid contact type."
            ]
        })

    # OTP is single-use.
    contact_otp.delete()

    return user