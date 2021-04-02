from aiohttp import web
from .views import BlogHandler


async def blog_routes(app: web.Application, handler: BlogHandler) -> None:
    app.router.add_get('/', handler.index, name='index')
    app.router.add_get('/contact', handler.contact, name='contact')
    app.router.add_get('/about', handler.about, name='about')
    app.router.add_get('/{key}', handler.post, name='post')
