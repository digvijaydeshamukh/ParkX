from django.urls import path

from ..views.pages_views import (
    register_page,
)
urlpatterns = [
    # Register Page
    path("register/", register_page, name="register-page"),
]