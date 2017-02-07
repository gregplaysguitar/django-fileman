# -*- coding: utf-8 -*-

from django.contrib import admin
from django.db import models
from django.conf.urls import url

from . import views


class Upload(models.Model):
    class Meta:
        managed = False


@admin.register(Upload)
class UploadAdmin(admin.ModelAdmin):

    def get_urls(self):
        return [
            url(r'^(?:list/)?$', admin.sites.site.admin_view(views.index), {},
                'fileman_upload_changelist'),

            url(r'^list/_upload$',
                admin.sites.site.admin_view(views.upload), {},
                'fileman_upload_upload'),
            url(r'^list/(.*)/_upload$',
                admin.sites.site.admin_view(views.upload), {},
                'fileman_upload_upload'),

            url(r'^list/_add-dir$',
                admin.sites.site.admin_view(views.add_directory), {},
                'fileman_upload_add_directory'),
            url(r'^list/(.*)/_add-dir$',
                admin.sites.site.admin_view(views.add_directory), {},
                'fileman_upload_add_directory'),

            url(r'^list/(.*)/$', admin.sites.site.admin_view(views.index),
                {}, 'fileman_upload_changelist'),
            url(r'^delete/$', admin.sites.site.admin_view(views.delete), {},
                'fileman_upload_delete'),
            url(r'^rename/$', admin.sites.site.admin_view(views.rename), {},
                'fileman_upload_rename'),

            # url(r'^_tinymce$', admin.sites.site.admin_view(views.index), {},
            #     'fileman_tinymce_dialog'),

            url(r'^_linklist$', admin.sites.site.admin_view(views.link_list),
                {}, 'fileman_link_list'),

        ]
