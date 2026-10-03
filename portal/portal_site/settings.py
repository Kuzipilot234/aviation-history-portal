"""Django settings for Kuzey's Aviation and History Portal.

Configuration comes from environment variables. For local development,
put them in portal/.env (see .env.example).
"""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

SECRET_KEY = os.environ.get("SECRET_KEY", "")
if not SECRET_KEY:
    if not DEBUG:
        raise RuntimeError("Set the SECRET_KEY environment variable.")
    SECRET_KEY = "local-development-only-key"

# Ignore stray spaces or quotes pasted around the key in a dashboard.
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "").strip().strip("\"'")
GROQ_MODEL = "openai/gpt-oss-120b"

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
ALLOWED_HOSTS += [h for h in os.environ.get("ALLOWED_HOSTS", "").split(",") if h]
# Render sets this to the service's public hostname.
RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
CSRF_TRUSTED_ORIGINS = [f"https://{h}" for h in ALLOWED_HOSTS if h not in ("localhost", "127.0.0.1")]

INSTALLED_APPS = [
    "django.contrib.staticfiles",
    "core",
    "news",
    "ai",
    "games",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "portal_site.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.template.context_processors.i18n",
                "core.context_processors.navigation",
            ],
        },
    },
]

WSGI_APPLICATION = "portal_site.wsgi.application"

# No models yet. SQLite is here so Django features that need a database
# (accounts, admin) can be added later.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# A file cache is shared by all gunicorn workers on the same machine.
# It holds the RSS feed, the daily briefing, rate limits and sessions.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": BASE_DIR / ".cache",
    }
}
SESSION_ENGINE = "django.contrib.sessions.backends.cache"

LANGUAGE_CODE = "en"
# The site's languages. Visitors get their browser's language when it is one
# of these, and can switch with the menu in the top bar.
LANGUAGES = [
    ("en", "English"),
    ("tr", "Türkçe"),
    ("fr", "Français"),
    ("es", "Español"),
]
LOCALE_PATHS = [BASE_DIR / "locale"]
TIME_ZONE = "Europe/Istanbul"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
        if not DEBUG
        else "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
    # httpx logs every request at INFO; only show its problems.
    "loggers": {"httpx": {"level": "WARNING"}},
}
