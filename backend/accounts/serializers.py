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

    role = serializers.ChoiceField(
        choices=Roles.choices,
        default=Roles.VEHICLE_OWNER
    )


    def validate_email(self,value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email is already registered.")

        return value

    def validate_phone(self,value):
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Phone number already registered.")

        return value