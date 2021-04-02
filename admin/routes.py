from aiohttp import web
from .views import AdminHandler


async def admin_routes(app: web.Application, handler: AdminHandler) -> None:
    app.router.add_get('/login', handler.login, name='login')
    app.router.add_post('/login', handler.login, name='login')
    app.router.add_get('/logout', handler.logout, name='logout')
    app.router.add_get('/register', handler.register, name='register')
    app.router.add_post('/register', handler.register, name='register')
    app.router.add_get('/admin', handler.admin, name='admin')
    app.router.add_get('/admin/posts', handler.admin_posts, name='admin_posts')
    app.router.add_get('/admin/users', handler.admin_users, name='admin_users')
    app.router.add_get('/create_post', handler.create_post, name='create_post')
    app.router.add_post('/create_post', handler.create_post, name='create_post')
    app.router.add_get('/edit_post/{key}', handler.edit_post, name='edit_post')
    app.router.add_post('/edit_post/{key}', handler.edit_post, name='edit_post')
