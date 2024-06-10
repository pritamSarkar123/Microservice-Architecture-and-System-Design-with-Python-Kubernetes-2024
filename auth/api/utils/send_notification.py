import datetime
import json
import smtplib
import ssl
from email.message import EmailMessage


async def send_email(settings, token, username):
    try:
        message = f"The token : {token} is generated at: {datetime.datetime.now()}, please use the token and new password to reset the password"

        from_email = settings.email_from
        app_password = settings.app_password

        msg = EmailMessage()
        msg["Subject"] = "Reset Password"
        msg["From"] = from_email
        msg["To"] = username

        msg.set_content(message)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(from_email, app_password)
            smtp.send_message(msg)

        return True, "Successfully send password change email"

    except Exception as e:
        return False, f"Error sending password change email due to : {str(e)}"
