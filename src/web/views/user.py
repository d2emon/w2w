from flask import g, session, url_for, render_template, redirect, flash
from flask_login import login_required, logout_user
from flask_babel import gettext
from web import app, db, oid
from web.forms import LoginForm, EditForm
from web.models.user import User


@app.route('/login', methods=['GET', 'POST', ])
@oid.loginhandler
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])
    return render_template('user/login.html',
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
    posts = user.posts.paginate(page, app.config.get('POSTS_PER_PAGE', 3), False)
    return render_template('user/user.html',
                           user=user,
                           posts=posts,
                           slug=nickname,
                           )


@app.route('/edit', methods=['POST', 'GET', ])
@login_required
def edit():
    form = EditForm(g.user.nickname, obj=g.user)
    if form.validate_on_submit():
        form.populate_obj(g.user)
        db.session.add(g.user)
        db.session.commit()
        flash(gettext("Your changes have been saved."))
        return redirect(url_for('user', nickname=g.user.nickname))
    return render_template('user/edit.html',
                           form=form,
                           )
