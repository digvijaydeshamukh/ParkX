from django.contrib import admin
from .models import Vehicle


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "vehicle_type",
        "registration_number",
        "is_default",
        "created_at",
    )
    list_filter = (
        "vehicle_type",
        "is_default",
    )
    search_fields = (
        "registration_number",
        "user__email",
    )