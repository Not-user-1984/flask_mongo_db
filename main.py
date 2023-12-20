import random
import re
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

@app.route('/sign-in/', methods=['POST'])
def sign_in():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not validate_credentials(email, password):
        return jsonify({'message': 'Invalid credentials format'}), 400

    user = authenticate_user(email, password)

    if not user:
        return jsonify({'message': 'Invalid credentials'}), 401

    access_token = create_access_token(identity=email)

    return jsonify({
        'token': access_token,
        'name': user.get('name'),
        'site': user.get('site'),
        'email': user.get('email')
    }), 200


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
    msg = EmailMessage()
    msg.set_content(f'Your temporary password: {password}')
    msg['Subject'] = 'Your Temporary Password'
    msg['From'] = 'your_email@example.com'
    msg['To'] = email

    with smtplib.SMTP('localhost', 1025) as smtp:
        smtp.send_message(msg)


def validate_email(email):
    # Простая проверка формата email
    email_regex = r'^[\w\-.]+@[a-zA-Z\d\-.]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None


def validate_password(password):
    # Проверка пароля на соответствие требованиям (например, длина не менее 8 символов)
    return len(password) >= 8


def validate_site(site):
    return bool(site.strip())


def validate_registration_data(name, phone, email, site):
    if not all([name, phone, email, site]):
        raise ValueError('All fields are required.')

    if not validate_email(email):
        raise ValueError('Invalid email format.')

    if not validate_site(site):
        raise ValueError('Invalid site format.')

    return True


def generate_temporary_password(length=10):
    characters = string.ascii_letters + string.digits + string.punctuation
    temporary_password = ''.join(random.choice(characters) for i in range(length))
    return temporary_password


if __name__ == '__main__':
    app.run(debug=True)