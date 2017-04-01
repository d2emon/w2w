from flask import g, url_for, redirect, flash
from flask_login import login_required
from flask_babel import gettext
from web import app, db
from web.models.user import User
from web.emails import follower_notification


@app.route('/follow/<nickname>')
@login_required
def follow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash(gettext('User %(nickname)s not found.', name=nickname))
        return redirect(url_for('index'))
    if user == g.user:
        flash(gettext("Cannot follow yourself!"))
        return redirect(url_for('user', nickname=nickname))
    u = g.user.follow(user)
    if u is None:
        flash(gettext('Cannot follow %(nickname)s!', name=nickname))
        return redirect(url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash(gettext('You are now following %(nickname)s!', name=nickname))
    follower_notification(user, g.user)
    return redirect(url_for('user', nickname=nickname))


@app.route('/unfollow/<nickname>')
@login_required
def unfollow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash(gettext('User %(nickname)s not found.', name=nickname))
        return redirect(url_for('index'))
    if user == g.user:
        flash(gettext("Cannot unfollow yourself!"))
        return redirect(url_for('user', nickname=nickname))
    u = g.user.unfollow(user)
    if u is None:
        flash(gettext('Cannot unfollow %(nickname)s!', name=nickname))
        return redirect(url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash(gettext('You have stopped following %(nickname)s!', name=nickname))
    return redirect(url_for('user', nickname=nickname))
