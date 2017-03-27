from flask import g, session, url_for, render_template, redirect, flash
from flask_login import login_required, logout_user
from flask_babel import gettext
from web import app, db, oid
from web.forms import LoginForm, EditForm
from web.models import User
from config import POSTS_PER_PAGE


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
                           providers=app.config['OPENID_PROVIDERS'],
                           )


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/user/<nickname>')
@app.route("/user/<nickname>/<int:page>", methods=["GET", "POST", ])
@login_required
def user(nickname, page=1):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash(gettext('User %(nickname)s not found.', nickname=nickname))
        return redirect(url_for('index'))
    posts = user.posts.paginate(page, POSTS_PER_PAGE, False)
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
        flash(gettext("Your changes have been saved."))
        return redirect(url_for('edit'))
    else:
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
    return render_template('edit.html',
                           form=form,
                           )
