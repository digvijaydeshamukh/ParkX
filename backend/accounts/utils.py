import secrets
import string
from django.conf import settings
from django.contrib.auth.hashers import make_password,check_password
from .models import User

#Generate an otp
def generate_otp():
    minimum = 10 ** (settings.OTP_LENGTH - 1)
    maximum = (10 ** settings.OTP_LENGTH) - 1

    return str(secrets.randbelow(maximum - minimum + 1) + minimum)

#hash otp
def make_otp_hash(otp):
    # Hash the OTP before storing it.
    return make_password(otp)

#check otp
def verify_otp_hash(plain_otp,otp_hash):
    # Verify the entered OTP against the stored hash.
    return check_password(plain_otp,otp_hash)

def hash_password(password):
    return make_password(password)

def generate_unique_username():
    
    # Generate a unique username for the user.

    characters = string.ascii_uppercase + string.digits

    while True:
        random_part = "".join(
            secrets.choice(characters)
            for _ in range(8)
        )

        username = (
            settings.USERNAME_PREFIX +
            random_part
        )

        if not User.objects.filter(username=username).exists():
            return username