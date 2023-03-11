## Blog Publishing Project

Блог-платформа **Yatube** (она же социальная сеть) для публикации постов, комментирования чужих творений, подписки на интересных авторов.
Проба пера, знакомство с _Django_, попытка создать проект самому.

В проекте использованы: `Python 3.9, Django 4.0.3, SQLite, HTML, CSS, unittest, etc.`

### Инструкция по запуску
- Склонируйте проект `git clone https://github.com/Andrey-Kugubaev/yatube_project_n.git` 
- установите и активируйте виртуальное окружение
`python -m venv venv (или python3 -m venv venv) / source venv/Scripts/activate (или source venv/bin/activate)`
- установите зависимости `pip install -r requirements.txt`
- создайте файл `.env`, где пропишите ключ для _settings.py_
- создать базу данных и выполнить миграции `python manage.py makemigrations`
`python manage.py migrate`
- запустите сервер `python manage.py runserver`
