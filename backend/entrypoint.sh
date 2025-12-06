#!/bin/sh

# Abort the script if any command fails
set -e

# --- User and Permission Management ---
# Get the host user's UID and GID from environment variables
PUID=${HOST_UID:-1000}
PGID=${HOST_GID:-1000}

# Check if the appuser's UID and GID match the host's
CURRENT_UID=$(id -u appuser)
CURRENT_GID=$(id -g appuser)

if [ "$CURRENT_UID" != "$PUID" ] || [ "$CURRENT_GID" != "$PGID" ]; then
    echo "---> Updating appuser UID to $PUID and GID to $PGID..."
    # Change the UID and GID of the appuser
    groupmod -o -g "$PGID" appuser
    usermod -o -u "$PUID" appuser
fi

# --- Project Initialization ---
# Check if manage.py exists. If not, initialize the Django project.
if [ ! -f "manage.py" ]; then
    echo "---> Initializing Django project..."

    # Create Django project and apps
    django-admin startproject config .
    mkdir -p apps/core
    python manage.py startapp core apps/core
    mkdir -p apps/users
    python manage.py startapp users apps/users

    # Correct the app names in their AppConfig
    sed -i "s/name = 'core'/name = 'apps.core'/" apps/core/apps.py
    sed -i "s/name = 'users'/name = 'apps.users'/" apps/users/apps.py

    # Create the wait_for_db management command
    mkdir -p apps/core/management/commands
    touch apps/core/management/__init__.py
    touch apps/core/management/commands/__init__.py

    # Create wait_for_db.py command
    cat <<'EOF' > apps/core/management/commands/wait_for_db.py
import time
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError

class Command(BaseCommand):
    """Django command to pause execution until database is available"""
    
    help = 'Wait for database to be available'

    def add_arguments(self, parser):
        parser.add_argument(
            '--timeout',
            type=int,
            default=60,
            help='Maximum time to wait for database (seconds)'
        )

    def handle(self, *args, **options):
        self.stdout.write('Waiting for database...')
        timeout = options['timeout']
        start_time = time.time()
        db_conn = None
        
        while not db_conn:
            try:
                db_conn = connections['default']
                with db_conn.cursor() as cursor:
                    cursor.execute('SELECT 1')
                break
            except OperationalError:
                if time.time() - start_time > timeout:
                    self.stderr.write(
                        self.style.ERROR(
                            f'❌ Database connection timeout after {timeout} seconds'
                        )
                    )
                    raise
                self.stdout.write('⏳ Database unavailable, waiting 1 second...')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('✅ Database available!'))
EOF

    # Create structured settings directory
    mkdir -p config/settings
    touch config/settings/__init__.py

    # Create config/settings/base.py
    cat <<'EOF' > config/settings/base.py
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Applications
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'corsheaders',
]

LOCAL_APPS = [
    'apps.core',
    'apps.users',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "config.wsgi.application"

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    { "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator", },
    { "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", },
    { "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator", },
    { "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator", },
]

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
EOF

    # Create config/settings/development.py
    cat <<'EOF' > config/settings/development.py
import os
from .base import *

# Development settings
DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "backend"]

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB"),
        "USER": os.environ.get("POSTGRES_USER"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
        "HOST": os.environ.get("POSTGRES_HOST"),
        "PORT": os.environ.get("POSTGRES_PORT"),
    }
}
EOF

    # Create config/settings/production.py
    cat <<'EOF' > config/settings/production.py
from .base import *

# Production configuration
DEBUG = False

# Replace with your production sites domain
ALLOWED_HOSTS = ["yoursite.com", "www.yoursite.com"]
EOF

    # Remove the original settings file
    rm config/settings.py

    # Update manage.py, asgi.py, and wsgi.py to use the new settings
    sed -i "s/os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')/os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')/" manage.py
    sed -i "s/os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')/os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')/" config/asgi.py
    sed -i "s/os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')/os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')/" config/wsgi.py

    # Create main URLs configuration
    cat <<'EOF' > config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.core.urls')),
    path('api/users/', include('apps.users.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
EOF

    # Create Celery configuration
    cat <<'EOF' > config/celery.py
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
EOF

    # Update config/__init__.py to import celery
    # Note: This might need adjustment depending on final project structure
    cat <<'EOF' > config/__init__.py
# This file can be left empty or used for package-level initializations.
from .celery import app as celery_app

__all__ = ('celery_app',)
EOF

    # Create core app URLs and views
    cat <<'EOF' > apps/core/urls.py
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('health/', views.health_check, name='health-check'),
]
EOF

    cat <<'EOF' > apps/core/views.py
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return JsonResponse({
        'status': 'ok',
        'message': 'API is running'
    })
EOF

    # Create core app serializers
    cat <<'EOF' > apps/core/serializers.py
from rest_framework import serializers

# Core serializers will go here
EOF

    # Create users app URLs, views, and serializers
    cat <<'EOF' > apps/users/urls.py
from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # User URLs will go here
]
EOF

    cat <<'EOF' > apps/users/views.py
from rest_framework import viewsets
from django.contrib.auth.models import User

# User views will go here
EOF

    cat <<'EOF' > apps/users/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')
        read_only_fields = ('id',)
EOF

    # Make sure apps/__init__.py exists
    touch apps/__init__.py

    echo "---> Django project initialized."
fi

# --- Runtime Operations ---
# Ensure the app directory and volumes are owned by the appuser
echo "---> Setting permissions..."
chown -R appuser:appuser /app

# Check if DJANGO_SETTINGS_MODULE is set
if [ -z "$DJANGO_SETTINGS_MODULE" ]; then
  echo "Error: DJANGO_SETTINGS_MODULE is not set."
  exit 1
fi

echo "Waiting for the database..."
gosu appuser python manage.py wait_for_db

echo "Applying database migrations..."
gosu appuser python manage.py migrate

echo "Collecting static files..."
gosu appuser python manage.py collectstatic --noinput

# Executes the main command of the container as the appuser
echo "---> Starting server..."
exec gosu appuser "$@"
