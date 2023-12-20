
from datetime import timedelta

from flask import Flask, jsonify, request
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, JWTManager
from flask_pymongo import PyMongo

from utilits import generate_temporary_password, send_password_email
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
    def __init__(self, name, phone, email, site, password):
        self.name = name
        self.phone = phone
        self.email = email
        self.site = site
        self.password = password


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
    send_password_email(email, temporary_password)
    access_token = create_access_token(identity=email)

    return jsonify({'token': access_token}), 200


# Регистрация пользователя
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




def _authenticate_user(email, temp_password):
    user = mongo.db.users.find_one({'email': email})
    if user:
        hashed_password = user.get('password')
        if bcrypt.check_password_hash(hashed_password, str(temp_password)):
            return user
    return False





if __name__ == '__main__':
    app.run(debug=True)