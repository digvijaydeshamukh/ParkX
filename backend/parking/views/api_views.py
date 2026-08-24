from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema

from ..models import (
    ParkingArea,
    ParkingFloor,
)

from ..serializers import (
    ParkingAreaSerializer,
    ParkingFloorSerializer,
)


def is_parking_owner(user):
    return user.role == "parking_owner"


class ParkingAreaListCreateView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Parking Areas"],
        summary="List parking owner's areas",
        description=(
            "Returns all parking areas owned by the currently "
            "authenticated parking owner."
        ),
        responses={
            200: ParkingAreaSerializer(many=True),
        },
    )
    def get(self, request):

        parking_areas = ParkingArea.objects.filter(
            owner=request.user
        ).order_by("-created_at")

        serializer = ParkingAreaSerializer(
            parking_areas,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["Parking Areas"],
        summary="Create parking area",
        description=(
            "Creates a new parking area for the currently "
            "authenticated parking owner."
        ),
        request=ParkingAreaSerializer,
        responses={
            201: ParkingAreaSerializer,
            403: {
                "description": (
                    "Only parking owners can create parking areas."
                )
            },
        },
    )
    def post(self, request):

        if not is_parking_owner(request.user):
            return Response(
                {
                    "detail": (
                        "Only parking owners can create parking areas."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ParkingAreaSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        parking_area = serializer.save(
            owner=request.user,
        )

        return Response(
            ParkingAreaSerializer(parking_area).data,
            status=status.HTTP_201_CREATED,
        )


class ParkingAreaDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):

        return get_object_or_404(
            ParkingArea,
            pk=pk,
        )

    @extend_schema(
        tags=["Parking Areas"],
        summary="Get parking area details",
        description=(
            "Returns the details of a parking area. "
            "The user must be authenticated."
        ),
        responses={
            200: ParkingAreaSerializer,
            404: {
                "description": "Parking area not found."
            },
        },
    )
    def get(self, request, pk):

        parking_area = self.get_object(pk)

        serializer = ParkingAreaSerializer(
            parking_area,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["Parking Areas"],
        summary="Update parking area",
        description=(
            "Updates a parking area owned by the currently "
            "authenticated parking owner."
        ),
        request=ParkingAreaSerializer,
        responses={
            200: ParkingAreaSerializer,
            403: {
                "description": (
                    "Only the owner can update the parking area."
                )
            },
            404: {
                "description": "Parking area not found."
            },
        },
    )
    def put(self, request, pk):

        if not is_parking_owner(request.user):
            return Response(
                {
                    "detail": (
                        "Only parking owners can update "
                        "parking areas."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        parking_area = self.get_object(pk)

        if parking_area.owner_id != request.user.id:
            return Response(
                {
                    "detail": (
                        "You cannot update another owner's "
                        "parking area."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ParkingAreaSerializer(
            parking_area,
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["Parking Areas"],
        summary="Partially update parking area",
        description=(
            "Partially updates a parking area owned by the "
            "currently authenticated parking owner."
        ),
        request=ParkingAreaSerializer,
        responses={
            200: ParkingAreaSerializer,
            403: {
                "description": (
                    "Only the owner can update the parking area."
                )
            },
            404: {
                "description": "Parking area not found."
            },
        },
    )
    def patch(self, request, pk):

        if not is_parking_owner(request.user):
            return Response(
                {
                    "detail": (
                        "Only parking owners can update "
                        "parking areas."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        parking_area = self.get_object(pk)

        if parking_area.owner_id != request.user.id:
            return Response(
                {
                    "detail": (
                        "You cannot update another owner's "
                        "parking area."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ParkingAreaSerializer(
            parking_area,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["Parking Areas"],
        summary="Delete parking area",
        description=(
            "Deletes a parking area owned by the currently "
            "authenticated parking owner."
        ),
        responses={
            204: {
                "description": "Parking area deleted successfully."
            },
            403: {
                "description": (
                    "Only the owner can delete the parking area."
                )
            },
            404: {
                "description": "Parking area not found."
            },
        },
    )
    def delete(self, request, pk):

        if not is_parking_owner(request.user):
            return Response(
                {
                    "detail": (
                        "Only parking owners can delete "
                        "parking areas."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        parking_area = self.get_object(pk)

        if parking_area.owner_id != request.user.id:
            return Response(
                {
                    "detail": (
                        "You cannot delete another owner's "
                        "parking area."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        parking_area.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )


# ==================================================
# PARKING FLOOR VIEWS
# ==================================================


class ParkingFloorListCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def get_parking_area(self, request, area_id):

        return get_object_or_404(
            ParkingArea,
            pk=area_id,
        )

    @extend_schema(
        tags=["Parking Floors"],
        summary="List parking area floors",
        description=(
            "Returns all floors belonging to a parking area."
        ),
        responses={
            200: ParkingFloorSerializer(many=True),
            404: {
                "description": "Parking area not found."
            },
        },
    )
    def get(self, request, area_id):

        parking_area = self.get_parking_area(
            request,
            area_id,
        )

        floors = ParkingFloor.objects.filter(
            parking_area=parking_area,
        ).order_by(
            "floor_number"
        )

        serializer = ParkingFloorSerializer(
            floors,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["Parking Floors"],
        summary="Create parking floor",
        description=(
            "Creates a new floor inside a parking area. "
            "Only the parking area owner can create floors."
        ),
        request=ParkingFloorSerializer,
        responses={
            201: ParkingFloorSerializer,
            400: {
                "description": "Invalid floor data or duplicate floor."
            },
            403: {
                "description": (
                    "Only the parking area owner can create floors."
                )
            },
            404: {
                "description": "Parking area not found."
            },
        },
    )
    def post(self, request, area_id):

        if not is_parking_owner(request.user):
            return Response(
                {
                    "detail": (
                        "Only parking owners can create "
                        "parking floors."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        parking_area = self.get_parking_area(
            request,
            area_id,
        )

        if parking_area.owner_id != request.user.id:
            return Response(
                {
                    "detail": (
                        "You cannot add floors to another "
                        "owner's parking area."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ParkingFloorSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        floor = serializer.save(
            parking_area=parking_area,
        )

        return Response(
            ParkingFloorSerializer(floor).data,
            status=status.HTTP_201_CREATED,
        )


class ParkingFloorDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get_floor(self, area_id, floor_id):

        return get_object_or_404(
            ParkingFloor,
            pk=floor_id,
            parking_area_id=area_id,
        )

    @extend_schema(
        tags=["Parking Floors"],
        summary="Get parking floor details",
        description=(
            "Returns the details of a floor belonging to "
            "the specified parking area."
        ),
        responses={
            200: ParkingFloorSerializer,
            404: {
                "description": "Parking floor not found."
            },
        },
    )
    def get(self, request, area_id, floor_id):

        floor = self.get_floor(
            area_id,
            floor_id,
        )

        serializer = ParkingFloorSerializer(
            floor,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["Parking Floors"],
        summary="Update parking floor",
        description=(
            "Updates a parking floor. Only the owner of the "
            "parent parking area can update it."
        ),
        request=ParkingFloorSerializer,
        responses={
            200: ParkingFloorSerializer,
            400: {
                "description": "Invalid floor data or duplicate floor."
            },
            403: {
                "description": (
                    "Only the parking area owner can update floors."
                )
            },
            404: {
                "description": "Parking floor not found."
            },
        },
    )
    def put(self, request, area_id, floor_id):

        if not is_parking_owner(request.user):
            return Response(
                {
                    "detail": (
                        "Only parking owners can update "
                        "parking floors."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        floor = self.get_floor(
            area_id,
            floor_id,
        )

        if floor.parking_area.owner_id != request.user.id:
            return Response(
                {
                    "detail": (
                        "You cannot update another owner's "
                        "parking floor."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ParkingFloorSerializer(
            floor,
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["Parking Floors"],
        summary="Partially update parking floor",
        description=(
            "Partially updates a parking floor. Only the owner "
            "of the parent parking area can update it."
        ),
        request=ParkingFloorSerializer,
        responses={
            200: ParkingFloorSerializer,
            400: {
                "description": "Invalid floor data or duplicate floor."
            },
            403: {
                "description": (
                    "Only the parking area owner can update floors."
                )
            },
            404: {
                "description": "Parking floor not found."
            },
        },
    )
    def patch(self, request, area_id, floor_id):

        if not is_parking_owner(request.user):
            return Response(
                {
                    "detail": (
                        "Only parking owners can update "
                        "parking floors."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        floor = self.get_floor(
            area_id,
            floor_id,
        )

        if floor.parking_area.owner_id != request.user.id:
            return Response(
                {
                    "detail": (
                        "You cannot update another owner's "
                        "parking floor."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ParkingFloorSerializer(
            floor,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["Parking Floors"],
        summary="Delete parking floor",
        description=(
            "Deletes a parking floor. Only the owner of the "
            "parent parking area can delete it."
        ),
        responses={
            204: {
                "description": "Parking floor deleted successfully."
            },
            403: {
                "description": (
                    "Only the parking area owner can delete floors."
                )
            },
            404: {
                "description": "Parking floor not found."
            },
        },
    )
    def delete(self, request, area_id, floor_id):

        if not is_parking_owner(request.user):
            return Response(
                {
                    "detail": (
                        "Only parking owners can delete "
                        "parking floors."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        floor = self.get_floor(
            area_id,
            floor_id,
        )

        if floor.parking_area.owner_id != request.user.id:
            return Response(
                {
                    "detail": (
                        "You cannot delete another owner's "
                        "parking floor."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        floor.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )