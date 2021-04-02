import io
import os
import aiohttp_csrf
import aiohttp_jinja2
from aiohttp import web
from core.utils import BASE_DIR, random_filename


@aiohttp_csrf.csrf_exempt
async def upload(request):
    data = await request.post()
    image = data.get('upload')
    buf = io.BytesIO(image.file.read())
    filename = image.filename
    extension = filename.split('.')[-1].lower()

    if extension not in ['jpg', 'gif', 'png', 'jpeg']:
        return web.json_response(
            {'error': {'message': 'Только изображение!'},
             'uploaded': 0}
        )

    filename = random_filename(filename)

    with open(f'{BASE_DIR}/uploads/{filename}', 'wb') as f:
        f.write(buf.getvalue())

    return web.json_response(
        {'filename': filename,
         'url': f'/uploads/{filename}',
         'uploaded': 1}
    )


async def file_browser(request):
    files = os.listdir(BASE_DIR / 'uploads')
    images = [
        image for image in files if image.split('.')[-1].lower() in ['jpg', 'gif', 'png', 'jpeg']
    ]
    response = await aiohttp_jinja2.render_template_async(
        'admin/file_browser.html',
        request,
        {'images': images}
    )
    return response
