#### Регистрация, авторизация, смену пароля Flask + MongoDB  
  
С начало я хотел найти готовую библиотеку регистрации прилепить к ней MongoDB и все.
так и появились еше две попытки реализации:  
1. [Django + Djoser](https://github.com/Not-user-1984/auth_django_mangodb)  
2. [FastApi + fastapi-users](https://github.com/Not-user-1984/FastAPI_auth_mongodb/tree/main)  
  
Если с Django шло сразу через костыли, нашлась [djongo-certego](https://pypi.org/project/djongo-certego/)  которая сделала даже миграции в mongo, но при создании users вываливалась  ошибка запроса, возможно можно было докрутить , но решил посмотреть что у вас FastApi c Mongo и в можно сделать на ней, но же решил посмотреть готовую библиотека, [FastAPI Users](https://fastapi-users.github.io/fastapi-users/12.1/configuration/databases/beanie/) хорошая дока, поддержка mongo, но опять при создании что там не так связями, зарылся (тут прям надо докрутить)  
  
И тут меня спас Flask которого я раньше не воспринимал ,  
пытался лишнего не ставить и писал сам всякие генераторы кодов, не стал все прятать в env  
  
jwt токен сделан через секретный ключ и email, решение может не такое хорошие, но можно заместо email использовать что-то другое, хеширование пароля через flask_bcrypt
### Запуск:

```
docker-compose up

там  развернеться база mongo 

и mailpit для смс на email
http://localhost:8025

запуск flask
python main.py

```

#### Запросы:

``` 
### Регистрация post ####

http://127.0.0.1:5000/sign-up/
{

"name": "dccууввasds2",

"phone": "22caвв2242",

"email": "fes2233@уmple.com",

"site": "в.caaofdm"

}


cмс на:
http://localhost:8025
```
```
### Aвторизация ####
http://127.0.0.1:5000/sign-in/

{

"email": "fes2233@уmple.com",

"password": "4589a358y"

```
````
#### Смена пароля ####
}
http://127.0.0.1:5000/recovery/
{

"email": "fes2233@уmple.com"

}

cысылка на:
http://localhost:8025

```
