import json
import smtplib
import ssl
from email.message import EmailMessage


def send_email(settings, message):
    try:
        message = json.loads(message)
        mp3_fid = message["mp3_fid"]

        from_email = settings.email_from
        app_password = settings.app_password

        msg = EmailMessage()
        msg["Subject"] = "MP3 Download"
        msg["From"] = from_email
        msg["To"] = message["username"]

        msg.set_content(f"mp3 file_id: {mp3_fid} is now ready!, expiry: 1 hour, created at: {message['created_at']}")

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(from_email, app_password)
            smtp.send_message(msg)

    except Exception as e:
        return f"Error sending notification email due to : {str(e)}"
