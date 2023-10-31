# YaTube
Проект социальной сети блогеров. 
Написан на чистом Django без использования Frontend-приложения.

## Стек технологий
Python 3.9
Django 2.2.16

## Как запустить проект в тестовом режиме.
- Клонировать проект на жесткий диск.
### Backend
(Windows)
- В папке /backend создать виртуальное окружение: $ python -m venv venv
- Активировать виртуальное окружение: $ source venv/Scripts/Activate
(Linux)
- В папке /backend создать виртуальное окружение: $ python3 -m venv venv
- Активировать виртуальное окружение: $ source source venv/bin/activate
Далее
- Установить зависимости: $ pip install -r requirements.py
- Выполнить миграции БД: $ python manage.py migrate
- Для доступа в админ-панель создайте супер-пользователя: $ python manage.py createsuperuser
- Запустить проект: $ python manage.py runserver
  Главная страница: http://127.0.0.1:8000/
  Админ-панель: http://127.0.0.1:8000/admin/
