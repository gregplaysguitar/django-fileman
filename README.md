django-fileman handles user-uploaded static files (images, media, documents)
and integrates with tinymce

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
        file_picker_callback: window.fileman.tinymceFilePickerCallback
        toolbar: 'link media image'
      });
    </script>

TinyMCE 4.x is required.


## Running tests

Use tox (<https://pypi.python.org/pypi/tox>):

    > pip install tox
    > cd path-to/django-fileman
    > tox
