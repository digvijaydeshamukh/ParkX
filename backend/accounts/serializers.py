from rest_framework import serializers
from .models import PendingRegistration,User,Roles
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
            phone=value
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

class VerifyOTPResponseSerializer(serializers.Serializer):
    message = serializers.CharField()