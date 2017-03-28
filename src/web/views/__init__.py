from datetime import datetime
from flask import g, session, request, url_for, render_template, redirect, flash, jsonify
from flask_login import current_user, login_user, login_required
from flask_babel import gettext
from flask_sqlalchemy import get_debug_queries
from guess_language import guessLanguage
from web import app, db, oid, lm, babel
from web.forms import PostForm, SearchForm
from web.models import User, ROLE_USER, Post, Movie
from web.translate import translate


@app.errorhandler(404)
def error404(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def error500(error):
    return render_template('500.html'), 500


@app.route("/", methods=["GET", "POST", ])
@app.route("/index", methods=["GET", "POST", ])
@app.route("/index/<int:page>", methods=["GET", "POST", ])
def index(page=1):
    form = PostForm()
    if form.validate_on_submit():
        language = guessLanguage(form.post.data)
        if language == 'UNKNOWN' or len(language) > 5:
            language = ''
        post = Post(
            body=form.post.data,
            timestamp=datetime.utcnow(),
            author=g.user,
            language=language,
        )
        db.session.add(post)
        db.session.commit()
        flash(gettext('Your post is now live!'))
        return redirect(url_for('index'))
    user = g.user
    movies = Movie.query.paginate(1, app.config.get('POSTS_PER_PAGE', 4), False)
    posts = g.user.followed_posts().paginate(page, app.config.get('POSTS_PER_PAGE', 3), False)
    return render_template("index.html",
                           title="Home",
                           user=user,
                           movies=movies,
                           posts=posts,
                           form=form,
                           )


@app.route('/translate', methods=['POST', ])
@login_required
def translatePost():
    t = translate(
        request.form['sourceLang'],
        request.form['destLang'],
        request.form['text'],
    )
    return jsonify(t)


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
    g.movies = Movie.query.paginate(1, app.config.get('POSTS_PER_PAGE', 3), False)
    g.genres = [gettext('Anime')] * 36


@app.after_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= app.config.get('TABASE_QUERY_TIMEOUT', 10):
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
