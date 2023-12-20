from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
import smtplib
from email.message import EmailMessage

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
    name = data['name']
    phone = data['phone']
    email = data['email']
    site = data['site']

    existing_user = mongo.db.users.find_one({'email': email})
    if existing_user:
        return jsonify({'message': 'User already exists'}), 400

    new_user = User(name, phone, email, site, 'randompassword')  # Генерация временного пароля
    mongo.db.users.insert_one({
        'name': new_user.name,
        'phone': new_user.phone,
        'email': new_user.email,
        'site': new_user.site,
        'password': new_user.password
    })

    # Создание JWT Token
    access_token = create_access_token(identity=email)

    # Отправка токена на почту
    msg = EmailMessage()
    msg.set_content(f'Your access token: {access_token}')
    msg['Subject'] = 'Your Access Token'
    msg['From'] = 'your_email@example.com'  # Замените на ваш email
    msg['To'] = email

    with smtplib.SMTP('localhost', 1025) as smtp:  # Используйте адрес и порт Mainpit
        smtp.send_message(msg)

    return jsonify({'token_sent': True}), 200


# Авторизация пользователя
@app.route('/sign-in/', methods=['POST'])
def sign_in():
    data = request.json
    email = data['email']
    password = data['password']

    user = mongo.db.users.find_one({'email': email})
    if not user or not bcrypt.check_password_hash(user['password'], password):
        return jsonify({'message': 'Invalid credentials'}), 401

    access_token = create_access_token(identity=email)
    return jsonify({
        'token': access_token,
        'name': user['name'],
        'site': user['site'],
        'email': user['email']
    }), 200


if __name__ == '__main__':
    app.run(debug=True)