import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from django.utils.csp import CSP

BASE_DIR = Path(__file__).resolve().parent.parent


def env(name, default=None):
    value = os.environ.get(name, default)
    if value is None:
        raise ImproperlyConfigured(f"Set the {name} environment variable.")
    return value


SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env("DJANGO_DEBUG", "false") == "true"
ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "members",
    "experiences",
    "ideas",
]

AUTH_USER_MODEL = "members.Member"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.csp.ContentSecurityPolicyMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "mettakin.urls"
WSGI_APPLICATION = "mettakin.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB", "mettakin"),
        "USER": env("POSTGRES_USER", "mettakin"),
        "PASSWORD": env("POSTGRES_PASSWORD"),
        "HOST": env("POSTGRES_HOST", "localhost"),
        "PORT": env("POSTGRES_PORT", "5432"),
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Runs tasks in the request for now. A worker backend comes when real work needs it.
TASKS = {"default": {"BACKEND": "django.tasks.backends.immediate.ImmediateBackend"}}

LANGUAGE_CODE = "en"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# Nothing from other origins: no trackers, no third-party scripts.
SECURE_CSP = {"default-src": [CSP.SELF]}
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

# Server errors reach the steward by email, without member content. Off when unset.
ALERT_EMAIL = env("ALERT_EMAIL", "")
EMAIL_HOST = env("EMAIL_HOST", "")
EMAIL_PORT = int(env("EMAIL_PORT", "465"))
EMAIL_USE_SSL = True
EMAIL_HOST_USER = env("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", "")
EMAIL_TIMEOUT = 10
DEFAULT_FROM_EMAIL = SERVER_EMAIL = EMAIL_HOST_USER or "webmaster@localhost"

# Replaces Django's error email, which carries the request and local variables.
# Nothing from django.security or 404s is mailed.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"debug": {"()": "django.utils.log.RequireDebugTrue"}},
    "handlers": {
        # Development only: production logs no messages, since URLs can hold titles.
        "console": {"class": "logging.StreamHandler", "filters": ["debug"]},
        "alert": {"class": "mettakin.alerts.AlertHandler", "level": "ERROR"},
        "journal": {"class": "logging.StreamHandler"},
    },
    "loggers": {
        "mettakin.deletions": {"handlers": ["journal"], "level": "INFO", "propagate": False},
        "django": {"handlers": ["console"], "level": "INFO"},
        "django.request": {"handlers": ["console", "alert"], "level": "ERROR", "propagate": False},
    },
}
