from collections import namedtuple
from aiohttp import web
from markupsafe import Markup


def error(message: str) -> str:
    return Markup('''
    <div class="alert alert-danger alert-dismissible fade show" role="alert">
                                    %s
        <button type="button" class="close" data-dismiss="alert" aria-label="Close">
            <span aria-hidden="true">&times;</span>
        </button>
    </div>''' % message)


def success(message: str) -> str:
    return Markup('''
    <div class="alert alert-success alert-dismissible fade show" role="alert">
                                    %s
        <button type="button" class="close" data-dismiss="alert" aria-label="Close">
            <span aria-hidden="true">&times;</span>
        </button>
    </div>''' % message)


async def messages(request: web.Request) -> dict:
    Messages = namedtuple('Messages', ['error', 'success'])
    return {'messages': Messages(error=error, success=success)}
