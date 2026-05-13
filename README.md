# 2026-VK-EDU-Web-12-Mazanov-V

Django-проект для VK Education.

## Запуск проекта

### Вариант 1: Локальный запуск

1. Создайте виртуальное окружение и активируйте его:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Запустите сервер разработки:
```bash
python manage.py runserver
```

Сервер будет доступен по адресу: http://127.0.0.1:8000

### Вариант 2: Запуск через Docker Compose

1. Убедитесь, что Docker и Docker Compose установлены в вашей системе.

2. Соберите и запустите контейнеры:
```bash
docker compose up --build
```

Сервер будет доступен по адресу: http://localhost:8000

Для остановки выполните:
```bash
docker compose down
```
