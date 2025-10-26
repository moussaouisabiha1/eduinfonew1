# --- START OF FILE app/backend/eduinfo/settings.py ---
import os
from pathlib import Path
from decouple import config # Assure-toi que cet import est en haut
import pymysql
pymysql.install_as_MySQLdb()

BASE_DIR = Path(__file__).resolve().parent.parent

# Charger les variables depuis .env ou les variables d'environnement du système
SECRET_KEY = config('SECRET_KEY') # Va chercher SECRET_KEY dans .env
DEBUG = config('DEBUG', default=False, cast=bool) # default=False si non trouvé, cast=bool convertit "True"/"False" en booléen

# ALLOWED_HOSTS depuis .env (chaîne séparée par des virgules)
# Si ALLOWED_HOSTS n'est pas dans .env, utilise 'localhost,127.0.0.1' par défaut
allowed_hosts_str = config('ALLOWED_HOSTS', default='localhost,127.0.0.1')
ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_str.split(',') if host.strip()]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'cloudinary_storage',
    'cloudinary',
    'main',
    # 'whitenoise', # On n'ajoute pas whitenoise à INSTALLED_APPS, juste le middleware
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Pour servir les statiques en prod
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'eduinfo.urls'

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

WSGI_APPLICATION = 'eduinfo.wsgi.application'

# Base de données
# Pour le développement local, on garde SQLite.
# En production, la plateforme de déploiement fournira une DATABASE_URL
# que dj_database_url (si tu l'installes) peut lire.
# Pour l'instant, cette config est OK pour le local.
import dj_database_url # Importe-le si tu l'as installé (pip install dj_database_url)
DATABASES = {
    # Tente de lire DATABASE_URL depuis .env (ou variables d'environnement système)
    # Si non trouvé, utilise SQLite par défaut.
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600 # Optionnel: durée de vie des connexions
    )
}


LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Fichiers statiques
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles_build' / 'static' # Pour collectstatic
# Optionnel: si tu utilises WhiteNoise pour compresser et mettre en cache les statiques en prod
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Fichiers médias (gérés par Cloudinary)
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
MEDIA_URL = '/media/' # Les URLs viendront de Cloudinary
MEDIA_ROOT = BASE_DIR / 'media_temp_uploads' # Pour uploads temporaires locaux

# Configuration Cloudinary - lue depuis .env
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': config('CLOUDINARY_API_KEY'),
    'API_SECRET': config('CLOUDINARY_API_SECRET'),
    'SECURE': True,
    'RESOURCE_TYPE': config('CLOUDINARY_RESOURCE_TYPE', default='auto'), # 'auto' est une bonne option
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS Configuration
# En production, tu devras spécifier les origines autorisées via la variable d'env CORS_ALLOWED_ORIGINS
# Exemple dans .env: CORS_ALLOWED_ORIGINS=http://localhost:3000,https://ton-frontend.com
# cors_allowed_origins_str = config('CORS_ALLOWED_ORIGINS', default='http://localhost:3000')
# CORS_ALLOWED_ORIGINS = [origin.strip() for origin in cors_allowed_origins_str.split(',') if origin.strip()]
# Pour l'instant, on utilise CORS_ALLOW_ALL_ORIGINS pour le développement.
CORS_ALLOW_ALL_ORIGINS = config('CORS_ALLOW_ALL_ORIGINS', default=True, cast=bool)
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "https://eduinfo-flame.vercel.app",
]


REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ]
}
# --- END OF FILE app/backend/eduinfo/settings.py ---
