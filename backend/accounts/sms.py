from django.conf import settings


def send_sms_otp(phone, otp):
    """
    Development-only SMS sender.

    The OTP is printed to the container logs instead of
    being sent through a real SMS provider.
    """

    print(
        "\n"
        "========== PARKX DEV SMS ==========\n"
        f"To: {phone}\n"
        f"OTP: {otp}\n"
        f"Valid for: {settings.OTP_EXPIRY_MINUTES} minutes\n"
        "===================================\n"
    )