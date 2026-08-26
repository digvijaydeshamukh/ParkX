from django.shortcuts import render

# Register Page view
def register_page(request):
    return render(request, "register.html")


#Home / landing page view
def home_page(request):
    return render(request, "home.html")

#Login page view
def login_page(request):
    return render(request, "login.html")

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

#Profile page view
def profile_page(request):
    return render(request, "profile.html")

#Reset password page view
def password_reset_page(request):
    return render(request, "password_reset.html")

# Verify phone page view
def verify_phone_page(request):
    return render(request, "verify_phone.html")

# Change password page view
def change_password_page(request):
    return render(request, "change_password.html")

# Edit contact page view
def edit_contact_page(request):
    return render(request, "edit_contact.html")
