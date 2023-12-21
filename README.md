#### Регистрация, авторизация, смену пароля Flask + MongoDB  
  
Сначало я хотел найти готовую библиотеку регистрации прилепить к ней MongoDB и все.
Так и появились еше две попытки реализации:  
1. [Django + Djoser](https://github.com/Not-user-1984/auth_django_mangodb)  
2. [FastApi + fastapi-users](https://github.com/Not-user-1984/FastAPI_auth_mongodb/tree/main)  
  
Если с Django шло сразу через костыли, нашлась [djongo-certego](https://pypi.org/project/djongo-certego/)  которая сделала даже миграции в mongo, но при создании users вываливалась  ошибка запроса, возможно можно было докрутить , но решил посмотреть что у вас FastApi c Mongo и в можно сделать на ней, но же решил посмотреть готовую библиотека, [FastAPI Users](https://fastapi-users.github.io/fastapi-users/12.1/configuration/databases/beanie/) хорошая дока, поддержка mongo, но опять при создании что там не так связями, зарылся (тут прям надо докрутить)  
  
И тут меня спас Flask которого я раньше не воспринимал...

Пытался лишнего не ставить и писал сам всякие генераторы кодов, не стал все прятать в env и распихвать по папкам и conf файл, возмoжно чуть позже навиду порядок.
  
Jwt токен сделан через секретный ключ и email, решение может не такое хорошие, но можно заместо email использовать что-то другое, хеширование пароля через flask_bcrypt.
### Запуск:

```
docker-compose up

и mailpit для смс на email
http://localhost/mailhog/

```

#### Запросы:

``` 
### Регистрация post ####

http://localhost/sign-up/
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
http://localhost/sign-in/

{

"email": "fes2233@уmple.com",

"password": "4589a358y"

```
````
#### Смена пароля ####
}
http://localhost/recovery/
{

"email": "fes2233@уmple.com"

}

cысылка на:
http://localhost:8025

```
