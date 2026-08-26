from django.shortcuts import render

#add all pages view inside this page view of accounts 

# Page views
def register_page(request):
    return render(request, "register.html")