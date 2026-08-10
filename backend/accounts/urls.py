from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    VerifyOTPView,
    LoginView,
    ForgotPasswordAPIView,
    VerifyResetOTPAPIView,
    ResetPasswordAPIView,
    ResendResetOTPAPIView,
)

urlpatterns = [
    path("register/",RegisterView.as_view(),name = "register",),
    path("verify-otp/",VerifyOTPView.as_view(),name="verify-otp"),
    path("login/",LoginView.as_view(),name="login",),
    path("token/refresh/",TokenRefreshView.as_view(),name="token-refresh",),
    path("forgot-password/",ForgotPasswordAPIView.as_view(),name="forgot-password",),
    path("verify-reset-otp/",VerifyResetOTPAPIView.as_view(),name="verify-reset-otp",),
    path("reset-password/",ResetPasswordAPIView.as_view(),name="reset-password"),
    path( "resend-reset-otp/", ResendResetOTPAPIView.as_view(), name="resend-reset-otp" ),
]