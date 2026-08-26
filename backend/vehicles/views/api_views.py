from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema,OpenApiResponse
from rest_framework.response import Response
from rest_framework import status


from ..models import (
    Vehicle,
)

from ..serializers import (
    # Vehical Serializers
    VehicleSerializer,
    VehicleResponseSerializer,
)


# Vehicle list Api View 
class VehicleListCreateView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Vehicles"],
        summary="List user's vehicles",
        description=(
            "Returns all vehicles registered by the currently "
            "authenticated user. The default vehicle is returned first."
        ),
        responses={
            200: VehicleSerializer(many=True),
        },
    )
    def get(self, request):

        vehicles = Vehicle.objects.filter(
            user=request.user
        ).order_by("-is_default", "-created_at")

        serializer = VehicleSerializer(
            vehicles,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @extend_schema(
        tags=["Vehicles"],
        summary="Add a vehicle",
        description=(
            "Adds a new vehicle for the currently authenticated user. "
            "The user is automatically assigned to the vehicle."
        ),
        request=VehicleSerializer,
        responses={
            201: VehicleResponseSerializer,
            400: OpenApiResponse(
                description="Invalid vehicle data."
            ),
        },
    )
    def post(self, request):

        serializer = VehicleSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        has_vehicle = Vehicle.objects.filter(
            user=request.user
        ).exists()

        vehicle = serializer.save(
            user=request.user,
            is_default=not has_vehicle
        )

        return Response(
            {
                "message": "Vehicle added successfully.",
                "vehicle": VehicleSerializer(vehicle).data
            },
            status=status.HTTP_201_CREATED
        )

# Vehicle details api view
class VehicleDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, request, pk):

        try:
            return Vehicle.objects.get(
                pk=pk,
                user=request.user
            )

        except Vehicle.DoesNotExist:
            return None

    @extend_schema(
        tags=["Vehicles"],
        summary="Get vehicle details",
        description=(
            "Returns the details of a vehicle belonging to the "
            "currently authenticated user."
        ),
        responses={
            200: VehicleSerializer,
            404: OpenApiResponse(
                description="Vehicle not found."
            ),
        },
    )
    def get(self, request, pk):

        vehicle = self.get_object(
            request,
            pk
        )

        if vehicle is None:

            return Response(
                {
                    "detail": "Vehicle not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = VehicleSerializer(
            vehicle
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @extend_schema(
        tags=["Vehicles"],
        summary="Update vehicle",
        description=(
            "Updates the details of a vehicle belonging to the "
            "currently authenticated user."
        ),
        request=VehicleSerializer,
        responses={
            200: VehicleResponseSerializer,
            400: OpenApiResponse(
                description="Invalid vehicle data."
            ),
            404: OpenApiResponse(
                description="Vehicle not found."
            ),
        },
    )
    def patch(self, request, pk):

        vehicle = self.get_object(
            request,
            pk
        )

        if vehicle is None:

            return Response(
                {
                    "detail": "Vehicle not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = VehicleSerializer(
            vehicle,
            data=request.data,
            partial=True
        )

        serializer.is_valid(
            raise_exception=True
        )

        vehicle = serializer.save()

        return Response(
            {
                "message": "Vehicle updated successfully.",
                "vehicle": VehicleSerializer(vehicle).data
            },
            status=status.HTTP_200_OK
        )

    @extend_schema(
        tags=["Vehicles"],
        summary="Delete vehicle",
        description=(
            "Deletes a vehicle belonging to the currently "
            "authenticated user."
        ),
        responses={
            200: OpenApiResponse(
                description="Vehicle deleted successfully."
            ),
            404: OpenApiResponse(
                description="Vehicle not found."
            ),
        },
    )
    def delete(self, request, pk):

        vehicle = self.get_object(
            request,
            pk
        )

        if vehicle is None:

            return Response(
                {
                    "detail": "Vehicle not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        was_default = vehicle.is_default

        vehicle.delete()

        if was_default:

            next_vehicle = (
                Vehicle.objects
                .filter(user=request.user)
                .order_by("-created_at")
                .first()
            )

            if next_vehicle:

                next_vehicle.is_default = True

                next_vehicle.save(
                    update_fields=[
                        "is_default",
                        "updated_at"
                    ]
                )

        return Response(
            {
                "message": "Vehicle deleted successfully."
            },
            status=status.HTTP_200_OK
        )
# Set default api view
class SetDefaultVehicleView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Vehicles"],
        summary="Set default vehicle",
        description=(
            "Sets a vehicle belonging to the currently authenticated "
            "user as the default vehicle. Any previously selected "
            "default vehicle is automatically unset."
        ),
        responses={
            200: VehicleResponseSerializer,
            404: OpenApiResponse(
                description="Vehicle not found."
            ),
        },
    )
    def post(self, request, pk):

        try:

            vehicle = Vehicle.objects.get(
                pk=pk,
                user=request.user
            )

        except Vehicle.DoesNotExist:

            return Response(
                {
                    "detail": "Vehicle not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        Vehicle.objects.filter(
            user=request.user,
            is_default=True
        ).update(
            is_default=False
        )

        vehicle.is_default = True

        vehicle.save(
            update_fields=[
                "is_default",
                "updated_at"
            ]
        )

        return Response(
            {
                "message": "Default vehicle updated successfully.",
                "vehicle": VehicleSerializer(vehicle).data
            },
            status=status.HTTP_200_OK
        )
