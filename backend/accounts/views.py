from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema,OpenApiResponse
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser


from .serializers import (

    # Register Serializer
    RegisterSerializer,
    RegisterResponseSerializer,
    VerifyOTPSerializer,
    VerifyOTPResponseSerializer,

    # Login serializers
    LoginSerializer,
    LoginResponseSerializer,

    # Forgot password Serializers
    ForgotPasswordSerializer,
    ForgotPasswordResponseSerializer,

    # Reset Password Serializers
    VerifyResetOTPSerializer,
    VerifyResetOTPResponseSerializer,
    ResetPasswordSerializer,
    ResetPasswordResponseSerializer,
    ResendResetOTPSerializer,

    # Profile serializers
    ProfileSerializer,
    ProfileUpdateResponseSerializer,

    # Vehical Serializers
    VehicleSerializer,
    VehicleResponseSerializer,

    # Phone OTP serializers
    VerifyPhoneOTPSerializer,
    VerifyPhoneOTPResponseSerializer,
    SendPhoneVerificationOTPResponseSerializer,
    ResendPhoneVerificationOTPResponseSerializer,

    # Change Phone number serializers
    # ChangePhoneNumberSerializer,
    # ChangePhoneNumberResponseSerializer,

    # Contact Change Serializers
    ContactChangeRequestSerializer,
    VerifyContactChangeOTPSerializer,
    ContactChangeResponseSerializer,
    VerifyContactChangeOTPResponseSerializer,

)
from .services import (

    # Registration
    register_user,
    verify_registration_otp,

    # Forgot Password
    forgot_password,
    verify_password_reset_otp,
    reset_password,
    resend_password_reset_otp,

    # Phone Verification
    send_phone_verification_otp_service,
    verify_phone_otp,
    resend_phone_verification_otp,

    # Phone Number Change
    # request_phone_number_change,
    # verify_phone_number_change,

    # Contact Change
    request_contact_change,
    verify_contact_change,
    resend_contact_change_otp,

)

from .models import (
    Vehicle,
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

#Forgot page view
def forgot_page(request):
    return render(request, "forgot_password.html")

#verify otp page view
def verify_otp_page(request):
    return render(request, "verify_otp.html")

#Reset password view
def reset_password_page(request):
    return render(request, "reset_password.html")

#Dashboard view
def dashboard_page(request):
    return render(request, "dashboard.html")


#Resent Otp Api View
class ResendResetOTPAPIView(APIView):

    @extend_schema(
        tags=["Accounts"],
        summary="Resend password reset OTP",
        description=(
            "Resends a password reset OTP to the user's email "
            "if an account exists."
        ),
        request=ResendResetOTPSerializer,
        responses={
            200: ForgotPasswordResponseSerializer,
            429: OpenApiResponse(
                description="OTP resend cooldown active."
            ),
        },
    )
    def post(self, request):

        serializer = ResendResetOTPSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        remaining_seconds = resend_password_reset_otp(
            serializer.validated_data["email"]
        )

        if remaining_seconds is not None:
            return Response(
                {
                    "detail": (
                        "Please wait before requesting "
                        "another OTP."
                    ),
                    "retry_after": remaining_seconds,
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        return Response(
            {
                "message": (
                    "If an account exists with this email, "
                    "a new password reset OTP has been sent."
                )
            },
            status=status.HTTP_200_OK,
        )
    
# Profile view
class ProfileView(APIView):

    permission_classes = [IsAuthenticated]

    parser_classes = [
        MultiPartParser,
        FormParser,
        JSONParser,
    ]
    
    @extend_schema(
        tags=["Accounts"],
        summary="Get user profile",
        description=(
            "Returns the profile information of the currently "
            "authenticated user."
        ),
        responses={
            200: ProfileSerializer,
        },
    )
    def get(self, request):

        serializer = ProfileSerializer(request.user)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @extend_schema(
        tags=["Accounts"],
        summary="Update user profile",
        description=(
            "Updates the profile information of the currently "
            "authenticated user. Username and email cannot be changed."
        ),
        request=ProfileSerializer,
        responses={
            200: ProfileUpdateResponseSerializer,
            400: OpenApiResponse(
                description="Invalid profile data."
            ),
        },
    )
    def patch(self, request):

        serializer = ProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():

            serializer.save()

            return Response(
                {
                    "message": "Profile updated successfully.",
                    "user": serializer.data
                },
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

# Vehicle list Api View 
class VehicleListCreateView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Vehicles"],
        summary="List user's vehicles",
        description=(
            "Returns all vehicles registered by the currently "
            "authenticated user. The default vehicle is returned first."
        ),
        responses={
            200: VehicleSerializer(many=True),
        },
    )
    def get(self, request):

        vehicles = Vehicle.objects.filter(
            user=request.user
        ).order_by("-is_default", "-created_at")

        serializer = VehicleSerializer(
            vehicles,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @extend_schema(
        tags=["Vehicles"],
        summary="Add a vehicle",
        description=(
            "Adds a new vehicle for the currently authenticated user. "
            "The user is automatically assigned to the vehicle."
        ),
        request=VehicleSerializer,
        responses={
            201: VehicleResponseSerializer,
            400: OpenApiResponse(
                description="Invalid vehicle data."
            ),
        },
    )
    def post(self, request):

        serializer = VehicleSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        has_vehicle = Vehicle.objects.filter(
            user=request.user
        ).exists()

        vehicle = serializer.save(
            user=request.user,
            is_default=not has_vehicle
        )

        return Response(
            {
                "message": "Vehicle added successfully.",
                "vehicle": VehicleSerializer(vehicle).data
            },
            status=status.HTTP_201_CREATED
        )

# Vehicle details api view
class VehicleDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, request, pk):

        try:
            return Vehicle.objects.get(
                pk=pk,
                user=request.user
            )

        except Vehicle.DoesNotExist:
            return None

    @extend_schema(
        tags=["Vehicles"],
        summary="Get vehicle details",
        description=(
            "Returns the details of a vehicle belonging to the "
            "currently authenticated user."
        ),
        responses={
            200: VehicleSerializer,
            404: OpenApiResponse(
                description="Vehicle not found."
            ),
        },
    )
    def get(self, request, pk):

        vehicle = self.get_object(
            request,
            pk
        )

        if vehicle is None:

            return Response(
                {
                    "detail": "Vehicle not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = VehicleSerializer(
            vehicle
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @extend_schema(
        tags=["Vehicles"],
        summary="Update vehicle",
        description=(
            "Updates the details of a vehicle belonging to the "
            "currently authenticated user."
        ),
        request=VehicleSerializer,
        responses={
            200: VehicleResponseSerializer,
            400: OpenApiResponse(
                description="Invalid vehicle data."
            ),
            404: OpenApiResponse(
                description="Vehicle not found."
            ),
        },
    )
    def patch(self, request, pk):

        vehicle = self.get_object(
            request,
            pk
        )

        if vehicle is None:

            return Response(
                {
                    "detail": "Vehicle not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = VehicleSerializer(
            vehicle,
            data=request.data,
            partial=True
        )

        serializer.is_valid(
            raise_exception=True
        )

        vehicle = serializer.save()

        return Response(
            {
                "message": "Vehicle updated successfully.",
                "vehicle": VehicleSerializer(vehicle).data
            },
            status=status.HTTP_200_OK
        )

    @extend_schema(
        tags=["Vehicles"],
        summary="Delete vehicle",
        description=(
            "Deletes a vehicle belonging to the currently "
            "authenticated user."
        ),
        responses={
            200: OpenApiResponse(
                description="Vehicle deleted successfully."
            ),
            404: OpenApiResponse(
                description="Vehicle not found."
            ),
        },
    )
    def delete(self, request, pk):

        vehicle = self.get_object(
            request,
            pk
        )

        if vehicle is None:

            return Response(
                {
                    "detail": "Vehicle not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        was_default = vehicle.is_default

        vehicle.delete()

        if was_default:

            next_vehicle = (
                Vehicle.objects
                .filter(user=request.user)
                .order_by("-created_at")
                .first()
            )

            if next_vehicle:

                next_vehicle.is_default = True

                next_vehicle.save(
                    update_fields=[
                        "is_default",
                        "updated_at"
                    ]
                )

        return Response(
            {
                "message": "Vehicle deleted successfully."
            },
            status=status.HTTP_200_OK
        )
# Set default api view
class SetDefaultVehicleView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Vehicles"],
        summary="Set default vehicle",
        description=(
            "Sets a vehicle belonging to the currently authenticated "
            "user as the default vehicle. Any previously selected "
            "default vehicle is automatically unset."
        ),
        responses={
            200: VehicleResponseSerializer,
            404: OpenApiResponse(
                description="Vehicle not found."
            ),
        },
    )
    def post(self, request, pk):

        try:

            vehicle = Vehicle.objects.get(
                pk=pk,
                user=request.user
            )

        except Vehicle.DoesNotExist:

            return Response(
                {
                    "detail": "Vehicle not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        Vehicle.objects.filter(
            user=request.user,
            is_default=True
        ).update(
            is_default=False
        )

        vehicle.is_default = True

        vehicle.save(
            update_fields=[
                "is_default",
                "updated_at"
            ]
        )

        return Response(
            {
                "message": "Default vehicle updated successfully.",
                "vehicle": VehicleSerializer(vehicle).data
            },
            status=status.HTTP_200_OK
        )
#Profile page view
def profile_page(request):
    return render(request, "profile.html")

#Reset password page view
def password_reset_page(request):
    return render(request, "password_reset.html")


# phone verification views
class SendPhoneVerificationOTPView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Phone Verification"],
        summary="Send phone verification OTP",
        description=(
            "Generates a verification OTP for the authenticated user's "
            "phone number and sends it through the configured SMS service. "
            "The OTP is stored securely as a hash and expires after the "
            "configured OTP expiry period."
        ),
        responses={
            200: SendPhoneVerificationOTPResponseSerializer,
            400: OpenApiResponse(
                description=(
                    "Phone number is missing or the phone number "
                    "is already verified."
                )
            ),
            401: OpenApiResponse(
                description="Authentication credentials were not provided."
            ),
        },
    )
    def post(self, request):

        send_phone_verification_otp_service(
            request.user
        )

        response_data = {
            "message": "Phone verification OTP sent successfully."
        }

        serializer = SendPhoneVerificationOTPResponseSerializer(
            response_data
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class VerifyPhoneOTPView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Phone Verification"],
        summary="Verify phone number",
        description=(
            "Verifies the OTP entered by the authenticated user. "
            "If the OTP is valid and has not expired, the user's "
            "phone_verified status is changed to true and the OTP "
            "is deleted so that it cannot be reused."
        ),
        request=VerifyPhoneOTPSerializer,
        responses={
            200: VerifyPhoneOTPResponseSerializer,
            400: OpenApiResponse(
                description=(
                    "Invalid, expired, missing, or already-used OTP, "
                    "or the phone number is already verified."
                )
            ),
            401: OpenApiResponse(
                description="Authentication credentials were not provided."
            ),
        },
    )

    def post(self, request):

        serializer = VerifyPhoneOTPSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = verify_phone_otp(
            user=request.user,
            otp=serializer.validated_data["otp"]
        )

        response_data = {
            "message": "Phone number verified successfully.",
            "user": user,
        }

        response_serializer = VerifyPhoneOTPResponseSerializer(
            response_data
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK
        )


class ResendPhoneVerificationOTPView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Phone Verification"],
        summary="Resend phone verification OTP",
        description=(
            "Resends a new phone verification OTP to the authenticated "
            "user's phone number. A resend cooldown is enforced to "
            "prevent repeated OTP requests."
        ),
        responses={
            200: ResendPhoneVerificationOTPResponseSerializer,
            400: OpenApiResponse(
                description=(
                    "Phone number is missing or the phone number "
                    "is already verified."
                )
            ),
            401: OpenApiResponse(
                description="Authentication credentials were not provided."
            ),
            429: OpenApiResponse(
                description=(
                    "OTP resend cooldown is still active. "
                    "The response includes the remaining cooldown time."
                )
            ),
        },
    )
    
    def post(self, request):

        remaining_seconds = resend_phone_verification_otp(
            request.user
        )

        if remaining_seconds is not None:
            return Response(
                {
                    "message": (
                        "Please wait before requesting another OTP."
                    ),
                    "remaining_seconds": remaining_seconds,
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        response_data = {
            "message": "Phone verification OTP resent successfully."
        }

        serializer = ResendPhoneVerificationOTPResponseSerializer(
            response_data
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

# class ChangePhoneNumberView(APIView):

#     permission_classes = [IsAuthenticated]

#     @extend_schema(
#         tags=["Phone Verification"],
#         summary="Request phone number change",
#         description=(
#             "Starts the phone number change process for the authenticated "
#             "user. The new phone number is not saved to the user's profile "
#             "until the OTP sent to the new number is successfully verified."
#         ),
#         request=ChangePhoneNumberSerializer,
#         responses={
#             200: ChangePhoneNumberResponseSerializer,
#             400: OpenApiResponse(
#                 description=(
#                     "Invalid phone number or the phone number "
#                     "is already registered."
#                 )
#             ),
#             401: OpenApiResponse(
#                 description="Authentication credentials were not provided."
#             ),
#         },
#     )
#     def post(self, request):

#         serializer = ChangePhoneNumberSerializer(
#             data=request.data
#         )

#         serializer.is_valid(
#             raise_exception=True
#         )

#         request_phone_number_change(
#             user=request.user,
#             new_phone=serializer.validated_data["phone"]
#         )

#         return Response(
#             {
#                 "message": (
#                     "OTP sent successfully to the new phone number."
#                 )
#             },
#             status=status.HTTP_200_OK
#         )

# class VerifyPhoneNumberChangeView(APIView):

#     permission_classes = [IsAuthenticated]

#     @extend_schema(
#         tags=["Phone Verification"],
#         summary="Verify new phone number",
#         description=(
#             "Verifies the OTP sent to the new phone number. "
#             "The new phone number is saved to the user's profile "
#             "only after successful OTP verification."
#         ),
#         request=VerifyPhoneOTPSerializer,
#         responses={
#             200: VerifyPhoneOTPResponseSerializer,
#             400: OpenApiResponse(
#                 description=(
#                     "Invalid, expired, or missing OTP."
#                 )
#             ),
#             401: OpenApiResponse(
#                 description="Authentication credentials were not provided."
#             ),
#         },
#     )
#     def post(self, request):

#         serializer = VerifyPhoneOTPSerializer(
#             data=request.data
#         )

#         serializer.is_valid(
#             raise_exception=True
#         )

#         user = verify_phone_number_change(
#             user=request.user,
#             otp=serializer.validated_data["otp"]
#         )

#         return Response(
#             {
#                 "message": (
#                     "Phone number changed and verified successfully."
#                 ),
#                 "user": user,
#             },
#             status=status.HTTP_200_OK
#         )

# Contact Change Views

class ContactChangeView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Contact Change"],
        summary="Request contact details change",
        description=(
            "Starts the contact change process for the authenticated "
            "user. The new email address or phone number is not saved "
            "until the OTP is successfully verified."
        ),
        request=ContactChangeRequestSerializer,
        responses={
            200: ContactChangeResponseSerializer,
            400: OpenApiResponse(
                description=(
                    "Invalid contact details or the contact is "
                    "already registered."
                )
            ),
            401: OpenApiResponse(
                description="Authentication credentials were not provided."
            ),
        },
    )
    def post(self, request):

        serializer = ContactChangeRequestSerializer(
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(
            raise_exception=True
        )

        request_contact_change(
            user=request.user,
            contact_type=serializer.validated_data["contact_type"],
            new_contact=serializer.validated_data["new_contact"],
        )

        return Response(
            {
                "message": (
                    "OTP sent successfully to the new contact."
                )
            },
            status=status.HTTP_200_OK
        )


class VerifyContactChangeOTPView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Contact Change"],
        summary="Verify contact change OTP",
        description=(
            "Verifies the OTP sent to the new email address or "
            "phone number. The contact details are updated only "
            "after successful OTP verification."
        ),
        request=VerifyContactChangeOTPSerializer,
        responses={
            200: VerifyContactChangeOTPResponseSerializer,
            400: OpenApiResponse(
                description=(
                    "Invalid, expired, or missing OTP."
                )
            ),
            401: OpenApiResponse(
                description="Authentication credentials were not provided."
            ),
        },
    )
    def post(self, request):

        serializer = VerifyContactChangeOTPSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = verify_contact_change(
            user=request.user,
            otp=serializer.validated_data["otp"],
        )

        response_data = {
            "message": (
                "Contact details changed successfully."
            ),
            "user": user,
        }

        response_serializer = (
            VerifyContactChangeOTPResponseSerializer(
                response_data
            )
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK
        )
# Resent Otp for contact change
@extend_schema(
    tags=["Contact Change"],
    summary="Resend contact change OTP",
    description=(
        "Resends the OTP for an existing pending contact change request. "
        "The OTP is sent to the previously requested email address or "
        "phone number. A resend cooldown is enforced."
    ),
    responses={
        200: OpenApiResponse(
            description="Contact change OTP resent successfully."
        ),
        401: OpenApiResponse(
            description="Authentication credentials were not provided."
        ),
        429: OpenApiResponse(
            description="OTP resend cooldown is still active."
        ),
        400: OpenApiResponse(
            description="No pending contact change request found."
        ),
    },
)
class ResendContactChangeOTPView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        remaining_seconds = resend_contact_change_otp(
            request.user
        )

        if remaining_seconds is not None:
            return Response(
                {
                    "message": (
                        "Please wait before requesting another OTP."
                    ),
                    "remaining_seconds": remaining_seconds,
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        return Response(
            {
                "message": (
                    "Contact change OTP resent successfully."
                )
            },
            status=status.HTTP_200_OK,
        )