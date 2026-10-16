
import os
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv

# ============================================================
# CAMINHOS E VARIÁVEIS DE AMBIENTE
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

# Carrega o .env da raiz do repositório, se existir
load_dotenv(BASE_DIR.parent / '.env')


# ============================================================
# CONFIGURAÇÕES BÁSICAS
# ============================================================

SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-insecure-nao-use-em-producao'

DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

# Domínios permitidos pelo Django
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get('ALLOWED_HOSTS', '').split(',')
    if host.strip()
]

# Adiciona o domínio do Render sem https://
_render_url = os.environ.get('RENDER_EXTERNAL_URL')

if _render_url:
    _render_host = urlparse(_render_url).hostname

    if _render_host:
        ALLOWED_HOSTS.append(_render_host)

# Permite o acesso local durante o desenvolvimento
if not ALLOWED_HOSTS and DEBUG:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Origens confiáveis para requisições HTTPS e formulários
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',')
    if origin.strip()
]

if _render_url:
    _render_origin = f'https://{urlparse(_render_url).netloc}'

    if _render_origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(_render_origin)


# ============================================================
# APLICAÇÕES
# ============================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'produtos',
    'carrinho',
    'usuarios',
]


# ============================================================
# MIDDLEWARE
# ============================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ============================================================
# URLS
# ============================================================

ROOT_URLCONF = 'ecomerce.urls'

WSGI_APPLICATION = 'ecomerce.wsgi.application'


# ============================================================
# TEMPLATES
# ============================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'carrinho.context_processors.carrinho_ativo',
            ],
        },
    },
]


# ============================================================
# BANCO DE DADOS
# ============================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ============================================================
# VALIDAÇÃO DE SENHA
# ============================================================

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


# ============================================================
# INTERNACIONALIZAÇÃO
# ============================================================

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True


# ============================================================
# ARQUIVOS ESTÁTICOS
# ============================================================

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'assets',
]

STATIC_ROOT = BASE_DIR / 'staticfiles'

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage',
    },
}

WHITENOISE_MAX_AGE = 60 * 60 * 24 * 365


# ============================================================
# E-MAIL
# ============================================================

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# ============================================================
# ARQUIVOS DE MÍDIA
# ============================================================

MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media'


# ============================================================
# SEGURANÇA EM PRODUÇÃO
# ============================================================

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
