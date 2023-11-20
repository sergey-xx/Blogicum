# Blogicum
Проект социальной сети блогеров.
### Возможности:
- писать текстовые посты
- прикреплять фото к постам
- писать текстовые комментарии к постам
- подписываться на авторов
- ставить ❤
  
Написан на чистом Django без использования Frontend-приложения.

## Стек технологий
- Python 3.9
- Django 2.2.16
- HTML
- Bootstrap

## Как запустить проект в тестовом режиме.
Клонировать проект на жесткий диск.
```
git@github.com:sergey-xx/Blogicum.git
```

### Backend
**(Windows)**

В папке /backend создать виртуальное окружение:
```shell
> python -m venv venv
```
Активировать виртуальное окружение:
```shell
> source venv/Scripts/Activate
```

**(Linux)**

В папке /backend создать виртуальное окружение:
  
```bash
$ python3 -m venv venv
```
Активировать виртуальное окружение:
```bash
$ source venv/bin/activate
```

Далее

Установить зависимости:
```bash
$ pip install -r requirements.py
```
Выполнить миграции БД:
```bash
$ python manage.py migrate
```
Для доступа в админ-панель создайте супер-пользователя:
```bash
$ python manage.py createsuperuser
```

Запустить проект:
```bash
$ python manage.py runserver
```

После запуска сервера главная страница доступна по адресу: http://127.0.0.1:8000/

Админ-панель: http://127.0.0.1:8000/admin/

Пример рабочего сайта (работает временно): http://blogicum.ddns.net/

## Стек технологий сервера:
- nginx
- Gunicorn
