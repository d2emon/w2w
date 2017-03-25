#! /bin/bash
git pull
pip install -r requirements.txt
bower install
cd src
export FLASK_APP=run_server.py
flask db upgrade head
# pybabel extract -F babel.cfg -o messages.pot web
# pybabel update -i messages.pot -d web/translations
pybabel compile -d web/translations