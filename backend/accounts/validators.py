import re
from django.core.exceptions import ValidationError

#Validated an indian mobile number
def phone_number_validator(value):
    if not re.fullmatch(r"^[6-9]\d{9}$",value):
        raise ValidationError("Enter a valid 10 digit mobile number.")


#validates password
def password_validator(value):
    """
    Validate password strength.
    Rules:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    - No spaces
    """
    if len(value) < 8:
        raise ValidationError("Password must be atleast 8 character long.")

    if " " in value:
        raise ValidationError("Password can not contain spaces.")

    if not re.search(r"[A-Z]",value):
        raise ValidationError("Password must contain one uppercase letter.")

    if not re.search(r"[a-z]", value):
        raise ValidationError(
            "Password must contain one lowercase letter."
        )

    if not re.search(r"\d",value):
        raise ValidationError("Password must contain atleast one digit.")

    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]",value):
        raise ValidationError("Password must contain atleast one special charater.")

#validates name
def person_name_validator(value):
    value = value.strip()

    if len(value) < 2:
        raise ValidationError("Name at least contain 2 characters.")

    if len(value) > 50: 
        raise ValidationError("Name cannot exceed 50 characters.")

    if not re.fullmatch(r"[A-Za-z]+(?: [A-Za-z]+)*",value):
        raise ValidationError("Name can contain only letters and single spaces.")

# Validates Vehicle Registration number
def vehicle_registration_validator(value):

    value = value.strip().upper()

    pattern = r"^[A-Z]{2}[0-9]{2}[A-Z]{1,3}[0-9]{4}$"

    if not re.fullmatch(pattern, value):
        raise ValidationError(
            "Enter a valid vehicle registration number, "
            "for example MH12AB1234."
        )