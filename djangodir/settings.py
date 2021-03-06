"""
Django settings for djangodir project.

Generated by 'django-admin startproject' using Django 3.0.8.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '--yjqc4huj%964&yfxgpb$yq&v7j22e@x7z^ooj#g!=5ao5h+&'

# SECURITY WARNING: don't run with debug turned on in production!

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
	'corsheaders',
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'ocr',
	'huey.contrib.djhuey',
]

MIDDLEWARE = [
	'corsheaders.middleware.CorsMiddleware',
	'django.middleware.security.SecurityMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'djangodir.urls'

TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		# 'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'djangodir.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
# CORS_ORIGIN_WHITELIST = ('http://127.0.0.1:8000',)
CORS_ORIGIN_ALLOW_ALL = True

DEBUG = True
DOMAIN = "http://127.0.0.1:8001"

BAIDU_APP_ID = '19547688'
BAIDU_API_KEY = '36TjcLXSGlP2In46SBGzpsO3'
BAIDU_SECRET_KEY = 'OmY6bieqW4oQLpoGV2EWhg7m3tSCGY34'

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.mysql',
		'NAME': 'django-ocr',
		'HOST': '127.0.0.1',
		'PORT': '3306',
		'USER': 'root',
		'PASSWORD': '123456',
		'OPTIONS': {'charset': 'utf8mb4'}
	}
}

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_PATH = DOMAIN + MEDIA_URL

HUEY = {
	'huey_class': 'huey.RedisHuey',  # Huey implementation to use.
	'name': DATABASES['default']['NAME'],  # Use db name for huey.
	'results': True,  # Store return values of tasks.
	'store_none': False,  # If a task returns None, do not save to results.
	'immediate': False,  # If DEBUG=True, run synchronously.
	'utc': True,  # Use UTC for all times internally.
	'blocking': True,  # Perform blocking pop rather than poll Redis.
	'connection': {
		'host': 'localhost',
		'port': 6379,
		'db': 0,
		'connection_pool': None,  # Definitely you should use pooling!
		# ... tons of other options, see redis-py for details.

		# huey-specific connection parameters.
		'read_timeout': 1,  # If not polling (blocking pop), use timeout.
		'url': None,  # Allow Redis config via a DSN.
	},
	'consumer': {
		'workers': 1,
		'worker_type': 'thread',
		'initial_delay': 0.1,  # Smallest polling interval, same as -d.
		'backoff': 1.15,  # Exponential backoff using this rate, -b.
		'max_delay': 10.0,  # Max possible polling interval, -m.
		'scheduler_interval': 1,  # Check schedule every second, -s.
		'periodic': True,  # Enable crontab feature.
		'check_worker_health': True,  # Enable worker health checks.
		'health_check_interval': 1,  # Check worker health every second.
	},
}
