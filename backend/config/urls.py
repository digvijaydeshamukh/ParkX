from django.contrib import admin
from django.urls import path,include

from django.conf import settings
from django.conf.urls.static import static

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Accounts
    path("accounts/",include("accounts.urls.pages_urls")),
    path("api/accounts/", include("accounts.urls.api_urls")),

    # Vehicle
    path("vehicle/",include("vehicles.urls.pages_urls")),
    path("api/vehicles/",include("vehicles.urls.api_urls")),

    # Parking
    path("parking/",include("parking.urls.page_urls")),
    path("api/parking/",include("parking.urls.api_urls")),
    

     # OpenAPI Schema
    path(
        "api/schema/",
        SpectacularAPIView.as_view(),
        name="schema",
    ),

    # Swagger UI
    path(
        "swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),

    # ReDoc UI
    path(
        "redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
