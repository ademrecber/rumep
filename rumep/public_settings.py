"""Database-free public website. Legacy database/admin settings remain separate."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get('SECRET_KEY', '')
DEBUG = False
ALLOWED_HOSTS = ['rumep.net', 'www.rumep.net', '.up.railway.app', 'localhost', '127.0.0.1', 'testserver']
ROOT_URLCONF = 'rumep.public_urls'
WSGI_APPLICATION = 'rumep.public_wsgi.application'
INSTALLED_APPS = ['django.contrib.staticfiles', 'django.contrib.messages']
DATABASES = {'default': {'ENGINE': 'django.db.backends.dummy'}}
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]
MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'
TEMPLATES = [{'BACKEND': 'django.template.backends.django.DjangoTemplates',
              'DIRS': [BASE_DIR / 'main/templates'], 'APP_DIRS': True,
              'OPTIONS': {'context_processors': [
                  'django.template.context_processors.request',
                  'django.contrib.messages.context_processors.messages']}}]
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'main/static']
STORAGES = {'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage'}}
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CSRF_TRUSTED_ORIGINS = ['https://rumep.net', 'https://www.rumep.net', 'https://*.up.railway.app']
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
LANGUAGE_CODE = 'tr'
TIME_ZONE = 'Europe/Istanbul'
USE_TZ = True
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_TIMEOUT = 10
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')

