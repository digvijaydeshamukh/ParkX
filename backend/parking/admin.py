from django.contrib import admin

from .models import ParkingArea


@admin.register(ParkingArea)
class ParkingAreaAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "owner",
        "city",
        "is_active",
        "created_at",
    )

    list_filter = (
        "city",
        "is_active",
    )

    search_fields = (
        "name",
        "city",
        "address",
        "owner__email",
    )