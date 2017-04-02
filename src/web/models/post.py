from web import app, db
import flask_whooshalchemy as whooshalchemy


class Post(db.Model):
    __searchable__ = ['body', ]

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    language = db.Column(db.String(5))

    def __repr__(self):
        return "<Post {}>".format(self.body)

    # Query shortcuts
    @staticmethod
    def by_id(id):
        return Post.query.get_or_404(id)

    def search(query):
        return Post.query.whoosh_search(query, app.config.get('MAX_SEARCH_RESULTS', 100)).all()


whooshalchemy.whoosh_index(app, Post)
