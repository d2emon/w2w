from flask_wtf import FlaskForm
from wtforms import TextField, BooleanField, TextAreaField
from wtforms.validators import Required, Length
from web.models import User


class LoginForm(FlaskForm):
    openid = TextField('openid', validators=[Required(), ])
    remember_me = BooleanField('remember_me', default=False)


class EditForm(FlaskForm):
    nickname = TextField('nickname', validators=[Required(), ])
    about_me = TextAreaField('about_me', validators=[Length(min=0, max=140), ])

    def __init__(self, original_nickname, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        self.original_nickname = original_nickname

    def validate(self):
        if not FlaskForm.validate(self):
            return False

        if self.nickname.data == self.original_nickname:
            return True

        user = User.query.filter_by(nickname=self.nickname.data).first()
        if user is not None:
            self.nickname.errors.append("This nickname is allready in use. Please choose another one.")
            return False
        return True


class PostForm(FlaskForm):
    post = TextField('post', validators=[Required(), ])


class SearchForm(FlaskForm):
    search = TextField('search', validators=[Required(), ])
