# -*- coding: utf-8 -*-

from django.db import models


class Upload(models.Model):
    class Meta:
        managed = False
        default_permissions = []
        permissions = (
            ('change_upload', 'Can upload files'),
        )
