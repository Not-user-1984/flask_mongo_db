import secrets
import smtplib
import string
from email.message import EmailMessage
import hashlib

def send_email(email, data, user_msg):
    """
    Sends an email message with the provided data.
    """
    msg = EmailMessage()
    msg.set_content(f'{user_msg}: {data}')
    msg['Subject'] = 'Your Temporary Password'
    msg['From'] = 'your_email@example.com'
    msg['To'] = 'test@test.com'

    with smtplib.SMTP('localhost', 1025) as smtp:
        smtp.send_message(msg)


def generate_temporary_password():
    """
    Generates a temporary password.
    """
    digits = ''.join(secrets.choice(string.digits) for _ in range(6))
    letters = ''.join(secrets.choice(string.ascii_letters) for _ in range(2))
    temporary_password = ''.join(secrets.choice(digits + letters) for _ in range(8))
    return temporary_password

def generate_hash(email):
    """
    Generates a hash based on the email.
    """
    return hashlib.sha256(email.encode()).hexdigest()
