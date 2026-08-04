from django.conf import settings
from django.core.mail import send_mail

def send_registration_otp(email,first_name,otp):
    # send registration otp to user's email

    subject = "ParkX - Verify Your Email"

    message = (
        f"Hello {first_name},\n\n"
        f"Your otp for ParkX registration is {otp},\n\n"
        f"This otp is valid for "
        f"{settings.OTP_EXPIRY_MINUTES} minutes.\n\n"
        "If you did not request this registration, "
        "please ignore this email.\n\n"
        "Regards,\n"
        "ParkX Team"

    )

    send_mail(
        subject=subject,
        message = message,
        from_email = settings.DEFAULT_FROM_EMAIL,
        recipient_list = [email],
        fail_silently = False,
    )
    