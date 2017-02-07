# -*- coding: utf-8 -*-

import os
import json
import shutil

from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import Http404, HttpResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib import messages

from .forms import AddDirectoryForm, UploadForm, RenameForm


DIR = getattr(settings, 'FILEMAN_DIRECTORY', 'user')


def get_full_path(path):
    return os.path.join(settings.MEDIA_ROOT, DIR, path)


def get_url(path):
    return os.path.join(settings.MEDIA_URL, DIR, path)


def is_safe_path(path):
    return os.path.abspath(get_full_path(path)).startswith(get_full_path(''))


ROW_TEMPLATE = """
  <li class="{type} {state}">
    <div class="item-wrap">
      <a href="{url}{popup_qs}" class="item {type}">
        {name}
      </a>
      <a href="{delete_url}" class="delete">delete</a>
      <a href="{rename_url}" class="rename">rename</a>
    </div>
    {sub}
  </li>
"""
EXTRAS_TEMPLATE = """
  <li class="extras">
    <a class="add-file" href="{add_file_url}{popup_qs}">↑ Upload file</a>
    <a class="add-directory" href="{add_directory_url}{popup_qs}">
      + Create subdirectory</a>
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
        bits.append(ROW_TEMPLATE.format(
            state='active' if sub else '',
            sub=sub,
            popup_qs='?_popup=1' if add_popup_qs else '',
            **data
        ))
    bits.append(EXTRAS_TEMPLATE.format(
        popup_qs='?_popup=1' if is_popup else '',
        **raw_data['extras']
    ))

    return ''.join(bits)


def read_dir(cur_path, expand=False):
    results = []
    for f in os.listdir(get_full_path(cur_path)):
        if f.startswith('.'):
            continue
        sub_path = os.path.join(cur_path, f)
        result = {
            'name': f,
            'rename_url': '%s?path=%s' % (
                reverse('admin:fileman_upload_rename'),
                sub_path,
            ),
            'delete_url': '%s?path=%s' % (
                reverse('admin:fileman_upload_delete'),
                sub_path,
            )
        }
        if os.path.isdir(get_full_path(sub_path)):
            # add trailing slashes to avoid false matches
            if expand is True or os.path.join(expand, '').startswith(
                    os.path.join(sub_path, '')):
                sub_results = read_dir(sub_path, expand)
                url = reverse('admin:fileman_upload_changelist',
                              args=(cur_path, ))
            else:
                sub_results = []
                url = reverse('admin:fileman_upload_changelist',
                              args=(sub_path, ))

            result.update({
                'type': 'directory',
                'path': sub_path,
                'sub_results': sub_results,
                'url': url,
            })
        else:
            result.update({
                'type': 'file',
                'url': get_url(sub_path),
            })
        results.append(result)

    # directories first
    results.sort(key=lambda r: r['type'] != 'directory')

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
    if not os.path.exists(get_full_path(path)):
        raise Http404('Path not found')

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
    <span>{name}</span>
    {sub}
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
        bits.append(DELETE_ROW_TEMPLATE.format(
            sub=sub,
            **data
        ))

    return ''.join(bits)


def delete(request):
    path = request.GET.get('path')
    is_dir = os.path.isdir(get_full_path(path))

    if not is_safe_path(path):
        return redirect('admin:fileman_upload_changelist')

    if request.method == 'POST':
        if is_dir:
            shutil.rmtree(get_full_path(path))
        else:
            os.remove(get_full_path(path))

        msg = '%s was deleted' % path
        messages.add_message(request, messages.INFO, msg)
        return redirect('admin:fileman_upload_changelist')

    if is_dir:
        delete_results = render_delete_results(read_dir(path, True))
    else:
        delete_results = None

    return render(request, 'fileman/delete.html', {
        'app_label': 'fileman',
        'title': 'Delete',
        'delete_results': delete_results,
        'path': path,
    })


def rename(request):
    path = request.GET.get('path')
    old_name = path.split(os.path.sep)[-1]

    if not is_safe_path(path):
        return redirect('admin:fileman_upload_changelist')

    if not os.path.exists(get_full_path(path)):
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
                shutil.move(get_full_path(path), get_full_path(new_path))

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
    if request.method == 'POST':
        form = AddDirectoryForm(request.POST)
        if form.is_valid():
            dirname = form.cleaned_data['name'].replace('/', '-')
            new_dir = os.path.join(path, dirname)
            full_dir = get_full_path(new_dir)

            if is_safe_path(new_dir):
                if not os.path.exists(full_dir):
                    os.mkdir(full_dir)
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
        for f in os.listdir(get_full_path(cur_path)):
            if f.startswith('.'):
                continue

            sub_path = os.path.join(cur_path, f)
            if os.path.isdir(get_full_path(sub_path)):
                sub = read_dir(sub_path)
                if len(sub):
                    results.append({
                        'title': f,
                        'menu': sub,
                    })
            else:
                results.append({
                    'title': f,
                    'value': get_url(sub_path),
                })

        # directories first
        results.sort(key=lambda r: 'menu' not in r)

        return results

    return HttpResponse(json.dumps(read_dir('')),
                        content_type="application/json")
