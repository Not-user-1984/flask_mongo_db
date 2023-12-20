import re

from flask_jwt_extended import decode_token


def validate_password(password):
    return len(password) >= 8


def validate_site(site):
    return bool(site.strip())


def validate_email(email):
    # Простая проверка на наличие @ и .
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))


def validate_registration_data(name, phone, email, site):
    if not all([name, phone, email, site]):
        raise ValueError('All fields are required.')

    if not validate_email(email):
        raise ValueError('Invalid email format.')

    if not validate_site(site):
        raise ValueError('Site cannot be empty.')
    return True


def validate_credentials(email, password):
    if not email or not password:
        return False
    return True


def validate_token(token, email):
    token_type, token = token.split()
    if email == decode_token(token)['sub']:
        return True, 200
    if token_type != 'Bearer':
        raise ValueError('Token should be of type Bearer')
    return False
