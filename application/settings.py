import os
import sys
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env.local")
load_dotenv(BASE_DIR / ".env.docker")

SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-dev-only-change-in-env",
)

DEBUG = os.environ.get("DEBUG", "True").lower() in ("1", "true", "yes")

_raw_hosts = os.environ.get("ALLOWED_HOSTS", "").strip()
ALLOWED_HOSTS = [h.strip() for h in _raw_hosts.split(",") if h.strip()] if _raw_hosts else []

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.postgres",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "core",
    "questions",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "core.middleware.InvalidateDeletedUserMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if DEBUG and not (len(sys.argv) > 1 and sys.argv[1] == "test"):
    INSTALLED_APPS = [*INSTALLED_APPS, "debug_toolbar"]
    MIDDLEWARE = [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
        *MIDDLEWARE,
    ]

ROOT_URLCONF = "application.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
            BASE_DIR / "core" / "templates",
            BASE_DIR / "questions" / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "application.wsgi.application"


_db_name = os.environ.get("POSTGRES_DB") or os.environ.get("DB_NAME")
if _db_name:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": _db_name,
            "USER": os.environ.get("POSTGRES_USER")
            or os.environ.get("DB_USER", "postgres"),
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD")
            or os.environ.get("DB_PASSWORD", ""),
            "HOST": os.environ.get("POSTGRES_HOST")
            or os.environ.get("DB_HOST", "localhost"),
            "PORT": os.environ.get("POSTGRES_PORT")
            or os.environ.get("DB_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [
    BASE_DIR / "static",
    BASE_DIR / "questions" / "static",
]

MEDIA_URL = "media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

INTERNAL_IPS = ["127.0.0.1"]

if DEBUG:
    def _show_debug_toolbar(request):
        return True

    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK": _show_debug_toolbar,
    }
    
CENTRIFUGO_HOST = os.environ.get("CENTRIFUGO_HOST", "localhost")
CENTRIFUGO_PORT = os.environ.get("CENTRIFUGO_PORT", "9000")
CENTRIFUGO_API_KEY = os.environ.get("CENTRIFUGO_API_KEY", "17I-1zkkrLHHMeK_nOzCW7oxtYCGWvHJqXtsyIHKTkDrxBJblIK4vFsdJvyCBMGshh5z_Gk0Cu0yDBrdwYtiAA")
CENTRIFUGO_TOKEN_KEY = os.environ.get("CENTRIFUGO_TOKEN_KEY", "vheAhEAv99bP68zPTexlGCl7cyIbHXgq_v-r_Sh7wUEKmXn6q3D6tm5A06ksFBjEG3NokcJ96KicBdpzBp9HFw")

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = os.environ.get("REDIS_PORT", "6379")
REDIS_CACHE_DB = os.environ.get("REDIS_CACHE_DB", "1")
REDIS_BROKER_DB = os.environ.get("REDIS_BROKER_DB", "2")
REDIS_BEAT_DB = os.environ.get("REDIS_BEAT_DB", "3")

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CACHE_DB}",
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        "TIMEOUT": 60 * 10,
    }
}

CELERY_BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_BROKER_DB}"
CELERY_RESULT_BACKEND = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_BEAT_DB}"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"

CELERY_BEAT_SCHEDULER = "redbeat.RedBeatScheduler"
CELERY_REDBEAT_REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_BEAT_DB}"

CELERY_BEAT_SCHEDULE = {
    "recalc-popular-tags-every-hour": {
        "task": "questions.tasks.recalculate_popular_tags_cache",
        "schedule": 60 * 60,
        "args": (10,),
    },
    "recalc-best-members-every-15-min": {
        "task": "questions.tasks.recalculate_best_members_cache",
        "schedule": 15 * 60,
        "args": (10,),
    }
}

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST", "maildev")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "1025"))
EMAIL_USE_TLS =  os.environ.get("EMAIL_USE_TLS", "False").lower() in ("1", "true", "yes")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@local.dev")