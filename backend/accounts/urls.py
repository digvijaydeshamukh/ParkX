from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    VerifyOTPView,
    LoginView,
)

urlpatterns = [
    path("register/",RegisterView.as_view(),name = "register",),
    path("verify-otp/",VerifyOTPView.as_view(),name="verify-otp"),
    path("login/",LoginView.as_view(),name="login",),
    path("token/refresh/",TokenRefreshView.as_view(),name="token-refresh",),
]