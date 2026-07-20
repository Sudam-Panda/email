from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_page, name="login"),
    path("verify/", views.verify_otp, name="verify_otp"),
]