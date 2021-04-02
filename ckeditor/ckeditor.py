from markupsafe import Markup


class CKEditor:
    def __init__(self, app=None):
        self.app = app

    async def config(self, name='ckeditor', custom_config='', **kwargs):
        extra_plugins = kwargs.get('extra_plugins', self.app['CKEDITOR_EXTRA_PLUGINS'])

        file_uploader = kwargs.get('file_uploader', self.app['CKEDITOR_FILE_UPLOADER'])
        file_browser = kwargs.get('file_browser', self.app['CKEDITOR_FILE_BROWSER'])

        if file_uploader or file_browser and 'filebrowser' not in extra_plugins:
            extra_plugins.append('filebrowser')

        language = kwargs.get('language', self.app['CKEDITOR_LANGUAGE'])
        height = kwargs.get('height', self.app['CKEDITOR_HEIGHT'])
        width = kwargs.get('width', self.app['CKEDITOR_WIDTH'])

        code_theme = kwargs.get('code_theme', self.app['CKEDITOR_CODE_THEME'])

        return Markup('''
                <script type="text/javascript">
                document.addEventListener("DOMContentLoaded", function (event) {
                    CKEDITOR.replace( "%s", {
                        language: "%s",
                        height: %s,
                        width: %s,
                        codeSnippet_theme: "%s",
                        imageUploadUrl: "%s",
                        filebrowserUploadUrl: "%s",
                        filebrowserBrowseUrl: "%s",
                        extraPlugins: "%s",
                        %s
                    });
                    });
                </script>
                ''' % (
            name, language, height, width, code_theme, file_uploader, file_uploader, file_browser,
            ','.join(extra_plugins), custom_config
        ))


async def setup_ckeditor(app):
    app.setdefault('CKEDITOR_SERVE_LOCAL', True)
    app.setdefault('CKEDITOR_LANGUAGE', '')
    app.setdefault('CKEDITOR_HEIGHT', 400)
    app.setdefault('CKEDITOR_WIDTH', 0)
    app.setdefault('CKEDITOR_CODE_THEME', 'monokai_sublime')
    app.setdefault('CKEDITOR_FILE_UPLOADER', '/upload')
    app.setdefault('CKEDITOR_FILE_BROWSER', '/file_browser')
    app.setdefault('CKEDITOR_UPLOAD_ERROR_MESSAGE', 'Upload failed.')
    app.setdefault('CKEDITOR_EXTRA_PLUGINS', [])
    app.ckeditor = CKEditor(app)
    app.ckeditor_config = await app.ckeditor.config('text')
