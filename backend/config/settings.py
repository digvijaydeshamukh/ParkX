from pathlib import Path
from decouple import config
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

PROJECT_ROOT = BASE_DIR.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config(
    "DEBUG",
    default=False,
    cast=bool,
)

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="",
    cast=lambda v: [host.strip() for host in v.split(",") if host.strip()],
)


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    "drf_spectacular",
]

LOCAL_APPS = [
    'accounts',
]

INSTALLED_APPS += LOCAL_APPS

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}

# SPECTACULAR_SETTINGS = {
#     "TITLE": "ParkX API",
#     "DESCRIPTION": "Backend APIs for the ParkX Parking Management System",
#     "VERSION": "1.0.0",
# }

SPECTACULAR_SETTINGS = {
    "TITLE": "ParkX API",
    "DESCRIPTION": "Backend APIs for the ParkX Parking Management System",
    "VERSION": "1.0.0",

    "COMPONENTS": {
        "securitySchemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        }
    },
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR.parent / 'frontend' / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST"),
        "PORT": config("DB_PORT", cast=int),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = "Asia/Kolkata"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

STATICFILES_DIRS = [
    BASE_DIR.parent / "frontend" / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = "accounts.User"

# Application settings
PENDING_REGISTRATION_EXPIRY_DAYS = config(
    "PENDING_REGISTRATION_EXPIRY_DAYS",
    default=7,
    cast=int,
)

OTP_EXPIRY_MINUTES = config(
    "OTP_EXPIRY_MINUTES",
    default=5,
    cast=int,
)

OTP_LENGTH = config(
    "OTP_LENGTH",
    default=6,
    cast=int,
)

USERNAME_PREFIX = config(
    "USERNAME_PREFIX",
    default="parkx_",
)

OTP_RESEND_COOLDOWN_SECONDS = int(
    config("OTP_RESEND_COOLDOWN_SECONDS", "60")
)


#Email settings
EMAIL_HOST = config("EMAIL_HOST")

EMAIL_PORT = config(
    "EMAIL_PORT",
    cast=int,
)

EMAIL_HOST_USER = config("EMAIL_HOST_USER")

EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")

EMAIL_USE_TLS = config(
    "EMAIL_USE_TLS",
    cast=bool,
)


