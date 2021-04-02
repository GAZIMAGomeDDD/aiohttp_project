import aiohttp_csrf
import yaml
import pathlib
import os
import uuid
from aiohttp import web
from passlib.handlers.sha2_crypt import sha256_crypt


BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
TEMPLATES_ROOT = pathlib.Path(__file__).parent.parent / 'templates'
FORM_FIELD_NAME = '_csrf_token'
COOKIE_NAME = 'csrf_token'


def random_filename(old_filename):
    ext = os.path.splitext(old_filename)[1]
    new_filename = uuid.uuid4().hex + ext
    return new_filename


def setup_csrf_token(app: web.Application) -> None:
    csrf_policy = aiohttp_csrf.policy.FormPolicy(FORM_FIELD_NAME)
    csrf_storage = aiohttp_csrf.storage.CookieStorage(secret_phrase='token', cookie_name=COOKIE_NAME)
    aiohttp_csrf.setup(app, policy=csrf_policy, storage=csrf_storage)


def get_config() -> dict:
    with open(BASE_DIR / 'config' / 'config.yml', 'r') as file:
        config = yaml.safe_load(file)
        return config


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return sha256_crypt.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> sha256_crypt.hash:
    return sha256_crypt.hash(password)


def cyrillic_to_latin(text):
    cyrillic_letters = {
        u'а': u'a',
        u'б': u'b',
        u'в': u'v',
        u'г': u'g',
        u'д': u'd',
        u'е': u'e',
        u'ё': u'e',
        u'ж': u'zh',
        u'з': u'z',
        u'и': u'i',
        u'й': u'y',
        u'к': u'k',
        u'л': u'l',
        u'м': u'm',
        u'н': u'n',
        u'о': u'o',
        u'п': u'p',
        u'р': u'r',
        u'с': u's',
        u'т': u't',
        u'у': u'u',
        u'ф': u'f',
        u'х': u'h',
        u'ц': u'ts',
        u'ч': u'ch',
        u'ш': u'sh',
        u'щ': u'sch',
        u'ъ': u'',
        u'ы': u'y',
        u'ь': u'',
        u'э': u'e',
        u'ю': u'yu',
        u'я': u'ya'
    }
    text = text.replace(' ', '_').lower()
    temp = ''

    for ch in text:
        temp += cyrillic_letters.get(ch, ch)

    return temp
