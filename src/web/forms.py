from flask_wtf import FlaskForm
from flask_babel import gettext
from wtforms import TextField, BooleanField, TextAreaField, HiddenField, FieldList
from wtforms.validators import Required, Length, Regexp
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from web.models import Genre
from web.models.user import User
from guess_language import guessLanguage


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

        if self.nickname.data != User.make_valid_nickname(self.nickname.data):
            self.nickname.errors.append(gettext("This nickname has invalid characters. Please use letters, numbers and underscores only."))
            return False

        user = User.query.filter_by(nickname=self.nickname.data).first()
        if user is not None:
            self.nickname.errors.append(gettext("This nickname is allready in use. Please choose another one."))
            return False
        return True


class PostForm(FlaskForm):
    post = TextField('post', validators=[Required(), ])

    def language(self):
        language = guessLanguage(self.post.data)
        if language == 'UNKNOWN' or len(language) > 5:
            language = ''
        return language


class SearchForm(FlaskForm):
    search = TextField('search', validators=[Required(), ])


class MovieForm(FlaskForm):
    title = TextField(gettext('Title'), validators=[Required(), ])
    original_title = TextField(gettext('Original title'))
    slug = TextField(gettext('URL'), validators=[
        Required(),
        Length(min=1, max=64),
        Regexp("[a-zA-Z0-9_\-]*"),
    ])
    wiki_url = TextField(gettext('Wiki'))
    genre_ids = FieldList(QuerySelectField(gettext('Genre'), get_label='title', query_factory=lambda: Genre.alphabet(), allow_blank=True), min_entries=1)
    image = HiddenField()
    description = TextAreaField(gettext('Description'))

    def applyGenres(self, genres):
        if genres.count():
            print(genres)
            while len(self.genre_ids) > 0:
                self.genre_ids.pop_entry()
        for genre in genres:
            self.genre_ids.append_entry(genre)


class GenreForm(FlaskForm):
    title = TextField(gettext('Title'), validators=[Required(), ])
    slug = TextField(gettext('URL'), validators=[
        Required(),
        Length(min=1, max=64),
        Regexp("[a-zA-Z0-9_\-]*"),
    ])
    description = TextAreaField(gettext('Description'))
