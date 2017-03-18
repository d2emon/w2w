from flask import render_template
from web import app


@app.route("/")
@app.route("/index")
def index():
    user = {'nickname': "D2emon", }
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