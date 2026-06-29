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

3. Примените миграции (если бд не подготовлена):

```bash
python manage.py migrate
```

4. Запустите сервер разработки:

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

При старте контейнера `web` автоматически выполняется `migrate`. Сервер будет доступен по адресу: http://localhost:8000

Для остановки выполните:

```bash
docker compose down
```

## Заполнение тестовыми данными (`fill_db`)

Команда создаёт пользователей, вопросы, ответы, теги и лайки. Аргумент **ratio** — коэффициент наполнения (целое число ≥ 1): чем больше `ratio`, тем больше записей (пользователей `ratio`, вопросов `ratio×10`, ответов `ratio×100` и т.д.).

Пароль у созданных пользователей для входа: `password123` (логины `user_0`, `user_1`, …).

### На локалке

Из активированного виртуального окружения, из корня проекта:

```bash
python manage.py migrate
python manage.py fill_db 10
```

### В Docker

```bash
docker compose exec web python manage.py fill_db 10
```

Число `10` можно заменить на любой другой `ratio` ≥ 1. Перед запуском настройте постгрю и переменные окружения

Сервис в `docker-compose.yml` называется `web`. Команда выполняется в том же окружении, что и приложение (PostgreSQL из compose уже доступен контейнеру `web`).

## Как настроить постгрю

Настройки подхватываются из файлов **`.env.local`** и **`.env.docker`** в корне проекта, пример — в [`.env.example`](.env.example)

### Переменные

| Переменная | Значение по умолчанию  |
|------------|------------------------------|
| `POSTGRES_DB` | `PostgreSQL` |
| `POSTGRES_USER` | `postgres` |
| `POSTGRES_PASSWORD` | `пустая строка` |
| `POSTGRES_HOST` | `localhost` |
| `POSTGRES_PORT` | `5432` |

### Запуск PostgreSQL

**Отдельно через докер**:

1. Поднимите контейнер с PostgreSQL 

```bash
docker run -d --name vkedu-pg -e POSTGRES_DB=vkedu_web -e POSTGRES_USER=vkedu -e POSTGRES_PASSWORD=vkedu -p 5433:5432 postgres:16-alpine
```

2. Заполните `env.local`

3. Выполните `python manage.py migrate` (и при необходимости `fill_db`) из venv.

**Сразу через докер**: 

Постгря и приложение уже описаны в [`docker-compose.yml`](docker-compose.yml); переменные для `web` заданы в compose, отдельный `.env.local` для контейнера не обязателен, если не переопределяете значения. Сервис `db` поднимает постгрю; приложение в `web` подключается к нему по `POSTGRES_HOST=127.0.0.1` и `POSTGRES_PORT=5432` внутри контейнера.