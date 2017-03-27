#! /bin/bash
echo "Installing app"
git pull
echo "Installing pip dependencies"
pip install -r requirements.txt
echo "Installing bower dependencies"
bower install
echo "Change dir"
cd src
export FLASK_APP=run_server.py
echo "Setting up FLASK_APP to '$FLASK_APP'"
echo "Upgrading db"
flask db upgrade head
# pybabel extract -F babel.cfg -o messages.pot web
# pybabel update -i messages.pot -d web/translations
echo "Compiling translations"
pybabel compile -d web/translations
