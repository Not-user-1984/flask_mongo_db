import random
import re
import secrets
import smtplib
import string
from datetime import timedelta
from email.message import EmailMessage

from flask import Flask, jsonify, request
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, decode_token, JWTManager
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/usersdb'
app.config['JWT_SECRET_KEY'] = 'super-secret'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
mongo = PyMongo(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)


# Модель пользователя
class User:
    def __init__(self, name, phone, email, site, password):
        self.name = name
        self.phone = phone
        self.email = email
        self.site = site
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')


@app.route('/sign-up/', methods=['POST'])
def sign_up():
    data = request.json
    name = data.get('name')
    phone = data.get('phone')
    email = data.get('email')
    site = data.get('site')

    if not validate_registration_data(name, phone, email, site):
        return jsonify({'message': 'Invalid registration data format'}), 400

    existing_user = mongo.db.users.find_one({'email': email})
    if existing_user:
        return jsonify({'message': 'User already exists'}), 400

    temporary_password = generate_temporary_password()
    hashed_password = bcrypt.generate_password_hash(temporary_password).decode('utf-8')

    new_user = User(name, phone, email, site, hashed_password)
    mongo.db.users.insert_one({
        'name': new_user.name,
        'phone': new_user.phone,
        'email': new_user.email,
        'site': new_user.site,
        'password': new_user.password
    })
    _send_password_email(email, temporary_password)
    access_token = create_access_token(identity=email)

    return jsonify({'token': access_token}), 200


# Регистрация пользователя

def validate_credentials(email, password):
    if not email or not password:
        return False
    if not validate_email(email) or not validate_password(password):
        return False
    return True


def authenticate_user(email, password):
    user = mongo.db.users.find_one({'email': email})
    if not user or not bcrypt.check_password_hash(user['password'], password):
        return None
    return user


def validate_authorization_header(auth_header):
    if not auth_header:
        return False
    try:
        token_type, token = auth_header.split()
        if token_type != 'Bearer':
            raise ValueError('Token should be of type Bearer')
        return token
    except ValueError:
        return False


def validate_token(token, email):
    try:
        decoded_token = decode_token(token, options={"verify_signature": False})
        if decoded_token['identity'] != email:
            raise ValueError('Invalid token')
        return True
    except:
        return False


def _send_password_email(email, password):
    print(email)
    print(password)
    msg = EmailMessage()
    msg.set_content(f'Your temporary password: {password}')
    msg['Subject'] = 'Your Temporary Password'
    msg['From'] = 'your_email@example.com'
    msg['To'] = f'{email}'

    with smtplib.SMTP('localhost', 1025) as smtp:
        smtp.send_message(msg)


def validate_password(password):
    return len(password) >= 8


def validate_site(site):
    return bool(site.strip())


def validate_registration_data(name, phone, email, site):
    if not all([name, phone, email, site]):
        raise ValueError('All fields are required.')

    return True


def generate_temporary_password():
    digits = ''.join(secrets.choice(string.digits) for _ in range(6))
    letters = ''.join(secrets.choice(string.ascii_letters) for _ in range(2))
    temporary_password = ''.join(secrets.choice(digits + letters) for _ in range(8))
    return temporary_password


if __name__ == '__main__':
    app.run(debug=True)