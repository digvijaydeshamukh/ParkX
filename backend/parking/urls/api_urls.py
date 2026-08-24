from django.urls import path

from ..views.api_views import (
    # Parking Area API views
    ParkingAreaListCreateView,
    ParkingAreaDetailView,

    # Parking Floor API views
    ParkingFloorListCreateView,
    ParkingFloorDetailView,
)


urlpatterns = [
    # Parking Area API URLs
    path(
        "areas/",
        ParkingAreaListCreateView.as_view(),
        name="parking-area-list-create",
    ),
    path(
        "areas/<int:pk>/",
        ParkingAreaDetailView.as_view(),
        name="parking-area-detail",
    ),

    # Parking Floor API URLs
    path(
        "areas/<int:area_id>/floors/",
        ParkingFloorListCreateView.as_view(),
        name="parking-floor-list-create",
    ),
    path(
        "areas/<int:area_id>/floors/<int:floor_id>/",
        ParkingFloorDetailView.as_view(),
        name="parking-floor-detail",
    ),
]