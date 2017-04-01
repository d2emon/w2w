from web import app, db, resize
from gravatar import gravatar
import flask_whooshalchemy as whooshalchemy
from sqlalchemy.sql.expression import func
from datetime import datetime
from slugify import slugify


movie_genres = db.Table(
    'movie_genres',
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.id')),
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id')),
)


class Movie(db.Model):
    __searchable__ = ['description', ]

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140), nullable=False)
    original_title = db.Column(db.String(140), nullable=True)
    slug = db.Column(db.String(64), nullable=False, unique=True)
    image = db.Column(db.String(64), nullable=True)
    description = db.Column(db.UnicodeText)
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    genres = db.relationship(
        'Genre',
        secondary=movie_genres,
        # primaryjoin=(movie_genres.c.movie_id == id),
        # secondaryjoin=(movie_genres.c.genre_id == id),
        backref=db.backref('movies', lazy='dynamic'),
        lazy='dynamic',
    )

    def __repr__(self):
        return "<Movie {}>".format(self.title)

    def has_genre(self, genre):
        return self.genres.filter(movie_genres.c.genre_id == genre.id).count() > 0

    def add_genre(self, genre):
        if not self.has_genre(genre):
            self.genres.append(genre)
        return self

    def del_genre(self, genre):
        if self.has_genre(genre):
            self.genres.remove(genre)
        return self

    @property
    def genre_names(self):
        return ', '.join([genre.title.lower() for genre in self.genres]).capitalize()

    @staticmethod
    def ordered(order_by=''):
        q = Movie.query
        if order_by == 'alpha':
            q = q.order_by(Movie.title)
        else:
            q = q.order_by(Movie.timestamp.desc())
        return q

    @staticmethod
    def by_random():
        return Movie.query.order_by(func.random())

    def avatar(self, width=128, height=None):
        if self.image:
            try:
                url = "static/upload/{}".format(self.image)
                constraints = []
                if width:
                    constraints.append(str(width))
                else:
                    constraints.append('')
                if height:
                    constraints.append(str(height))

                size = "x".join(constraints)
                return resize(url, str(size))
            except:
                pass
        if (height is None) or (width < height):
            size = width
        else:
            size = height
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
        d = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        d['genres'] = [g.title for g in self.genres]
        return d

    def from_dict(self, data):
        for k, v in data.items():
            if k in self.__table__.columns:
                setattr(self, k, v)
        genres = data.get('genres', [])
        for g in genres:
            genre = Genre.query.filter_by(title=g).first()
            if genre is None:
                genre = Genre(title=g)
                db.session.add(genre)
            self.add_genre(genre)

    @staticmethod
    def from_yml(data, user_id=None):

        movies = []
        for d in data:
            m = Movie()
            # {'slug': 'sekretnye-materialy'}

            slug = d.get('slug')
            slug = Movie.make_unique_slug(slug)

            m.from_dict({
                "title": d.get('title', 'UNTITLED'),
                "slug": slug,
                "image": d.get('image'),
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

    @staticmethod
    def make_slug(title):
        slug = slugify(title)
        if Genre.query.filter_by(slug=slug).first() is None:
            return slug
        version = 2
        while True:
            new_slug = slug + str(version)
            if Genre.query.filter_by(slug=new_slug).first() is None:
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
    def from_yml(data):
        genres = []
        for d in data:
            g = Genre()
            # {'slug': 'sekretnye-materialy'}

            slug = d.get('slug')
            slug = Genre.make_slug(slug)

            g.from_dict({
                "title": d.get('title', 'UNTITLED'),
                "slug": slug,
                "description": d.get('description'),
            })
            genres.append(g)
        return genres


whooshalchemy.whoosh_index(app, Movie)
whooshalchemy.whoosh_index(app, Person)
whooshalchemy.whoosh_index(app, Genre)