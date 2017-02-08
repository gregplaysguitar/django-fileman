django-fileman adds user-uploaded static files to the django admin 
(i.e. images, media, documents) and integrates with tinymce

[![Circle CI](https://circleci.com/gh/gregplaysguitar/django-fileman.svg?style=svg)](https://circleci.com/gh/gregplaysguitar/django-fileman)
[![codecov](https://codecov.io/gh/gregplaysguitar/django-fileman/branch/master/graph/badge.svg)](https://codecov.io/gh/gregplaysguitar/django-fileman)
[![Latest Version](https://img.shields.io/pypi/v/django-fileman.svg?style=flat)](https://pypi.python.org/pypi/django-fileman/)


Requirements
------------

- Python 2.7, 3.4 or 3.5
- Django 1.8+


Installation
------------

1. Download the source from https://pypi.python.org/pypi/django-fileman/
   and run `python setup.py install`, or:

        > pip install django-fileman

2. Add fileman to `INSTALLED_APPS`
3. Set `FILEMAN_DIRECTORY` to a subdirectory of your `MEDIA_ROOT` (make sure
   it exists, it won't be created). Defaults to `'user'`
4. Make sure the [django admin](https://docs.djangoproject.com/en/1.10/ref/contrib/admin/)
   is installed correctly
   

Usage
-----

You should now have an "Uploads" section in your django admin which allows you to 
manage/upload files under your `FILEMAN_DIRECTORY`.

TinyMCE
-------

There are two options for TinyMCE integration. The simplest is to set TinyMCE's
`link_list` parameter to the url for 'admin:fileman_link_list', i.e.

    tinymce.init({
      selector: 'textarea',
      plugins : 'link',
   	  link_list: '{% url "admin:fileman_link_list" %}',
   	  toolbar: 'link'
    });

this should work with any modern TinyMCE version (from 3 onwards)

Alternately, set TinyMCE's file_picker_callback option to integrate with the
image, media and link dialogs. For example, in your `admin/base_site.html`
template:

    <script type="text/javascript"
            src="{% static 'tinymce/tinymce.min.js' %}"></script>
    {% include 'fileman/static.html' %}
    <script type="text/javascript" charset="utf-8">
      tinymce.init({
        selector: 'textarea',
        plugins : 'link media image',
        file_picker_callback: window.fileman.tinymceFilePickerCallback,
        toolbar: 'link media image'
      });
    </script>

TinyMCE 4.x is required.


## Running tests

Use tox (<https://pypi.python.org/pypi/tox>):

    > pip install tox
    > cd path-to/django-fileman
    > tox
