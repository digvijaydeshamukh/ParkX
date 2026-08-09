from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.views import TokenObtainPairView


from .serializers import (
    RegisterSerializer,
    RegisterResponseSerializer,
    VerifyOTPSerializer,
    VerifyOTPResponseSerializer,
    LoginSerializer,
    LoginResponseSerializer,
    ForgotPasswordSerializer,
    ForgotPasswordResponseSerializer,
    VerifyResetOTPSerializer,
    VerifyResetOTPResponseSerializer,
    ResetPasswordSerializer,
    ResetPasswordResponseSerializer,
)
from .services import (
    register_user,
    verify_registration_otp,
    forgot_password,
    verify_password_reset_otp,
    reset_password,
)

# API views

class RegisterView(APIView):
    @extend_schema(
        tags=["Accounts"],
        summary="Register a new user",
        description="Creates or updates a pending registration and sends an OTP to the user's email.",
        request=RegisterSerializer,
        responses={
            201: RegisterResponseSerializer,
        },
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        register_user(serializer.validated_data)

        return Response(
            {
                "message": "OTP sent successfully.",
                "email" : serializer.validated_data['email'],
            },
            status = status.HTTP_201_CREATED
        )

class VerifyOTPView(APIView):

    @extend_schema(
        tags=["Accounts"],
        summary="Verify registration OTP",
        description="Verifies OTP and creates the user account.",
        request=VerifyOTPSerializer,
        responses={
            201: VerifyOTPResponseSerializer,
        },
    )
    def post(self, request):

        serializer = VerifyOTPSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        verify_registration_otp(
            serializer.validated_data
        )

        return Response(
            {
                "message": "Registration successful."
            },
            status=status.HTTP_201_CREATED
        )

# Page views
def register_page(request):
    return render(request, "register.html")


#Home / landing page views
def home_page(request):
    return render(request, "home.html")

#Login page
def login_page(request):
    return render(request, "login.html")

@extend_schema(
    tags=["Accounts"],
    summary="Login user",
    description="Authenticates the user using email and password and returns JWT access and refresh tokens.",
    request=LoginSerializer,
    responses={
        200: LoginResponseSerializer,
    },
)
# Login view
class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer

# Forgot password view
class ForgotPasswordAPIView(APIView):
    @extend_schema(
    tags=["Accounts"],
    summary="Request password reset OTP",
    description="Sends a password reset OTP to the user's email if an account exists.",
    request=ForgotPasswordSerializer,
    responses={
        200: ForgotPasswordResponseSerializer,
    },
)
    def post(self, request):

        serializer = ForgotPasswordSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        forgot_password(
            serializer.validated_data["email"]
        )

        return Response(
            {
                "message": (
                    "If an account exists with this email, "
                    "a password reset OTP has been sent."
                )
            },
            status=status.HTTP_200_OK,
        )

# Verify forgot Password
@extend_schema(
    tags=["Accounts"],
    summary="Verify password reset OTP",
    description=(
        "Verifies the password reset OTP and returns a short-lived "
        "reset token when the OTP is valid."
    ),
    request=VerifyResetOTPSerializer,
    responses={
        200: VerifyResetOTPResponseSerializer,
    },
)
class VerifyResetOTPAPIView(APIView):

    def post(self, request):

        serializer = VerifyResetOTPSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        reset_token = verify_password_reset_otp(
            email=serializer.validated_data["email"],
            otp=serializer.validated_data["otp"],
        )

        return Response(
            {
                "message": "OTP verified successfully.",
                "reset_token": reset_token,
            },
            status=status.HTTP_200_OK,
        )

# Reset Password view
@extend_schema(
    tags=["Accounts"],
    summary="Reset user password",
    description=(
        "Resets the user's password using the short-lived "
        "password reset token received after OTP verification."
    ),
    request=ResetPasswordSerializer,
    responses={
        200: ResetPasswordResponseSerializer,
    },
)
class ResetPasswordAPIView(APIView):

    def post(self, request):

        serializer = ResetPasswordSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        reset_password(
            reset_token=serializer.validated_data["reset_token"],
            password=serializer.validated_data["password"],
        )

        return Response(
            {
                "message": "Password reset successfully."
            },
            status=status.HTTP_200_OK,
        )