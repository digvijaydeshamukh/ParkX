from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema,OpenApiResponse
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAdminUser
from accounts.models import User,Roles
from django.contrib.auth import logout
from django.shortcuts import redirect


from ..serializers import (

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

    # Phone OTP serializers
    VerifyPhoneOTPSerializer,
    VerifyPhoneOTPResponseSerializer,
    SendPhoneVerificationOTPResponseSerializer,
    ResendPhoneVerificationOTPResponseSerializer,


    # Contact Change Serializers
    ContactChangeRequestSerializer,
    VerifyContactChangeOTPSerializer,
    ContactChangeResponseSerializer,
    VerifyContactChangeOTPResponseSerializer,

    # Change Password Serializer
    ChangePasswordSerializer,
    ChangePasswordResponseSerializer,

    # Create/List Parking Owner Serializer
    CreateParkingOwnerSerializer,
    ParkingOwnerListResponseSerializer,
    ParkingOwnerSerializer,

    # Parking Owner Serializer
    PromoteParkingOwnerResponseSerializer,
    DemoteParkingOwnerResponseSerializer,
    DeleteUserResponseSerializer,
    
    # Resolve parking area serializer
    ResolveParkingOwnershipSerializer,
    ResolveParkingOwnershipResponseSerializer,

)
from ..services import (

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

    # Contact Change
    request_contact_change,
    verify_contact_change,
    resend_contact_change_otp,

    # Create Parking Owner
    create_parking_owner,

    # Parking Owner Operations by admin
    promote_user_to_parking_owner,
    demote_parking_owner,
    delete_parking_owner,

    # Delete any User
    delete_user,

    # Resolves Parking area ownerships
    resolve_parking_ownership,
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
    tags=["Forgot Password"],
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
    tags=["Forgot Password"],
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

# Verify Contact Change OTP view
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

# Change Password
class ChangePasswordAPIView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Change Password"],
        summary="Change authenticated user's password",
        description=(
            "Changes the password of the currently authenticated user. "
            "The current password must be provided and verified before "
            "the new password is saved."
        ),
        request=ChangePasswordSerializer,
        responses={
            200: ChangePasswordResponseSerializer,
            400: OpenApiResponse(
                description=(
                    "Current password is incorrect, passwords do not "
                    "match, or the new password is invalid."
                )
            ),
            401: OpenApiResponse(
                description=(
                    "Authentication credentials were not provided."
                )
            ),
        },
    )
    def post(self, request):

        serializer = ChangePasswordSerializer(
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(
            raise_exception=True
        )

        request.user.set_password(
            serializer.validated_data["new_password"]
        )

        request.user.save(
            update_fields=["password"]
        )

        return Response(
            {
                "message": "Password changed successfully."
            },
            status=status.HTTP_200_OK,
        )

# Create Parking Owner Api View
class ParkingOwnerListCreateView(APIView):

    permission_classes = [IsAdminUser]

    @extend_schema(
        tags=["Admin"],
        summary="Create a parking owner",
        description=(
            "Allows an authenticated staff/admin user to create "
            "a parking owner account."
        ),
        request=CreateParkingOwnerSerializer,
        responses={
            201: OpenApiResponse(
                description="Parking owner created successfully."
            ),
            400: OpenApiResponse(
                description="Invalid parking owner data."
            ),
            403: OpenApiResponse(
                description="Admin privileges required."
            ),
        },
    )
    def post(self, request):

        serializer = CreateParkingOwnerSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = create_parking_owner(
            serializer.validated_data
        )

        return Response(
            {
                "message": "Parking owner created successfully.",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "role": user.role,
                },
            },
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        tags=["Admin"],
        summary="List parking owners",
        description=(
            "Returns the total number of parking owners and "
            "their details. Only authenticated admin users "
            "can access this endpoint."
        ),
        responses={
            200: ParkingOwnerListResponseSerializer,
            403: OpenApiResponse(
                description="Admin privileges required."
            ),
        },
    )
    def get(self, request):

        parking_owners = User.objects.filter(
            role=Roles.PARKING_OWNER
        ).order_by("id")

        serializer = ParkingOwnerSerializer(
            parking_owners,
            many=True
        )

        response_data = {
            "count": parking_owners.count(),
            "parking_owners": serializer.data,
        }

        response_serializer = ParkingOwnerListResponseSerializer(
            response_data
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )

# Promote Existing User to Parking Owner
class PromoteParkingOwnerView(APIView):

    permission_classes = [IsAdminUser]

    @extend_schema(
        tags=["Admin"],
        summary="Promote a vehicle owner to parking owner",
        description=(
            "Allows an authenticated staff/admin user to promote "
            "an existing vehicle owner to parking owner."
        ),
        responses={
            200: PromoteParkingOwnerResponseSerializer,
            400: OpenApiResponse(
                description="Invalid promotion request."
            ),
            403: OpenApiResponse(
                description="Admin privileges required."
            ),
            404: OpenApiResponse(
                description="User not found."
            ),
        },
    )
    def patch(self, request, user_id):

        user = promote_user_to_parking_owner(
            user_id=user_id
        )


        response_data = {
            "message": "User promoted to parking owner successfully.",
            "user": user,
        }

        response_serializer = PromoteParkingOwnerResponseSerializer(
            response_data
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )
        
# Demote To vehicle owner
class DemoteParkingOwnerView(APIView):

    permission_classes = [IsAdminUser]

    @extend_schema(
        tags=["Admin"],
        summary="Demote a parking owner",
        description=(
            "Demotes a parking owner to vehicle owner after resolving "
            "ownership of all parking areas. Areas can be reassigned "
            "to another parking owner or deactivated. Any unspecified "
            "area is automatically deactivated."
        ),
        request=ResolveParkingOwnershipSerializer,
        responses={
            200: ResolveParkingOwnershipResponseSerializer,
            400: OpenApiResponse(
                description="Invalid ownership resolution."
            ),
            403: OpenApiResponse(
                description="Admin privileges required."
            ),
            404: OpenApiResponse(
                description="User not found."
            ),
        },
    )
    def patch(self, request, user_id):

        user = User.objects.filter(
            id=user_id
        ).first()

        if not user:
            return Response(
                {
                    "detail": "User not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if user.id == request.user.id:
            return Response(
                {
                    "detail": "You cannot demote yourself."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ResolveParkingOwnershipSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        resolved_areas = resolve_parking_ownership(
            user=user,
            decisions=serializer.validated_data["decisions"],
            operation="demote",
        )

        return Response(
            {
                "message": "Parking owner demoted successfully.",
                "demoted": True,
                "parking_areas": resolved_areas,
            },
            status=status.HTTP_200_OK,
        )
    
# Delete Parking owner
class DeleteParkingOwnerView(APIView):

    permission_classes = [IsAdminUser]

    @extend_schema(
        tags=["Admin"],
        summary="Delete a parking owner",
        description=(
            "Deletes a parking owner after resolving ownership of "
            "all parking areas. Areas can be reassigned to another "
            "parking owner or deactivated. Any unspecified area "
            "is automatically deactivated."
        ),
        request=ResolveParkingOwnershipSerializer,
        responses={
            200: ResolveParkingOwnershipResponseSerializer,
            400: OpenApiResponse(
                description="Invalid ownership resolution."
            ),
            403: OpenApiResponse(
                description="Admin privileges required."
            ),
            404: OpenApiResponse(
                description="User not found."
            ),
        },
    )
    def delete(self, request, user_id):

        user = User.objects.filter(
            id=user_id
        ).first()

        if not user:
            return Response(
                {
                    "detail": "User not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if user.id == request.user.id:
            return Response(
                {
                    "detail": "You cannot delete yourself."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ResolveParkingOwnershipSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        resolved_areas = resolve_parking_ownership(
            user=user,
            decisions=serializer.validated_data["decisions"],
            operation="delete",
        )

        return Response(
            {
                "message": "Parking owner deleted successfully.",
                "deleted": True,
                "parking_areas": resolved_areas,
            },
            status=status.HTTP_200_OK,
        )

# Delete any User
class DeleteUserView(APIView):

    permission_classes = [IsAdminUser]

    @extend_schema(
        tags=["Admin"],
        summary="Delete a user",
        description="Deletes a specific user account.",
        responses={
            200: DeleteUserResponseSerializer,
            403: OpenApiResponse(
                description="Admin privileges required."
            ),
            404: OpenApiResponse(
                description="User not found."
            ),
        },
    )
    def delete(self, request, user_id):

        user = User.objects.filter(
            id=user_id
        ).first()

        if not user:
            return Response(
                {
                    "detail": "User not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if user.id == request.user.id:
            return Response(
                {
                    "detail": "You cannot delete yourself."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        delete_user(user)

        return Response(
            {
                "message": "User deleted successfully."
            },
            status=status.HTTP_200_OK,
        )

# Resolve Parking Ownership view
class ResolveParkingOwnershipView(APIView):

    permission_classes = [IsAdminUser]

    @extend_schema(
        tags=["Admin"],
        summary="Resolve parking ownership before owner removal",
        description=(
            "Allows an admin to resolve every parking area owned by a "
            "parking owner before demotion or deletion. Each area can "
            "either be reassigned to another parking owner or deactivated. "
            "Any unspecified area is automatically deactivated."
        ),
        request=ResolveParkingOwnershipSerializer,
        responses={
            200: ResolveParkingOwnershipResponseSerializer,
            400: OpenApiResponse(
                description="Invalid ownership resolution."
            ),
            403: OpenApiResponse(
                description="Admin privileges required."
            ),
            404: OpenApiResponse(
                description="Parking owner not found."
            ),
        },
    )
    def patch(self, request, user_id):

        user = User.objects.filter(
            id=user_id
        ).first()

        if not user:
            return Response(
                {
                    "detail": "User not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if user.id == request.user.id:
            return Response(
                {
                    "detail": (
                        "You cannot demote or delete yourself."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ResolveParkingOwnershipSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        resolved_areas = resolve_parking_ownership(
            user=user,
            decisions=serializer.validated_data.get(
                "decisions",
                []
            ),
            operation=serializer.validated_data["operation"],
        )

        response_data = {
            "message": (
                "Parking ownership resolved successfully."
            ),
            "parking_areas": resolved_areas,
        }

        if serializer.validated_data["operation"] == "demote":
            response_data["demoted"] = True
        else:
            response_data["deleted"] = True

        response_serializer = (
            ResolveParkingOwnershipResponseSerializer(
                response_data
            )
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )