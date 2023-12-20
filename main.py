import smtplib
from datetime import timedelta
from email.message import EmailMessage

from flask import Flask, jsonify, request
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, JWTManager, decode_token
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


@app.route('/sign-in/', methods=['POST'])
def sign_in():
    data = request.json
    email = data['email']
    password = data['password']

    existing_user = mongo.db.users.find_one({'email': email})
    if existing_user:
        return jsonify({'message': 'User already exists'}), 400

    access_token = create_access_token(identity=email)

    new_user = User(email, password)
    mongo.db.users.insert_one({
        'email': new_user.email,
        'password': new_user.password
    })
    return jsonify({'token_sent_email': True},
                   {'token': access_token},
                   ), 200


# Авторизация пользователя
@app.route('/sign-up/', methods=['POST'])
def sign_up():
    data = request.json
    site = data.get('site')
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Invalid credentials'}), 400

    user = mongo.db.users.find_one({'email': email})

    if not user or not bcrypt.check_password_hash(user['password'], password):
        return jsonify({'message': 'Invalid credentials'}), 401
    print(user)

    auth_header = request.headers.get('Authorization')

    print(auth_header)

    if not auth_header:
        return jsonify({'message': 'Missing Authorization header'}), 401

    try:
        token_type, token = auth_header.split()
        if token_type != 'Bearer':
            raise ValueError('Token should be of type Bearer')
    except ValueError:
        return jsonify({'message': 'Invalid token format'}), 401

    try:
        decoded_token = decode_token(auth_header)
        if decoded_token['identity'] != email:
            raise ValueError('Invalid token')
    except:
        return jsonify({'message': 'Invalid token'}), 401

    return jsonify({
        'token': token,
        'name': user['name'],
        'site': user['site'],
        'email': user['email']
    }), 200


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



if __name__ == '__main__':
    app.run(debug=True)