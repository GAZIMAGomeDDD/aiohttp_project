from aiohttp import web
import aiohttp_jinja2
import asyncio
from paginate import Page
from core.db import users, posts


class BlogHandler:
    async def index(self, request: web.Request) -> web.Response:
        loop = asyncio.get_event_loop()
        page = request.rel_url.query.get('page', '1')
        posts_list = await request.app.database.fetch_all(query=posts.select().order_by(-posts.c.id))
        paged_posts = await loop.run_in_executor(
            None, Page, [dict(result) for result in posts_list], page, 6
        )
        context = {'title': 'salam', 'posts': paged_posts}
        response = aiohttp_jinja2.render_template_async(
            'blog/index.html', request, context
        )

        return await response

    async def post(self, request: web.Request) -> web.Response:
        match_info = request.match_info
        where = posts.c.slug == match_info['key']
        query = posts.select().where(where)
        post = await request.app.database.fetch_one(query)

        if post is None:
            return await aiohttp_jinja2.render_template_async(
                template_name='blog/404.html',
                request=request,
                context={'title': 404},
                status=404)

        context = {'title': post['title'], 'post': post}
        response = aiohttp_jinja2.render_template_async(
            'blog/post.html', request, context
        )

        return await response

    async def about(self, request: web.Request) -> web.Response:
        context = {'title': ''}
        response = aiohttp_jinja2.render_template_async(
            'blog/about.html', request, context
        )

        return await response

    async def contact(self, request: web.Request) -> web.Response:
        context = {'title': ''}
        response = aiohttp_jinja2.render_template_async(
            'blog/contact.html', request, context
        )

        return await response
