from datetime import datetime
from flask import g, session, request, url_for, render_template, redirect, flash, jsonify
from flask_login import current_user, login_user, login_required
from flask_babel import gettext
from flask_sqlalchemy import get_debug_queries
from werkzeug.utils import secure_filename
from web import app, db, oid, lm, babel
from web.forms import PostForm, SearchForm
from web.models import User, ROLE_USER, Post, Movie, Genre
import os
from config import basedir


@app.errorhandler(404)
def error404(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def error500(error):
    return render_template('500.html'), 500


@app.route("/", methods=["GET", "POST", ])
@app.route("/index", methods=["GET", "POST", ])
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            body=form.post.data,
            timestamp=datetime.utcnow(),
            author=g.user,
            language=form.language(),
        )
        db.session.add(post)
        db.session.commit()
        flash(gettext('Your post is now live!'))
        return redirect(url_for('index'))

    try:
        moviepage = int(request.args.get('movies', 1))
    except ValueError:
        moviepage = 1
    movies = Movie.ordered(session.get('sort_by')).paginate(moviepage, app.config.get('BRIEF_MOVIES_PER_PAGE', 6), False)

    try:
        postpage = int(request.args.get('page', 1))
    except ValueError:
        postpage = 1
    if g.user.is_authenticated:
        q = g.user.followed_posts()
    else:
        q = Post.query
    posts = q.paginate(postpage, app.config.get('POSTS_PER_PAGE', 3), False)

    return render_template("index.html",
                           title="Home",
                           movies=movies,
                           posts=posts,
                           form=form,
                           )


@app.route('/translate', methods=['POST', ])
def translatePost():
    from translate import translate

    try:
        t = translate(
            request.form['sourceLang'],
            request.form['destLang'],
            request.form['text'],
        )
    except ValueError:
        t = gettext("Error: Unexpected error.")
    return jsonify(t)


def import_yml(filename, user_id=None):
    import yaml
    data = dict()
    with open(filename, encoding="utf-8") as f:
        data = yaml.load(f)

    movies = Movie.from_yml(data.get("movies", []), user_id)
    for m in movies:
        db.session.add(m)
    db.session.commit()


@app.route('/import', methods=['GET', 'POST'])
@login_required
def import_file():
    if request.method == 'POST':
        if 'importfile' not in request.files:
            flash(gettext('No file uploaded.'))
            return redirect(request.url)

        f = request.files['importfile']
        if not f.filename:
            flash(gettext('No file uploaded.'))
            return redirect(request.url)

        if f and allowed_file(f.filename):
            filename = secure_filename(f.filename)
            full_filename = os.path.join(basedir, 'tmp', filename)
            f.save(full_filename)

            import_yml(full_filename, g.user.id)
            return redirect(url_for('index'))
        else:
            flash(gettext('File %(filename)s is not allowed.', filename=f.filename))
            return redirect(request.url)
    return render_template("upload.html")


def allowed_file(filename):
    if filename == 'w2w.yml':
        return True
    return False


@app.before_request
def before_request():
    from datetime import datetime
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()

    g.search_form = SearchForm()
    g.locale = get_locale()
    g.movies = Movie.by_random().limit(app.config.get('MOVIES_PER_PAGE', 0)).all()
    g.genres = Genre.query.all()

    sort_by = request.args.get('sort_by')
    if sort_by:
        session['sort_by'] = sort_by
    wld = request.args.get('wld')
    if wld is not None:
        session['wld'] = wld
    nsfw = request.args.get('nsfw')
    if nsfw is not None:
        session['nsfw'] = not (not nsfw)


@app.after_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= app.config.get('DATABASE_QUERY_TIMEOUT', 10):
            app.logger.warning("SLOW QUERY: {}\nParameters: {}\nDuration: {}s\nContext: {}\n".format(query.statement, query.parameters, query.duration, query.context()))
    return response


@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "":
        flash(gettext("Invalid login. Please try again."))
        return redirect(url_for('login'))
    user = User.query.filter_by(email=resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        nickname = User.make_valid_nickname(nickname)
        nickname = User.make_unique_nickname(nickname)
        user = User(nickname=nickname, email=resp.email, role=ROLE_USER)

        db.session.add(user)
        db.session.commit()

        db.session.add(user.follow(user))
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember=remember_me)
    return redirect(request.args.get('next') or url_for('index'))


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(app.config.get('LANGUAGES', dict()).keys())


from web.views.user import *
from web.views.follow import *
from web.views.post import *
from web.views.movies import *
