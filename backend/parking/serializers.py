from rest_framework import serializers

from .models import (
    ParkingArea,
    ParkingFloor,
)


# Parking Area Serializer
class ParkingAreaSerializer(serializers.ModelSerializer):

    owner = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )

    class Meta:
        model = ParkingArea
        fields = [
            "id",
            "owner",
            "name",
            "address",
            "city",
            "description",
            "latitude",
            "longitude",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "owner",
            "created_at",
            "updated_at",
        ]

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Parking area name cannot be blank."
            )

        return value

    def validate_address(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Address cannot be blank."
            )

        return value

    def validate_city(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "City cannot be blank."
            )

        return value

    def validate_latitude(self, value):
        if value is not None and not -90 <= value <= 90:
            raise serializers.ValidationError(
                "Latitude must be between -90 and 90."
            )

        return value

    def validate_longitude(self, value):
        if value is not None and not -180 <= value <= 180:
            raise serializers.ValidationError(
                "Longitude must be between -180 and 180."
            )

        return value


class ParkingAreaCreateSerializer(ParkingAreaSerializer):

    class Meta(ParkingAreaSerializer.Meta):
        fields = [
            "name",
            "address",
            "city",
            "description",
            "latitude",
            "longitude",
            "is_active",
        ]

# Parking area update serializer
class ParkingAreaUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ParkingArea
        fields = [
            "name",
            "address",
            "city",
            "description",
            "latitude",
            "longitude",
            "is_active",
        ]

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Parking area name cannot be blank."
            )

        return value

    def validate_address(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Address cannot be blank."
            )

        return value

    def validate_city(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "City cannot be blank."
            )

        return value

    def validate_latitude(self, value):
        if value is not None and not -90 <= value <= 90:
            raise serializers.ValidationError(
                "Latitude must be between -90 and 90."
            )

        return value

    def validate_longitude(self, value):
        if value is not None and not -180 <= value <= 180:
            raise serializers.ValidationError(
                "Longitude must be between -180 and 180."
            )

        return value

# Parking Floor Serializer
class ParkingFloorSerializer(serializers.ModelSerializer):

    parking_area = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )

    class Meta:
        model = ParkingFloor

        fields = [
            "id",
            "parking_area",
            "floor_number",
            "name",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "parking_area",
            "created_at",
            "updated_at",
        ]

    def validate_floor_number(self, value):

        if value < -5:
            raise serializers.ValidationError(
                "Floor number cannot be less than -5. "
                "A maximum of 5 basement levels is allowed."
            )

        if value > 20:
            raise serializers.ValidationError(
                "Floor number cannot be greater than 20. "
                "A maximum of 20 above-ground floors is allowed."
            )

        return value

    def validate_name(self, value):

        return value.strip()

    def validate(self, attrs):

        parking_area = self.context.get("parking_area")

        if parking_area is None:
            return attrs

        floor_number = attrs.get(
            "floor_number",
            getattr(self.instance, "floor_number", None),
        )

        existing_floor = ParkingFloor.objects.filter(
            parking_area=parking_area,
            floor_number=floor_number,
        )

        if self.instance:
            existing_floor = existing_floor.exclude(
                pk=self.instance.pk
            )

        if existing_floor.exists():
            raise serializers.ValidationError(
                {
                    "floor_number": (
                        "This floor number already exists "
                        "in this parking area."
                    )
                }
            )

        return attrs