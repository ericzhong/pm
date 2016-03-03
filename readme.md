# About

PM is a Project Management platform.

# Run

## Init Database

    cd src
    python initial_data.py
    python manage.py makemigrations pm
    python manage.py migrate --no-initial-data
    python manage.py loaddata initial_data.yaml

## Create Super User

    python manage.py createsuperuser

## Run

    python manage.py runserver 8000