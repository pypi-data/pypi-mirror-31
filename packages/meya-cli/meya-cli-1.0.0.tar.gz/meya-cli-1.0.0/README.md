# meya-cli
Command line utility for connecting with Meya Bot API and services

Installation
------------

1. Download the code

        git clone https://github.com/ekalvi/meya-cli.git
        cd meya-cli

2. Install dependencies ([virtualenv](http://virtualenv.readthedocs.org/en/latest/) is recommended.)

        mkdir env
        virtualenv env
        . env/bin/activate
        pip install --upgrade pip
        pip install -U -r requirements.txt

Tests
-----

        python -m unittest discover tests