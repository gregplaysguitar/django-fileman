# -*- coding: utf-8 -*-

from django import forms


class AddDirectoryForm(forms.Form):
    name = forms.CharField()


class UploadForm(forms.Form):
    upload = forms.FileField()


class RenameForm(forms.Form):
    new_name = forms.CharField()
