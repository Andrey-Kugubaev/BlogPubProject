# yatube_project_n
Социальная сеть блогеров

###Название проекта
Yatube
###Краткое описание
социальная сеть
###Технологии в проекте
Python 3.9
Django 4.0.3
###Инструкция по запуску
- Установите и активируйте виртуальное окружение
####для развертывания проекта на другой машине необходимо выполнять
- pip install -r requirements.txt
###Автор
Андрей Грин



###Команды по ходу проекта
####обновелние пакета pip
_python -m pip install --upgrade pip_
####Устновка DjanGo
_pip install Django_
####создание проекта, его базовой структуры (точка запускает проект в текущей дериктории)
_django-admin startproject yatube ._
####создание файла зависимостей
_pip freeze > requirements.txt_
####Создание приложения и его регистрация
_django-admin startapp posts_
####Проектирование адресов в urls.py

####Добавление шаблонов

#####Ссылки, namespaсe и name
#####Подключение CSS и Static

#####Подключение функции пользвателей, подключение форм
#####Создание страниц регистрации

#####Создание раздела об авторе
_django-admin startapp about_

#####Создание страниц пользователя и отдельного поста
#####Создание страниц группы, добавления и редактированя поста

#####Написание тестов для проекта
