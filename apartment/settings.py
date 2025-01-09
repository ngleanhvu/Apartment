"""
Django settings for apartment project.

Generated by 'django-admin startproject' using Django 5.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""
import hashlib
import hmac
import uuid
from pathlib import Path

from django.conf.global_settings import INTERNAL_IPS

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-!rbys3%m8k5bvdyuqwn8x%^%-n!@h3#hf^lpc0g(p2alcms&75'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '10.0.2.2']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apartmentapp.apps.ApartmentAppConfig',
    'ckeditor',
    'ckeditor_uploader',
    'drf_yasg',
    'oauth2_provider',
    'corsheaders'
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
    )
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware'
]

CORS_ALLOW_ALL_ORIGINS = True

ROOT_URLCONF = 'apartment.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'apartment.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'apartment_db',
        'USER': 'root',
        'PASSWORD': '1234',
    }
}

AUTH_USER_MODEL = 'apartmentapp.User'

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

CKEDITOR_UPLOAD_PATH = 'upload_ckeditor_dir/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

import cloudinary

cloudinary.config(
    cloud_name="dea1l3vvu",
    api_key="632729326888512",
    api_secret="lOmmfYvysmFHA1lgmPZRg0hUuZM",
    secure=True
)

OAUTH2_PROVIDER = {'OAUTH2_BACKEND_CLASS': 'oauth2_provider.oauth2_backends.JSONOAuthLibCore'}

# Stripe
STRIPE_TEST_SECRET_KEY = 'sk_test_51QVllgLGRlPpjKfjbEEn7dEVvjYxYgwsUigFw7vBqjfcFnGWSNXJYBihEGEb1Krw08HyRzHVn5Ja3joFMb3oNf6t007VdyyRUh'
STRIPE_TEST_PUBLIC_KEY = 'pk_test_51QVllgLGRlPpjKfjb0kJx1duZJodKVhBPgUrlEqAWHSweobrx0xToWMeFmfwbfMQ72QOzSOTnDyqjR5Fq6XODa1H007P3RGFcj'
STRIPE_TEST_ENDPOINT_SECRET = 'whsec_SlMnWE5i83YxE1DOGXnHQDIFGzX9kBm8'
STRIPE_TEST_SUCCESS_URL = 'http://127.0.0.1:8000/success/'
STRIPE_TEST_ERROR_URL = 'http://127.0.0.1:8000/cancel/'

# Momo
# parameters send to MoMo get get payUrl
MOMO_END_POINT = "https://test-payment.momo.vn/v2/gateway/api/create"
MOMO_PATTERN_CODE = "MOMO"
MOMO_ACCESS_KEY = "F8BBA842ECF85"
MOMO_SECRET_KEY = "K951B6PE1waDMi640xX08PD3vg6EkVlz"
MOMO_RETURN_URL = "apm://payment/success"
MOMO_NOTIFY_URL = "http://127.0.0.1:8000/api/payment/webhook/momo/"
MOMO_REQUEST_TYPE = "captureWallet"
MOMO_REDIRECT_URL = 'apm://payment/success'
MOMO_IPN_URL = 'https://478a-14-186-144-166.ngrok-free.app/transactions/webhook/momo/'
