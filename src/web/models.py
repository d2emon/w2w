from web import app, db
from gravatar import gravatar
import flask_whooshalchemy as whooshalchemy
import yaml
from datetime import datetime


ROLE_USER = 0
ROLE_ADMIN = 1


followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id')),
)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    role = db.Column(db.SmallInteger, default=ROLE_USER)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    movies = db.relationship('Movie', backref='posted_by', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime)
    followed = db.relationship(
        'User',
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic',
    )

    def __repr__(self):  # pragma: no cover
        return "<User {}>".format(self.nickname)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonimous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)
        except NameError:
            return str(self.id)

    def avatar(self, size):
        return gravatar(self.email, size)

    @staticmethod
    def make_valid_nickname(nickname):
        import re
        return re.sub('[^\w]', '', nickname)

    @staticmethod
    def make_unique_nickname(nickname):
        if User.query.filter_by(nickname=nickname).first() is None:
            return nickname
        version = 2
        while True:
            new_nickname = nickname + str(version)
            if User.query.filter_by(nickname=new_nickname).first() is None:
                break
            version += 1
        return new_nickname

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            return self

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return self

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        return Post.query.join(followers, (followers.c.followed_id == Post.user_id)).filter(followers.c.follower_id == self.id).order_by(Post.timestamp.desc())


class Post(db.Model):
    __searchable__ = ['body', ]

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    language = db.Column(db.String(5))

    def __repr__(self):
        return "<Post {}>".format(self.body)


class Movie(db.Model):
    __searchable__ = ['description', ]

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140), nullable=False)
    slug = db.Column(db.String(64), nullable=False, unique=True)
    description = db.Column(db.UnicodeText)
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return "<Movie {}>".format(self.title)

    def avatar(self, size=128):
        return gravatar(self.slug, size)

    @staticmethod
    def make_unique_slug(slug):
        if Movie.query.filter_by(slug=slug).first() is None:
            return slug
        version = 2
        while True:
            new_slug = slug + str(version)
            if Movie.query.filter_by(slug=new_slug).first() is None:
                break
            version += 1
        return new_slug

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def from_dict(self, data):
        for k, v in data.items():
            if k in self.__table__.columns:
                setattr(self, k, v)

    @staticmethod
    def from_yml(filename, user_id=None):
        data = []
        with open(filename) as f:
            data = yaml.load(f)

        movies = []
        for d in data:
            m = Movie()
            # {'slug': 'sekretnye-materialy'}

            slug = d.get('slug')
            slug = Movie.make_unique_slug(slug)

            m.from_dict({
                "title": d.get('title', 'UNTITLED'),
                "slug": slug,
                "description": d.get('description'),
                "user_id": user_id,
                "timestamp": d.get('timestamp', datetime.utcnow())
            })
            movies.append(m)
        return movies

    @property
    def wikipedia(self):
        return "https://ru.wikipedia.org/wiki/{}".format(self.title)


class Person(db.Model):
    __searchable__ = ['firstname', 'lastname', 'fullname', 'description', ]

    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(64))
    lastname = db.Column(db.String(64))
    fullname = db.Column(db.String(140))
    slug = db.Column(db.String(64), nullable=False, unique=True)
    description = db.Column(db.UnicodeText)

    def __repr__(self):
        return "<Person {}>".format(self.get_name())

    def get_name(self):
        if self.fullname:
            return self.fullname
        else:
            return "{} {}".format(self.firstname, self.lastname)

    def avatar(self, size=128):
        return gravatar(self.get_name(), size)


class Genre(db.Model):
    __searchable__ = ['title', 'description', ]

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    slug = db.Column(db.String(64), nullable=False, unique=True)
    description = db.Column(db.UnicodeText)

    def __repr__(self):
        return "<Genre {}>".format(self.title)

    def avatar(self, size=128):
        return gravatar(self.get_name(), size)


whooshalchemy.whoosh_index(app, Post)
whooshalchemy.whoosh_index(app, Movie)
whooshalchemy.whoosh_index(app, Person)
whooshalchemy.whoosh_index(app, Genre)
