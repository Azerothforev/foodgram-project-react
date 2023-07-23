# praktikum_new_diplom
развертывание проекта на локалке через докер(заранее его запустите):
    скачайте репозиторий используя команду в git bash
        git clone git@github.com:*Ваш username*/foodgram-project-react.git

    откройте проект в IDE и сразу же добавьте туда .env с содержимым вида
        POSTGRES_DB=*название бд*
        POSTGRES_USER=*название юзера бд*
        POSTGRES_PASSWORD=*пароль для бд*
        DB_NAME=*название бд*#должно быть такое же, что и в POSTGRES_DB

        DB_HOST=foodgram_db
        DB_PORT=5432 #хост не меняйте
    
    находясь в главной директории создайте вирт. окружение используя команду:
        python -m venv venv

    активируйте вирт окружение:
        source venv/Scripts/activate

    перейдите в директорию backend и установите зависимости:
        cd backend/
        pip install -r requirements.txt

    сделайте миграции, но не применяйте их:
    #так как в проекте используется серверный постгре, который разворачивается в докере python manage.py migrate не сработает
        python manage.py makemigrations

    откройте WSl и создайте volume для postgre:
        docker volume create pg_data #для примера возьмите название pg_data

    теперь запустите его из главной директории(там, где у вас находится файл .env):
        docker run --name foodgram_db \ #название контейнера
               --env-file .env \ #файл .env для подключения к бд
               -v pg_data:/var/lib/postgresql/data \
               postgres:13.10

        контейнер не останавливайте, он нам еще нужен.

    откройте git bash и перейдите в проект по пути, в котором он у вас лежит и выполните команду:
        docker build -t foodgram_backend .  #создание образа бекенд части фудграма
    
    в WSL создайте сеть из контейнеров:
        docker network create django-network

    присоедините контейнер с бд к сети используя команду:
        docker network connect django-network foodgram_db #не забудьте, что контейнер у вас должен быть активен

    контейнер с бекендом у нас пока не подключен, добавим его в сеть прямо при старте используя команду:
        docker run --env-file .env \
                   --network django-network \
                   --name foodgram_backend_container \
                   -p 8000:8000 foodgram_backend
        команду надо выполнять из главной директории проекта.

    теперь выполняем миграции. Откройте WSL и выполните команду:
        docker exec foodgram_backend_container python manage.py migrate
    
    проверьте, что внутри бд миграции выполнились успешно:
        docker exec -it foodgram_db psql -U *Значение из переменной POSTGRES_USER* -d *значение из переменой POSTGRES_DB*
        в консоли введите команду \dt -она выведет список всех таблиц в базе данных
    
    миграции успешно применились, теперь остановите и удалите два контейнера:
        docker stop foodgram_db
        docker rm foodgram_db
        docker stop foodgram_backend_container
        docker rm foodgram_backend_container

    Перейдите в директорию, где лежит файл docker-compose.yml и выполните команду:
        docker compose stop && docker compose up --build
    
    Из этой же директории выполните миграции:
        docker compose exec backend python manage.py migrate

    осталось собрать статику бекенда и перенести в volume для статики(он создатся автоматически, так как уже добавлен в файле docker-compose.yml).
    Перейдите в директорию, где лежит файл docker-compose.yml и выполните команду:
        docker compose exec backend python manage.py collectstatic
        docker compose exec backend cp -r collected_static/. ../backend_static/static/

    откройте в браузере страницу по адресу localhost:8000/admin/ и убедитесь, что статика успешно добавилась.
    
    для создания суперюзера через докер откройте WSL и используйте команду:
        docker ps #найдите ваш контейнер backend и скопируйте его <container_id>
        docker exec -it <container_id> bash #вход в контейнер
        python manage.py createsuperuser #далее вводите всё, что вам пишет в консоли и у вас создатся суперюзер для входа в админку

    Если, все вышло успешно, то поздравляю, вы успешно на локалке развернули проект.

Развертывание проект на боевом(удаленном) сервере:
#для того, чтобы развернуть проект на удаленке вам для начала надо успешно развернуть проект на локалке
    Добавьте в settings.py строку:
        ALLOWED_HOSTS = ['*IP вашего удаленного сервера*', '127.0.0.1', 'localhost', '*ваше доменное имя*']

    Зарегистрируйтесь на DockerHub, после авторизуйтесь используя команду:
        docker login #выполняем команду внутри проекта

    Собираем образы в директориях frontend/, backend/ и gateway/:
        cd frontend  # В директории frontend...
        docker build -t *ваш username на dockerhub*/foodgram_frontend .  # ...сбилдить образ, назвать его taski_frontend
        cd ../backend  # То же в директории backend...
        docker build -t *ваш username на dockerhub*/foodgram_backend .
        cd ../gateway  # ...то же и в gateway
        docker build -t *ваш username на dockerhub*/foodgram_gateway . 

    Отправьте собранные образы фронтенда, бэкенда и Nginx на DockerHub:
        docker push *ваш username на dockerhub*/foodgram_frontend
        docker push *ваш username на dockerhub*/foodgram_backend
        docker push *ваш username на dockerhub*/foodgram_gateway

    откройте файл docker-compose.production.yml и поменяйте в backend, frontend и gateway строку image :
        image: *ваш username на dockerhub*/foodgram_backend
        image: *ваш username на dockerhub*/foodgram_frontend
        image: *ваш username на dockerhub*/foodgram_gateway
    
    запустите docker compose с этой конфигурацией используя команду:
        docker compose -f docker-compose.production.yml up
    
    сразу же соберите статику:
        docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
        docker compose -f docker-compose.production.yml exec backend cp -r collected_static/. ../backend_static/static/
    
    выполните миграции:
        docker compose -f docker-compose.production.yml exec backend python manage.py migrate
    
    после зайдите на ваш сервер, убедитесь, что у вас есть 2-3 лишних гб на сервере для развертывания проекта.
    Как только убедились - устанавливаем Docker и Docker Compose для Linux:
        sudo apt update
        sudo apt install curl
        curl -fSL https://get.docker.com -o get-docker.sh
        sudo sh ./get-docker.sh
        sudo apt-get install docker-compose-plugin
        #выполните эти команды поочередно

    установите nginx:
        sudo apt install nginx

    и запустите его:
        sudo systemctl start nginx

    Убедитесь, что Nginx успешно запущен:
        sudo systemctl status nginx

    Настройте автозапуск Nginx при старте системы:
        sudo systemctl enable nginx

    в главном пути на удаленном сервере создайте директорию foodgram.
    внутри этой директории создайте файл docker-compose.production.yml используя команду:
        sudo nano docker-compose.production.yml
        #добавьте в него содержимое из локального docker-compose.production.yml
    
    также поступите с файлом .env внутри foodgram.

    получите доменное имя на сайте https://www.noip.com/#как по мне там удобнее всего

    На сервере в редакторе nano откройте конфиг Nginx: 
        sudo nano /etc/nginx/sites-enabled/default\

    добавьте в него такое содержимое:
        server {
            server_name *ваше доменное имя*;

            location / {
                proxy_set_header Host $http_host;
                proxy_pass http://127.0.0.1:8000;
            }
            listen 80;
        }
    
    перезапускаем nginx:
        sudo systemctl reload nginx

    Выполняем:
        sudo certbot --nginx
    Выбираем свой домен.

    Перезапускаем nginx:
        sudo systemctl reload nginx
    
    выполняем команду внутри директории foodgram:
        sudo docker compose -f docker-compose.production.yml up -d
    
    Проверьте, что все нужные контейнеры запущены:
        sudo docker compose -f docker-compose.production.yml ps
    #должно быть запущено 3 контейнера

    После этого откройте браузер и перейдите по своему доменноиму имени.
    Если у вас всё работает, то поздравляю, вы развернули проект на удаленном сервере.
