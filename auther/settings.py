from django.conf import settings

REDIS_DB = settings.AUTHER['REDIS_DB']
MAX_SESSIONS = settings.AUTHER['MAX_SESSIONS']
TOKEN_NAME = settings.AUTHER['TOKEN_NAME']
TOKEN_DOMAIN = settings.AUTHER['TOKEN_DOMAIN']
TOKEN_PATH = settings.AUTHER['TOKEN_PATH']
TOKEN_HTTPONLY = settings.AUTHER['TOKEN_HTTPONLY']
TOKEN_EXPIRE = settings.AUTHER['TOKEN_EXPIRE']
TOKEN_SAMESITE = settings.AUTHER['TOKEN_SAMESITE']
TOKEN_SECURE = settings.AUTHER['TOKEN_SECURE']
LOGIN_PAGE = settings.AUTHER['LOGIN_PAGE']
