from flask import g, session, request, url_for, render_template, redirect, flash
from flask_login import current_user, login_user, login_required, logout_user
from web import app, db, oid, lm
from .forms import LoginForm, EditForm
from .models import User, ROLE_USER


@app.errorhandler(404)
def error404(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def error500(error):
    return render_template('500.html'), 500


@app.route("/")
@app.route("/index")
@login_required
def index():
    user = g.user
    posts = [
        {
            'author': {'nickname': "John"},
            'body': "Beautyfull day in Portland!",
        },
        {
            'author': {'nickname': "Susan"},
            'body': "The Avengers movie was so cool!",
        },
    ]
    return render_template("index.html",
                           title="Home",
                           user=user,
                           posts=posts,
                           )


@app.route('/login', methods=['GET', 'POST', ])
@oid.loginhandler
def login():
    # https://openid-provider.appspot.com/d2emonium
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        # return oidc.user_getfield('email')
        return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])
        # flash('Login requested for OpenID="' + form.openid.data + '", remember_me=' + str(form.remember_me.data))
    return render_template('login.html',
                           title='Sign In',
                           form=form,
                           providers=app.config['OPENID_PROVIDERS'])


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/user/<nickname>')
@login_required
def user(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User ' + nickname + ' not found.')
        return redirect(url_for('index'))
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'},
    ]
    return render_template('user.html',
                           user=user,
                           posts=posts,
                           )


@app.route('/edit', methods=['POST', 'GET', ])
@login_required
def edit():
    form = EditForm(g.user.nickname)
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash("Your changes have been saved.")
        return redirect(url_for('edit'))
    else:
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
    return render_template('edit.html',
                           form=form,
                           )


@app.before_request
def before_request():
    from datetime import datetime
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()


@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "":
        flash("Invalid login. Please try again.")
        return redirect(url_for('login'))
    user = User.query.filter_by(email=resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        nickname = User.make_unique_nickname(nickname)
        user = User(nickname=nickname, email=resp.email, role=ROLE_USER)

        db.session.add(user)
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
