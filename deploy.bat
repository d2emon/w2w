echo "Installing app"
git pull
echo "Installing pip dependencies"
pip install -r requirements.txt
echo "Compiling translations"
pybabel compile -d web\translations
echo "Change dir"
cd src
set FLASK_APP=run_server.py
echo "Setting up FLASK_APP to '%FLASK_APP%'"
echo "Upgrading db"
flask db upgrade head
cd ..
echo "Installing bower dependencies"
bower install
