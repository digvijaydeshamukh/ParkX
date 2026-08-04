from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import RegisterSerializer
from .services import register_user


# Create your views here.

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        register_user(serializer.validated_data)

        return Response(
            {
                "message": "OTP sent successfully.",
                "email" : serializer.validated_data['email'],
            },
            status = status.HTTP_200_OK
        )
