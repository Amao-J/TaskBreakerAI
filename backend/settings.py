from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
import os

import dj_database_url

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

#SECRET_KEY = os.getenv('SECRET_KEY')
SECRET_KEY = 'Sj8iAUPjSTuMb6D8AqGgjVAJcgz1KTNHtV+KkpguWGc='

DEBUG = True

ALLOWED_HOSTS = ['pina1-db.onrender.com']

CSRF_COOKIE_SECURE = False

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'api',
    'rest_framework',
    'corsheaders',
    'django.contrib.sites',
    "allauth",
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'blocksite',
    
]


CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:8000', 'http://localhost:8000','http://localhost:3000','http://pina1-db.onrender.com']

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [ 
        'rest_framework.permissions.IsAuthenticated',
    ],
}


SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": [
            "profile",
            "email"
        ],
        "AUTH_PARAMS": {"access_type": "offline"},
    }
}


SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=12),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
  
]

ROOT_URLCONF = 'backend.urls'

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

SITE_ID =4


AUTH_USER_MODEL = 'api.User'

WSGI_APPLICATION = 'backend.wsgi.application'

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
}



#DATABASES = {
 #   'default': dj_database_url.config(default='postgres://amao:na52blueivy@localhost/postgres')
#}

DATABASES = {
    'default': dj_database_url.config(
      default='postgresql://amao:ZtBC3QYh6AjomosoIhySUjhPcgyj5bwC@dpg-csqtieq3esus7384j9j0-a/pina1_db'
  )
}



EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'yomijonathan8@gmail.com'
EMAIL_HOST_PASSWORD = 'zfvjowapphevcrbt'


AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

STATIC_URL = '/static/'

STATIC_ROOT=BASE_DIR / 'staticfiles'


MEDIA_URL='/media/'
MEDIA_ROOT=BASE_DIR / 'mediafiles'



CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:3000/",
        "http://127.0.0.1:3000/",
        "http://pina1-db.onrender.com"
    ]


GOOGLE_CLIENT_ID = '544667592754-iivubmf0hnuecef851fpip1hpshg74jo.apps.googleusercontent.com'
GOOGLE_SECRET = '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'

AUTHENTICATION_BACKENDS = (
    'allauth.account.auth_backends.AuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend',
)

ALLOWED_HOSTS = ['127.0.0.1', 'localhost','pina1-db.onrender.com']

# Login and Logout Redirect
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# django-allauth settings
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'



ACCOUNT_ADAPTER = 'api.adapters.CustomAccountAdapter' 
SOCIALACCOUNT_ADAPTER = 'api.adapters.CustomSocialAccountAdapter'

