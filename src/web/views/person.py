from flask import request, render_template, redirect, url_for, flash, jsonify, session
from flask_login import login_required
from flask_babel import gettext
from web import app, db
from web.models import Movie, Person
from web.forms import PersonForm


@app.route('/slug/person', methods=['POST', ])
def person_slug():
    firstname = request.form.get('firstname')
    lastname = request.form.get('lastname')
    fullname = request.form.get('fullname')
    slug = Person.make_slug(firstname, lastname, fullname)
    resp = {
        "firstname": firstname,
        "lastname": lastname,
        "fullname": fullname,
        "slug": slug,
    }
    return jsonify(resp)


@app.route('/person/<slug>')
def view_person(slug=None):
    if slug is None:
        person = None
    else:
        person = Person.by_slug(slug)
    page = 1
    # movies = Movie.by_director(person, order_by=session.get('sort_by')).paginate(page, app.config.get('BRIEF_MOVIES_PER_PAGE', 6), False)
    movies = person.directed.paginate(page, app.config.get('BRIEF_MOVIES_PER_PAGE', 6), False)
    print("Directed", person.directed)
    return render_template('person/view.html',
                           person=person,
                           movies=movies,
                           )


@app.route('/person/add', methods=['POST', 'GET', ])
@login_required
def add_person():
    person = Person()
    form = PersonForm()
    if form.validate_on_submit():
        form.populate_obj(person)
        db.session.add(person)
        db.session.commit()
        flash(gettext("Your changes have been saved."))
        return redirect(url_for('view_person', slug=person.slug))
    return render_template('person/edit.html',
                           form=form,
                           )


@app.route('/person/<slug>/edit', methods=['POST', 'GET', ])
@login_required
def edit_person(slug):
    person = Person.by_slug(slug)
    form = PersonForm(obj=person)
    if form.validate_on_submit():
        form.populate_obj(person)
        db.session.add(person)
        db.session.commit()
        flash(gettext("Your changes have been saved."))
        return redirect(url_for('view_person', slug=person.slug))
    return render_template('person/edit.html',
                           form=form,
                           )
