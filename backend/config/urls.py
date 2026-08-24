from django.contrib import admin
from django.urls import path,include

from django.conf import settings
from django.conf.urls.static import static

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

from accounts.views import ( 
    register_page, 
    home_page,
    login_page,
    forgot_page,
    forgot_reset_password_page,
    verify_otp_page,
    change_password_page,
    dashboard_page,
    profile_page,
    password_reset_page,
    verify_phone_page,
    edit_contact_page,
)

urlpatterns = [

    path('admin/', admin.site.urls),
    path("api/accounts/", include("accounts.urls")),
    path("api/vehicles/",include("vehicles.urls")),

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

     # Register Page
    path("register/", register_page, name="register-page"),
    #Homepage
    path("home/", home_page, name="home-page"),
    #Login
    path("login/", login_page, name="login-page"),
    #Forgot page
    path("forgot-password/", forgot_page, name="forgot-password-page"),
    #Verify otp page
    path("verify-otp/", verify_otp_page, name="verify-otp-page"),
    #Forgot reset password page 
    path("forgot-reset/", forgot_reset_password_page, name="forgot-reset-page"),
    #Reset password page
    path("change-password/", change_password_page, name="change-password-page"),
    #Dashboard page
    path("dashboard/", dashboard_page, name="dashboard-page"),
    #Profile page
    path("profile/", profile_page, name="profile-page"),
    #Password reset page
    path("password_reset/", password_reset_page, name="password-reset-page"),
    #Verify phone page
    path("verify-phone/", verify_phone_page, name="verify-phone-page"),
    #Edit contact page
    path("edit-contact", edit_contact_page, name="edit-contact-page"),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
