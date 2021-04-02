import asyncio
import io
from datetime import datetime
import asyncpg
from PIL import Image
from aiohttp import web
import aiohttp_jinja2
import aiohttp_csrf
from aiohttp_session import get_session
from paginate import Page
from core.utils import get_password_hash, BASE_DIR, cyrillic_to_latin
from .forms import (
    UserCreationForm, PostCreateForm, LoginForm,
    ValidUsernameRequired, ValidPasswordRequired
)
import sqlalchemy as sa
from core.db import users, posts
from core.utils import random_filename


def login_required(func):
    async def wrapped(self, request, *args, **kwargs):
        self.app = request.app
        self.router = self.app.router
        self.session = await get_session(request)

        if 'user' not in self.session:
            return web.HTTPFound(self.router['login'].url_for())

        return await func(self, request, *args, **kwargs)

    return wrapped


class AdminHandler:
    def __init__(self):
        self.loop = asyncio.get_event_loop()

    @login_required
    async def edit_post(self, request: web.Request) -> web.Response:
        token = await aiohttp_csrf.generate_token(request)
        match_info = request.match_info
        where = posts.c.id == int(match_info['key'])
        query = posts.select().where(where)
        post = await request.app.database.fetch_one(query)
        form = PostCreateForm(data={
            'title': post['title'], 'description': post['description'], 'text': post['text']
        })
        response = await aiohttp_jinja2.render_template_async(
            template_name='admin/create_post.html',
            request=request,
            context={'form': form, 'edit': True, 'key': match_info['key'], 'token': token,
                     'title': f'Изменить пост {post["id"]}'}
        )

        if request.method == 'POST':
            data = await request.post()
            database = request.app.database
            form = PostCreateForm(data)

            if form.validate():
                title = form.title.data
                description = form.description.data
                title_image = form.title_image.data
                text = form.text.data
                buf = io.BytesIO(title_image.file.read())
                filename = random_filename(title_image.filename)

                with open(f'{BASE_DIR}/static/media/posts/{filename}', 'wb') as f:
                    f.write(buf.getvalue())

                await database.execute(
                    posts.update().where(where).values(
                        title=title,
                        description=description,
                        slug=cyrillic_to_latin(title),
                        title_image=f'/media/posts/{filename}',
                        text=text,
                    )
                )

                return web.HTTPFound(
                    request.app.router['admin_posts'].url_for()
                )

            return await aiohttp_jinja2.render_template_async(
                template_name='admin/create_post.html',
                request=request,
                context={'form': form, 'edit': True, 'key': match_info['key'], 'token': token,
                         'title': f'Изменить пост {post["id"]}'}
            )

        return response

    @login_required
    async def create_post(self, request: web.Request) -> web.Response:
        form = PostCreateForm()
        token = await aiohttp_csrf.generate_token(request)
        response = await aiohttp_jinja2.render_template_async(
            template_name='admin/create_post.html',
            request=request,
            context={'form': form, 'token': token, 'title': 'Создать пост'}
        )

        if request.method == 'POST':
            data = await request.post()
            database = request.app.database
            form = PostCreateForm(data)

            if form.validate():
                title = form.title.data
                description = form.description.data
                title_image = form.title_image.data
                text = form.text.data
                buf = io.BytesIO(title_image.file.read())
                filename = random_filename(title_image.filename)

                with open(f'{BASE_DIR}/static/media/posts/{filename}', 'wb') as f:
                    f.write(buf.getvalue())

                await database.execute(
                    posts.insert().values(
                        title=title,
                        description=description,
                        slug=cyrillic_to_latin(title),
                        title_image=f'/media/posts/{filename}',
                        text=text,
                        date=datetime.today(),
                        user=request.user
                    )
                )

                return web.HTTPFound(
                    request.app.router['admin_posts'].url_for()
                )

            return await aiohttp_jinja2.render_template_async(
                template_name='admin/create_post.html',
                request=request,
                context={'form': form, 'token': token, 'title': 'Создать пост'}
            )

        return response

    @login_required
    async def admin(self, request):
        return await aiohttp_jinja2.render_template_async(
            template_name='admin/admin.html',
            request=request,
            context={'title': 'Админка'}
        )

    @login_required
    async def admin_posts(self, request: web.Request) -> web.Response:
        posts_list = await request.app.database.fetch_all(query=posts.select().order_by(posts.c.id))
        page = request.rel_url.query.get('page', '1')
        paged_posts = await self.loop.run_in_executor(
            None, Page, [dict(result) for result in posts_list], page, 10
        )
        response = await aiohttp_jinja2.render_template_async(
            template_name='admin/admin2.html',
            request=request,
            context={'objects_list': paged_posts, 'title': 'Посты'}
        )

        return response

    @login_required
    async def admin_users(self, request: web.Request) -> web.Response:
        users_list = await request.app.database.fetch_all(query=users.select().order_by(users.c.id))
        page = request.rel_url.query.get('page', '1')
        paged_users = await self.loop.run_in_executor(
            None, Page, [dict(result) for result in users_list], page, 10
        )
        response = await aiohttp_jinja2.render_template_async(
            template_name='admin/admin2.html',
            request=request,
            context={'objects_list': paged_users, 'users': True, 'title': 'Пользователи'}
        )

        return response

    async def register(self, request: web.Request) -> web.Response:
        form = UserCreationForm()
        token = await aiohttp_csrf.generate_token(request)
        error = ''
        context = {'token': token, 'form': form,
                   'title': 'Регистрация', 'error': error}
        response = await aiohttp_jinja2.render_template_async(
            template_name='admin/register.html',
            request=request,
            context=context
        )
        if request.method == 'POST':
            data = await request.post()
            form = UserCreationForm(data)

            if form.validate():
                username = form.username.data
                email = form.email.data
                avatar = form.file.data
                password = get_password_hash(form.password2.data)
                database = request.app.database
                filename = random_filename(avatar.filename)

                try:
                    await database.execute(
                        users.insert().values(
                            name=username,
                            avatar=f'/media/users/{filename}',
                            email=email,
                            password=password,
                            date=datetime.today(),
                            disabled=False
                        )
                    )
                    await self.apply_image(
                        self.loop, avatar.file.read(), filename
                    )

                except asyncpg.exceptions.UniqueViolationError as err:
                    error = 'Пользователь с таким email уже зарегистрирован' if 'email' in str(err) \
                        else 'Пользователь с таким именем уже зарегистрирован'
                    context = {'token': token, 'form': form,
                               'title': 'Регистрация', 'error': error}
                    response = await aiohttp_jinja2.render_template_async(
                        template_name='admin/register.html',
                        request=request,
                        context=context
                    )

                    return response

                return web.HTTPFound(
                    request.app.router['login'].url_for()
                )

            context = {'token': token, 'form': form,
                       'title': 'Регистрация', 'error': error}
            response = await aiohttp_jinja2.render_template_async(
                template_name='admin/register.html',
                request=request,
                context=context
            )

            return response

        return web.HTTPFound('/admin') if request.is_authenticated else response

    async def login(self, request: web.Request) -> web.Response:
        if request.is_authenticated:
            raise web.HTTPFound(
                request.app.router['admin'].url_for()
            )

        form = LoginForm()
        token = await aiohttp_csrf.generate_token(request)
        context = {'token': token, 'form': form, 'title': 'Войти'}
        response = await aiohttp_jinja2.render_template_async(
            template_name='admin/login.html',
            request=request,
            context=context,
        )

        if request.method == 'POST':
            data = await request.post()
            form = LoginForm(data)
            username = form.username.data
            password = form.password.data
            database = request.app.database
            where = sa.and_(
                users.c.name == username,
                sa.not_(users.c.disabled)
            )
            query = users.select().where(where)
            user = await database.fetch_one(query=query)
            form.username.validators.clear()
            form.username.validators.append(
                ValidUsernameRequired(user)
            )
            form.password.validators.clear()
            form.password.validators.append(
                ValidPasswordRequired(user, password)
            )

            if form.validate():
                request.session['user'] = user['id']

                return web.HTTPFound(
                    request.app.router['admin'].url_for()
                )

            context = {'token': token, 'form': form, 'title': 'Войти'}
            response = await aiohttp_jinja2.render_template_async(
                template_name='admin/login.html',
                request=request,
                context=context
            )

            return response

        return response

    @login_required
    async def logout(self, request: web.Request) -> web.Response:
        request.session.pop('user')

        return web.HTTPFound(
            request.app.router['index'].url_for()
        )

    @staticmethod
    async def apply_image(loop: asyncio.get_event_loop,
                          img_content: bytes,
                          filename: str) -> None:
        buf = io.BytesIO(img_content)
        img = Image.open(buf)
        new_img = await loop.run_in_executor(None, img.resize, (256, 256), Image.LANCZOS)
        out_buf = io.BytesIO()
        new_img.save(out_buf, format="JPEG")
        with open(f'{BASE_DIR}/static/media/users/{filename}', 'wb') as f:
            f.write(out_buf.getvalue())
