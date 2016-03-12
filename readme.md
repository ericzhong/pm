# About

PM is a Project Management platform.

# Install Dependencies

    pip install -r requirements.txt
    bower install

# Run

## Init Database

    cd src
    python manage.py migrate
    python init_db.py

## Create Super User

    python manage.py createsuperuser

## Run

    python manage.py runserver 8000