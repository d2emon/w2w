from flask import g, url_for, render_template, redirect, flash, request, jsonify, make_response
from flask_login import login_required
from flask_babel import gettext
import yaml
from web import app, db
from web.forms import MovieForm
from web.models import Movie, Genre


@app.route('/slug/movie', methods=['POST', ])
def movie_slug():
    title = request.form.get('title')
    slug = Movie.make_slug(title)
    resp = {
        "title": title,
        "slug": slug,
    }
    return jsonify(resp)


@app.route('/movie/<slug>', methods=['POST', 'GET', ])
def view_movie(slug):
    movie = Movie.by_slug(slug=slug)
    return render_template('movie/view.html',
                           movie=movie,
                           )


@app.route('/movie/add', methods=['POST', 'GET', ])
@login_required
def add_movie():
    movie = Movie()
    form = MovieForm()
    if form.validate_on_submit():
        form.populate_obj(movie)
        movie.normalize(g.user.id)
        db.session.add(movie)

        movie.update_genres([genre.data for genre in form.genre_ids])
        db.session.commit()
        flash(gettext("Your changes have been saved."))
        return redirect(url_for('view_movie', slug=movie.slug))
    return render_template('movie/edit.html',
                           form=form,
                           )


@app.route('/movie/<slug>/edit', methods=['POST', 'GET', ])
@login_required
def edit_movie(slug):
    movie = Movie.by_slug(slug=slug)
    if movie.user_id and g.user.id != movie.user_id:
        flash(gettext("Your can edit only your movies."))
        return redirect(url_for('index'))
    form = MovieForm(obj=movie)
    if form.validate_on_submit():
        form.populate_obj(movie)
        movie.normalize(g.user.id)
        db.session.add(movie)

        movie.update_genres([genre.data for genre in form.genre_ids])
        db.session.commit()
        flash(gettext("Your changes have been saved."))
        return redirect(url_for('view_movie', slug=movie.slug))
    form.applyGenres(movie.genres)
    return render_template('movie/edit.html',
                           form=form,
                           )


@app.route('/random/movie')
def random_movie():
    movie = Movie.by_random().first()
    if movie is None:
        return redirect(url_for('index'))
    return redirect(url_for('view_movie', slug=movie.slug))


@app.route('/export/w2w.yml')
def export_movies():
    movies = Movie.query.all()
    genres = Genre.query.all()
    values = {
        'movies': [m.as_dict() for m in movies],
        'genres': [g.as_dict() for g in genres],
    }
    response = make_response(yaml.dump(values, default_flow_style=False, encoding='utf-8', allow_unicode=True))
    response.headers['Content-Type'] = 'text/yaml'
    response.headers['Content-Disposition'] = 'attachment; filename=w2w.yml'
    # return jsonify(values)
    return response


@app.route('/upload/image/movie', methods=['POST'])
@login_required
def upload_movie_image():
    from werkzeug.utils import secure_filename
    from config import basedir
    import os
    if 'file' not in request.files:
        return jsonify({
            'status': False,
            'Message': gettext('No file uploaded.'),
        })

    f = request.files['file']
    if not f.filename:
        return jsonify({
            'status': False,
            'Message': gettext('No file uploaded.'),
        })

    if f:
        name, ext = os.path.splitext(f.filename)
        name = secure_filename(name)
        if not name:
            name = 'untitled'
        filename = ''.join([name, ext])
        version = 1
        while True:
            full_filename = os.path.join(basedir, 'static', 'upload', filename)
            if not os.path.isfile(full_filename):
                break
            version += 1
            filename = ''.join([name, str(version), ext])
        f.save(full_filename)

        return jsonify({
            'status': True,
            'Message': gettext('Ok.'),
            'filename': filename,
        })
    else:
        return jsonify({
            'status': True,
            'Message': gettext('File %(filename)s is not allowed.', filename=f.filename),
        })
