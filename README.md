<h1 align="center">Hi there, I'm <a href="https://github.com/Azerothforev" target="_blank">Dmitriy</a> 
<img src="https://github.com/blackcater/blackcater/raw/main/images/Hi.gif" height="32"/></h1>

## Веб-фреймворки: Django и Django REST Framework

Приветствую! Я - Дмитрий, начинающий Python-разработчик, специализирующийся на Django и Django REST Framework (DRF). Мои основные области знаний и опыта включают:

Django: Разработка полнофункциональных веб-приложений с использованием Django, включая моделирование данных, маршрутизацию, представления и шаблоны.
Django REST Framework: Создание RESTful API с помощью DRF, включая сериализацию данных, настройку эндпоинтов и обработку запросов и ответов.
Я стремлюсь к постоянному самосовершенствованию и самообразованию, чтобы расширить свои знания и навыки в различных областях разработки веб-приложений. Я открыт для новых вызовов и готов применять свои знания и опыт для создания качественного программного обеспечения.

Если у вас есть вопросы или предложения сотрудничества, не стесняйтесь связаться со мной. Буду рад принять участие в интересных проектах и внести свой вклад в развитие сообщества разработчиков.
## Контакты для связи:
- Электронная почта: dmitrii.shalenko@yandex.ru
- Другие профили в социальных сетях:
  - Telegram: @azerothforev

# Проект Foodgram

![Github actions](https://github.com/mariyabykova/foodgram-project-react/actions/workflows/main.yml/badge.svg)


### Описание
Проект "Foodgram" – это "продуктовый помощник". На этом сервисе авторизированные пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд. Для неавторизированных пользователей доступны просмотр рецептов и страниц авторов. 
## Функционал
для навторизованных пользователей:
    1. просмотр рецептов на главной странице.
    2. просмотр профиля автора рецепта.
    3. регистрация на сайте
для авторизованных пользователей:
    1. создание, редактирование, удаление, частичное редактирование рецептов.
    2. подписки\отписки для на других пользователей.
    3. добавление рецептов в избранное.
    4. фильтрация по тегам в корзине, избранном и на главной странице.
    5. скачивание ваших рецептов прямиком из корзины
    6. просмотр всех рецептов от определенного автора
    7. смена пароля.

## Стек технологий

![python version](https://img.shields.io/badge/Python-3.9.10-yellowgreen) 
![django version](https://img.shields.io/badge/Django-3.2-yellowgreen)  
![djangorestframework version](https://img.shields.io/badge/djangorestframework-3.12.4-yellowgreen) 
![docker version](https://img.shields.io/badge/Docker-latest-blue)
![javascript version](https://img.shields.io/badge/JavaScript-latest-yellow)

### развертывание проекта на локалке через докер(заранее его запустите):
1. Форкните и скачайте репозиторий используя команду в git bash
```
        git clone git@github.com:*Ваш username*/foodgram-project-react.git
```
2. Откройте проект в IDE и сразу же добавьте туда .env с содержимым вида:
```
  POSTGRES_DB=*название бд*
  POSTGRES_USER=*название юзера бд*
  POSTGRES_PASSWORD=*пароль для бд*
  DB_NAME=*название бд*#должно быть такое же, что и в POSTGRES_DB

  DB_HOST=foodgram_db
  DB_PORT=5432 #хост не меняйте
``` 
3. Находясь в главной директории создайте вирт. окружение используя команду:
```
  python -m venv venv
```
4. Активируйте вирт окружение:
```
  source venv/Scripts/activate
```
5.Перейдите в директорию backend и установите зависимости:
```
  cd backend/
  pip install -r requirements.txt
```
6. Сделайте миграции, но не применяйте их:
```
  #Так как в проекте используется серверный постгре, который разворачивается в докере python manage.py migrate не сработает
  python manage.py makemigrations
```
7. Откройте WSl и создайте volume для postgre:
```
  docker volume create pg_data #для примера возьмите название pg_data
```
8. Теперь запустите его из главной директории(там, где у вас находится файл .env):
```
  docker run --name foodgram_db \ #название контейнера
             --env-file .env \ #файл .env для подключения к бд
             -v pg_data:/var/lib/postgresql/data \
             postgres:13.10

  контейнер не останавливайте, он нам еще нужен.
```
9. Откройте git bash и перейдите в проект по пути, в котором он у вас лежит и выполните команду:
```
  docker build -t foodgram_backend .  #создание образа бекенд части фудграма
```
10. В WSL создайте сеть из контейнеров:
```
  docker network create django-network
```
11. Присоедините контейнер с бд к сети используя команду:
```
  docker network connect django-network foodgram_db #не забудьте, что контейнер у вас должен быть активен
```
12. Контейнер с бекендом у нас пока не подключен, добавим его в сеть прямо при старте используя команду:
```
  docker run --env-file .env \
             --network django-network \
             --name foodgram_backend_container \
             -p 8000:8000 foodgram_backend
  команду надо выполнять из главной директории проекта.
```
13. Теперь выполняем миграции. Откройте WSL и выполните команду:
```
  docker exec foodgram_backend_container python manage.py migrate
```
14. Проверьте, что внутри бд миграции выполнились успешно:
```
  docker exec -it foodgram_db psql -U *Значение из переменной POSTGRES_USER* -d *значение из переменой POSTGRES_DB*
  в консоли введите команду \dt -она выведет список всех таблиц в базе данных
```    
15. Миграции успешно применились, теперь остановите и удалите два контейнера:
```
  docker stop foodgram_db
  docker rm foodgram_db
  docker stop foodgram_backend_container
  docker rm foodgram_backend_container
```
16. Перейдите в директорию, где лежит файл docker-compose.yml и выполните команду:
```
  docker compose stop && docker compose up --build
```
17. Из этой же директории выполните миграции:
```
  docker compose exec backend python manage.py migrate
  Осталось собрать статику бекенда и перенести в volume для статики(он создатся автоматически, так как уже добавлен в файле docker-compose.yml).
```
18. Перейдите в директорию, где лежит файл docker-compose.yml и выполните команду:
```
  docker compose exec backend python manage.py collectstatic
  docker compose exec backend cp -r collected_static/. ../backend_static/static/

  Откройте в браузере страницу по адресу localhost:8000/admin/ и убедитесь, что статика успешно добавилась.
```
19. Для создания суперюзера через докер откройте WSL и используйте команду:
```
  docker ps #найдите ваш контейнер backend и скопируйте его <container_id>
  docker exec -it <container_id> bash #вход в контейнер
  python manage.py createsuperuser #далее вводите всё, что вам пишет в консоли и у вас создатся суперюзер для входа в админку

  Если, все вышло успешно, то поздравляю, вы успешно на локалке развернули проект.
```
### Развертывание проект на боевом(удаленном) сервере:
#Для того, чтобы развернуть проект на удаленке вам для начала надо успешно развернуть проект на локалке
1. Добавьте в settings.py строку:
```
  ALLOWED_HOSTS = ['*IP вашего удаленного сервера*', '127.0.0.1', 'localhost', '*ваше доменное имя*']
```
2. Зарегистрируйтесь на DockerHub, после авторизуйтесь используя команду:
```
  docker login #выполняем команду внутри проекта
```
3. Собираем образы в директориях frontend/, backend/ и gateway/:
```
  cd frontend  # В директории frontend...
  docker build -t *ваш username на dockerhub*/foodgram_frontend .  # ...сбилдить образ, назвать его taski_frontend
  cd ../backend  # То же в директории backend...
  docker build -t *ваш username на dockerhub*/foodgram_backend .
  cd ../gateway  # ...то же и в gateway
  docker build -t *ваш username на dockerhub*/foodgram_gateway . 
```
4. Отправьте собранные образы фронтенда, бэкенда и Nginx на DockerHub:
```
  docker push *ваш username на dockerhub*/foodgram_frontend
  docker push *ваш username на dockerhub*/foodgram_backend
  docker push *ваш username на dockerhub*/foodgram_gateway
```
5. Откройте файл docker-compose.production.yml и поменяйте в backend, frontend и gateway строку image :
```
  image: *ваш username на dockerhub*/foodgram_backend
  image: *ваш username на dockerhub*/foodgram_frontend
  image: *ваш username на dockerhub*/foodgram_gateway
```
6. Запустите docker compose с этой конфигурацией используя команду:
```
  docker compose -f docker-compose.production.yml up
```
7. Сразу же соберите статику:
```
  docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
  docker compose -f docker-compose.production.yml exec backend cp -r collected_static/. ../backend_static/static/
```
8. Выполните миграции:
```
  docker compose -f docker-compose.production.yml exec backend python manage.py migrate
  После зайдите на ваш сервер, убедитесь, что у вас есть 2-3 лишних гб на сервере для развертывания проекта.
```
9. Как только убедились - устанавливаем Docker и Docker Compose для Linux:
```
  sudo apt update
  sudo apt install curl
  curl -fSL https://get.docker.com -o get-docker.sh
  sudo sh ./get-docker.sh
  sudo apt-get install docker-compose-plugin
  #выполните эти команды поочередно
```
10. Установите nginx:
```
  sudo apt install nginx
```
11. И запустите его:
```
  sudo systemctl start nginx
```
12. Убедитесь, что Nginx успешно запущен:
```
  sudo systemctl status nginx
```
13. Настройте автозапуск Nginx при старте системы:
```
  sudo systemctl enable nginx
  В главном пути на удаленном сервере создайте директорию foodgram.
```
13. Внутри этой директории создайте файл docker-compose.production.yml используя команду:
```
  sudo nano docker-compose.production.yml
  #добавьте в него содержимое из локального docker-compose.production.yml
    
  Также поступите с файлом .env внутри foodgram.

  Получите доменное имя на сайте https://www.noip.com/#как по мне там удобнее всего
```
14. На сервере в редакторе nano откройте конфиг Nginx: 
```
  sudo nano /etc/nginx/sites-enabled/default\
```
15. Добавьте в него такое содержимое:
```
  server {
      server_name *ваше доменное имя*;

      location / {
      proxy_set_header Host $http_host;
      proxy_pass http://127.0.0.1:8000;
      }
      listen 80;
  }
```
16. Перезапускаем nginx:
```
  sudo systemctl reload nginx
```
17. Выполняем:
```
  sudo certbot --nginx
```
18. Выбираем свой домен.

19. Перезапускаем nginx:
```
  sudo systemctl reload nginx
```
20. Выполняем команду внутри директории foodgram:
```
  sudo docker compose -f docker-compose.production.yml up -d
```
21. Проверьте, что все нужные контейнеры запущены:
```
  sudo docker compose -f docker-compose.production.yml ps
  #Должно быть запущено 3 контейнера

  После этого откройте браузер и перейдите по своему доменноиму имени.
  Если у вас всё работает, то поздравляю, вы развернули проект на удаленном сервере.
```

### В API доступны следующие эндпоинты:

* ```/api/users/```  Get-запрос – получение списка пользователей. POST-запрос – регистрация нового пользователя. Доступно без токена.

* ```/api/users/{id}``` GET-запрос – персональная страница пользователя с указанным id (доступно без токена).

* ```/api/users/me/``` GET-запрос – страница текущего пользователя. PATCH-запрос – редактирование собственной страницы. Доступно авторизированным пользователям. 

* ```/api/users/set_password``` POST-запрос – изменение собственного пароля. Доступно авторизированным пользователям. 

* ```/api/auth/token/login/``` POST-запрос – получение токена. Используется для авторизации по емейлу и паролю, чтобы далее использовать токен при запросах.

* ```/api/auth/token/logout/``` POST-запрос – удаление токена. 

* ```/api/tags/``` GET-запрос — получение списка всех тегов. Доступно без токена.

* ```/api/tags/{id}``` GET-запрос — получение информации о теге о его id. Доступно без токена. 

* ```/api/ingredients/``` GET-запрос – получение списка всех ингредиентов. Подключён поиск по частичному вхождению в начале названия ингредиента. Доступно без токена. 

* ```/api/ingredients/{id}/``` GET-запрос — получение информации об ингредиенте по его id. Доступно без токена. 

* ```/api/recipes/``` GET-запрос – получение списка всех рецептов. Возможен поиск рецептов по тегам и по id автора (доступно без токена). POST-запрос – добавление нового рецепта (доступно для авторизированных пользователей).

* ```/api/recipes/?is_favorited=1``` GET-запрос – получение списка всех рецептов, добавленных в избранное. Доступно для авторизированных пользователей. 

* ```/api/recipes/is_in_shopping_cart=1``` GET-запрос – получение списка всех рецептов, добавленных в список покупок. Доступно для авторизированных пользователей. 

* ```/api/recipes/{id}/``` GET-запрос – получение информации о рецепте по его id (доступно без токена). PATCH-запрос – изменение собственного рецепта (доступно для автора рецепта). DELETE-запрос – удаление собственного рецепта (доступно для автора рецепта).

* ```/api/recipes/{id}/favorite/``` POST-запрос – добавление нового рецепта в избранное. DELETE-запрос – удаление рецепта из избранного. Доступно для авторизированных пользователей. 

* ```/api/recipes/{id}/shopping_cart/``` POST-запрос – добавление нового рецепта в список покупок. DELETE-запрос – удаление рецепта из списка покупок. Доступно для авторизированных пользователей. 

* ```/api/recipes/download_shopping_cart/``` GET-запрос – получение текстового файла со списком покупок. Доступно для авторизированных пользователей. 

* ```/api/users/{id}/subscribe/``` GET-запрос – подписка на пользователя с указанным id. POST-запрос – отписка от пользователя с указанным id. Доступно для авторизированных пользователей

* ```/api/users/subscriptions/``` GET-запрос – получение списка всех пользователей, на которых подписан текущий пользователь Доступно для авторизированных пользователей.
