from flask import request, render_template, redirect, url_for, flash, jsonify, session
from flask_login import login_required
from flask_babel import gettext
from web import app, db
from web.models import Genre, Movie 
from web.forms import GenreForm


@app.route('/slug/genre', methods=['POST', ])
def genre_slug():
    title = request.form.get('title')
    slug = Genre.make_slug(title)
    resp = {
        "title": title,
        "slug": slug,
    }
    return jsonify(resp)


@app.route('/genre/<slug>', methods=['POST', 'GET', ])
def view_genre(slug):
    genre = Genre.query.filter_by(slug=slug).first()
    if genre is None:
        flash(gettext('%(title)s not found.', title=slug))
        return redirect(url_for('index'))
    movies = Movie.ordered(session.get('sort_by')).paginate(1, app.config.get('BRIEF_MOVIES_PER_PAGE', 6), False)
    return render_template('genre/view.html',
                           genre=genre,
                           movies=movies,
                           )


@app.route('/genre/add', methods=['POST', 'GET', ])
@login_required
def add_genre():
    form = GenreForm()
    if form.validate_on_submit():
        genre = Genre()
        form.populate_obj(genre)
        db.session.add(genre)
        db.session.commit()
        flash(gettext("Your changes have been saved."))
        return redirect(url_for('view_genre', slug=genre.slug))
    return render_template('genre/edit.html',
                           form=form,
                           )
    

@app.route('/genre/<slug>/edit', methods=['POST', 'GET', ])
@login_required
def edit_genre(slug):
    genre = Genre.query.filter_by(slug=slug).first()
    if not genre:
        flash(gettext("This genre doesn't exist."))
        return redirect(url_for('add_genre'))
    form = GenreForm(obj=genre)
    if form.validate_on_submit():
        form.populate_obj(genre)
        db.session.add(genre)
        db.session.commit()
        flash(gettext("Your changes have been saved."))
        return redirect(url_for('view_genre', slug=genre.slug))
    return render_template('genre/edit.html',
                           form=form,
                           )