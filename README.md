# Платформа для обмена вещами

Система для организации бартерных обменов между пользователями.

## Требования
- Python 3.8+
- Django 4.0+

## Установка
1. Клонировать репозиторий:
```bash
git clone https://github.com/yourusername/barter_system.git
cd barter_system
Создать виртуальное окружение:

bash
python -m venv venv
source venv/bin/activate  # Linux/MacOS
venv\Scripts\activate  # Windows
Установить зависимости:

bash
pip install -r requirements.txt
Выполнить миграции:

bash
python manage.py migrate
Создать суперпользователя (опционально):

bash
python manage.py createsuperuser
Запустить сервер:

bash
python manage.py runserver
