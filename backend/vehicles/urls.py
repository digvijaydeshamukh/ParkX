from django.urls import path
from .views import (
    # Vehicles
    VehicleListCreateView,
    VehicleDetailView,
    SetDefaultVehicleView,
)

urlpatterns = [
 # Vehicles
    path("",VehicleListCreateView.as_view(),name="vehicle-list-create"),
    path("<int:pk>/",VehicleDetailView.as_view(),name="vehicle-detail"),
    path("<int:pk>/set-default/",SetDefaultVehicleView.as_view(),name="vehicle-set-default"),
]