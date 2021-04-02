from wtforms import (
    Form, StringField, validators, widgets, FileField
)
from ckeditor import CKEditorField
from core.utils import verify_password


def check_password(form: Form, field: StringField) -> None:
    password1 = form.password1.data
    password2 = field.data

    if password1 and password2 and password1 != password2:
        raise validators.ValidationError("Пароли не совпадают!")


class ImageFileRequired:

    def __init__(self, message=None):
        self.message = message

    def __call__(self, form: Form, field: StringField) -> None:
        message = self.message or 'Требуется файл изображения'
        extension = str(field.data.filename).split('.')[-1].lower()

        if extension not in ['jpg', 'png', 'jpeg']:
            raise validators.ValidationError(message)


class ValidUsernameRequired:

    def __init__(self, user, message=None):
        self.message = message
        self.user = user

    def __call__(self, form: Form, field: StringField) -> None:
        message = self.message or 'Пользователь с таким именем не существует!'
        if self.user is None:
            raise validators.ValidationError(message)


class ValidPasswordRequired:

    def __init__(self, user, password, message=None):
        self.message = message
        self.user = user
        self.password = password

    def __call__(self, form: Form, field: StringField) -> None:
        message = self.message or 'Вы ввели не верный пароль!'

        if self.user is not None:
            hashed = self.user['password']
            if not verify_password(self.password, hashed):
                raise validators.ValidationError(message)


class LoginForm(Form):
    username = StringField(
        'Имя пользователя',
        [validators.InputRequired(),
         validators.Length(min=5, max=30)]
    )
    password = StringField(
        'Пароль',
        [validators.InputRequired()],
        widget=widgets.PasswordInput()
    )


class UserCreationForm(Form):

    file = FileField(
        'Аватарка', [
            validators.DataRequired(),
            ImageFileRequired()
        ]
    )

    username = StringField(
        'Имя пользователя',
        [validators.Length(min=5, max=30),
         validators.InputRequired()]
    )

    email = StringField(
        'Email',
        [validators.Email(),
         validators.InputRequired()]
    )

    password1 = StringField(
        'Пароль',
        widget=widgets.PasswordInput()
    )

    password2 = StringField(
        'Повторите пароль',
        [validators.InputRequired(),
         validators.Length(min=5, max=30),
         check_password],
        widget=widgets.PasswordInput()
    )


class PostCreateForm(Form):
    title = StringField(
        'Заглавие',
        [validators.Length(min=30, max=125),
         validators.InputRequired()]
    )
    description = StringField(
        'Описание',
        [validators.Length(min=30, max=250)]
    )
    title_image = FileField(
        'Заглавное изображение',
        [ImageFileRequired(),
         validators.DataRequired()]
    )
    text = CKEditorField(
        'Текст',
        [validators.DataRequired()]
    )
