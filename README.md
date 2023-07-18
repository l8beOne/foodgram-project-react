# Foodrgam

## Описание проекта:
«Продуктовый помощник» — это сайт, на котором можно публиковать собственные рецепты, добавлять чужие рецепты в избранное, подписываться на других авторов и создавать список покупок для заданных блюд.
## Технологии:
* Python 3.9.10
* Django 3.2
* Django Rest Framework 3.12.4
* PostgreSQL
* API
* JWT
* Postman
* Nginx
* Docker
* JSON
* YAML
* Telegram
## Развертывание проекта на сервере:

1. Установите на сервере `docker` и `docker-compose`.
2. Создайте файл .env в заведомо созданной дирректории foodgram на сервере. Шаблон для создания этого файла: `.env.example`.
3. Добавьте в файл main.yml строку: `sudo docker compose -f docker-compose.yml exec backend python manage.py loading_csv_files`.
4. Сделайте пуш в свой аккаунт на GitHub, после этого запустится workflow и сделает все действия для того, чтобы сервер работал.
5. Документация к API находится по адресу: <http://localhost/api/docs/redoc.html>.
## Автор
Климентий Пролецкий (l8beOne)