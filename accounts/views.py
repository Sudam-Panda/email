import random

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
            print("Sending email to:", email)

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
            print("SMTP ERROR:", str(e))

            # Show OTP for testing if email fails
            return HttpResponse(f"""
                <h2>Email Sending Failed</h2>
                <p><b>Error:</b> {e}</p>
                <hr>
                <h3>Generated OTP (Testing Only)</h3>
                <h2>{otp}</h2>
            """)

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
