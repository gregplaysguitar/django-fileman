# -*- coding: utf-8 -*-
import re

from django import forms


def validate_directory_name(name):
    if re.search(r'[^A-Za-z0-9_\-]', name):
        msg = 'Only letters, numbers, and the characters _ and - are allowed'
        raise forms.ValidationError(msg)
    return name


class AddDirectoryForm(forms.Form):
    name = forms.CharField()

    def clean_name(self):
        return validate_directory_name(self.cleaned_data['name'])


class UploadForm(forms.Form):
    upload = forms.FileField()


class RenameForm(forms.Form):
    new_name = forms.CharField()

    def clean_new_name(self):
        return validate_directory_name(self.cleaned_data['new_name'])
