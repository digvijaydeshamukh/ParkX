from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer 
from .models import (
    PendingRegistration,
    User,
    Roles,
    ContactChangeType,
)

from vehicles.models import Vehicle

from .validators import(
    phone_number_validator,
    password_validator,
    person_name_validator
)

class RegisterSerializer(serializers.Serializer):

    first_name = serializers.CharField(
        max_length=150,
        trim_whitespace=True,
        validators = [person_name_validator]
    )

    last_name = serializers.CharField(
        max_length=150,
        trim_whitespace=True,
        validators = [person_name_validator]
    )

    email = serializers.EmailField()

    phone = serializers.CharField(
        max_length=15,
        validators = [phone_number_validator]
    )

    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
        validators = [password_validator]
    )

    confirm_password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )



    def validate_email(self,value):
        value = value.lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email is already registered.")

        return value

    def validate_phone(self,value):
        if User.objects.filter(
            phone=value,
            phone_verified=True
        ).exists():

            raise serializers.ValidationError(
                "Phone number already registered."
            )

        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password": [
                    "Passwords do not match."
                ]
            })

        attrs.pop("confirm_password")
        return attrs

class RegisterResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    email = serializers.EmailField()

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(
        max_length = 6,
        min_length = 6,
        trim_whitespace = True,
        write_only = True,
    )

#Verify OTP
class VerifyOTPResponseSerializer(serializers.Serializer):
    message = serializers.CharField()

#Login
class LoginSerializer(TokenObtainPairSerializer):
    default_error_messages = {
        "no_active_account": "Invalid email or password."
    }

    def validate(self, attrs):
        data = super().validate(attrs)

        data["user"] = {
            "id": self.user.id,
            "username": self.user.username,
            "first_name": self.user.first_name,
            "email": self.user.email,
            "role": self.user.role,
        }

        return data

#Login User Serializer
class LoginUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    first_name = serializers.CharField()
    email = serializers.EmailField()
    role = serializers.CharField()

#Login Response serializer
class LoginResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = LoginUserSerializer()

#Forgot Password serializer
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

#Forgot Password Response serializer
class ForgotPasswordResponseSerializer(serializers.Serializer):
    message = serializers.CharField()

# Verify Reset Otp
class VerifyResetOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(
        min_length=6,
        max_length=6,
        trim_whitespace=True,
        write_only=True,
    )

#Verfy Reset Otp Responce
class VerifyResetOTPResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    reset_token = serializers.CharField()

# Reset Password Serializer
class ResetPasswordSerializer(serializers.Serializer):
    reset_token = serializers.CharField(
        write_only=True
    )

    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
        validators=[password_validator]
    )

    confirm_password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password": [
                    "Passwords do not match."
                ]
            })

        attrs.pop("confirm_password")

        return attrs

# Reset Password Response Serializer
class ResetPasswordResponseSerializer(serializers.Serializer):
    message = serializers.CharField()

#Resend Otp Serializer
class ResendResetOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

# User Profile serializer
class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User

        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "phone",
            "phone_verified",
            "profile_image",
        ]

        read_only_fields = [
            "username",
            "email",
            "phone",
            "phone_verified",
        ]

# User Profile Response serializer
class ProfileUpdateResponseSerializer(serializers.Serializer):

    message = serializers.CharField()

    user = ProfileSerializer()

# Verify Phone OTP
class VerifyPhoneOTPSerializer(serializers.Serializer):

    otp = serializers.CharField(
        min_length=6,
        max_length=6,
        trim_whitespace=True,
        write_only=True,
    )


# Verify Phone Response Serializer
class VerifyPhoneOTPResponseSerializer(serializers.Serializer):

    message = serializers.CharField()
    user = ProfileSerializer()

# Send Phone Verification OTP Response
class SendPhoneVerificationOTPResponseSerializer(serializers.Serializer):

    message = serializers.CharField()

# Resend Phone Verification OTP Response
class ResendPhoneVerificationOTPResponseSerializer(serializers.Serializer):

    message = serializers.CharField()

    remaining_seconds = serializers.IntegerField(
        required=False
    )

# Change Phone Number Serializer
# class ChangePhoneNumberSerializer(serializers.Serializer):

#     phone = serializers.CharField(
#         max_length=15,
#         validators=[phone_number_validator]
#     )

# # Change Phone Number Response Serializer
# class ChangePhoneNumberResponseSerializer(serializers.Serializer):

#     message = serializers.CharField()

# Contact Change Details

# ==============================
# Contact Change Serializers
# ==============================

class ContactChangeRequestSerializer(serializers.Serializer):

    contact_type = serializers.ChoiceField(
        choices=ContactChangeType.choices
    )

    new_contact = serializers.CharField(
        max_length=254,
        trim_whitespace=True
    )

    def validate(self, attrs):

        contact_type = attrs["contact_type"]
        new_contact = attrs["new_contact"].strip()

        # ------------------------------
        # Email Change
        # ------------------------------

        if contact_type == ContactChangeType.EMAIL:

            email = serializers.EmailField().run_validation(
                new_contact
            )

            email = email.lower()

            # Do not allow the user to change
            # to their current email.
            if email == self.context["request"].user.email.lower():
                raise serializers.ValidationError({
                    "new_contact": [
                        "This is already your current email address."
                    ]
                })

            # Prevent duplicate email accounts.
            if User.objects.filter(
                email__iexact=email
            ).exclude(
                id=self.context["request"].user.id
            ).exists():

                raise serializers.ValidationError({
                    "new_contact": [
                        "Email is already registered."
                    ]
                })

            attrs["new_contact"] = email

        # ------------------------------
        # Phone Change
        # ------------------------------

        elif contact_type == ContactChangeType.PHONE:

            phone_number_validator(new_contact)

            # Do not allow the user to change
            # to their current phone number.
            if new_contact == self.context["request"].user.phone:
                raise serializers.ValidationError({
                    "new_contact": [
                        "This is already your current phone number."
                    ]
                })

            # Prevent duplicate verified phone numbers.
            if User.objects.filter(
                phone=new_contact,
                phone_verified=True
            ).exclude(
                id=self.context["request"].user.id
            ).exists():

                raise serializers.ValidationError({
                    "new_contact": [
                        "Phone number is already registered."
                    ]
                })

            attrs["new_contact"] = new_contact

        return attrs


class VerifyContactChangeOTPSerializer(serializers.Serializer):

    otp = serializers.CharField(
        min_length=6,
        max_length=6,
        trim_whitespace=True,
        write_only=True
    )


class ContactChangeResponseSerializer(serializers.Serializer):

    message = serializers.CharField()


class VerifyContactChangeOTPResponseSerializer(serializers.Serializer):

    message = serializers.CharField()

    user = ProfileSerializer()

# Change Password Serializer
class ChangePasswordSerializer(serializers.Serializer):

    current_password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    new_password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
        validators=[password_validator],
    )

    confirm_password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    def validate(self, attrs):

        user = self.context["request"].user

        # Verify current password
        if not user.check_password(
            attrs["current_password"]
        ):
            raise serializers.ValidationError({
                "current_password": [
                    "Current password is incorrect."
                ]
            })

        # New password and confirm password
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password": [
                    "Passwords do not match."
                ]
            })

        # Prevent using the same password
        if user.check_password(
            attrs["new_password"]
        ):
            raise serializers.ValidationError({
                "new_password": [
                    "New password must be different from the current password."
                ]
            })

        attrs.pop("confirm_password")

        return attrs


# Change Password Response Serializer
class ChangePasswordResponseSerializer(serializers.Serializer):

    message = serializers.CharField()

# Create Parking Owner Serializer
class CreateParkingOwnerSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
        validators=[password_validator],
    )

    confirm_password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    class Meta:
        model = User

        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "password",
            "confirm_password",
        ]

    def validate_email(self, value):

        value = value.lower()

        if User.objects.filter(
            email__iexact=value
        ).exists():

            raise serializers.ValidationError(
                "Email is already registered."
            )

        return value

    def validate_phone(self, value):

        if User.objects.filter(
            phone=value,
            phone_verified=True
        ).exists():

            raise serializers.ValidationError(
                "Phone number already registered."
            )

        return value

    def validate(self, attrs):

        if attrs["password"] != attrs["confirm_password"]:

            raise serializers.ValidationError({
                "confirm_password": [
                    "Passwords do not match."
                ]
            })

        attrs.pop("confirm_password")

        return attrs

# Promote User to Parking Owner Serializer
class PromotedUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "phone",
            "role",
        ]

# Promote user to Parking Owner Responce serializer
class PromoteParkingOwnerResponseSerializer(serializers.Serializer):

    message = serializers.CharField()
    user = LoginUserSerializer()

class DemoteParkingOwnerResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    user = LoginUserSerializer()


class DeleteUserResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
 

class ParkingAreaOwnershipDecisionSerializer(serializers.Serializer):

    parking_area_id = serializers.IntegerField()

    action = serializers.ChoiceField(
        choices=[
            ("reassign", "Reassign"),
            ("deactivate", "Deactivate"),
        ]
    )

    new_owner_id = serializers.IntegerField(
        required=False,
        allow_null=True,
    )

    def validate(self, attrs):

        action = attrs["action"]
        new_owner_id = attrs.get("new_owner_id")

        # Reassignment requires a new owner
        if action == "reassign" and not new_owner_id:
            raise serializers.ValidationError({
                "new_owner_id": [
                    "New owner is required when reassigning a parking area."
                ]
            })

        # Deactivation must not contain a new owner
        if action == "deactivate" and new_owner_id:
            raise serializers.ValidationError({
                "new_owner_id": [
                    "New owner must not be provided when deactivating "
                    "a parking area."
                ]
            })

        return attrs

# Resolve Parking Ownership Serializers

class ResolveParkingOwnershipSerializer(serializers.Serializer):
    decisions = ParkingAreaOwnershipDecisionSerializer(
        many=True,
        required=False,
        default=list
    )
    
    def validate_decisions(self, value):

        parking_area_ids = [
            decision["parking_area_id"]
            for decision in value
        ]

        if len(parking_area_ids) != len(set(parking_area_ids)):
            raise serializers.ValidationError(
                "A parking area cannot appear more than once."
            )

        return value


class ResolveParkingOwnershipResponseSerializer(serializers.Serializer):

    message = serializers.CharField()

    demoted = serializers.BooleanField(
        required=False
    )

    deleted = serializers.BooleanField(
        required=False
    )

    parking_areas = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )

class ResolvedParkingAreaSerializer(serializers.Serializer):

    id = serializers.IntegerField()

    name = serializers.CharField()

    action = serializers.CharField()

    new_owner_id = serializers.IntegerField(
        required=False
    )

# Parking Owner Serializer
class ParkingOwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "phone",
            "phone_verified",
            "role",
            "is_active",
        ]


class ParkingOwnerListResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    parking_owners = ParkingOwnerSerializer(many=True)