from django.contrib import admin
from django.urls import path,include

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
    verify_otp_page,
    reset_password_page,
    dashboard_page,
    profile_page,
    password_reset_page,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/accounts/", include("accounts.urls")),

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
    #Reset password page
    path("reset-password/", reset_password_page, name="reset-password-page"),
    #Dashboard page
    path("dashboard/", dashboard_page, name="dashboard-page"),
    #Profile page
    path("profile/", profile_page, name="profile-page"),
    #Password reset page
    path("password_reset/", password_reset_page, name="password-reset-page"),
]
