from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from ..views.api_views import (
    # Registration
    RegisterView,
    VerifyOTPView,

    # Login
    LoginView,

    # Forgot Password
    ForgotPasswordAPIView,
    VerifyResetOTPAPIView,
    ResetPasswordAPIView,
    ResendResetOTPAPIView,

    # Profile
    ProfileView,

    # Phone Verification
    SendPhoneVerificationOTPView,
    VerifyPhoneOTPView,
    ResendPhoneVerificationOTPView,

    # Old Phone Number Change
    # ChangePhoneNumberView,

    # Contact Change
    ContactChangeView,
    VerifyContactChangeOTPView,
    ResendContactChangeOTPView,

    # Create List Parking Owner
    ParkingOwnerListCreateView,

    # Parking Owner
    PromoteParkingOwnerView,
    DemoteParkingOwnerView,
    DeleteParkingOwnerView,

    # Delete User
    DeleteUserView,

    # Change Password 
    ChangePasswordAPIView
)

urlpatterns = [
    # Registration
    path("register/",RegisterView.as_view(),name = "register",),
    path("verify-otp/",VerifyOTPView.as_view(),name="verify-otp"),

    # Login / JWT
    path("login/",LoginView.as_view(),name="login",),
    path("token/refresh/",TokenRefreshView.as_view(),name="token-refresh",),

    # Forgot Password
    path("forgot-password/",ForgotPasswordAPIView.as_view(),name="forgot-password",),
    path("verify-reset-otp/",VerifyResetOTPAPIView.as_view(),name="verify-reset-otp",),
    path("reset-password/",ResetPasswordAPIView.as_view(),name="reset-password"),
    path( "resend-reset-otp/", ResendResetOTPAPIView.as_view(), name="resend-reset-otp" ),

    # Profile
    path("profile/",ProfileView.as_view(),name="profile"),

    # Phone Verification
    path("phone/send-otp/",SendPhoneVerificationOTPView.as_view(),name="send-phone-verification-otp",),
    path("phone/verify-otp/",VerifyPhoneOTPView.as_view(),name="verify-phone-otp",),
    path("phone/resend-otp/",ResendPhoneVerificationOTPView.as_view(),
    name="resend-phone-verification-otp",),

    path(
        "contact/change/",
        ContactChangeView.as_view(),
        name="contact-change",
    ),

    path(
        "contact/change/verify-otp/",
        VerifyContactChangeOTPView.as_view(),
        name="verify-contact-change-otp",
    ),

    path(
        "contact/change/resend-otp/",
        ResendContactChangeOTPView.as_view(),
        name="resend-contact-change-otp",
    ),

    # Change password
    path(
        "change-password/",
        ChangePasswordAPIView.as_view(),
        name="change-password",
    ),

    # Create List Parking Owner 
    path(
        "admin/parking-owners/",
        ParkingOwnerListCreateView.as_view(),
        name="create-list-parking-owner",
    ),

    # Promote Existing User
    path(
        "admin/users/<int:user_id>/promote-parking-owner/",
        PromoteParkingOwnerView.as_view(),
        name="promote-parking-owner",
    ),

    # Demote Parking owner to vehicle owner
    path(
        "admin/users/<int:user_id>/demote-parking-owner/",
        DemoteParkingOwnerView.as_view(),
        name="demote-parking-owner",
    ),

    # Deletes Parking Owner
    path(
        "admin/parking-owners/<int:user_id>/",
        DeleteParkingOwnerView.as_view(),
        name="delete-parking-owner",
    ),

    # Deletes Any user
    path(
        "admin/users/<int:user_id>/",
        DeleteUserView.as_view(),
        name="delete-user",
    ),

]