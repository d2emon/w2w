from web import app, db, resize
from gravatar import gravatar
from flask import url_for
import flask_whooshalchemy as whooshalchemy
from sqlalchemy.sql.expression import func
from datetime import datetime
from slugify import slugify


movie_genres = db.Table(
    'movie_genres',
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.id')),
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id')),
)


movie_directors = db.Table(
    'movie_directors',
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.id')),
    db.Column('person_id', db.Integer, db.ForeignKey('person.id')),
)


class Movie(db.Model):
    __searchable__ = ['description', ]

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140), nullable=False)
    original_title = db.Column(db.String(140), nullable=True)
    slug = db.Column(db.String(64), nullable=False, unique=True)
    wiki_url = db.Column(db.String(64), nullable=True)
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
    directors = db.relationship(
        'Person',
        secondary=movie_directors,
        # primaryjoin=(movie_genres.c.movie_id == id),
        # secondaryjoin=(movie_genres.c.genre_id == id),
        backref=db.backref('directed', lazy='dynamic'),
        lazy='dynamic',
    )

    def __repr__(self):
        return "<Movie {}>".format(self.title)

    @staticmethod
    def make_slug(title):
        '''
        Making slug
        '''
        slug = slugify(title)
        if Movie.query.filter_by(slug=slug).first() is None:
            return slug
        version = 2
        while True:
            new_slug = slug + str(version)
            if Movie.query.filter_by(slug=new_slug).first() is None:
                break
            version += 1
        return new_slug

    def normalize(self, user_id):
        if not self.user_id:
            self.user_id = user_id
        self.timestamp = datetime.utcnow()

    def has_genre(self, genre):
        if genre is None:
            return False
        return self.genres.filter(movie_genres.c.genre_id == genre.id).count() > 0

    def add_genre(self, genre):
        if genre is None:
            return self
        if not self.has_genre(genre):
            self.genres.append(genre)
        return self

    def del_genre(self, genre):
        if genre is None:
            return self
        if self.has_genre(genre):
            self.genres.remove(genre)
        return self

    def has_director(self, director):
        if director is None:
            return False
        return self.directors.filter(movie_directors.c.person_id == director.id).count() > 0

    def add_director(self, director):
        print('ADD DIRECTOR', director)

        if director is None:
            return self
        if not self.has_director(director):
            self.directors.append(director)
        return self

    def del_director(self, director):
        if director is None:
            return self
        if self.has_director(director):
            self.directors.remove(director)
        return self

    def update_genres(self, genres):
        for genre in self.genres:
            if genre not in genres:
                self.del_genre(genre)
        for genre in genres:
            if genre:
                self.add_genre(genre)
        return self

    def update_directors(self, directors):
        print("DIRECTORS", directors)
        for director in self.directors:
            if director not in directors:
                self.del_director(director)
        for director in directors:
            if director:
                self.add_director(director)
        print("DIRECTORS", self.directors.all())
        return self

    @property
    def genre_names(self):
        return ', '.join([genre.title.lower() for genre in self.genres]).capitalize()

    def avatar(self, width=128, height=None):
        if self.image:
            try:
                url = url_for('static', filename="upload/{}".format(self.image))
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

    def as_dict(self):
        d = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        d['genres'] = [g.title for g in self.genres]
        d['directors'] = [p.slug for p in self.directors]
        return d

    def from_dict(self, data):
        for k, v in data.items():
            if k in self.__table__.columns:
                setattr(self, k, v)
        db.session.add(self)
        genres = data.get('genres', [])
        for g in genres:
            genre = Genre.query.filter_by(title=g).first()
            if genre is None:
                genre = Genre(title=g)
                db.session.add(genre)
            self.add_genre(genre)
        directors = data.get('directors', [])
        for p in directors:
            director = Person.query.filter_by(slug=p).first()
            if director is None:
                director = Person(slug=p)
                db.session.add(director)
            self.add_director(director)

    @staticmethod
    def from_yml(data, user_id=None):

        movies = []
        for d in data:
            m = Movie()
            # {'slug': 'sekretnye-materialy'}

            slug = d.get('slug')
            slug = Movie.make_slug(slug)

            m.from_dict({
                "title": d.get('title', 'UNTITLED'),
                "slug": slug,
                "wiki_url": d.get('wiki_url'),
                "image": d.get('image'),
                "description": d.get('description'),
                "user_id": user_id,
                "timestamp": d.get('timestamp', datetime.utcnow()),
                "genres": d.get('genres', []),
                "directors": d.get('directors', []),

            })
            movies.append(m)
        return movies

    @property
    def wikipage(self):
        if self.wiki_url:
            return self.wiki_url
        return self.title

    @property
    def wikipedia(self):
        return "https://ru.wikipedia.org/wiki/{}".format(self.wikipage)

    # Query shortcuts
    @staticmethod
    def ordered(order_by=''):
        q = Movie.query
        if order_by == 'alpha':
            q = q.order_by(Movie.title)
        else:
            q = q.order_by(Movie.timestamp.desc())
        return q

    @staticmethod
    def by_slug(slug):
        return Movie.query.filter_by(slug=slug).first_or_404()

    @staticmethod
    def by_genre(genre, order_by=''):
        q = Movie.ordered(order_by)
        if genre is None:
            return q.filter(~Movie.genres.any())
        return q.filter(Movie.genres.contains(genre))

    @staticmethod
    def by_director(director, order_by=''):
        q = Movie.ordered(order_by)
        if director is None:
            return q.filter(~Movie.directors.any())
        return q.filter(Movie.directors.contains(director))

    @staticmethod
    def by_random():
        return Movie.query.order_by(func.random())


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

    @staticmethod
    def make_slug(firstname, lastname='', fullname=''):
        '''
        Making slug
        '''
        p = Person(
            firstname=firstname,
            lastname=lastname,
            fullname=fullname,
        )

        slug = slugify(p.get_name())
        if Person.query.filter_by(slug=slug).first() is None:
            return slug
        version = 2
        while True:
            new_slug = slug + str(version)
            if Person.query.filter_by(slug=new_slug).first() is None:
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
        persons = []
        for d in data:
            p = Person()

            slug = d.get('slug')
            slug = Person.make_slug(slug)

            p.from_dict({
                "firstname": d.get('firstname'),
                "lastname": d.get('lastname'),
                "fullname": d.get('fullname'),
                "slug": slug,
                "description": d.get('description'),
            })
            persons.append(p)
        return persons

    def avatar(self, width=128, height=None):
        return gravatar(self.get_name(), width)

    # Query shortcuts
    @staticmethod
    def by_slug(slug):
        return Person.query.filter_by(slug=slug).first_or_404()

    @staticmethod
    def alphabet():
        return Person.query.order_by(Person.lastname)


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
        '''
        Making slug
        '''
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

    # Query shortcuts
    @staticmethod
    def by_slug(slug):
        return Genre.query.filter_by(slug=slug).first_or_404()

    @staticmethod
    def alphabet():
        return Genre.query.order_by(Genre.title).all()


whooshalchemy.whoosh_index(app, Movie)
whooshalchemy.whoosh_index(app, Person)
whooshalchemy.whoosh_index(app, Genre)
