from redis import Redis

from auther.settings import TOKEN_DB, OTP_DB

tokens = Redis(db=TOKEN_DB, encoding='utf-8')
passwords = Redis(db=OTP_DB, encoding='utf-8')
