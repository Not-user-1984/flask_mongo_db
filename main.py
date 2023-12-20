import hashlib
from datetime import timedelta

from flask import Flask, jsonify, request
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, JWTManager
from flask_pymongo import PyMongo

from utilits import generate_temporary_password, send_email
from validate import validate_credentials, validate_registration_data, validate_token

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/usersdb'
app.config['JWT_SECRET_KEY'] = 'super-secret'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
mongo = PyMongo(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)


# Модель пользователя
class User:
    def __init__(self, name, phone, email, site, password, hash_reset):
        self.name = name
        self.phone = phone
        self.email = email
        self.site = site
        self.password = password
        self.hash_reset = hash_reset


@app.route('/sign-up/', methods=['POST'])
def sign_up():
    data = request.json
    name = data.get('name')
    phone = data.get('phone')
    email = data.get('email')
    site = data.get('site')
    hash_reset = None

    if not validate_registration_data(name, phone, email, site):
        return jsonify({'message': 'Invalid registration data format'}), 400

    existing_user = mongo.db.users.find_one({'email': email})
    if existing_user:
        return jsonify({'message': 'User already exists'}), 400

    temporary_password = generate_temporary_password()
    hashed_password = bcrypt.generate_password_hash(temporary_password).decode('utf-8')
    new_user = User(name, phone, email, site, hashed_password, hash_reset)
    mongo.db.users.insert_one({
        'name': new_user.name,
        'phone': new_user.phone,
        'email': new_user.email,
        'site': new_user.site,
        'password': new_user.password,
        'hash': None
    })
    send_email(email, temporary_password, "Your Temporary Password")
    access_token = create_access_token(identity=email)

    return jsonify({'token': access_token}), 200


@app.route('/sign-in/', methods=['POST'])
def sign_in():
    data = request.json
    email = data.get('email')
    temp_password = data.get('password')

    if not validate_credentials(email, temp_password):
        return jsonify({'message': 'Invalid credentials format'}), 400

    user = _authenticate_user(email, temp_password)

    if not user:
        return jsonify({'message': 'Invalid email or password'}), 401

    token = request.headers.get('Authorization')
    if not validate_token(token, email):
        return jsonify({'message': 'Invalid token'}), 401

    return jsonify({
        'token': token,
        'name': user['name'],
        'site': user['site'],
        'email': user['email']
    }), 200


@app.route('/recovery/', methods=['POST'])
def recovery():
    data = request.json
    email = data.get('email')

    if not email:
        return jsonify({'message': 'Email is required.'}), 400

    existing_user = mongo.db.users.find_one({'email': email})
    if not existing_user:
        return jsonify({'message': 'User not found.'}), 404

    hash_value = _generate_hash(email)
    mongo.db.users.update_one(
        {'email': email},
        {'$set': {'hash_reset': hash_value}}
    )
    recovery_link = f"http://127.0.0.1:5000/recovery/{hash_value}/"
    send_email(email, recovery_link, 'Follow the links')
    return jsonify({'message': 'Recovery link sent.', 'link': recovery_link}), 200


# Смена пароля
@app.route('/recovery/<hash>/', methods=['POST'])
def change_password(hash):
    data = request.json
    password = data.get('password')

    if not password:
        return jsonify({'message': 'Password is required.'}), 400

    user = mongo.db.users.find_one({'hash_reset': hash})

    if not user:
        return jsonify({'message': 'Invalid or expired recovery link.'}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    mongo.db.users.update_one({'hash_reset': hash}, {'$set': {'password': hashed_password}})
    access_token = create_access_token(identity=user['email'])

    mongo.db.users.update_one({'hash_reset': hash}, {'$unset': {'hash_reset': ''}})
    user = mongo.db.users.find_one({'hash_reset': hash})

    return jsonify({'token': access_token}), 200


def _authenticate_user(email, temp_password):
    user = mongo.db.users.find_one({'email': email})
    if user:
        hashed_password = user.get('password')
        if bcrypt.check_password_hash(hashed_password, str(temp_password)):
            return user
    return False


def _generate_hash(email):
    return hashlib.sha256(email.encode()).hexdigest()


if __name__ == '__main__':
    app.run(debug=True)