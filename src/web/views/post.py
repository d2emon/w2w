from flask import g, url_for, render_template, redirect, flash
from flask_login import login_required
from flask_babel import gettext
from web import app, db
from web.models.post import Post


@app.route('/del/<int:id>')
@login_required
def delete(id):
    post = Post.by_id(id)
    if post.author.id != g.user.id:
        flash(gettext('You cannot delete this post.'))
        return redirect(url_for('index'))
    db.session.delete(post)
    db.session.commit()
    flash(gettext("Your post has been deleted."))
    return redirect(url_for('index'))


@app.route('/search', methods=["POST", ])
def search():
    if not g.search_form.validate_on_submit():
        return redirect(url_for('index'))
    return redirect(url_for('search_results', query=g.search_form.search.data))


@app.route('/search_results/<query>')
def search_results(query):
    results = Post.search(query)
    return render_template('search_results.html',
                           query=query,
                           posts=results,
                           )
