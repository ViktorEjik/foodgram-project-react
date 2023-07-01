[![.github/workflows/foodgram_workflow.yml](https://github.com/ViktorEjik/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)](https://github.com/ViktorEjik/foodgram-project-react/actions/workflows/foodgram_workflow.yml)

# Foodgram

```
http:/51.250.4.81/
admin@mail.ru
login: admin
password: admin
```

### Описание
Сервис, на котором пользователи будут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволит пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

# Порядок запуска
## Запуск проекта локально
Клонировать репозиторий и перейти в него:
```
git clone https://github.com/KAChernenko/foodgram-project-react.git
```

Создать и активировать виртуальное окружение, обновить pip и установить зависимости:
```
python -m venv venv
. venv/bin/activate
python -m pip install --upgrade pip
cd backend
pip install -r requirements.txt
```

## Для запуска локально:
```
python manage.py runserver
```

Создать базу данных:
```
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

Для запуска frontend:


```
cd infra
docker-compose up -d
```

## Для работы с удаленным сервером:
* Выполните вход на свой удаленный сервер
```
ssh <username>@<ip>
```

* Установите docker на сервер:
```
sudo apt install docker.io 

```
* Установите docker-compose на сервер:
```
sudo apt install docker-compose
```
* Скопируйте файлы docker-compose.yml и nginx.conf из директории infra на сервер:
```
scp infra/docker-compose.yml <username>@<host>:/home/<username>/docker-compose.yml
scp infra/nginx.conf <username>@<host>:/home/<username>/nginx.conf
```

### Примеры api запросов:
**`GET` | Список рецептов: `http://51.250.4.81/api/recipes/`**

```
{
  "count": 123,
  "next": "http://foodgram.example.org/api/recipes/?page=4",
  "previous": "http://foodgram.example.org/api/recipes/?page=2",
  "results": [
    {
      "id": 0,
      "tags": [
        {
          "id": 0,
          "name": "Завтрак",
          "color": "#E26C2D",
          "slug": "breakfast"
        }
      ],
      "author": {
        "email": "user@example.com",
        "id": 0,
        "username": "string",
        "first_name": "Вася",
        "last_name": "Пупкин",
        "is_subscribed": false
      },
      "ingredients": [
        {
          "id": 0,
          "name": "Картофель отварной",
          "measurement_unit": "г",
          "amount": 1
        }
      ],
      "is_favorited": true,
      "is_in_shopping_cart": true,
      "name": "string",
      "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
      "text": "string",
      "cooking_time": 1
    }
  ]
}
```
