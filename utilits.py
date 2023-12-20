import secrets
import smtplib
import string
from email.message import EmailMessage


def send_password_email(email, password):
    print(email)
    print(password)
    msg = EmailMessage()
    msg.set_content(f'Your temporary password: {password}')
    msg['Subject'] = 'Your Temporary Password'
    msg['From'] = 'your_email@example.com'
    msg['To'] = 'test@test.com'

    with smtplib.SMTP('localhost', 1025) as smtp:
        smtp.send_message(msg)


def generate_temporary_password():
    digits = ''.join(secrets.choice(string.digits) for _ in range(6))
    letters = ''.join(secrets.choice(string.ascii_letters) for _ in range(2))
    temporary_password = ''.join(secrets.choice(digits + letters) for _ in range(8))
    return temporary_password
