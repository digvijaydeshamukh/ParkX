import re
from django.core.exceptions import ValidationError


# Validates Vehicle Registration number
def vehicle_registration_validator(value):

    value = value.strip().upper()

    pattern = r"^[A-Z]{2}[0-9]{2}[A-Z]{1,3}[0-9]{4}$"

    if not re.fullmatch(pattern, value):
        raise ValidationError(
            "Enter a valid vehicle registration number, "
            "for example MH12AB1234."
        )