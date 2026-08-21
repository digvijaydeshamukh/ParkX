from rest_framework import serializers
from .models import (
    Vehicle,
)

# Vehicle serializer
class VehicleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Vehicle

        fields = [
            "id",
            "vehicle_type",
            "registration_number",
            "brand",
            "model",
            "color",
            "is_default",
        ]

        read_only_fields = [
            "id",
            "is_default",
        ]

    def validate_registration_number(self, value):

            return value.strip().upper()

# Vehicle Response Serializer
class VehicleResponseSerializer(serializers.Serializer):

    message = serializers.CharField()
    vehicle = VehicleSerializer()
