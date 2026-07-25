import random
import traceback

from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.http import HttpResponse

from .models import EmailOTP


def login_page(request):
    if request.method == "POST":

        email = request.POST.get("email")
        otp = str(random.randint(100000, 999999))

        # Delete previous OTP
        EmailOTP.objects.filter(email=email).delete()

        # Save new OTP
        EmailOTP.objects.create(
            email=email,
            otp=otp
        )

        try:
            print("=" * 60)
            print("Sending email to:", email)
            print("EMAIL_BACKEND:", settings.EMAIL_BACKEND)
            print("EMAIL_HOST:", settings.EMAIL_HOST)
            print("EMAIL_PORT:", settings.EMAIL_PORT)
            print("EMAIL_USE_TLS:", settings.EMAIL_USE_TLS)
            print("EMAIL_HOST_USER:", settings.EMAIL_HOST_USER)
            print("DEFAULT_FROM_EMAIL:", settings.DEFAULT_FROM_EMAIL)

            if settings.EMAIL_HOST_PASSWORD:
                print("EMAIL_HOST_PASSWORD: Loaded Successfully")
            else:
                print("EMAIL_HOST_PASSWORD: NOT FOUND")

            print("=" * 60)

            send_mail(
                subject="Your Login OTP",
                message=f"""
Hello,

Your OTP is: {otp}

This OTP is valid for one login attempt.

Thank you,
MyShow Team
""",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )

            print("✅ Email sent successfully.")

        except Exception as e:

            print("=" * 60)
            print("SMTP ERROR")
            print(type(e))
            print(repr(e))
            traceback.print_exc()
            print("=" * 60)

            return HttpResponse(
                f"""
                <h2>Email Sending Failed</h2>

                <b>Error Type:</b><br>
                {type(e)}<br><br>

                <b>Error:</b><br>
                {e}<br><br>

                <h3>Generated OTP (Testing Only)</h3>
                <h2>{otp}</h2>

                <hr>

                <pre>{traceback.format_exc()}</pre>
                """
            )

        return redirect(f"/verify/?email={email}")

    return render(request, "accounts/login.html")


def verify_otp(request):

    email = request.GET.get("email")

    if request.method == "POST":

        email = request.POST.get("email")
        otp = request.POST.get("otp")

        try:
            data = EmailOTP.objects.filter(email=email).latest("created_at")

            if data.otp == otp:
                data.is_verified = True
                data.save()

                return render(
                    request,
                    "accounts/success.html",
                    {"email": email},
                )

            return render(
                request,
                "accounts/verify_otp.html",
                {
                    "email": email,
                    "message": "Invalid OTP",
                },
            )

        except EmailOTP.DoesNotExist:

            return render(
                request,
                "accounts/verify_otp.html",
                {
                    "email": email,
                    "message": "OTP Not Found",
                },
            )

    return render(
        request,
        "accounts/verify_otp.html",
        {"email": email},
    )
