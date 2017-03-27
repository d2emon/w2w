from flask import url_for, render_template, redirect, flash
from flask_login import login_required
from flask_babel import gettext
from web import app, db
from web.forms import MovieForm
from web.models import Movie


@app.route('/movie/add', methods=['POST', 'GET', ])
@login_required
def add_movie():
    form = MovieForm()
    if form.validate_on_submit():
        movie = Movie()
        form.populate_obj(movie)
        db.session.add(movie)
        db.session.commit()
        flash(gettext("Your changes have been saved."))
        return redirect(url_for('index'))
        # movie = Movie()
    return render_template('movie/edit.html',
                           form=form,
                           )


@app.route('/movie/<slug>/edit', methods=['POST', 'GET', ])
@login_required
def edit_movie(slug):
    movie = Movie.query.filter_by(slug=slug).first()
    form = MovieForm(obj=movie)
    if form.validate_on_submit():
        form.populate_obj(movie)
        db.session.add(movie)
        db.session.commit()
        flash(gettext("Your changes have been saved."))
        return redirect(url_for('index'))
    return render_template('movie/edit.html',
                           form=form,
                           )
