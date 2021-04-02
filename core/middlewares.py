import aiohttp_jinja2
from aiohttp import web
from aiohttp_session import get_session


async def request_user_middleware(app, handler):

    async def middleware(request):
        request.session = await get_session(request)
        request.user = None
        request.is_authenticated = False
        user = request.session.get('user')

        if user is not None:
            request.user = user
            request.is_authenticated = True

        return await handler(request)

    return middleware


async def handle_404(request):
    return aiohttp_jinja2.render_template(
        template_name='blog/404.html',
        request=request,
        context={'title': 404}
    )


async def handle_500(request):
    return aiohttp_jinja2.render_template(
        template_name='blog/500.html',
        request=request,
        context={'title': 500}
    )


def create_error_middleware(overrides):
    @web.middleware
    async def error_middleware(request, handler):

        try:
            return await handler(request)

        except web.HTTPException as ex:
            override = overrides.get(ex.status)

            if override:
                resp = await override(request)
                resp.set_status(ex.status)
                return resp

            raise

        except:
            resp = await overrides[500](request)
            resp.set_status(500)
            return resp

    return error_middleware


error_middleware = create_error_middleware({
        404: handle_404,
        500: handle_500
    })
