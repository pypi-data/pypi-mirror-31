
# Government of Canada theme for Concierge
This is the Government of Canada theme for Concierge.

## Quick start

### Install

    pip install concierge_theme_gc

### Configure
Add "concierge_theme_gc" to concierge's INSTALLED_APPS by adding it your
config.py's INSTALLED_APPS_PREFIX array.

    INSTALLED_APPS_PREFIX = [
        'concierge-theme-gc',
        ...
    ]

Make sure to also create and run migrations attached to the theme with:

    python manage.py makemigrations
    python manage.py migrate

## Development
If you plan on making changes to the theme, instead of installing it using
pip, clone the repo and execute the following commands.

    python setup.py develop
    cd concierge_theme_gc
    yarn
    yarn build

If you want to make changes to the javascript or CSS files with live reload,
run the following in a terminal from the concierge_theme_pleio folder:

    yarn watch

## Building
To create a bundle ready for distribution, execute the following commands:

    (cd concierge_theme_gc && yarn && yarn build)
    python setup.py sdist
