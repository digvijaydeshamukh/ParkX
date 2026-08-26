from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    User,
    PendingRegistration,
    PasswordResetOTP,
    PhoneVerificationOTP,
    ContactChangeOTP,
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    list_display = (
        "email",
        "first_name",
        "last_name",
        "phone",
        "phone_verified",
        "role",
        "is_active",
        "created_at",
    )

    search_fields = (
        "email",
        "first_name",
        "last_name",
        "phone",
    )

    list_filter = (
        "role",
        "phone_verified",
        "is_active",
        "is_staff",
        "is_superuser",
    )

    ordering = ("-created_at",)


@admin.register(PendingRegistration)
class PendingRegistrationAdmin(admin.ModelAdmin):

    list_display = (
        "email",
        "first_name",
        "last_name",
        "phone",
        "role",
        "otp_created_at",
        "expires_at",
        "created_at",
    )

    search_fields = (
        "email",
        "phone",
        "first_name",
        "last_name",
    )

    list_filter = (
        "role",
    )

    ordering = ("-created_at",)


@admin.register(PasswordResetOTP)
class PasswordResetOTPAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "otp_created_at",
        "expires_at",
        "reset_token_expires_at",
        "created_at",
    )

    search_fields = (
        "user__email",
    )

    ordering = ("-created_at",)


@admin.register(PhoneVerificationOTP)
class PhoneVerificationOTPAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "phone",
        "otp_created_at",
        "expires_at",
        "created_at",
    )

    search_fields = (
        "user__email",
        "phone",
    )

    ordering = ("-created_at",)


@admin.register(ContactChangeOTP)
class ContactChangeOTPAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "contact_type",
        "new_contact",
        "otp_created_at",
        "expires_at",
        "created_at",
    )

    search_fields = (
        "user__email",
        "new_contact",
    )

    list_filter = (
        "contact_type",
    )

    ordering = ("-created_at",)