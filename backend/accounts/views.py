from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema

from .serializers import (
    RegisterSerializer,
    RegisterResponseSerializer,
    VerifyOTPSerializer,
    VerifyOTPResponseSerializer,
)
from .services import (
    register_user,
    verify_registration_otp
)

# Create your views here.

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