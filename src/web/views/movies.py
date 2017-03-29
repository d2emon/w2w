from flask import g, url_for, render_template, redirect, flash, request, jsonify, make_response
from flask_login import login_required
from flask_babel import gettext
from slugify import slugify
from datetime import datetime
import yaml
from web import app, db
from web.forms import MovieForm
from web.models import Movie


@app.route('/movie/<slug>', methods=['POST', 'GET', ])
def view_movie(slug):
    movie = Movie.query.filter_by(slug=slug).first()
    if movie is None:
        flash(gettext('%(title)s not found.', title=slug))
        return redirect(url_for('index'))
    return render_template('movie/view.html',
                           movie=movie,
                           )


@app.route('/movie/add', methods=['POST', 'GET', ])
@login_required
def add_movie():
    form = MovieForm()
    if form.validate_on_submit():
        movie = Movie()
        form.populate_obj(movie)
        movie.timestamp = datetime.utcnow()
        movie.user_id = g.user.id
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
    if not movie:
        flash(gettext("This movie doesn't exist."))
        return redirect(url_for('index'))
    if movie.user_id and g.user.id != movie.user_id:
        flash(gettext("Your can edit only your movies."))
        return redirect(url_for('index'))
    form = MovieForm(obj=movie)
    if form.validate_on_submit():
        form.populate_obj(movie)
        if not movie.user_id:
            movie.user_id = g.user.id
        movie.timestamp = datetime.utcnow()
        db.session.add(movie)
        db.session.commit()
        flash(gettext("Your changes have been saved."))
        return redirect(url_for('index'))
    return render_template('movie/edit.html',
                           form=form,
                           )


@app.route('/random/movie')
def random_movie():
    movie = Movie.by_random().first()
    return redirect(url_for('view_movie', slug=movie.slug))


@app.route('/slug/movie', methods=['POST', ])
def get_slug():
    title = request.form.get('title')
    slug = slugify(title)
    resp = {
        "title": title,
        "slug": slug,
    }
    if Movie.query.filter_by(slug=slug).first() is None:
        return jsonify(resp)
    version = 2
    while True:
        new_slug = slug + str(version)
        if Movie.query.filter_by(slug=new_slug).first() is None:
            break
        version += 1
    resp["slug"] = new_slug
    return jsonify(resp)


@app.route('/export/movies.yml')
def export_movies():
    movies = Movie.query.all()
    values = {
        'movies': [m.as_dict() for m in movies],
    }
    response = make_response(yaml.dump(values, default_flow_style=False, encoding='utf-8', allow_unicode=True))
    response.headers['Content-Type'] = 'text/yaml'
    response.headers['Content-Disposition'] = 'attachment; filename=w2w.yml'
    # return jsonify(values)
    return response
