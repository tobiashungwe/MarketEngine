# email_sender.py

import smtplib
from email.message import EmailMessage

def send_email(to_email, subject, body, from_email='your-email@example.com', password='your-app-password'):
    """Send an email using SMTP."""
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(from_email, password)
            smtp.send_message(msg)
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")
