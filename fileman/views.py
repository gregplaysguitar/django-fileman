# -*- coding: utf-8 -*-

import os
import json
# import shutil

from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.conf import settings
# from django.http import Http404
from django.http import HttpResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib import messages
from django.template import Template, Context

from .forms import AddDirectoryForm, UploadForm, RenameForm


DIR = getattr(settings, 'FILEMAN_DIRECTORY', 'user')


def get_full_path(path):
    return os.path.join(DIR, path)


def get_url(path):
    return default_storage.url('/'.join((DIR, path)))


def is_safe_path(path):
    return os.path.normpath(get_full_path(path)).startswith(get_full_path(''))


def storage_listdir(path):
    return default_storage.listdir(get_full_path(path))


def storage_exists(path):
    return default_storage.exists(get_full_path(path))


def storage_delete(path):
    return default_storage.delete(get_full_path(path))


ROW_TEMPLATE = """
  <li class="{{ type }} {{ state }}">
    <div class="item-wrap">
      <a href="{{ url }}{{ popup_qs }}" class="item {{ type }}">
        {{ name }}
      </a>
      {% if delete_url %}
        <a href="{{ delete_url }}" class="delete">delete</a>
      {% endif %}
      {% if rename_url %}
        <a href="{{ rename_url }}" class="rename">rename</a>
      {% endif %}
    </div>
    {{ sub|safe }}
  </li>
"""
EXTRAS_TEMPLATE = """
  <li class="extras">
    <a class="add-file" href="{{ add_file_url }}{{ popup_qs }}">
      ↑ Upload file</a>
    <!--
    <a class="add-directory" href="{{ add_directory_url }}{{ popup_qs }}">
      + Create subdirectory</a>
    -->
  </li>
"""


def render_index_results(raw_data, is_popup=False):
    bits = []
    for data in raw_data['list']:
        if data['type'] == 'directory' and data['sub_results']:
            sub = '<ul>{0}</ul>'.format(
                render_index_results(data['sub_results'], is_popup))
        else:
            sub = ''
        add_popup_qs = is_popup and data['type'] == 'directory'
        bits.append(Template(ROW_TEMPLATE).render(Context(dict(
            state='active' if sub else '',
            sub=sub,
            popup_qs='?_popup=1' if add_popup_qs else '',
            **data
        ))))
    bits.append(Template(EXTRAS_TEMPLATE).render(Context(dict(
        popup_qs='?_popup=1' if is_popup else '',
        **raw_data['extras']
    ))))

    return ''.join(bits)


def read_dir(cur_path, expand=False):
    results = []

    dirs, files = storage_listdir(cur_path)

    def get_result(name):
        sub_path = os.path.join(cur_path, name)
        return {
            'name': name,
            'path': sub_path,
            # 'rename_url': '%s?path=%s' % (
            #     reverse('admin:fileman_upload_rename'),
            #     sub_path,
            # ),
        }

    for d in dirs:
        result = get_result(d)
        # add trailing slashes to avoid false matches
        if expand is True or os.path.join(expand, '').startswith(
                os.path.join(result['path'], '')):
            sub_results = read_dir(result['path'], expand)
            url = reverse('admin:fileman_upload_changelist',
                          args=(cur_path, ))
        else:
            sub_results = []
            url = reverse('admin:fileman_upload_changelist',
                          args=(result['path'], ))

        result.update({
            'type': 'directory',
            'sub_results': sub_results,
            'url': url,
        })
        results.append(result)

    for f in files:
        if f.startswith('.'):
            continue

        result = get_result(f)
        result.update({
            'type': 'file',
            'url': get_url(result['path']),
            'delete_url': '%s?path=%s' % (
                reverse('admin:fileman_upload_delete'),
                result['path'],
            )
        })
        results.append(result)

    args = [cur_path] if cur_path else []
    add_file_url = reverse('admin:fileman_upload_upload', args=args)
    add_directory_url = reverse(
        'admin:fileman_upload_add_directory', args=args)

    return {
        'list': results,
        'extras': {
            'add_file_url': add_file_url,
            'add_directory_url': add_directory_url,
        },
    }


def index(request, path=''):
    # full_path = get_full_path(path)
    # if not os.path.exists(full_path):
    #     if path:
    #         raise Http404('Path not found')
    #     else:
    #         raise Exception('FILEMAN_DIRECTORY does not exist')

    is_popup = request.GET.get('_popup', False)
    raw_results = read_dir('', path)

    return render(request, 'fileman/index.html', {
        'app_label': 'fileman',
        'title': 'Uploads',
        'results': render_index_results(raw_results, is_popup=is_popup),
        'is_popup': is_popup,
    })


DELETE_ROW_TEMPLATE = """
  <li>
    <span>{{ name }}</span>
    {{ sub }}
  </li>
"""


def render_delete_results(raw_data):
    bits = []
    for data in raw_data['list']:
        # print (data)
        if data['type'] == 'directory' and data['sub_results']:
            sub = '<ul>{0}</ul>'.format(
                render_delete_results(data['sub_results']))
        else:
            sub = ''
        bits.append(Template(DELETE_ROW_TEMPLATE).render(Context(dict(
            sub=sub,
            **data
        ))))

    return ''.join(bits)


def delete(request):
    path = request.GET.get('path')

    # NOTE don't allow directory deletion, because boto doesn't let us
    # TODO work around this, ala django-filebrowser?
    # filebrowser/storage.py

    if not storage_exists(path) or not is_safe_path(path):
        return redirect('admin:fileman_upload_changelist')

    if request.method == 'POST':
        # if is_dir(path):
        #     shutil.rmtree(get_full_path(path))
        # else:
        #     os.remove(get_full_path(path))

        storage_delete(path)
        msg = '%s was deleted' % path
        messages.add_message(request, messages.INFO, msg)
        return redirect('admin:fileman_upload_changelist')

    # if is_dir:
    #     delete_results = render_delete_results(read_dir(path, True))
    # else:
    #     delete_results = None

    return render(request, 'fileman/delete.html', {
        'app_label': 'fileman',
        'title': 'Delete',
        # 'delete_results': delete_results,
        'path': path,
    })


def rename(request):
    # currently not used - TODO re-enable, see django-filebrowser

    path = request.GET.get('path')
    old_name = path.split(os.path.sep)[-1]

    if not is_safe_path(path):
        return redirect('admin:fileman_upload_changelist')

    if not storage_exists(path):
        msg = "%s doesn't exist" % (path)
        messages.add_message(request, messages.WARNING, msg)
        return redirect('admin:fileman_upload_changelist')

    if request.method == 'POST':
        form = RenameForm(request.POST)
        if form.is_valid():
            new_name = form.cleaned_data['new_name']
            new_path = os.path.join(
                *(path.split(os.path.sep)[:-1] + [new_name]))

            if is_safe_path(new_path):
                # TODO
                # shutil.move(get_full_path(path), get_full_path(new_path))

                msg = '%s was renamed to %s' % (old_name, new_name)
                messages.add_message(request, messages.INFO, msg)
                return redirect('admin:fileman_upload_changelist', new_path)
    else:
        form = RenameForm()

    return render(request, 'fileman/rename.html', {
        'app_label': 'fileman',
        'title': 'Rename',
        'path': path,
        'form': form,
        'old_name': old_name,
    })


def upload(request, path=''):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload = form.cleaned_data['upload']
            file_path = os.path.join(DIR, path, upload.name)
            default_storage.save(file_path, ContentFile(upload.read()))

            url = reverse(
                'admin:fileman_upload_changelist', args=(path, ))
            return redirect(url + '?' + request.GET.urlencode())
    else:
        form = UploadForm()

    return render(request, 'fileman/upload.html', {
        'app_label': 'fileman',
        'title': 'Upload file',
        'form': form,
        'is_popup': request.GET.get('_popup', False),
    })


def add_directory(request, path=''):
    # TODO re-enable

    if request.method == 'POST':
        form = AddDirectoryForm(request.POST)
        if form.is_valid():
            dirname = form.cleaned_data['name']
            new_dir = os.path.join(path, dirname)

            if is_safe_path(new_dir):
                if not storage_exists(new_dir):
                    # TODO
                    # os.mkdir(full_dir)
                    msg = '%s was created' % new_dir
                    messages.add_message(request, messages.INFO, msg)

                url = reverse(
                    'admin:fileman_upload_changelist', args=(new_dir, ))
                return redirect(url + '?' + request.GET.urlencode())
    else:
        form = AddDirectoryForm()

    return render(request, 'fileman/add_directory.html', {
        'app_label': 'fileman',
        'title': 'Create directory',
        'form': form,
        'is_popup': request.GET.get('_popup', False),
    })


def link_list(request):
    """Provide a list of links to uploaded files in a format compatible with
       tinyMCE's link_list parameter - see
       https://www.tinymce.com/docs/plugins/link/#link_list
    """

    def read_dir(cur_path):
        results = []
        dirs, files = storage_listdir(cur_path)

        for d in dirs:
            sub_path = os.path.join(cur_path, d)
            sub = read_dir(sub_path)
            if len(sub):
                results.append({
                    'title': d,
                    'menu': sub,
                })

        for f in files:
            if f.startswith('.'):
                continue

            results.append({
                'title': f,
                'value': get_url(sub_path),
            })

        return results

    return HttpResponse(json.dumps(read_dir('')),
                        content_type="application/json")
