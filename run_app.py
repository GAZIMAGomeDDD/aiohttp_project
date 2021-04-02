import argparse
import asyncio
import logging

import aiohttp_autoreload
import aiohttp_csrf
import aiohttp_jinja2
import aioredis
import jinja2
from aiohttp import web
from aiohttp_session import session_middleware
from aiohttp_session.redis_storage import RedisStorage

from admin.routes import admin_routes
from admin.views import AdminHandler
from blog.routes import blog_routes
from blog.views import BlogHandler
from ckeditor import setup_ckeditor
from ckeditor.views import upload, file_browser
from core.db import database
from core.messages import messages
from core.middlewares import request_user_middleware, error_middleware
from core.utils import (
    BASE_DIR, TEMPLATES_ROOT,
    get_config, setup_csrf_token
)

try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass


async def init_app(app: web.Application) -> web.Application:
    REDIS_CONFIG = get_config()['redis']
    redis_pool = await aioredis.create_pool(
        (REDIS_CONFIG['host'],
         REDIS_CONFIG['port'])
    )
    middlewares = [
        session_middleware(RedisStorage(redis_pool)),
        request_user_middleware,
        aiohttp_csrf.csrf_middleware,
        error_middleware
    ]
    handlers = (
        AdminHandler(),
        BlogHandler()
    )

    app.middlewares.extend(middlewares)
    app.redis_pool = redis_pool
    aiohttp_jinja2.setup(
        app, enable_async=True,
        loader=jinja2.FileSystemLoader(TEMPLATES_ROOT),
        context_processors=[
            aiohttp_jinja2.request_processor,
            messages
        ],
    )
    app['static_root_url'] = '/static'
    app.database = database
    await setup_ckeditor(app)
    await app.database.connect()
    app.router.add_post('/upload', upload, name='upload')
    app.router.add_get('/file_browser', file_browser, name='file_browser')
    await admin_routes(app, handlers[0])
    await blog_routes(app, handlers[1])
    app.router.add_static('/static', path=str(BASE_DIR / 'static'), name='static')
    app.router.add_static('/uploads', path=str(BASE_DIR / 'uploads'), name='uploads')
    app.on_cleanup.append(cleanup)
    return app


async def cleanup(app: web.Application) -> None:
    app.redis_pool.close()
    await app.redis_pool.wait_closed()
    await app.database.disconnect()


def main():
    app = web.Application(client_max_size=1024 ** 4)
    setup_csrf_token(app)
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--reload',
        action='store_true'
    )
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG)

    if args.reload:
        aiohttp_autoreload.start()

    web.run_app(
        init_app(app),
        host=get_config()['host'],
        port=get_config()['port']
    )


if __name__ == '__main__':
   main()
