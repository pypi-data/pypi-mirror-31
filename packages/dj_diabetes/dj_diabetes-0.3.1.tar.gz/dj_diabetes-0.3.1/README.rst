.. image:: https://codeclimate.com/github/foxmask/dj-diabetes/badges/gpa.svg
    :target: https://codeclimate.com/github/foxmask/dj-diabetes
    :alt: Code Climate


.. image:: https://coveralls.io/repos/github/foxmask/dj-diabetes/badge.svg
   :target: https://coveralls.io/github/foxmask/django-th
   :alt: Test Coverage


.. image:: https://scrutinizer-ci.com/g/foxmask/dj-diabetes/badges/quality-score.png?b=master
    :target: https://scrutinizer-ci.com/g/foxmask/dj-diabetes/?branch=master
    :alt: Scrutinizer Code Quality


.. image:: https://travis-ci.org/foxmask/dj-diabetes.svg?branch=master
    :target: https://travis-ci.org/foxmask/dj-diabetes
    :alt: Travis Status


.. image:: http://img.shields.io/pypi/v/dj-diabetes.svg
    :target: https://pypi.python.org/pypi/dj-diabetes/
    :alt: Latest version


.. image:: http://img.shields.io/badge/python-3.6-orange.svg
    :target: https://pypi.python.org/pypi/dj-diabetes/
    :alt: Python version supported


.. image:: http://img.shields.io/badge/license-BSD-blue.svg
    :target: https://pypi.python.org/pypi/dj-diabetes/
    :alt: License


===============
Django Diabetes
===============

Django Diabetes is a personal Glucose Manager

It allows you to follow your daily health

Improvements
============

As I'm not suffering from diabetes, I am very open to suggestions for improvement of this project that I designed for a friend.
For example with the type of examinations, etc...
Currently I maintain the project by evolving versions of python and django.

Requirements:
=============

* Python 3.6
* Django 2
* arrow 0.12.x


Installation:
=============

to get the project, from your virtualenv, do :

.. code:: system

    git clone https://github.com/push-things/dj-diabetes.git

to add the needed modules , do :

.. code:: python

    pip install -r requirements.txt

create a new user who will be the admin :

.. code:: python

   python manage.py createsuperuser

and at least :

.. code:: python

    python manage.py makemigrations dj_diabetes
    python manage.py migrate dj_diabetes
    python manage.py loaddata dj_diabetes_preferences.json
    python manage.py createsuperuser

to startup the database and load the data



.. image:: http://foxmask.trigger-happy.eu/static/2014/06/glucose_manager-1024x771.png
