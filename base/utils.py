from django.conf import settings
from django.core.mail import send_mail


def send_password_reset_email(email, email_token):
    subject = "Password Reset Link Ecommerce"
    email_from = settings.EMAIL_HOST_USER
    message = f"Hi, \n\nPlease click the link below to reset your password.\n\n http://127.0.0.1:8000/account/reset_password/{email_token}\n\nThank you."
    # print(message)
    return send_mail(subject, message, email_from, [email])

def send_login_otp(email, otp):
    subject = "Log In OTP for Ecommerce"
    email_from = settings.EMAIL_HOST_USER
    message = f"Hi, \n\nPlease find below OTP for login.\n\n {otp}"
    # print(message)
    return send_mail(subject, message, email_from, [email])
